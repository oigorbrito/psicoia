"""Loopback end-to-end contract check for the web API.

Runs the real FastAPI/SQLite/auth/persistence stack. The OpenAI-compatible model
provider is a deterministic synthetic substitute, not evidence for a real model,
embedding provider, clinical behavior, or production readiness.

Run with the web requirements installed:
    python tests/backend_e2e.py
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "src" / "web"


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, *_args: Any) -> None:
        # Closing the backend aborts keep-alive sockets; avoid noisy expected resets.
        pass


class SyntheticProviderHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size) or b"{}")
        if self.path.endswith("/chat/completions"):
            messages = payload.get("messages", [])
            last = str(messages[-1].get("content", "")) if messages else ""
            if "provider-error" in last:
                body = json.dumps({"error": {"message": "synthetic provider failure"}}).encode()
                self.send_response(503)
            else:
                body = json.dumps({
                    "id": "chatcmpl-synthetic",
                    "object": "chat.completion",
                    "created": 1,
                    "model": "synthetic",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "Resposta sintética de teste."}, "finish_reason": "stop"}],
                }).encode()
                self.send_response(200)
        elif self.path.endswith("/embeddings"):
            records = payload.get("input", [])
            if isinstance(records, str):
                records = [records]
            body = json.dumps({
                "object": "list",
                "data": [{"object": "embedding", "index": i, "embedding": [1.0, 0.0]} for i, _ in enumerate(records)],
                "model": payload.get("model", "synthetic"),
            }).encode()
            self.send_response(200)
        else:
            body = b"{}"
            self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: Any) -> None:
        pass


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class BackendProcess:
    def __init__(self, env: dict[str, str], port: int, log_path: Path):
        self.env = env
        self.port = port
        self.log_path = log_path
        self.process: subprocess.Popen[str] | None = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self) -> None:
        self.log_file = self.log_path.open("w", encoding="utf-8")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--app-dir", str(WEB_DIR),
             "--host", "127.0.0.1", "--port", str(self.port), "--log-level", "warning"],
            cwd=ROOT,
            env=self.env,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"backend exited early; see {self.log_path}")
            try:
                response = httpx.get(self.base_url + "/health", timeout=0.5)
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        raise TimeoutError(f"backend did not start; see {self.log_path}")

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if hasattr(self, "log_file"):
            self.log_file.close()


def require(response: httpx.Response, status: int, label: str) -> httpx.Response:
    assert response.status_code == status, (
        f"{label}: expected {status}, got {response.status_code}: {response.text}"
    )
    return response


def main() -> None:
    provider_port, backend_port = free_port(), free_port()
    provider = QuietThreadingHTTPServer(("127.0.0.1", provider_port), SyntheticProviderHandler)
    provider_thread = threading.Thread(target=provider.serve_forever, daemon=True)
    provider_thread.start()

    with tempfile.TemporaryDirectory(prefix="psicoia-block10-") as temp_name:
        temp = Path(temp_name)
        skill_root = temp / "skills"
        for sect in ("bt", "cbt", "het", "pdt", "pmt"):
            for stage in ("stage1", "stage2", "stage3"):
                folder = skill_root / sect / stage
                folder.mkdir(parents=True)
                (folder / "meta_skills.json").write_text("{}", encoding="utf-8")
                (folder / "micro_skills.json").write_text("{}", encoding="utf-8")

        baseline = yaml.safe_load((ROOT / "configs/baselines/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
        baseline.update({
            "base_url": f"http://127.0.0.1:{provider_port}/v1",
            "api_key_env": "SGLANG_API_KEY",
            "model": "synthetic",
            "timeout_sec": 2,
            "max_retries": 1,
            "retry_sleep_sec": 0,
        })
        baseline_path = temp / "baseline.yaml"
        baseline_path.write_text(yaml.safe_dump(baseline), encoding="utf-8")

        runtime = yaml.safe_load((ROOT / "configs/runtime/psychagent_sglang_local.yaml").read_text(encoding="utf-8"))
        runtime.update({
            "psychagent_skill_base_dir": str(skill_root),
            "psychagent_skill_sects": "all",
            "psychagent_embedding_base_url": f"http://127.0.0.1:{provider_port}/v1",
            "psychagent_embedding_api_key_env": "PSICOIA_SYNTHETIC_EMBEDDING_KEY",
            "psychagent_embedding_max_retries": 1,
            "psychagent_embedding_retry_sleep_sec": 0,
        })
        runtime_path = temp / "runtime.yaml"
        runtime_path.write_text(yaml.safe_dump(runtime), encoding="utf-8")

        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(ROOT / "src"),
            "DB_URL": f"sqlite:///{(temp / 'api.sqlite3').as_posix()}",
            "PSYCHAGENT_WEB_BASELINE_CONFIG": str(baseline_path),
            "PSYCHAGENT_WEB_RUNTIME_CONFIG": str(runtime_path),
            "SGLANG_API_KEY": "synthetic-not-a-secret",
            "PSICOIA_SYNTHETIC_EMBEDDING_KEY": "synthetic-not-a-secret",
        })
        backend = BackendProcess(env, backend_port, temp / "backend.log")
        backend.start()
        try:
            client = httpx.Client(base_url=backend.base_url, timeout=10)
            # Public/reference endpoints and health.
            assert require(client.get("/health"), 200, "health").json()["status"] == "ok"
            schools = require(client.get("/schools"), 200, "schools").json()
            assert any(school["id"] == "cbt" for school in schools)
            assert require(client.get("/stages"), 200, "stages").json()

            # Auth, real SQLite persistence, and access control.
            one = require(client.post("/auth/register", json={"username": "synthetic-one", "password": "local-password"}), 200, "register").json()
            token = one["token"]
            duplicate = require(client.post("/auth/register", json={"username": "synthetic-one", "password": "local-password"}), 400, "duplicate registration")
            assert duplicate.json()["detail"] == "Este nome de usuário já está em uso."
            invalid_credentials = require(client.post("/auth/login", json={"username": "synthetic-one", "password": "wrong"}), 401, "invalid credentials")
            assert invalid_credentials.json()["detail"] == "Nome de usuário ou senha incorretos."
            two = require(client.post("/auth/register", json={"username": "synthetic-two", "password": "local-password"}), 200, "second user").json()
            missing_token = require(client.get("/courses"), 401, "unauthenticated course list")
            assert missing_token.json()["detail"] == "Token de acesso não informado."
            auth = {"Authorization": f"Bearer {token}"}
            auth_two = {"Authorization": f"Bearer {two['token']}"}

            unknown_school = require(client.post("/courses", headers=auth, json={"school_id": "invalid-school"}), 404, "unknown school")
            assert unknown_school.json()["detail"] == "Abordagem não encontrada."
            created = require(client.post("/courses", headers=auth, json={
                "school_id": "cbt", "title": "synthetic course", "goal_summary": "synthetic goal",
                "auto_start_first_visit": True, "opening_note": "synthetic note",
            }), 200, "create course + first visit").json()
            course = created["course"]
            visit = created["created_visit"]
            course_id, visit_id = course["course_id"], visit["visit_id"]
            assert visit["status"] == "open" and len(visit["messages"]) >= 2
            require(client.get("/courses", headers=auth), 200, "list courses")
            require(client.get(f"/courses/{course_id}", headers=auth), 200, "get course")
            require(client.get(f"/courses/{course_id}", headers=auth_two), 403, "course ownership")
            patched = require(client.patch(f"/courses/{course_id}", headers=auth, json={
                "title": "updated synthetic course", "goals": ["goal one", "goal two"],
            }), 200, "update course").json()
            assert patched["title"] == "updated synthetic course" and len(patched["goals"]) == 2
            require(client.get(f"/courses/{course_id}/visits", headers=auth), 200, "list visits")
            require(client.get(f"/visits/{visit_id}", headers=auth), 200, "get visit")
            require(client.get(f"/visits/{visit_id}", headers=auth_two), 403, "visit ownership")
            require(client.post(f"/courses/{course_id}/visits", headers=auth, json={}), 409, "duplicate open visit")
            invalid_message = require(client.post(f"/visits/{visit_id}/messages", headers=auth, json={"text": ""}), 422, "empty message validation")
            assert invalid_message.json()["detail"][0]["msg"] == "O valor informado é menor que o mínimo permitido."

            posted = require(client.post(f"/visits/{visit_id}/messages", headers=auth, json={"text": "synthetic user message"}), 200, "send message").json()
            assert posted["visit"]["message_count"] >= 4
            count_before_failure = posted["visit"]["message_count"]
            require(client.post(f"/visits/{visit_id}/messages", headers=auth, json={"text": "provider-error"}), 502, "provider failure")
            after_failure = require(client.get(f"/visits/{visit_id}", headers=auth), 200, "state after provider failure").json()
            assert after_failure["message_count"] == count_before_failure, "failed generation must roll back user message"
            require(client.post(f"/courses/{course_id}/complete", headers=auth, json={"summary": "course summary"}), 409, "complete with open visit")

            closed = require(client.post(f"/visits/{visit_id}/close", headers=auth, json={"summary": "synthetic session summary"}), 200, "close visit").json()
            assert closed["status"] == "closed" and closed["summary"] == "synthetic session summary"
            closed_state = require(client.get(f"/visits/{visit_id}", headers=auth), 200, "localized closed visit state").json()
            assert any(
                item["text"] == "--- Esta sessão foi encerrada e o progresso foi salvo. ---"
                for item in closed_state["messages"]
            )
            require(client.post(f"/visits/{visit_id}/close", headers=auth, json={}), 409, "close twice")
            completed = require(client.post(f"/courses/{course_id}/complete", headers=auth, json={"summary": "course summary"}), 200, "complete course").json()
            assert completed["status"] == "completed"
            archived = require(client.post(f"/courses/{course_id}/archive", headers=auth), 200, "archive course").json()
            assert archived["status"] == "archived"
            require(client.post(f"/courses/{course_id}/visits", headers=auth, json={}), 409, "visit on archived course")

            # Verify persistence across a real backend process restart.
            client.close()
            backend.stop()
            backend = BackendProcess(env, backend_port, temp / "backend-restart.log")
            backend.start()
            with httpx.Client(base_url=backend.base_url, timeout=10) as restarted:
                login = require(restarted.post("/auth/login", json={"username": "synthetic-one", "password": "local-password"}), 200, "login after restart").json()
                persisted = require(restarted.get("/courses", headers={"Authorization": f"Bearer {login['token']}"}), 200, "persisted courses after restart").json()
                assert any(item["course_id"] == course_id and item["status"] == "archived" for item in persisted)
            print("PASS: 16 business routes exercised over loopback HTTP; SQLite/auth persisted across restart.")
            print("PASS: auth/ownership, validation, lifecycle transitions, and generation rollback negatives.")
            print("LIMIT: synthetic local OpenAI-compatible provider and empty synthetic skill catalogs; no real model/embedding/provider or clinical equivalence demonstrated.")
        finally:
            backend.stop()
            provider.shutdown()
            provider.server_close()
            provider_thread.join(timeout=2)


if __name__ == "__main__":
    main()
