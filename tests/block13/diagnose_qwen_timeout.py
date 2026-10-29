"""Instrument the previously timed-out Qwen mean-pooling + Qwen chat combination.

Uses only already-installed local models, synthetic nonclinical prompts and local
loopback servers. Writes machine measurements to reports/block13/qwen_timeout_diagnostic.json.
"""
from __future__ import annotations

import concurrent.futures
import ctypes
import csv
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://127.0.0.1:11434"


def request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 180) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read())
    return result, (time.perf_counter() - started) * 1000


def installed_model(model: str = MODEL) -> tuple[Path, Path]:
    ollama = Path(shutil.which("ollama") or "")
    if not ollama.is_file():
        raise RuntimeError("Ollama executable is unavailable")
    server = ollama.parent / "lib" / "ollama" / "llama-server.exe"
    root = Path(os.environ.get("OLLAMA_MODELS", Path.home() / ".ollama" / "models"))
    name, _, tag = model.partition(":")
    manifest = root / "manifests" / "registry.ollama.ai" / "library" / name / tag
    data = json.loads(manifest.read_text(encoding="utf-8"))
    layer = next(x for x in data["layers"] if x["mediaType"] == "application/vnd.ollama.image.model")
    blob = root / "blobs" / layer["digest"].replace(":", "-")
    if not server.is_file() or not blob.is_file():
        raise RuntimeError(f"missing installed runtime/model: {server}, {blob}")
    return server, blob


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t), ("PrivateUsage", ctypes.c_size_t)]


def memory_snapshot(pid: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"pid": pid}
    if os.name == "nt":
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            result["ram_total_gib"] = round(status.ullTotalPhys / 1024**3, 2)
            result["ram_available_gib"] = round(status.ullAvailPhys / 1024**3, 2)
            result["ram_load_percent"] = int(status.dwMemoryLoad)
        if pid:
            handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if handle:
                counters = PROCESS_MEMORY_COUNTERS_EX()
                counters.cb = ctypes.sizeof(counters)
                if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                    result["process_working_set_mib"] = round(counters.WorkingSetSize / 1024**2, 1)
                    result["process_peak_working_set_mib"] = round(counters.PeakWorkingSetSize / 1024**2, 1)
                ctypes.windll.kernel32.CloseHandle(handle)
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu", "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        result["gpu"] = gpu.stdout.strip() if gpu.returncode == 0 else gpu.stderr.strip()
    except Exception as exc:
        result["gpu"] = f"unavailable: {exc}"
    try:
        loaded, _ = request_json(OLLAMA_URL + "/api/ps", timeout=3)
        result["ollama_loaded_models"] = loaded.get("models", [])
    except Exception as exc:
        result["ollama_loaded_models"] = f"unavailable: {exc}"
    try:
        tasklist = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, timeout=5)
        result["model_processes"] = [row for row in csv.reader(tasklist.stdout.splitlines()) if row and any(token in row[0].lower() for token in ("ollama", "llama-server"))]
    except Exception as exc:
        result["model_processes"] = f"unavailable: {exc}"
    return result


def embed(url: str, texts: list[str]) -> tuple[float, int]:
    _, elapsed = request_json(url + "/v1/embeddings", {"model": MODEL, "input": texts}, timeout=180)
    return elapsed, len(texts)


