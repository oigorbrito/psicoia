"""CLI entrypoint for the standalone PsychAgent sample framework."""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import replace
from pathlib import Path
from typing import Optional

try:
    from src.shared.file_utils import project_root
except ModuleNotFoundError:  # pragma: no cover - supports PYTHONPATH=src execution style
    from shared.file_utils import project_root

from .core.schemas import BaselineConfig, RuntimeConfig
from .io.config_loader import load_baseline_config, load_dataset_config, load_runtime_config
from .io.dataset_loader import DatasetLoader


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute os fluxos de demonstração independentes do PsicoIA.")
    parser.add_argument(
        "--mode",
        choices=["psychagent"],
        default="psychagent",
        help="Modo de execução. Somente o modo de compatibilidade psychagent é suportado.",
    )
    parser.add_argument(
        "--baseline",
        default="configs/baselines/psychagent_sglang_local.yaml",
        help="Caminho do arquivo YAML de configuração de baseline.",
    )
    parser.add_argument(
        "--runtime",
        default="configs/runtime/psychagent_sglang_local.yaml",
        help="Caminho do arquivo YAML de configuração de runtime.",
    )
    parser.add_argument(
        "--dataset",
        default="configs/datasets/profiles_sample.yaml",
        help="Caminho do arquivo YAML de configuração do conjunto de dados.",
    )
    parser.add_argument(
        "--resume",
        dest="resume",
        action="store_true",
        help="Força a opção resume=True.",
    )
    parser.add_argument(
        "--no-resume",
        "--no_resume",
        dest="resume",
        action="store_false",
        help="Força a opção resume=False.",
    )
    parser.set_defaults(resume=None)
    parser.add_argument("--overwrite", action="store_true", help="Substitui os resultados existentes.")
    parser.add_argument("--concurrency", type=int, default=None, help="Substitui a concorrência do runtime.")
    parser.add_argument("--save_dir", default=None, help="Substitui o diretório de resultados do runtime.")
    parser.add_argument(
        "--strict-config",
        action="store_true",
        help="Falha diante de chaves desconhecidas ou não utilizadas (obsoletas/removidas) no runtime.",
    )
    parser.add_argument("--log_level", default="INFO", help="Nível de registro de eventos (logging).")
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


async def run_from_args(args: argparse.Namespace) -> int:
    root = project_root()

    baseline_cfg = load_baseline_config(str(root / args.baseline))
    runtime_cfg, runtime_audit = load_runtime_config(
        str(root / args.runtime),
        strict=bool(args.strict_config),
        return_audit=True,
    )
    dataset_cfg = load_dataset_config(str(root / args.dataset))

    runtime_cfg = _apply_runtime_overrides(
        runtime_cfg,
        resume_override=args.resume,
        overwrite_override=args.overwrite,
        concurrency_override=args.concurrency,
        save_dir_override=args.save_dir,
    )

    baseline_cfg = _apply_baseline_runtime_overrides(baseline_cfg, runtime_cfg)

    variant_cfg = runtime_cfg

    logger = logging.getLogger("psychagent_sample")
    logger.info("Auditoria da configuração de runtime: %s", runtime_audit.to_dict())
    logger.info("Configuração efetiva de runtime: %s", variant_cfg.to_dict())
    logger.info("Configuração efetiva de baseline: %s", baseline_cfg.to_dict())
    dataset_loader = DatasetLoader(dataset_cfg, logger=logger)
    cases = dataset_loader.load_cases(seed=variant_cfg.random_seed)

    logger.info("%s caso(s) carregado(s) de %s", len(cases), str(root / args.dataset))
    runner = _build_runner(args.mode, baseline_cfg, variant_cfg, root)

    result = await runner.run_cases(cases)

    logger.info("Resumo da execução: %s", result.to_dict())
    print("Resumo da execução")
    print(f"  total_cases: {result.total_cases}")
    print(f"  succeeded: {result.succeeded}")
    print(f"  partially_completed: {result.partially_completed}")
    print(f"  failed_due_to_retries: {result.failed_due_to_retries}")
    print(f"  crashed: {result.crashed}")
    print(f"  skipped_completed: {result.skipped_completed}")
    return 0 if result.crashed == 0 else 1


def _build_runner(
    mode: str,
    baseline_cfg: BaselineConfig,
    runtime_cfg: RuntimeConfig,
    project_root: Path,
) -> object:
    if mode != "psychagent":
        raise ValueError(f"Modo não suportado: {mode}")

    prompt_root = project_root / "prompts"

    from .runner import PsychAgentRunner
    return PsychAgentRunner(
        baseline_config=baseline_cfg,
        runtime_config=runtime_cfg,
        prompt_root=prompt_root,
        logger=logging.getLogger("psychagent_sample"),
    )


def _apply_runtime_overrides(
    runtime_cfg: RuntimeConfig,
    *,
    resume_override: Optional[bool],
    overwrite_override: bool,
    concurrency_override: Optional[int],
    save_dir_override: Optional[str],
) -> RuntimeConfig:
    overwrite_value = overwrite_override or runtime_cfg.overwrite
    resume_value = runtime_cfg.resume if resume_override is None else bool(resume_override)
    if overwrite_value:
        resume_value = False

    merged = replace(
        runtime_cfg,
        concurrency=concurrency_override if concurrency_override is not None else runtime_cfg.concurrency,
        save_dir=save_dir_override if save_dir_override is not None else runtime_cfg.save_dir,
        resume=resume_value,
        overwrite=overwrite_value,
    )
    merged.validate()
    return merged


def _apply_baseline_runtime_overrides(
    baseline_cfg: BaselineConfig,
    runtime_cfg: RuntimeConfig,
) -> BaselineConfig:
    max_sessions = runtime_cfg.max_sessions if runtime_cfg.max_sessions is not None else baseline_cfg.max_sessions
    max_turns = runtime_cfg.max_counselor_turns if runtime_cfg.max_counselor_turns is not None else baseline_cfg.max_counselor_turns
    end_token = runtime_cfg.end_token if runtime_cfg.end_token is not None else baseline_cfg.end_token

    merged = BaselineConfig(
        name=baseline_cfg.name,
        family=baseline_cfg.family,
        backend=baseline_cfg.backend,
        model=baseline_cfg.model,
        base_url=baseline_cfg.base_url,
        api_key_env=baseline_cfg.api_key_env,
        temperature=baseline_cfg.temperature,
        max_tokens=baseline_cfg.max_tokens,
        memory_mode=baseline_cfg.memory_mode,
        max_sessions=max_sessions,
        max_counselor_turns=max_turns,
        end_token=end_token,
        timeout_sec=baseline_cfg.timeout_sec,
        max_retries=baseline_cfg.max_retries,
        retry_sleep_sec=baseline_cfg.retry_sleep_sec,
    )
    merged.validate()
    return merged


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    return asyncio.run(run_from_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
