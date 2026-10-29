"""Trace proxy-stage timings for the Block 12 E2E against the Block 13 fixture.

This wrapper imports but does not edit the immutable Block 12 baseline script.
The client timeout is reduced to 180 s to locate a slow stage, never increased.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PSICOIA_LOCAL_CHAT_MODEL", "qwen3.5:4b")
os.environ.setdefault("PSICOIA_LOCAL_EMBED_MODEL", "qwen3.5:4b")
source = ROOT / "tests/backend_block12_local_pipeline_e2e.py"
spec = importlib.util.spec_from_file_location("block12_immutable", source)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load Block 12 E2E baseline")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.DOC_FIXTURE = ROOT / "tests/fixtures/block13/retrieval_eval_v1.json"
module.BENCHMARK_FIXTURE = ROOT / "tests/fixtures/block13/retrieval_eval_v1.json"
if os.environ.get("PSICOIA_BLOCK13_SKIP_RETRIEVAL_METRICS") == "1":
    async def skip_precomputed_benchmark_metrics(**kwargs: Any) -> dict[str, Any]:
        return {"locale": kwargs["locale"], "skipped": "independent Block 13 benchmark was measured separately"}
    module.retrieval_metrics = skip_precomputed_benchmark_metrics

proxies: list[Any] = []
original_init = module.ProxyServer.__init__


def traced_init(self: Any, target: str) -> None:
    original_init(self, target)
    self.block13_inflight = None
    proxies.append(self)


module.ProxyServer.__init__ = traced_init
original_handler = module.ForwardHandler.do_POST


def traced_handler(self: Any) -> None:
    proxy = self.server
    started = time.perf_counter()
    proxy.block13_inflight = {"path": self.path, "started_at": time.time()}
    try:
        original_handler(self)
    finally:
        elapsed = (time.perf_counter() - started) * 1000
        record = proxy.records[-1] if proxy.records else {}
        print("PROXY_STAGE " + json.dumps({"path": self.path, "elapsed_ms": round(elapsed, 1),
              "status": record.get("status"), "input_count": len(record.get("inputs", [])),
              "input_chars": [len(str(x)) for x in record.get("inputs", [])],
              "model": record.get("model"), "usage": record.get("usage"),
              "finish_reason": record.get("finish_reason"),
              "public_chars": len(record.get("response_text", "")),
              "reasoning_chars": record.get("reasoning_field_length")}, ensure_ascii=False), flush=True)
        proxy.block13_inflight = None


module.ForwardHandler.do_POST = traced_handler
original_post = module.httpx.Client.post


def traced_post(self: Any, url: Any, *args: Any, **kwargs: Any) -> Any:
    path = str(url)
    if "/messages" in path or "/visits" in path:
        started = time.perf_counter()
        print(f"API_ROUTE_START {path}", flush=True)
        try:
            response = original_post(self, url, *args, **kwargs)
            print(f"API_ROUTE_DONE {path} status={response.status_code} elapsed_ms={(time.perf_counter()-started)*1000:.1f}", flush=True)
            return response
        except Exception as exc:
            print(f"API_ROUTE_ERROR {path} error={type(exc).__name__} elapsed_ms={(time.perf_counter()-started)*1000:.1f}", flush=True)
            raise
    return original_post(self, url, *args, **kwargs)


module.httpx.Client.post = traced_post
OriginalClient = module.httpx.Client


class BoundedDiagnosticClient(OriginalClient):
    def __init__(self, *args: Any, **kwargs: Any):
        if kwargs.get("timeout") == 300:
            kwargs["timeout"] = 180
        super().__init__(*args, **kwargs)


module.httpx.Client = BoundedDiagnosticClient

try:
    module.main()
except Exception as exc:
    print(f"E2E_ERROR {type(exc).__name__}: {exc}", flush=True)
    for index, proxy in enumerate(proxies):
        summary = [{"path": r.get("path"), "elapsed_ms": r.get("elapsed_ms"), "status": r.get("status"),
                    "input_count": len(r.get("inputs", [])), "model": r.get("model"),
                    "usage": r.get("usage"), "finish_reason": r.get("finish_reason"),
                    "public_chars": len(r.get("response_text", "")),
                    "reasoning_chars": r.get("reasoning_field_length")} for r in proxy.records]
        print("PROXY_SUMMARY " + json.dumps({"proxy": index, "target": proxy.target,
              "inflight": proxy.block13_inflight, "completed": summary}, ensure_ascii=False), flush=True)
    raise
