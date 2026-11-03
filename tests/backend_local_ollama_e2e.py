"""Real local generation + llama.cpp mean-pooled embeddings through the web API.

Requires Ollama with the configured chat model already installed. This script
never downloads models. llama-server and the API bind only to 127.0.0.1; SQLite,
catalogs and provider logs are temporary. All input/catalog records are synthetic.

Run inside the isolated web dependency environment:
    python tests/backend_local_ollama_e2e.py
"""
from __future__ import annotations

import json
import math
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "src" / "web"
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = os.environ.get("PSICOIA_LOCAL_MODEL", "phi4-mini:3.8b")
FIXTURE_DIR = ROOT / "tests/fixtures/block11"
LANGUAGE_FIXTURE = FIXTURE_DIR / "language_cases.json"
RETRIEVAL_FIXTURE = FIXTURE_DIR / "retrieval_docs.json"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def expect(response: httpx.Response, status: int, label: str) -> httpx.Response:
    assert response.status_code == status, f"{label}: expected {status}, got {response.status_code}: {response.text}"
    return response


def installed_ollama_model(model: str) -> tuple[Path, Path]:
    """Resolve an already-installed Ollama model layer and local llama-server."""
    ollama = shutil.which("ollama")
    if not ollama:
        raise RuntimeError("Ollama executable is not installed")
    ollama_path = Path(ollama)
    llama_server = ollama_path.parent / "lib" / "ollama" / "llama-server.exe"
    if not llama_server.is_file():
        raise RuntimeError(f"llama-server is not installed beside Ollama: {llama_server}")

    model_root = Path(os.environ.get("OLLAMA_MODELS", str(Path.home() / ".ollama" / "models")))
    name, _, tag = model.partition(":")
    manifest = model_root / "manifests" / "registry.ollama.ai" / "library" / name / (tag or "latest")
    if not manifest.is_file():
        raise RuntimeError(f"model manifest is absent; no model download will be attempted: {manifest}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    layer = next((item for item in data.get("layers", []) if item.get("mediaType") == "application/vnd.ollama.image.model"), None)
    if layer is None:
        raise RuntimeError(f"no Ollama model layer in manifest: {manifest}")
    blob = model_root / "blobs" / layer["digest"].replace(":", "-")
    if not blob.is_file():
        raise RuntimeError(f"installed model blob is absent: {blob}")
    return llama_server, blob


class ForwardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size)
        payload = json.loads(raw or b"{}")
        request_text = raw.decode("utf-8", errors="replace")
        proxy: ProxyServer = self.server  # type: ignore[assignment]
        start = time.perf_counter()
        with proxy.state_lock:
            fail = proxy.fail_next > 0 and (proxy.fail_match is None or proxy.fail_match in request_text)
            if fail:
                proxy.fail_next -= 1
        if fail:
            status = 503
            response_body = json.dumps({"error": {"message": "synthetic local dependency failure"}}).encode()
        else:
            request = urllib.request.Request(
                proxy.target + self.path,
                data=raw,
                headers={"Content-Type": "application/json", "Authorization": "Bearer loopback-only"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=240) as response:
                    status = response.status
                    response_body = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                response_body = exc.read()
            except Exception as exc:
                status = 502
                response_body = json.dumps({"error": {"message": str(exc)}}).encode()

        try:
            response_json = json.loads(response_body)
        except Exception:
            response_json = {}
        record: dict[str, Any] = {
            "path": self.path,
            "status": status,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "usage": response_json.get("usage", {}),
        }
        if self.path.endswith("/chat/completions"):
            record["messages"] = payload.get("messages", [])
            record["model"] = payload.get("model")
        elif self.path.endswith("/embeddings"):
            record["input"] = payload.get("input", [])
            vectors = response_json.get("data", [])
            record["vector_dimensions"] = [len(item.get("embedding", [])) for item in vectors]
        proxy.records.append(record)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Connection", "close")
        self.close_connection = True
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, *_args: Any) -> None:
        pass


class ProxyServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, _request: Any, _client_address: Any) -> None:
        pass

    def __init__(self, target: str):
        super().__init__(("127.0.0.1", 0), ForwardHandler)
        self.target = target.rstrip("/")
        self.records: list[dict[str, Any]] = []
        self.fail_next = 0
        self.fail_match: str | None = None
        self.state_lock = threading.Lock()
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def close(self) -> None:
        self.shutdown()
        self.server_close()
        self.thread.join(timeout=2)


