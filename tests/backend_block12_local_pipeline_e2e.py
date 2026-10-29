"""Local real-model integration, retrieval metrics, and language-alternation regression.

Requires already-installed Ollama chat and GGUF models plus its local llama-server
binary. No model downloads or paid APIs are used. All catalog/query/visit data is
synthetic and temporary. Run with the isolated web environment:
    python tests/backend_block12_local_pipeline_e2e.py
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
SRC = ROOT / "src"
WEB_DIR = ROOT / "src/web"
sys.path.insert(0, str(SRC))

from sample.backends.base import BackendSettings  # noqa: E402
from sample.backends.openai_api import OpenAIAPIBackend  # noqa: E402
from sample.core.schemas import RuntimeConfig  # noqa: E402
from sample.prompt_manager import PsychAgentPromptManager  # noqa: E402
from sample.skill_manager import SkillManager  # noqa: E402
from web.backend.psychagent_engine import PsychAgentWebBackend  # noqa: E402

OLLAMA_URL = "http://127.0.0.1:11434"
CHAT_MODEL = os.environ.get("PSICOIA_LOCAL_CHAT_MODEL", "qwen3.5:2b")
EMBED_MODEL = os.environ.get("PSICOIA_LOCAL_EMBED_MODEL", "phi4-mini:3.8b")
DOC_FIXTURE = ROOT / "tests/fixtures/block11/retrieval_docs.json"
BENCHMARK_FIXTURE = ROOT / "tests/fixtures/block12/retrieval_benchmark.json"
INTERNAL_MARKERS = ("<think", "</think", "<assessment", "<client_state", "<skill", "<strategy")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def expect(response: httpx.Response, status: int, label: str) -> httpx.Response:
    assert response.status_code == status, f"{label}: expected {status}, got {response.status_code}: {response.text}"
    return response


def installed_ollama_model(model: str) -> tuple[Path, Path]:
    ollama = shutil.which("ollama")
    if not ollama:
        raise RuntimeError("Ollama executable is not installed")
    executable = Path(ollama)
    llama_server = executable.parent / "lib" / "ollama" / "llama-server.exe"
    model_root = Path(os.environ.get("OLLAMA_MODELS", str(Path.home() / ".ollama" / "models")))
    name, _, tag = model.partition(":")
    manifest = model_root / "manifests" / "registry.ollama.ai" / "library" / name / (tag or "latest")
    if not llama_server.is_file() or not manifest.is_file():
        raise RuntimeError(f"local llama-server or installed model manifest missing: {llama_server}, {manifest}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    layer = next((item for item in data.get("layers", []) if item.get("mediaType") == "application/vnd.ollama.image.model"), None)
    if layer is None:
        raise RuntimeError(f"no model layer in installed manifest: {manifest}")
    blob = model_root / "blobs" / layer["digest"].replace(":", "-")
    if not blob.is_file():
        raise RuntimeError(f"model blob missing: {blob}")
    return llama_server, blob


class ForwardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size)
        payload = json.loads(raw or b"{}")
        request_text = raw.decode("utf-8", errors="replace")
        proxy: ProxyServer = self.server  # type: ignore[assignment]
        started = time.perf_counter()
        with proxy.state_lock:
            fail = proxy.fail_next > 0 and (proxy.fail_match is None or proxy.fail_match in request_text)
            if fail:
                proxy.fail_next -= 1
        if fail:
            status = 503
            response_body = json.dumps({"error": {"message": "synthetic loopback dependency failure"}}).encode()
        else:
            request = urllib.request.Request(
                proxy.target + self.path,
                data=raw,
                headers={"Content-Type": "application/json", "Authorization": "Bearer loopback-only"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=240) as response:
                    status, response_body = response.status, response.read()
            except urllib.error.HTTPError as exc:
                status, response_body = exc.code, exc.read()
            except Exception as exc:
                status = 502
                response_body = json.dumps({"error": {"message": str(exc)}}).encode()
        try:
            result = json.loads(response_body)
        except Exception:
            result = {}
        record: dict[str, Any] = {
            "path": self.path,
            "status": status,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "usage": result.get("usage", {}),
        }
        if self.path.endswith("/chat/completions"):
            record["model"] = payload.get("model")
            record["messages"] = payload.get("messages", [])
            choices = result.get("choices", [])
            if choices and isinstance(choices[0], dict):
                message = choices[0].get("message") or {}
                record["response_text"] = message.get("content", "") or ""
                record["reasoning_field_present"] = any(key in message for key in ("reasoning", "reasoning_content", "analysis"))
                record["reasoning_field_length"] = len(str(message.get("reasoning_content") or message.get("reasoning") or message.get("analysis") or ""))
                record["finish_reason"] = choices[0].get("finish_reason")
        elif self.path.endswith("/embeddings"):
            inputs = payload.get("input", [])
            record["inputs"] = inputs if isinstance(inputs, list) else [inputs]
            data = result.get("data", [])
            record["dimensions"] = [len(item.get("embedding", [])) for item in data]
            record["vectors"] = [item.get("embedding", []) for item in data]
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

    def __init__(self, target: str):
        super().__init__(("127.0.0.1", 0), ForwardHandler)
        self.target = target.rstrip("/")
        self.records: list[dict[str, Any]] = []
        self.fail_next = 0
        self.fail_match: str | None = None
        self.state_lock = threading.Lock()
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    def handle_error(self, _request: Any, _client_address: Any) -> None:
        pass

    @property
    def url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def close(self) -> None:
        self.shutdown()
        self.server_close()
        self.thread.join(timeout=2)


def start_embedding_server(executable: Path, blob: Path, port: int, log_path: Path):
    env = os.environ.copy()
    env["PATH"] = str(executable.parent) + os.pathsep + env.get("PATH", "")
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(executable), "-m", str(blob), "--embedding", "--pooling", "mean", "--host", "127.0.0.1",
         "--port", str(port), "-c", "512", "-ngl", "0", "--no-webui"],
        cwd=executable.parent,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log.close()
            raise RuntimeError(f"embedding server exited; inspect {log_path}")
        try:
            if httpx.get(url + "/health", timeout=1).status_code == 200:
                return process, log, url
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    process.terminate()
    log.close()
    raise TimeoutError(f"embedding server startup timeout; inspect {log_path}")


def create_catalogs(root: Path, fixture: dict[str, Any]) -> None:
    for stage in ("stage1", "stage2", "stage3"):
        folder = root / "cbt" / stage
        folder.mkdir(parents=True)
        (folder / "meta_skills.json").write_text("{}", encoding="utf-8")
        (folder / "micro_skills.json").write_text("{}", encoding="utf-8")
    stage_dir = root / "cbt" / "stage1"
    root_item = {"1": {"skill_id": "1", "skill_name": "Synthetic CBT skills", "skill_description": "Synthetic test parent.", "parent_ids": ["1"], "sect": "cbt"}}
    (stage_dir / "meta_skills.json").write_text(json.dumps(root_item, ensure_ascii=False), encoding="utf-8")
    for locale in ("en", "pt-BR"):
        (stage_dir / f"meta_skills.{locale}.json").write_text(json.dumps(root_item, ensure_ascii=False), encoding="utf-8")
        micro = {}
        for document in fixture["skill_documents"]:
            micro[document["id"]] = {
                **document[locale],
                "skill_id": document["id"],
                "parent_ids": ["1", document["id"]],
                "sect": "cbt",
            }
        (stage_dir / f"micro_skills.{locale}.json").write_text(json.dumps(micro, ensure_ascii=False), encoding="utf-8")


def start_backend(port: int, env: dict[str, str], log_path: Path):
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--app-dir", str(WEB_DIR), "--host", "127.0.0.1",
         "--port", str(port), "--log-level", "warning"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    log = log_path.open("w", encoding="utf-8")
    deadline = time.monotonic() + 180
    url = f"http://127.0.0.1:{port}"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log.close()
            raise RuntimeError(f"backend exited; inspect {log_path}")
        try:
            if httpx.get(url + "/health", timeout=1).status_code == 200:
                return process, log
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    process.terminate()
    log.close()
    raise TimeoutError("backend startup timeout")


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a or not b:
        raise RuntimeError(f"cannot compare embedding dimensions {len(a)} and {len(b)}")
    denominator = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / denominator if denominator else -1.0


def localized_catalog_texts(documents: list[dict[str, Any]], locale: str) -> list[str]:
    return [f"Trigger:{doc[locale]['trigger']}\nWhen_to_Use:{doc[locale]['when_to_use']}" for doc in documents]


def localized_catalog_merge_texts(documents: list[dict[str, Any]], locale: str) -> list[str]:
    texts = []
    for document in documents:
        skill = {
            **document[locale],
            "skill_id": document["id"],
            "parent_ids": ["1", document["id"]],
            "sect": "cbt",
        }
        texts.append(json.dumps(
            {key: value for key, value in skill.items() if key in {
                "skill_id", "skill_name", "skill_description", "trigger", "when_to_use", "parent_ids",
            }},
            ensure_ascii=False,
        ))
    return texts


def language_pass(text: str, locale: str) -> bool:
    lowered = text.casefold()
    markers = {
        "en": ("i'm", "you", "we", "let's", "thought", "anxious", "feel", "hello", "welcome", "glad"),
        "pt-BR": ("você", "vamos", "podemos", "sinto", "pensamento", "ansiedade", "juntos", "entendo", "olá", "claro", "bem-vindo", "gostaria"),
    }[locale]
    return any(marker in lowered for marker in markers) and not any("\u3400" <= ch <= "\u9fff" for ch in text)


def has_internal_output(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in INTERNAL_MARKERS)


async def retrieval_metrics(
    *,
    locale: str,
    language: str,
    skill_root: Path,
    embedding_proxy: ProxyServer,
    chat_proxy: ProxyServer,
    benchmark: dict[str, Any],
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    os.environ["BLOCK12_EMBED_KEY"] = "loopback-only-not-a-secret"
    runtime = RuntimeConfig.from_dict({
        "output_language": language,
        "psychagent_skill_base_dir": str(skill_root),
        "psychagent_skill_sects": "cbt",
        "psychagent_embedding_base_url": embedding_proxy.url + "/v1",
        "psychagent_embedding_api_key_env": "BLOCK12_EMBED_KEY",
        "psychagent_embedding_model": EMBED_MODEL,
        "psychagent_embedding_batch_size": 32,
        "psychagent_embedding_max_retries": 1,
        "psychagent_embedding_retry_sleep_sec": 0,
    })
    backend = OpenAIAPIBackend(BackendSettings(
        model=CHAT_MODEL, temperature=0, max_tokens=1024, timeout_sec=300,
        max_retries=1, retry_sleep_sec=0, base_url=chat_proxy.url + "/v1", api_key="loopback-only-not-a-secret",
    ))
    manager = SkillManager(backend=backend, runtime_config=runtime)
    index_begin = len(embedding_proxy.records)
    index_start = time.perf_counter()
    await manager.load_library()
    index_ms = (time.perf_counter() - index_start) * 1000

    goals = {"objective": ["Synthetic retrieval evaluation"]}
    selected_meta, _, selected_ids, _ = await manager.corse_filter(
        "cbt", goals, 1, n=20, model_kwgs={"max_tokens": 256}
    )
    candidates = [micro for item in selected_meta for micro in item.get("micro_skills", [])]
    assert len(candidates) == len(documents), f"{locale} coarse filter returned {len(candidates)} of {len(documents)} synthetic skills; ids={selected_ids}"
    assert {str(item["skill_id"]) for item in candidates} == {item["id"] for item in documents}

    original_embed = manager._embed_by_api
    query_embedding_events: list[dict[str, Any]] = []

    async def traced_embed(texts: list[str]) -> list[list[float]]:
        started = time.perf_counter()
        vectors = await original_embed(texts)
        query_embedding_events.append({
            "inputs": list(texts),
            "vectors": vectors,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
        })
        return vectors

    manager._embed_by_api = traced_embed
    prompt_manager = PsychAgentPromptManager(ROOT / "prompts/psychagent", "cbt")
    rows = []
    query_rows = [item for item in benchmark["queries"] if item["locale"] == locale]
    for query_case in query_rows:
        started = time.perf_counter()
        retrieved, rewrite_trace = await manager.retrive(
            sect="cbt",
            query=query_case["query"],
            session_stage=1,
            session_goals=goals,
            diag_hist=[],
            candidate_skills=candidates,
        )
        retrieval_ms = (time.perf_counter() - started) * 1000
        embedding_event = query_embedding_events[-1]
        assert embedding_event["inputs"] == [query_case["query"]], (
            f"{query_case['id']} query was transformed before embedding: {embedding_event['inputs']!r}"
        )
        query_vector = embedding_event["vectors"][0]
        candidate_dims = {len(item["embedding_to_retrive"]) for item in candidates}
        assert candidate_dims == {len(query_vector)}, f"{locale} mixed index/query dimensions: {candidate_dims} vs {len(query_vector)}"
        scored = sorted(
            ((manager._cosine_similarity(query_vector, item["embedding_to_retrive"]), str(item["skill_id"])) for item in candidates),
            reverse=True,
        )
        ranked_ids = [skill_id for _, skill_id in scored]
        selected_ranked = [str(item["skill_id"]) for item in retrieved]
        assert selected_ranked == ranked_ids[:5], f"{query_case['id']} top-k differs from computed cosine ranking"

        system_prompt = prompt_manager.render(
            "counselor_system",
            client_info={}, history=[], session_stage="Synthetic assessment",
            session_focus=["Synthetic retrieval evaluation"], homework_assigned_from_last_session=[],
            suggested_skills=retrieved, output_language=language,
        )
        system_prompt = PsychAgentWebBackend._append_output_language_contract(system_prompt, language)
        relevant = set(query_case["relevant_ids"])
        prompt_ids = [
            str(item["skill_id"])
            for item in retrieved
            if item["skill_name"] in system_prompt and item["skill_description"] in system_prompt
        ]
        context_hit = bool(relevant.intersection(prompt_ids))
        first_relevant_rank = next((rank for rank, item_id in enumerate(ranked_ids, 1) if item_id in relevant), None)
        rows.append({
            "query_id": query_case["id"],
            "query_language": locale,
            "query_dimension": len(query_vector),
            "query_norm": round(math.sqrt(sum(value * value for value in query_vector)), 6),
            "candidate_count": len(candidates),
            "ranked_ids": ranked_ids,
            "top_k": 5,
            "selected_ids": selected_ranked,
            "expected_ids": sorted(relevant),
            "reciprocal_rank": round(1 / first_relevant_rank, 6) if first_relevant_rank else 0,
            "recall_at_1": bool(relevant.intersection(ranked_ids[:1])),
            "recall_at_3": bool(relevant.intersection(ranked_ids[:3])),
            "recall_at_5": bool(relevant.intersection(ranked_ids[:5])),
            "context_relevant_in_rendered_prompt": context_hit,
            "embedding_query_ms": embedding_event["elapsed_ms"],
            "retrieval_total_ms": round(retrieval_ms, 1),
            "rewrite_skipped_for_locale": rewrite_trace.get("rewrite_skipped") == "localized_query_language_preserved",
        })

    n = len(rows)
    index_records = embedding_proxy.records[index_begin:]
    retrieval_inputs = [value for record in index_records if record["status"] == 200 for value in record.get("inputs", [])]
    expected_index_texts = localized_catalog_texts(documents, locale)
    assert all(text in retrieval_inputs for text in expected_index_texts), f"{locale} localized index inputs missing"
    return {
        "locale": locale,
        "embedding_model": EMBED_MODEL,
        "chat_model_for_coarse_filter": CHAT_MODEL,
        "documents_indexed": len(expected_index_texts),
        "candidate_count_after_coarse_filter": len(candidates),
        "embedding_dimensions": sorted(candidate_dims),
        "indexing_ms": round(index_ms, 1),
        "query_latency_ms_mean": round(sum(row["embedding_query_ms"] for row in rows) / n, 1),
        "query_count": n,
        "recall_at_1": round(sum(row["recall_at_1"] for row in rows) / n, 4),
        "recall_at_3": round(sum(row["recall_at_3"] for row in rows) / n, 4),
        "recall_at_5": round(sum(row["recall_at_5"] for row in rows) / n, 4),
        "mrr": round(sum(row["reciprocal_rank"] for row in rows) / n, 4),
        "context_relevant_rate_in_rendered_prompt": round(sum(row["context_relevant_in_rendered_prompt"] for row in rows) / n, 4),
        "query_traces": rows,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        installed = {item.get("name") for item in httpx.get(OLLAMA_URL + "/api/tags", timeout=3).json().get("models", [])}
    except Exception as exc:
        raise SystemExit(f"BLOCKED: Ollama is not available at {OLLAMA_URL}: {exc}")
    if CHAT_MODEL not in installed or EMBED_MODEL not in installed:
        raise SystemExit(f"BLOCKED: required local models absent; chat={CHAT_MODEL in installed}, embedding={EMBED_MODEL in installed}; no download attempted")
    try:
        llama_exe, embed_blob = installed_ollama_model(EMBED_MODEL)
    except Exception as exc:
        raise SystemExit(f"BLOCKED: no usable installed llama-server/model: {exc}")

    chat_loaded_before = any(item.get("name") == CHAT_MODEL for item in httpx.get(OLLAMA_URL + "/api/ps", timeout=3).json().get("models", []))
    docs_fixture = json.loads(DOC_FIXTURE.read_text(encoding="utf-8"))
    benchmark = json.loads(BENCHMARK_FIXTURE.read_text(encoding="utf-8"))
    language_names = {"en": "English", "pt-BR": "Português (Brasil)"}
    pipeline_started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="psicoia-block12-local-") as tmp_name:
        temp = Path(tmp_name)
        skill_root = temp / "synthetic-localized-skills"
        metric_skill_root = temp / "synthetic-metric-skills"
        create_catalogs(skill_root, docs_fixture)
        create_catalogs(metric_skill_root, docs_fixture)
        embedding_port = free_port()
        embed_start = time.perf_counter()
        embed_process, embed_log, embed_url = start_embedding_server(
            llama_exe, embed_blob, embedding_port, temp / "llama-embedding.log"
        )
        embedding_server_start_ms = round((time.perf_counter() - embed_start) * 1000, 1)
        chat_proxy = ProxyServer(OLLAMA_URL)
        embedding_proxy = ProxyServer(embed_url)
        try:
            # Retrieval metrics use the actual SkillManager, same localized catalogs,
            # real embedding endpoint, real coarse-filter model, and labeled query set.
            metric_results = []
            if os.environ.get("PSICOIA_OPENING_FALLBACK_ONLY") != "1":
                for locale in ("pt-BR", "en"):
                    metric_results.append(asyncio_run(retrieval_metrics(
                        locale=locale,
                        language=language_names[locale],
                        skill_root=metric_skill_root,
                        embedding_proxy=embedding_proxy,
                        chat_proxy=chat_proxy,
                        benchmark=benchmark,
                        documents=docs_fixture["skill_documents"],
                    )))

            if os.environ.get("PSICOIA_RETRIEVAL_ONLY") == "1":
                print(json.dumps({
                    "status": "PASS",
                    "mode": "real_local_embedding_retrieval_benchmark_only",
                    "chat_model_for_coarse_filter": CHAT_MODEL,
                    "embedding_model": EMBED_MODEL,
                    "embedding_server_start_ms": embedding_server_start_ms,
                    "retrieval_metrics": metric_results,
                    "pipeline_wall_time_ms": round((time.perf_counter() - pipeline_started) * 1000, 1),
                }, ensure_ascii=False, indent=2))
                return

            baseline = yaml.safe_load((ROOT / "configs/baselines/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
            baseline.update({
                "base_url": chat_proxy.url + "/v1", "api_key_env": "BLOCK12_CHAT_KEY",
                "model": CHAT_MODEL, "temperature": 0, "max_tokens": 1024,
                "timeout_sec": 300, "max_retries": 1, "retry_sleep_sec": 0,
            })
            baseline_path = temp / "baseline.yaml"
            baseline_path.write_text(yaml.safe_dump(baseline), encoding="utf-8")
            runtime = yaml.safe_load((ROOT / "configs/runtime/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
            runtime.update({
                "output_language": "English",
                "psychagent_skill_base_dir": str(skill_root),
                "psychagent_skill_sects": "cbt",
                "psychagent_embedding_base_url": embedding_proxy.url + "/v1",
                "psychagent_embedding_api_key_env": "BLOCK12_EMBED_KEY",
                "psychagent_embedding_model": EMBED_MODEL,
                "psychagent_embedding_batch_size": 32,
                "psychagent_embedding_max_retries": 1,
                "psychagent_embedding_retry_sleep_sec": 0,
            })
            runtime_path = temp / "runtime.yaml"
            runtime_path.write_text(yaml.safe_dump(runtime), encoding="utf-8")
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": str(ROOT / "src"),
                "DB_URL": f"sqlite:///{(temp / 'block12.sqlite3').as_posix()}",
                "PSYCHAGENT_WEB_BASELINE_CONFIG": str(baseline_path),
                "PSYCHAGENT_WEB_RUNTIME_CONFIG": str(runtime_path),
                "BLOCK12_CHAT_KEY": "loopback-only-not-a-secret",
                "BLOCK12_EMBED_KEY": "loopback-only-not-a-secret",
            })
            app_embed_start = len(embedding_proxy.records)
            app_chat_start = len(chat_proxy.records)
            api_port = free_port()
            api_url = f"http://127.0.0.1:{api_port}"
            startup_at = time.perf_counter()
            app, app_log = start_backend(api_port, env, temp / "backend.log")
            api_start_ms = round((time.perf_counter() - startup_at) * 1000, 1)
            persisted: list[dict[str, Any]] = []
            e2e_rows: list[dict[str, Any]] = []
            try:
                with httpx.Client(base_url=api_url, timeout=300) as client:
                    user = expect(client.post("/auth/register", json={"username": "block12-local", "password": "synthetic-only"}), 200, "register").json()
                    auth = {"Authorization": f"Bearer {user['token']}"}
                    course = expect(client.post("/courses", headers=auth, json={
                        "school_id": "cbt", "title": "synthetic locale alternation", "goal_summary": "synthetic retrieval test",
                        "auto_start_first_visit": False,
                    }), 200, "create course").json()["course"]
                    visit = expect(client.post(f"/courses/{course['course_id']}/visits", headers=auth, json={
                        "output_language": "Português (Brasil)",
                    }), 200, "open PT-BR visit").json()
                    visit_id = visit["visit_id"]
                    opening_status = next(item["text"] for item in visit["messages"] if item["role"] == "system")
                    assert opening_status == "A sessão 1 foi iniciada."
                    opening_answer = next(item["text"] for item in visit["messages"] if item["role"] == "assistant")
                    assert language_pass(opening_answer, "pt-BR"), f"opening response not in requested PT-BR: {opening_answer!r}"
                    assert not has_internal_output(opening_answer)
                    opening_record = next((record for record in reversed(chat_proxy.records) if any(
                        seed in str(message.get("content", ""))
                        for message in record.get("messages", [])
                        for seed in ("这是第1次会话", "This is session 1", "Esta é a sessão 1")
                    )), None)
                    assert opening_record and opening_record.get("response_text"), "opening was not generated by the local model"
                    assert opening_record.get("finish_reason") != "length", "provider truncated opening generation"

                    fallback_course = expect(client.post("/courses", headers=auth, json={
                        "school_id": "cbt", "title": "synthetic opening fallback", "goal_summary": "synthetic failure path",
                        "auto_start_first_visit": False,
                    }), 200, "create fallback course").json()["course"]
                    chat_proxy.fail_next = 4
                    chat_proxy.fail_match = "This is session 1"
                    fallback_opening = expect(client.post(f"/courses/{fallback_course['course_id']}/visits", headers=auth, json={
                        "output_language": "English",
                    }), 200, "localized opening fallback").json()
                    chat_proxy.fail_match = None
                    fallback_visit_id = fallback_opening["visit_id"]
                    fallback_opening_status = next(
                        item["text"] for item in fallback_opening["messages"] if item["role"] == "system"
                    )
                    assert fallback_opening_status == "Session 1 has started."
                    fallback_opening_answer = next(
                        item["text"] for item in fallback_opening["messages"] if item["role"] == "assistant"
                    )
                    assert language_pass(fallback_opening_answer, "en")
                    assert not has_internal_output(fallback_opening_answer)
                    assert fallback_opening_answer.startswith("Hello.")
                    opening_failure_attempts = sum(
                        1 for record in chat_proxy.records if record["status"] == 503
                        and any("This is session 1" in str(message.get("content", "")) for message in record.get("messages", []))
                    )
                    assert opening_failure_attempts == 4
                    if os.environ.get("PSICOIA_OPENING_FALLBACK_ONLY") == "1":
                        app.terminate()
                        app.wait(timeout=20)
                        app_log.close()
                        app, app_log = start_backend(api_port, env, temp / "backend-opening-fallback-restart.log")
                        with httpx.Client(base_url=api_url, timeout=180) as restarted:
                            restored = expect(
                                restarted.get(f"/visits/{fallback_visit_id}", headers=auth), 200,
                                "read localized opening fallback after restart",
                            ).json()
                            assert fallback_opening_answer in [
                                item["text"] for item in restored["messages"] if item["role"] == "assistant"
                            ]
                            assert fallback_opening_status in [
                                item["text"] for item in restored["messages"] if item["role"] == "system"
                            ]
                        print(json.dumps({
                            "status": "PASS",
                            "mode": "localized_opening_fallback_failure_injection",
                            "chat_failure_attempts": opening_failure_attempts,
                            "fallback_answer_language": "English",
                            "fallback_system_status": fallback_opening_status,
                            "fallback_answer": fallback_opening_answer,
                            "persisted_after_restart": True,
                        }, ensure_ascii=False, indent=2))
                        return

                    turns = [
                        {"id": "pt-first", "locale": "pt-BR", "language": "Português (Brasil)", "query": benchmark["queries"][16]},
                        {"id": "en-switch", "locale": "en", "language": "English", "query": benchmark["queries"][0]},
                        {"id": "pt-return", "locale": "pt-BR", "language": "Português (Brasil)", "query": benchmark["queries"][17]},
                    ]
                    for turn in turns:
                        query = turn["query"]["query"]
                        route_start = time.perf_counter()
                        response = expect(client.post(f"/visits/{visit_id}/messages", headers=auth, json={
                            "text": query, "output_language": turn["language"],
                        }), 200, f"real {turn['locale']} turn {turn['id']}").json()
                        route_ms = (time.perf_counter() - route_start) * 1000
                        answer = response["visit"]["messages"][-1]["text"]
                        assert not has_internal_output(answer), f"public response leaked internal markup for {turn['id']}: {answer!r}"
                        assert "output_language" not in response["visit"]

                        relevant_doc = next(item for item in docs_fixture["skill_documents"] if item["id"] == turn["query"]["relevant_ids"][0])
                        expected_title = relevant_doc[turn["locale"]]["skill_name"]
                        generation_requests = [
                            record for record in chat_proxy.records
                            if record["path"].endswith("/chat/completions")
                            and record["status"] == 200
                            and any(query in str(message.get("content", "")) for message in record.get("messages", []))
                            and (record.get("messages") or [{}])[0].get("role") == "system"
                        ]
                        final_request = generation_requests[-1]
                        final_system = final_request["messages"][0]["content"]
                        if not language_pass(answer, turn["locale"]):
                            raise AssertionError(f"wrong response language for {turn['id']}")
                        assert expected_title in final_system, f"retrieved localized skill not in model prompt for {turn['id']}"
                        assert "FINAL LANGUAGE AND OUTPUT CONTRACT" in final_system or "CONTRATO FINAL DE IDIOMA E SAÍDA" in final_system
                        assert turn["language"] in final_system
                        assert final_request.get("finish_reason") != "length", f"provider truncated generation for {turn['id']}"
                        e2e_rows.append({
                            "id": turn["id"], "locale": turn["locale"], "language_pass": True,
                            "target_skill_in_real_prompt": expected_title,
                            "response_length": len(answer), "route_ms": round(route_ms, 1),
                            "prompt_tokens": final_request.get("usage", {}).get("prompt_tokens"),
                            "completion_tokens": final_request.get("usage", {}).get("completion_tokens"),
                            "finish_reason": final_request.get("finish_reason"),
                        })
                        persisted.append({"answer": answer, "locale": turn["locale"], "query": query})

                    # Fault injected only into the local embedding proxy; cached index remains intact.
                    before_embedding_failure = response["visit"]["message_count"]
                    before_embedding_chat_records = len(chat_proxy.records)
                    embedding_proxy.fail_next = 3
                    embedding_proxy.fail_match = None
                    failure_recovery_text = "Synthetic embedding outage, please respond in English."
                    recovery_response = client.post(f"/visits/{visit_id}/messages", headers=auth, json={
                        "text": failure_recovery_text, "output_language": "English",
                    })
                    failed_embedding_calls = [r for r in embedding_proxy.records if r["status"] == 503]
                    assert len(failed_embedding_calls) >= 3
                    expect(recovery_response, 502, "embedding failure fails closed")
                    recovered = expect(client.get(f"/visits/{visit_id}", headers=auth), 200, "state after embedding failure").json()
                    assert recovered["message_count"] == before_embedding_failure
                    assert all(message["text"] != failure_recovery_text for message in recovered["messages"])
                    embedding_fallback_chat_calls = [
                        record for record in chat_proxy.records[before_embedding_chat_records:]
                        if any(failure_recovery_text in str(message.get("content", "")) for message in record.get("messages", []))
                    ]
                    assert not embedding_fallback_chat_calls, "retrieval failure must not generate without skill context"
                    embedding_failure_result = "502_fail_closed_and_rolled_back"
                    before_generation_failure = recovered["message_count"]

                    # Two attempts for the main response and two for fallback; transaction must roll back.
                    generation_failure_text = "block12-provider-failure-canary"
                    chat_proxy.fail_next = 4
                    chat_proxy.fail_match = generation_failure_text
                    failed = client.post(f"/visits/{visit_id}/messages", headers=auth, json={
                        "text": generation_failure_text, "output_language": "English",
                    })
                    expect(failed, 502, "generation failure rollback")
                    after_failure = expect(client.get(f"/visits/{visit_id}", headers=auth), 200, "state after failed generation").json()
                    assert after_failure["message_count"] == before_generation_failure
                    assert all(message["text"] != generation_failure_text for message in after_failure["messages"])

                    # All model-produced assistant text, including opening and fallback, is public text only.
                    assert all(message["role"] != "assistant" or not has_internal_output(message["text"]) for message in after_failure["messages"])
                    assert language_pass(opening_answer, "pt-BR"), f"opening response not in requested PT-BR: {opening_answer!r}"

                # API restart: authenticate and retrieve all persisted real-model replies.
                app_first_run_embed_end = len(embedding_proxy.records)
                app.terminate()
                app.wait(timeout=20)
                app_log.close()
                app, app_log = start_backend(api_port, env, temp / "backend-restart.log")
                with httpx.Client(base_url=api_url, timeout=180) as restarted:
                    login = expect(restarted.post("/auth/login", json={"username": "block12-local", "password": "synthetic-only"}), 200, "login after restart").json()
                    auth = {"Authorization": f"Bearer {login['token']}"}
                    restored = expect(restarted.get(f"/visits/{visit_id}", headers=auth), 200, "read persisted visit").json()
                    stored_assistant = [item["text"] for item in restored["messages"] if item["role"] == "assistant"]
                    for item in persisted:
                        assert item["answer"] in stored_assistant
                    assert all(not has_internal_output(text) for text in stored_assistant)
                    restored_fallback = expect(
                        restarted.get(f"/visits/{fallback_visit_id}", headers=auth), 200, "read localized fallback after restart"
                    ).json()
                    assert fallback_opening_answer in [
                        item["text"] for item in restored_fallback["messages"] if item["role"] == "assistant"
                    ]
                    assert fallback_opening_status in [
                        item["text"] for item in restored_fallback["messages"] if item["role"] == "system"
                    ]

                app_records = embedding_proxy.records[app_embed_start:app_first_run_embed_end]
                app_inputs = [value for record in app_records if record["status"] == 200 for value in record.get("inputs", [])]
                for locale in ("en", "pt-BR"):
                    expected_texts = localized_catalog_texts(docs_fixture["skill_documents"], locale)
                    assert all(text in app_inputs for text in expected_texts), f"app did not load isolated {locale} index"
                # One merge-index batch and one retrieval-index batch per locale;
                # switching back to PT-BR must reuse its in-process manager cache.
                locale_index_batches = {
                    locale: {
                        "merge": sum(
                            1 for record in app_records
                            if record["status"] == 200 and len(record.get("inputs", [])) == len(docs_fixture["skill_documents"])
                            and set(localized_catalog_merge_texts(docs_fixture["skill_documents"], locale)).issubset(set(record.get("inputs", [])))
                        ),
                        "retrieval": sum(
                            1 for record in app_records
                            if record["status"] == 200 and len(record.get("inputs", [])) == len(docs_fixture["skill_documents"])
                            and set(localized_catalog_texts(docs_fixture["skill_documents"], locale)).issubset(set(record.get("inputs", [])))
                        ),
                    }
                    for locale in ("en", "pt-BR")
                }
                expected_batches = {"en": {"merge": 1, "retrieval": 1}, "pt-BR": {"merge": 1, "retrieval": 1}}
                assert locale_index_batches == expected_batches, f"locale index/cache batches not isolated: {locale_index_batches}"

                successful_chat_records = [
                    record for record in chat_proxy.records[app_chat_start:]
                    if record["status"] == 200 and record["path"].endswith("/chat/completions")
                ]
                ps = httpx.get(OLLAMA_URL + "/api/ps", timeout=3).json().get("models", [])
                loaded_chat = next((item for item in ps if item.get("name") == CHAT_MODEL), {})
                output = {
                    "status": "PASS",
                    "chat_model": CHAT_MODEL,
                    "embedding_model": EMBED_MODEL,
                    "generation_config": {"temperature": 0, "max_tokens": 1024, "timeout_sec": 300},
                    "embedding_model_type": "general generative model pooled for embeddings; no dedicated embedding model was installed",
                    "embedding_runtime": "Ollama-installed llama-server --embedding --pooling mean, CPU-only",
                    "chat_model_loaded_before_run": chat_loaded_before,
                    "chat_model_loaded_bytes": loaded_chat.get("size"),
                    "chat_model_vram_bytes": loaded_chat.get("size_vram"),
                    "embedding_model_blob_bytes": embed_blob.stat().st_size,
                    "embedding_server_start_ms": embedding_server_start_ms,
                    "backend_api_start_ms": api_start_ms,
                    "pipeline_wall_time_ms": round((time.perf_counter() - pipeline_started) * 1000, 1),
                    "opening_generation": {
                        "language": "pt-BR", "language_pass": True,
                        "response_length": len(opening_answer),
                        "prompt_tokens": (opening_record.get("usage") or {}).get("prompt_tokens"),
                        "completion_tokens": (opening_record.get("usage") or {}).get("completion_tokens"),
                        "finish_reason": opening_record.get("finish_reason"),
                    },
                    "retrieval_metrics": metric_results,
                    "same_instance_language_sequence": [row["locale"] for row in e2e_rows],
                    "e2e_turns": e2e_rows,
                    "localized_opening_fallback": {
                        "provider_failure_attempts": 4,
                        "language_pass": language_pass(fallback_opening_answer, "en"),
                        "persisted_after_restart": True,
                    },
                    "localized_index_batches_in_api": locale_index_batches,
                    "failure_injection": {
                        "embedding_503s": len(failed_embedding_calls),
                        "embedding_failure_result": embedding_failure_result,
                        "embedding_fallback_chat_calls": len(embedding_fallback_chat_calls),
                        "embedding_failure_state_assertions_passed": True,
                        "generation_http_status": 502,
                        "generation_rollback_message_count": before_generation_failure == after_failure["message_count"],
                    },
                    "assistant_messages_persisted_after_restart": len(stored_assistant),
                    "successful_chat_responses": len(successful_chat_records),
                    "chat_usage_totals": {
                        "prompt_tokens": sum((record.get("usage") or {}).get("prompt_tokens", 0) for record in successful_chat_records),
                        "completion_tokens": sum((record.get("usage") or {}).get("completion_tokens", 0) for record in successful_chat_records),
                    },
                    "fixtures": [str(DOC_FIXTURE.relative_to(ROOT)), str(BENCHMARK_FIXTURE.relative_to(ROOT))],
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
                print("PASS: PT-BR -> EN -> PT-BR same-instance real retrieval/generation, localized index isolation, final-only persistence, fail-closed embedding rollback, generation rollback, and restart readback.")
            finally:
                if app.poll() is None:
                    app.terminate()
                    app.wait(timeout=20)
                app_log.close()
        finally:
            chat_proxy.close()
            embedding_proxy.close()
            if embed_process.poll() is None:
                embed_process.terminate()
                embed_process.wait(timeout=20)
            embed_log.close()


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    main()