def main() -> None:
    executable, blob = installed_model()
    port = 19387
    temp = Path(tempfile.mkdtemp(prefix="psicoia-b13-qwen-"))
    log_path = temp / "llama-server.log"
    log = log_path.open("w", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = str(executable.parent) + os.pathsep + env.get("PATH", "")
    args = [str(executable), "-m", str(blob), "--embedding", "--pooling", "mean", "--host", "127.0.0.1", "--port", str(port), "-c", "512", "-ngl", "0", "--no-webui"]
    started = time.perf_counter()
    process = subprocess.Popen(args, cwd=executable.parent, env=env, stdout=log, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    try:
        while time.perf_counter() - started < 180:
            if process.poll() is not None:
                raise RuntimeError(f"Qwen llama-server exited; inspect {log_path}")
            try:
                if request_json(url + "/health", timeout=2)[0].get("status") == "ok":
                    break
            except Exception:
                time.sleep(0.25)
        else:
            raise TimeoutError("Qwen embedding cold start exceeded 180 s")
        server_ready_seconds = time.perf_counter() - started
        initial_snapshot = memory_snapshot(process.pid)

        # Tokenization and embedding are timed separately for each input; each request is serial.
        samples = [
            "Clean and lubricate a bicycle chain after wiping off visible dirt.",
            "A shared folder has several similar file names; search by distinctive words and verify the document before changing it.",
            "Quero localizar um documento antigo numa pasta com muitas versões e confirmar o conteúdo antes de mover qualquer arquivo.",
            "How do I set the water chemistry for a tropical fish tank?",
        ]
        token_rows: list[dict[str, Any]] = []
        for text in samples:
            token_data, token_ms = request_json(url + "/tokenize", {"content": text, "add_special": False}, timeout=60)
            token_rows.append({"characters": len(text), "tokens": len(token_data.get("tokens", [])), "tokenization_ms": round(token_ms, 2)})

        # Baseline embedding calls before loading the second Qwen copy in Ollama.
        before_rows = []
        for text in samples:
            elapsed, count = embed(url, [text])
            before_rows.append({"characters": len(text), "items": count, "embedding_ms": round(elapsed, 2)})
        cold_embedding_snapshot = memory_snapshot(process.pid)

        # Deliberately load the same local Qwen model in Ollama, then measure the actual
        # standalone embedding and chat stages separately while both model servers stay resident.
        chat_payload = {"model": MODEL, "messages": [{"role": "system", "content": "Answer the synthetic household question briefly in English."},
                                                        {"role": "user", "content": "How should I clean a bicycle chain?"}],
                        "temperature": 0, "max_tokens": 256, "stream": False}
        chat_started = time.perf_counter()
        chat_data, chat_ms = request_json(OLLAMA_URL + "/v1/chat/completions", chat_payload, timeout=240)
        cold_chat_seconds = time.perf_counter() - chat_started
        choice = (chat_data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        chat_summary = {"elapsed_ms": round(chat_ms, 2), "finish_reason": choice.get("finish_reason"),
                        "prompt_tokens": (chat_data.get("usage") or {}).get("prompt_tokens"),
                        "completion_tokens": (chat_data.get("usage") or {}).get("completion_tokens"),
                        "public_text_characters": len(str(message.get("content") or "")),
                        "reasoning_field_characters": len(str(message.get("reasoning") or message.get("reasoning_content") or ""))}
        both_loaded_snapshot = memory_snapshot(process.pid)
        after_rows = []
        for text in samples:
            elapsed, count = embed(url, [text])
            after_rows.append({"characters": len(text), "items": count, "embedding_ms": round(elapsed, 2)})

        # Simultaneous requests intentionally measure resource contention; the application
        # normally awaits retrieval before chat generation, so this is a stress probe only.
        concurrent_started = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            embed_future = pool.submit(embed, url, [samples[1]])
            chat_future = pool.submit(request_json, OLLAMA_URL + "/v1/chat/completions", chat_payload, 240)
            concurrent_embed = embed_future.result()
            concurrent_chat = chat_future.result()
        concurrent_wall_ms = (time.perf_counter() - concurrent_started) * 1000
        final_snapshot = memory_snapshot(process.pid)

        output = {
            "model": MODEL,
            "server_args": args,
            "embedding_device": "llama-server CPU-only (-ngl 0)",
            "cpu_logical_count": os.cpu_count(),
            "cold_server_ready_seconds": round(server_ready_seconds, 2),
            "server_pid": process.pid,
            "server_log": str(log_path),
            "tokenization": token_rows,
            "embedding_before_chat_loaded": before_rows,
            "embedding_after_chat_loaded": after_rows,
            "cold_chat": chat_summary,
            "concurrent_stress": {"wall_ms": round(concurrent_wall_ms, 2), "embedding_ms": round(concurrent_embed[0], 2),
                                  "chat_ms": round(concurrent_chat[1], 2)},
            "snapshots": {"after_embedding_server_load": initial_snapshot, "after_initial_embeddings": cold_embedding_snapshot,
                          "both_models_loaded": both_loaded_snapshot, "after_concurrent_stress": final_snapshot},
            "concurrency_note": "The live request flow is sequential; the concurrent pair is a separate contention probe.",
            "limitations": "Four synthetic probes are diagnostic, not a retrieval quality benchmark. Local GPU and RAM observations are machine-specific.",
        }
        report_dir = ROOT / "reports/block13"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "qwen_timeout_diagnostic.json"
        report_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"DIAGNOSTIC_JSON={report_path}")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        log.close()
        print(f"LLAMA_SERVER_LOG={log_path}")


if __name__ == "__main__":
    main()