def start_embedding_server(executable: Path, model_blob: Path, port: int, log_path: Path):
    env = os.environ.copy()
    env["PATH"] = str(executable.parent) + os.pathsep + env.get("PATH", "")
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(executable), "-m", str(model_blob), "--embedding", "--pooling", "mean",
         "--host", "127.0.0.1", "--port", str(port), "-c", "512", "-ngl", "0", "--no-webui"],
        cwd=executable.parent, env=env, stdout=log, stderr=subprocess.STDOUT, text=True,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log.close()
            raise RuntimeError(f"local embedding server exited; inspect {log_path}")
        try:
            if httpx.get(url + "/health", timeout=1).status_code == 200:
                return process, log, url
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    process.terminate()
    log.close()
    raise TimeoutError(f"local embedding server startup timeout; inspect {log_path}")


def create_catalogs(root: Path, fixture: dict[str, Any]) -> None:
    docs = fixture["skill_documents"]
    for stage in ("stage1", "stage2", "stage3"):
        folder = root / "cbt" / stage
        folder.mkdir(parents=True)
        empty = json.dumps({}, ensure_ascii=False)
        (folder / "meta_skills.json").write_text(empty, encoding="utf-8")
        (folder / "micro_skills.json").write_text(empty, encoding="utf-8")
    stage_dir = root / "cbt" / "stage1"
    root_entry = {"1": {"skill_id": "1", "skill_name": "Synthetic CBT skill set", "skill_description": "Eight synthetic retrieval fixtures.", "parent_ids": ["1"], "sect": "cbt"}}
    (stage_dir / "meta_skills.json").write_text(json.dumps(root_entry, ensure_ascii=False), encoding="utf-8")
    for locale in ("en", "pt-BR"):
        localized_meta = {"1": {"skill_id": "1", "skill_name": "Synthetic CBT skill set", "skill_description": "Eight synthetic retrieval fixtures.", "parent_ids": ["1"], "sect": "cbt"}}
        localized_micro: dict[str, dict[str, Any]] = {}
        for document in docs:
            localized_micro[document["id"]] = {
                **document[locale],
                "skill_id": document["id"],
                "parent_ids": ["1", document["id"]],
                "sect": "cbt",
            }
        (stage_dir / f"meta_skills.{locale}.json").write_text(json.dumps(localized_meta, ensure_ascii=False), encoding="utf-8")
        (stage_dir / f"micro_skills.{locale}.json").write_text(json.dumps(localized_micro, ensure_ascii=False), encoding="utf-8")


def wait_backend(process: subprocess.Popen[str], url: str, log_path: Path) -> Any:
    log = log_path.open("w", encoding="utf-8")
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log.close()
            raise RuntimeError(f"backend exited; inspect {log_path}")
        try:
            if httpx.get(url + "/health", timeout=1).status_code == 200:
                return log
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    process.terminate()
    log.close()
    raise TimeoutError(f"backend startup timeout; inspect {log_path}")


def start_backend(port: int, env: dict[str, str], log_path: Path):
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--app-dir", str(WEB_DIR),
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True,
    )
    log = wait_backend(process, f"http://127.0.0.1:{port}", log_path)
    return process, log


