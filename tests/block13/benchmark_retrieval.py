"""Reproducible local Block 13 retrieval benchmark on the locked synthetic fixture."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import random
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagnose_qwen_timeout as resources  # noqa: E402
from sample.core.schemas import RuntimeConfig  # noqa: E402
from sample.prompt_manager import PsychAgentPromptManager  # noqa: E402
from sample.skill_manager import SkillManager  # noqa: E402
from web.backend.psychagent_engine import PsychAgentWebBackend  # noqa: E402

DATA_PATH = ROOT / "tests/fixtures/block13/retrieval_eval_v1.json"
CRITERIA_PATH = ROOT / "tests/fixtures/block13/criteria_v1.json"
MODELS = ["phi4-mini:3.8b", "qwen3.5:4b"]
KEY_ENV = "PSICOIA_BLOCK13_LOCAL_EMBED_KEY"


def post_json(url: str, payload: dict[str, Any], timeout: int = 180) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    request = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer local-only"}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read())
    return body, (time.perf_counter() - started) * 1000


def get_json(url: str, timeout: int = 2) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read())


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_embedding_server(model: str, log_path: Path):
    executable, blob = resources.installed_model(model)
    port = free_port()
    env = os.environ.copy()
    env["PATH"] = str(executable.parent) + os.pathsep + env.get("PATH", "")
    log = log_path.open("w", encoding="utf-8")
    args = [str(executable), "-m", str(blob), "--embedding", "--pooling", "mean", "--host", "127.0.0.1",
            "--port", str(port), "-c", "512", "-ngl", "0", "--no-webui"]
    started = time.perf_counter()
    process = subprocess.Popen(args, cwd=executable.parent, env=env, stdout=log, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    while time.perf_counter() - started < 180:
        if process.poll() is not None:
            raise RuntimeError(f"embedding server exited; inspect {log_path}")
        try:
            if get_json(url + "/health").get("status") == "ok":
                return process, log, url, time.perf_counter() - started, args
        except Exception:
            time.sleep(0.2)
    process.terminate()
    raise TimeoutError(f"embedding cold start exceeded 180 seconds; inspect {log_path}")


def tokenize(url: str, text: str) -> dict[str, Any]:
    body, elapsed = post_json(url + "/tokenize", {"content": text, "add_special": False}, timeout=60)
    return {"characters": len(text), "tokens": len(body.get("tokens", [])), "tokenization_ms": round(elapsed, 2)}


def relevant_text(doc: dict[str, Any], locale: str) -> str:
    data = doc[locale]
    return f"Trigger:{data.get('trigger', '')}\nWhen_to_Use:{data.get('when_to_use', '')}"


def merge_text(doc: dict[str, Any], locale: str) -> str:
    data = doc[locale]
    return json.dumps({key: data.get(key, "") for key in ("skill_name", "skill_description", "trigger", "when_to_use")}, ensure_ascii=False)


def create_catalog(root: Path, dataset: dict[str, Any], locale: str) -> None:
    for stage in ("stage1", "stage2", "stage3"):
        folder = root / "cbt" / stage
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "meta_skills.json").write_text("{}", encoding="utf-8")
        (folder / "micro_skills.json").write_text("{}", encoding="utf-8")
    stage_dir = root / "cbt" / "stage1"
    meta = {"root-1": {"skill_id": "root-1", "skill_name": "Synthetic task catalog", "skill_description": "Nonclinical test root.",
                        "parent_ids": ["root-1"], "sect": "cbt"}}
    localized = {}
    for doc in dataset["skill_documents"]:
        localized[doc["id"]] = {**doc[locale], "skill_id": doc["id"], "parent_ids": ["root-1", doc["id"]], "sect": "cbt"}
    (stage_dir / "meta_skills.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (stage_dir / f"meta_skills.{locale}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (stage_dir / f"micro_skills.{locale}.json").write_text(json.dumps(localized, ensure_ascii=False), encoding="utf-8")


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[max(0, math.ceil(p * len(ordered)) - 1)], 2)


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)]


def ndcg(ids: list[str], grades: dict[str, int], k: int = 5) -> float:
    def dcg(values: list[int]) -> float:
        return sum((2**grade - 1) / math.log2(rank + 2) for rank, grade in enumerate(values[:k]))
    actual = dcg([int(grades.get(item, 0)) for item in ids[:k]])
    ideal = dcg(sorted((int(v) for v in grades.values()), reverse=True))
    return actual / ideal if ideal else 0.0


def rank_metrics(rows: list[dict[str, Any]], threshold: float | None = None) -> dict[str, Any]:
    test = [r for r in rows if r["split"] == "test"]
    answered = [r for r in test if r["answerable"]]
    no_answer = [r for r in test if not r["answerable"]]
    values = []
    for row in test:
        ranked = row["ranked"]
        if threshold is not None:
            ranked = [x for x in ranked if x["similarity"] >= threshold]
        ids = [x["id"] for x in ranked[:5]]
        relevant = set(row["relevant_ids"])
        first = next((idx + 1 for idx, item in enumerate(ids) if item in relevant), None)
        rendered = set(row.get("rendered_skill_ids", []))
        prompt_ids = [item_id for item_id in ids if item_id in rendered]
        values.append({"id": row["id"], "answerable": row["answerable"], "hit1": bool(ids and ids[0] in relevant),
                       "hit5": bool(set(ids) & relevant), "mrr": 1 / first if first else 0.0,
                       "ndcg5": ndcg(ids, row["relevance"]), "useful_context": bool(set(prompt_ids) & relevant) if row["answerable"] else False,
                       "false_context": bool(prompt_ids) if not row["answerable"] else False,
                       "retrieved_ids": ids, "rendered_skill_ids": prompt_ids})
    by_id = {x["id"]: x for x in values}
    a = [by_id[x["id"]] for x in answered]
    u = [by_id[x["id"]] for x in no_answer]
    hit1 = sum(x["hit1"] for x in a)
    hit5 = sum(x["hit5"] for x in a)
    useful = sum(x["useful_context"] for x in a)
    false = sum(x["false_context"] for x in u)
    return {
        "test_queries": len(test), "answerable_n": len(answered), "no_answer_n": len(no_answer),
        "recall_at_1": round(hit1 / len(a), 4) if a else None, "recall_at_1_wilson95": wilson(hit1, len(a)),
        "recall_at_5": round(hit5 / len(a), 4) if a else None, "recall_at_5_wilson95": wilson(hit5, len(a)),
        "mrr": round(sum(x["mrr"] for x in a) / len(a), 4) if a else None,
        "ndcg_at_5": round(sum(x["ndcg5"] for x in a) / len(a), 4) if a else None,
        "useful_context_rate": round(useful / len(a), 4) if a else None,
        "useful_context_wilson95": wilson(useful, len(a)),
        "no_answer_false_context_rate": round(false / len(u), 4) if u else None,
        "no_answer_false_context_wilson95": wilson(false, len(u)),
        "per_query": values,
    }


def calibrate_threshold(rows: list[dict[str, Any]], grid: list[float]) -> dict[str, Any]:
    calibration = [r for r in rows if r["split"] == "calibration"]
    if not calibration:
        raise RuntimeError("missing calibration rows")
    choices = []
    for threshold in grid:
        positives = [r for r in calibration if r["answerable"]]
        negatives = [r for r in calibration if not r["answerable"]]
        tpr = sum(max(x["ranked"][0]["similarity"] for _ in [0]) >= threshold for x in positives) / len(positives) if positives else 0
        tnr = sum(max(x["ranked"][0]["similarity"] for _ in [0]) < threshold for x in negatives) / len(negatives) if negatives else 0
        choices.append({"threshold": threshold, "balanced_accuracy": (tpr + tnr) / 2, "sensitivity": tpr, "specificity": tnr})
    best_score = max(x["balanced_accuracy"] for x in choices)
    best = max((x for x in choices if x["balanced_accuracy"] == best_score), key=lambda x: x["threshold"])
    return {"selected": best, "grid_results": choices}


def bootstrap_difference(phi: list[dict[str, Any]], qwen: list[dict[str, Any]], metric: str, locale: str) -> dict[str, Any]:
    phi_map = {x["id"]: x for x in phi}
    qwen_map = {x["id"]: x for x in qwen}
    ids = [x for x in phi_map.keys() & qwen_map.keys() if phi_map[x]["answerable"]]
    if not ids:
        return {"n_paired": 0, "mean_difference_qwen_minus_phi": None, "bootstrap95": None}
    diffs = [float(qwen_map[x][metric]) - float(phi_map[x][metric]) for x in ids]
    rng = random.Random(13013)
    means = []
    for _ in range(10000):
        means.append(sum(diffs[rng.randrange(len(diffs))] for _ in diffs) / len(diffs))
    means.sort()
    return {"n_paired": len(ids), "mean_difference_qwen_minus_phi": round(sum(diffs) / len(diffs), 4),
            "bootstrap95": [round(means[249], 4), round(means[9749], 4)]}


def build_prompt(prompt_manager: PsychAgentPromptManager, selected: list[dict[str, Any]], locale: str) -> str:
    language = "English" if locale == "en" else "Português (Brasil)"
    client_info = {"static_traits": {"name": "Synthetic benchmark"}, "main_problem": "synthetic nonclinical task",
                   "topic": "retrieval benchmark", "core_demands": "find a matching synthetic task", "growth_experiences": []}
    system = prompt_manager.render("counselor_system", client_info=client_info, history=[], session_stage="Synthetic task",
                                   session_focus=["retrieve matching synthetic context"], homework_assigned_from_last_session=[],
                                   suggested_skills=selected, output_language=language)
    return PsychAgentWebBackend._append_output_language_contract(system, language)


async def main() -> None:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    criteria = json.loads(CRITERIA_PATH.read_text(encoding="utf-8"))
    assert criteria["criteria_locked_before_model_runs"] is True
    assert len(dataset["skill_documents"]) == 12 and len(dataset["queries"]) == 32
    assert all(set(q["relevant_ids"]) == set(q["relevance"]) and q.get("answerable", bool(q["relevance"])) == bool(q["relevance"]) for q in dataset["queries"])
    os.environ[KEY_ENV] = "local-loopback-only"
    report: dict[str, Any] = {"dataset_id": dataset["dataset_id"], "criteria_file": str(CRITERIA_PATH.relative_to(ROOT)),
                              "server_config": {"pooling": "mean", "ngl": 0, "context": 512, "batching": "provider library batches of 12"},
                              "hardware": {"logical_cpu_count": os.cpu_count()}, "candidates": {}, "paired_differences": {}}
    benchmark_rows: dict[str, dict[str, list[dict[str, Any]]]] = {}
    temp_root = Path(tempfile.mkdtemp(prefix="psicoia-block13-benchmark-"))
    logs = ROOT.parent / "temp/psicoia-block13-logs"
    logs.mkdir(parents=True, exist_ok=True)
    try:
        for model in MODELS:
            logfile = logs / (model.replace(":", "_") + ".log")
            process, log, url, cold_seconds, args = start_embedding_server(model, logfile)
            model_result: dict[str, Any] = {"server_cold_start_seconds": round(cold_seconds, 2), "server_args": args,
                                            "model_process_pid": process.pid,
                                            "resource_after_load": resources.memory_snapshot(process.pid), "locales": {}}
            benchmark_rows[model] = {}
            try:
                for locale, output_language in (("en", "English"), ("pt-BR", "Português (Brasil)")):
                    locale_root = temp_root / model.replace(":", "_") / locale
                    create_catalog(locale_root, dataset, locale)
                    runtime = RuntimeConfig.from_dict({"output_language": output_language,
                        "psychagent_skill_base_dir": str(locale_root), "psychagent_skill_sects": "cbt",
                        "psychagent_embedding_base_url": url + "/v1", "psychagent_embedding_api_key_env": KEY_ENV,
                        "psychagent_embedding_model": model, "psychagent_embedding_batch_size": 12,
                        "psychagent_embedding_max_retries": 1, "psychagent_embedding_retry_sleep_sec": 0})
                    manager = SkillManager(backend=None, runtime_config=runtime)
                    phase = {"name": "index"}
                    calls: list[dict[str, Any]] = []
                    original_embed = manager._embed_by_api
                    async def measured_embed(texts, _original=original_embed, _calls=calls, _phase=phase):
                        started = time.perf_counter()
                        vectors = await _original(texts)
                        _calls.append({"phase": _phase["name"], "items": len(texts), "characters": sum(len(x) for x in texts),
                                       "elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "dimensions": len(vectors[0]) if vectors else 0})
                        return vectors
                    manager._embed_by_api = measured_embed
                    index_start = time.perf_counter()
                    await manager.load_library()
                    index_seconds = time.perf_counter() - index_start
                    stage = manager.skill_lib["cbt"]["stage1"]
                    candidates = list(stage.micro.values())
                    prompt_manager = PsychAgentPromptManager(ROOT / "prompts/psychagent", "cbt")
                    locale_queries = [q for q in dataset["queries"] if q["locale"] == locale]
                    locale_doc_rows = []
                    for doc in dataset["skill_documents"]:
                        retrieval = relevant_text(doc, locale)
                        token_row = tokenize(url, retrieval)
                        phase["name"] = "individual_document"
                        start = time.perf_counter()
                        await manager._embed_by_api([retrieval])
                        locale_doc_rows.append({"id": doc["id"], **token_row,
                                                "embedding_ms": calls[-1]["elapsed_ms"], "characters": len(retrieval)})
                    locale_rows: list[dict[str, Any]] = []
                    query_token_rows = []
                    for query in locale_queries:
                        query_token = tokenize(url, query["query"])
                        query_token_rows.append({"id": query["id"], **query_token})
                        phase["name"] = "query"
                        query_start = time.perf_counter()
                        retrieved, _ = await manager.retrive(sect="cbt", query=query["query"], session_stage=1,
                            session_goals={}, diag_hist=[], top_k=5, candidate_skills=candidates)
                        retrieval_ms = (time.perf_counter() - query_start) * 1000
                        embedding_ms = calls[-1]["elapsed_ms"]
                        prompt_start = time.perf_counter()
                        system_prompt = build_prompt(prompt_manager, retrieved, locale)
                        prompt_ms = (time.perf_counter() - prompt_start) * 1000
                        ranked = [{"id": item["skill_id"], "similarity": float(item.get("similarity", 0.0))} for item in retrieved]
                        ids = {str(item["skill_id"]) for item in retrieved
                               if item.get("skill_name") and item["skill_name"] in system_prompt
                               and item.get("skill_description") and item["skill_description"] in system_prompt}
                        locale_rows.append({"id": query["id"], "locale": locale, "split": query["split"], "type": query["type"],
                            "answerable": bool(query["relevance"]), "query": query["query"], "relevance": query["relevance"],
                            "relevant_ids": query["relevant_ids"], "ranked": ranked, "max_similarity": ranked[0]["similarity"] if ranked else None,
                            "retrieval_total_ms": round(retrieval_ms, 2), "query_embedding_ms": embedding_ms,
                            "non_embedding_retrieval_overhead_ms": round(max(0.0, retrieval_ms - embedding_ms), 2),
                            "prompt_render_ms": round(prompt_ms, 2), "rendered_skill_ids": sorted(ids)})
                    benchmark_rows[model][locale] = locale_rows
                    index_calls = [x for x in calls if x["phase"] == "index"]
                    doc_calls = [x for x in calls if x["phase"] == "individual_document"]
                    query_calls = [x for x in calls if x["phase"] == "query"]
                    token_count = sum(x["tokens"] for x in locale_doc_rows)
                    q_tokens = sum(x["tokens"] for x in query_token_rows)
                    metrics_default = rank_metrics(locale_rows)
                    threshold_result = calibrate_threshold(locale_rows, criteria["open_set_threshold_experiment"]["threshold_grid"])
                    threshold_value = threshold_result["selected"]["threshold"]
                    metrics_calibrated = rank_metrics(locale_rows, threshold_value)
                    model_result["locales"][locale] = {
                        "document_count": len(locale_doc_rows), "query_count": len(locale_queries), "test_count": sum(x["split"] == "test" for x in locale_rows),
                        "index_wall_seconds": round(index_seconds, 2), "index_api_calls": index_calls,
                        "index_items": sum(x["items"] for x in index_calls), "index_documents_throughput_per_second": round(24 / index_seconds, 4) if index_seconds else None,
                        "retrieval_document_tokens": token_count, "query_tokens": q_tokens,
                        "individual_document_embedding_ms": {"median": percentile([x["embedding_ms"] for x in locale_doc_rows], .5),
                            "p95": percentile([x["embedding_ms"] for x in locale_doc_rows], .95), "per_document": locale_doc_rows},
                        "query_embedding_ms": {"median": percentile([x["query_embedding_ms"] for x in locale_rows], .5),
                            "p95": percentile([x["query_embedding_ms"] for x in locale_rows], .95),
                            "throughput_queries_per_second": round(len(query_calls) / (sum(x["elapsed_ms"] for x in query_calls) / 1000), 4) if query_calls else None,
                            "per_query": query_token_rows},
                        "retrieval_compute_overhead_ms": {"median": percentile([x["non_embedding_retrieval_overhead_ms"] for x in locale_rows], .5),
                            "p95": percentile([x["non_embedding_retrieval_overhead_ms"] for x in locale_rows], .95)},
                        "prompt_render_ms": {"median": percentile([x["prompt_render_ms"] for x in locale_rows], .5),
                            "p95": percentile([x["prompt_render_ms"] for x in locale_rows], .95)},
                        "metrics_without_threshold": metrics_default,
                        "calibration_threshold": threshold_result,
                        "metrics_with_calibration_threshold_on_test": metrics_calibrated,
                        "resource_after_index_and_queries": resources.memory_snapshot(process.pid),
                    }
                    print(f"BENCHMARK model={model} locale={locale} index_s={index_seconds:.1f} query_p95_ms={model_result['locales'][locale]['query_embedding_ms']['p95']} recall5={metrics_default['recall_at_5']} nDCG5={metrics_default['ndcg_at_5']}", flush=True)
                model_result["resource_after_benchmark"] = resources.memory_snapshot(process.pid)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                log.close()
            model_result["server_log"] = str(logfile)
            model_result["locales"] = model_result["locales"]
            report["candidates"][model] = model_result
        for locale in ("en", "pt-BR"):
            phi_rows = benchmark_rows["phi4-mini:3.8b"][locale]
            qwen_rows = benchmark_rows["qwen3.5:4b"][locale]
            phi_test = [x for x in rank_metrics(phi_rows)["per_query"] if x["id"] in {r["id"] for r in phi_rows if r["split"] == "test"}]
            qwen_test = [x for x in rank_metrics(qwen_rows)["per_query"] if x["id"] in {r["id"] for r in qwen_rows if r["split"] == "test"}]
            report["paired_differences"][locale] = {
                metric: bootstrap_difference(phi_test, qwen_test, metric, locale)
                for metric in ("hit1", "hit5", "mrr", "ndcg5")
            }
        report["candidate_availability"] = {"dedicated_local_embedding_model": "NOT_AVAILABLE", "inventory_source": "ollama list; no dedicated embedding model among installed local models; no download attempted"}
        report["limitations"] = ["Small synthetic nonclinical fixture; 12 held-out test queries per locale.",
            "Mean pooling of general generative models is not a dedicated embedding method.",
            "The no-threshold metrics reproduce current retrieval; thresholded test metrics are diagnostic only until an app-level threshold is explicitly configured and integrated."]
        report["criteria"] = criteria
        output = Path(os.environ.get("PSICOIA_BLOCK13_BENCHMARK_OUTPUT",
                                    "reports/block13/retrieval_benchmark_local_prompt_checked.json"))
        if not output.is_absolute():
            output = ROOT / output
        run_id = os.environ.get("PSICOIA_BLOCK13_RUN_ID", time.strftime("%Y%m%dT%H%M%S"))
        report["experiment"] = {
            "run_id": run_id,
            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "dataset_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
            "criteria_sha256": hashlib.sha256(CRITERIA_PATH.read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "model_blob_sha256": {model: Path(report["candidates"][model]["server_args"][2]).name.removeprefix("sha256-")
                                  for model in MODELS},
            "synthetic_only": True,
            "bootstrapping_seed": 13013,
            "paired_bootstrap_resamples": 10000,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"BENCHMARK_JSON={output}")
    finally:
        import shutil
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