def cosine(a: list[float], b: list[float]) -> float:
    denominator = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / denominator if denominator else -1.0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        installed = {item.get("name") for item in httpx.get(OLLAMA_URL + "/api/tags", timeout=3).json().get("models", [])}
    except Exception as exc:
        raise SystemExit(f"BLOCKED: Ollama is not running at {OLLAMA_URL}: {exc}")
    if MODEL not in installed:
        raise SystemExit(f"BLOCKED: {MODEL!r} is not installed; available models: {sorted(installed)}. No model download attempted.")
    try:
        llama_exe, model_blob = installed_ollama_model(MODEL)
    except Exception as exc:
        raise SystemExit(f"BLOCKED: local llama.cpp embedding runtime/model cannot be resolved: {exc}")

    languages: list[dict[str, Any]] = json.loads(LANGUAGE_FIXTURE.read_text(encoding="utf-8"))
    retrieval_fixture: dict[str, Any] = json.loads(RETRIEVAL_FIXTURE.read_text(encoding="utf-8"))
    initial_loaded = {item.get("name") for item in httpx.get(OLLAMA_URL + "/api/ps", timeout=3).json().get("models", [])}

    with tempfile.TemporaryDirectory(prefix="psicoia-block11-local-") as temp_name:
        temp = Path(temp_name)
        skill_root = temp / "synthetic-localized-skills"
        create_catalogs(skill_root, retrieval_fixture)

        embedding_port = free_port()
        embed_start = time.perf_counter()
        embedding_process, embedding_log, embedding_url = start_embedding_server(
            llama_exe, model_blob, embedding_port, temp / "llama-embedding.log"
        )
        embedding_server_start_ms = round((time.perf_counter() - embed_start) * 1000, 1)
        chat_proxy = ProxyServer(OLLAMA_URL)
        embedding_proxy = ProxyServer(embedding_url)

        baseline = yaml.safe_load((ROOT / "configs/baselines/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
        baseline.update({
            "base_url": chat_proxy.url + "/v1", "api_key_env": "BLOCK11_LOCAL_LLM_KEY",
            "model": MODEL, "temperature": 0, "max_tokens": 384,
            "timeout_sec": 180, "max_retries": 1, "retry_sleep_sec": 0,
        })
        baseline_path = temp / "baseline.yaml"
        baseline_path.write_text(yaml.safe_dump(baseline), encoding="utf-8")

        runtime = yaml.safe_load((ROOT / "configs/runtime/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
        runtime.update({
            "output_language": "English",
            "psychagent_skill_base_dir": str(skill_root),
            "psychagent_skill_sects": "cbt",
            "psychagent_embedding_base_url": embedding_proxy.url + "/v1",
            "psychagent_embedding_api_key_env": "BLOCK11_LOCAL_EMBED_KEY",
            "psychagent_embedding_model": MODEL,
            "psychagent_embedding_batch_size": 32,
            "psychagent_embedding_max_retries": 1,
            "psychagent_embedding_retry_sleep_sec": 0,
        })
        runtime_path = temp / "runtime.yaml"

        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(ROOT / "src"),
            "DB_URL": f"sqlite:///{(temp / 'pipeline.sqlite3').as_posix()}",
            "PSYCHAGENT_WEB_BASELINE_CONFIG": str(baseline_path),
            "PSYCHAGENT_WEB_RUNTIME_CONFIG": str(runtime_path),
            "BLOCK11_LOCAL_LLM_KEY": "loopback-only-not-a-secret",
            "BLOCK11_LOCAL_EMBED_KEY": "loopback-only-not-a-secret",
        })
        backend: subprocess.Popen[str] | None = None
        backend_log = None
        backend_url = ""
        timings: list[dict[str, Any]] = []
        persisted: list[dict[str, str]] = []
        failures: list[str] = []
        try:
            # Characterize actual pooled embeddings on the same versioned fixture.
            for case in languages:
                locale = "en" if case["output_language"] == "English" else "pt-BR"
                docs = retrieval_fixture["skill_documents"]
                texts = [f"Trigger:{item[locale]['trigger']}\nWhen_to_Use:{item[locale]['when_to_use']}" for item in docs]
                texts.append(retrieval_fixture["queries"][locale])
                vector_response = expect(httpx.post(embedding_proxy.url + "/v1/embeddings", json={"model": MODEL, "input": texts}, timeout=180), 200, f"real {locale} embeddings")
                vectors = [item["embedding"] for item in vector_response.json()["data"]]
                similarities = [(cosine(vector, vectors[-1]), docs[index]["id"]) for index, vector in enumerate(vectors[:-1])]
                ranking = sorted(similarities, reverse=True)
                assert ranking[0][1] == "10", f"{locale} retrieval fixture target was not top-ranked: {ranking}"

                runtime["output_language"] = case["output_language"]
                runtime_path.write_text(yaml.safe_dump(runtime), encoding="utf-8")
                backend_port = free_port()
                backend_url = f"http://127.0.0.1:{backend_port}"
                chat_begin, embed_begin = len(chat_proxy.records), len(embedding_proxy.records)
                backend_start_at = time.perf_counter()
                backend, backend_log = start_backend(backend_port, env, temp / f"backend-{locale}.log")
                backend_start_ms = (time.perf_counter() - backend_start_at) * 1000
                with httpx.Client(base_url=backend_url, timeout=300) as client:
                    user = expect(client.post("/auth/register", json={"username": f"local-{locale}", "password": "local-only"}), 200, "register").json()
                    auth = {"Authorization": f"Bearer {user['token']}"}
                    invalid = expect(client.post("/courses", headers=auth, json={
                        "school_id": "cbt", "auto_start_first_visit": False, "output_language": "es",
                    }), 422, "unsupported output_language")
                    assert "output_language" in invalid.text
                    course = expect(client.post("/courses", headers=auth, json={
                        "school_id": "cbt", "title": f"synthetic-{locale}", "goal_summary": "synthetic retrieval test",
                        "auto_start_first_visit": False,
                    }), 200, "create synthetic course").json()["course"]

                    start_at = time.perf_counter()
                    visit = expect(client.post(f"/courses/{course['course_id']}/visits", headers=auth, json={
                        "output_language": case["output_language"],
                    }), 200, f"real local session opening {locale}").json()
                    open_ms = (time.perf_counter() - start_at) * 1000
                    assert visit["status"] == "open"

                    query = retrieval_fixture["queries"][locale]
                    start_at = time.perf_counter()
                    result = expect(client.post(f"/visits/{visit['visit_id']}/messages", headers=auth, json={
                        "text": query, "output_language": case["output_language"],
                    }), 200, f"real retrieval + generation {locale}").json()
                    message_ms = (time.perf_counter() - start_at) * 1000
                    answer = result["visit"]["messages"][-1]["text"]
                    lowered = answer.casefold()
                    language_ok = any(marker in lowered for marker in case["expected_markers"]) and not any("\u3400" <= ch <= "\u9fff" for ch in answer)
                    if not language_ok:
                        failures.append(f"{locale}: generated response did not satisfy the language canary or contained Han text")
                    assert "output_language" not in result["visit"], "locale must remain request-time, not alter persisted response schema"

                    # The actual counselor prompt must contain the localized retrieved target, not the other locale's version.
                    target_title = docs[0][locale]["skill_name"]
                    other_locale_title = docs[0]["pt-BR" if locale == "en" else "en"]["skill_name"]
                    generation_requests = [
                        record for record in chat_proxy.records
                        if record["path"].endswith("/chat/completions")
                        and any(query in str(message.get("content", "")) for message in record.get("messages", []))
                    ]
                    assert generation_requests, f"provider did not receive the user query for {locale}"
                    final_system = generation_requests[-1]["messages"][0]["content"]
                    retrieved_titles = [document[locale]["skill_name"] for document in docs if document[locale]["skill_name"] in final_system]
                    context_ok = target_title in final_system and other_locale_title not in final_system
                    if not context_ok:
                        failures.append(f"{locale}: target synthetic context absent from final counselor prompt")
                    assert "{{ output_language }}" not in final_system
                    persisted.append({"visit_id": visit["visit_id"], "answer": answer, "locale": locale})

                    # Retrieval failure must fail closed: do not generate without skill context or persist the user turn.
                    before_failure_count = result["visit"]["message_count"]
                    chat_records_before_retrieval_failure = len(chat_proxy.records)
                    embedding_proxy.fail_next = 3
                    embedding_proxy.fail_match = None
                    retrieval_failure_text = query + " synthetic-embedding-failure"
                    retrieval_failure = client.post(f"/visits/{visit['visit_id']}/messages", headers=auth, json={
                        "text": retrieval_failure_text, "output_language": case["output_language"],
                    })
                    expect(retrieval_failure, 502, f"retrieval failure fails closed {locale}")
                    after_retrieval_failure = expect(
                        client.get(f"/visits/{visit['visit_id']}", headers=auth), 200,
                        f"state after retrieval failure {locale}",
                    ).json()
                    assert after_retrieval_failure["message_count"] == before_failure_count
                    assert all(message["text"] != retrieval_failure_text for message in after_retrieval_failure["messages"])
                    retrieval_failure_generations = [
                        record for record in chat_proxy.records[chat_records_before_retrieval_failure:]
                        if record["path"].endswith("/chat/completions")
                        and any(retrieval_failure_text in str(message.get("content", "")) for message in record.get("messages", []))
                    ]
                    assert not retrieval_failure_generations, "retrieval failure must not generate without skill context"

                    # Provider outage through the loopback proxy: API must return 502 and roll back the user turn.
                    count_before_generation_failure = after_retrieval_failure["message_count"]
                    failure_text = "provider-failure-canary synthetic request"
                    chat_proxy.fail_next = 4
                    chat_proxy.fail_match = failure_text
                    failed = client.post(f"/visits/{visit['visit_id']}/messages", headers=auth, json={
                        "text": failure_text, "output_language": case["output_language"],
                    })
                    expect(failed, 502, f"generation failure {locale}")
                    current = expect(client.get(f"/visits/{visit['visit_id']}", headers=auth), 200, "state after generation failure").json()
                    assert current["message_count"] == count_before_generation_failure

                    locale_chats = chat_proxy.records[chat_begin:]
                    locale_embeddings = embedding_proxy.records[embed_begin:]
                    successful_chats = [r for r in locale_chats if r["status"] == 200 and r["path"].endswith("/chat/completions")]
                    successful_embeddings = [r for r in locale_embeddings if r["status"] == 200 and r["path"].endswith("/embeddings")]
                    timings.append({
                        "locale": locale,
                        "model": MODEL,
                        "embedding_model_source": "Phi-4-mini-3.8B GGUF via llama.cpp llama-server --embedding --pooling mean (not a dedicated embedding-trained model)",
                        "embedding_dimensions": sorted({d for r in successful_embeddings for d in r.get("vector_dimensions", [])}),
                        "target_top1_cosine": round(ranking[0][0], 6),
                        "next_cosine": round(ranking[1][0], 6),
                        "api_startup_ms": round(backend_start_ms, 1),
                        "session_open_ms": round(open_ms, 1),
                        "message_total_ms": round(message_ms, 1),
                        "chat_calls": len(successful_chats),
                        "chat_tokens": [{"prompt": r.get("usage", {}).get("prompt_tokens"), "completion": r.get("usage", {}).get("completion_tokens")} for r in successful_chats],
                        "embedding_batches": [{"texts": len(r.get("input", [])), "dimensions": r.get("vector_dimensions"), "elapsed_ms": r["elapsed_ms"]} for r in successful_embeddings],
                        "answer": answer,
                        "retrieved_context": target_title,
                        "context_target_present": context_ok,
                        "prompt_skill_titles": retrieved_titles,
                        "final_system_prompt_excerpt": final_system[-1600:],
                        "language_canary_pass": language_ok,
                        "response_exposed_think_tag": "<think>" in answer.casefold(),
                    })
                backend.terminate()
                backend.wait(timeout=20)
                backend_log.close()
                backend = None
                backend_log = None

            # Database responses are persisted; restart the API but retain both local model servers.
            runtime["output_language"] = "English"
            runtime_path.write_text(yaml.safe_dump(runtime), encoding="utf-8")
            backend_port = free_port()
            backend_url = f"http://127.0.0.1:{backend_port}"
            backend, backend_log = start_backend(backend_port, env, temp / "backend-restart.log")
            with httpx.Client(base_url=backend_url, timeout=180) as restarted:
                for item in persisted:
                    login = expect(restarted.post("/auth/login", json={"username": f"local-{item['locale']}", "password": "local-only"}), 200, "login after restart").json()
                    auth = {"Authorization": f"Bearer {login['token']}"}
                    restored = expect(restarted.get(f"/visits/{item['visit_id']}", headers=auth), 200, "restore model answer").json()
                    assert any(m["role"] == "assistant" and m["text"] == item["answer"] for m in restored["messages"])

            ollama_ps = httpx.get(OLLAMA_URL + "/api/ps", timeout=3).json().get("models", [])
            ps = next((item for item in ollama_ps if item.get("name") == MODEL), {})
            output = {
                "chat_model": MODEL,
                "chat_provider": OLLAMA_URL,
                "chat_model_was_loaded_before_run": MODEL in initial_loaded,
                "embedding_runtime": "llama.cpp llama-server (Ollama-installed binary), --embedding --pooling mean, CPU-only",
                "embedding_model_blob_bytes": model_blob.stat().st_size,
                "embedding_server_start_ms": embedding_server_start_ms,
                "ollama_loaded_model_size_bytes": ps.get("size"),
                "ollama_loaded_model_vram_bytes": ps.get("size_vram"),
                "runs": timings,
                "responses_persisted_after_api_restart": len(persisted),
                "fixtures": [str(LANGUAGE_FIXTURE.relative_to(ROOT)), str(RETRIEVAL_FIXTURE.relative_to(ROOT))],
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            print("LIMIT: embedding vectors use mean pooling on a general Phi model; results are synthetic-fixture evidence only, not embedding-model quality or clinical validation.")
            print("SUBTEST FAILURES:", json.dumps(failures, ensure_ascii=False))
            if failures:
                print("PARTIAL: local generation, vector retrieval, fail-closed rollback, and persistence ran; language/context criteria failed.")
                raise SystemExit(1)
            print("PASS: all local synthetic-fixture subtests completed.")
        finally:
            if backend is not None and backend.poll() is None:
                backend.terminate()
                backend.wait(timeout=20)
            if backend_log is not None:
                backend_log.close()
            chat_proxy.close()
            embedding_proxy.close()
            if embedding_process.poll() is None:
                embedding_process.terminate()
                embedding_process.wait(timeout=20)
            embedding_log.close()


if __name__ == "__main__":
    main()
