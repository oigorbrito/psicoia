"""CLI entrypoint for PsychAgent RFT workflows."""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import replace
from typing import Optional

try:
    from src.sample.core.schemas import BaselineConfig, RuntimeConfig
    from src.sample.io.config_loader import load_baseline_config, load_dataset_config, load_runtime_config
    from src.sample.io.dataset_loader import DatasetLoader
    from src.shared.file_utils import project_root
except ModuleNotFoundError:  # pragma: no cover - supports PYTHONPATH=src execution style
    from sample.core.schemas import BaselineConfig, RuntimeConfig
    from sample.io.config_loader import load_baseline_config, load_dataset_config, load_runtime_config
    from sample.io.dataset_loader import DatasetLoader
    from shared.file_utils import project_root

from .core.schemas import RFTRuntimeConfig
from .io.config_loader import load_rft_config
from .runner import RFTPsychAgentRunner


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute os fluxos RFT do PsicoIA (base de pesquisa PsychAgent).")
    parser.add_argument(
        "--baseline",
        default="configs/baselines/psychagent_sglang_local.yaml",
        help="Caminho do arquivo YAML de configuração de baseline.",
    )
    parser.add_argument(
        "--runtime",
        default="configs/runtime/psychagent_sglang_local.yaml",
        help="Caminho do arquivo YAML de runtime da demonstração.",
    )
    parser.add_argument(
        "--dataset",
        default="configs/datasets/profiles_rft.yaml",
        help="Caminho do arquivo YAML de configuração do conjunto de dados.",
    )
    parser.add_argument(
        "--rft-config",
        default="configs/runtime/rft_default.yaml",
        help="Caminho do arquivo YAML de runtime do RFT.",
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
    parser.add_argument("--overwrite", action="store_true", help="Força a substituição dos resultados existentes.")
    parser.add_argument("--concurrency", type=int, default=None, help="Substitui a concorrência de casos no runtime.")
    parser.add_argument("--save_dir", default=None, help="Substitui o diretório de resultados do runtime.")
    parser.add_argument("--rollout-n", type=int, default=None, help="Substitui o valor rollout_n do RFT.")
    parser.add_argument("--rollout-concurrency", type=int, default=None, help="Substitui a concorrência de rollout.")
    parser.add_argument(
        "--reward-method-concurrency",
        type=int,
        default=None,
        help="Substitui a concorrência de métodos de recompensa.",
    )
    parser.add_argument(
        "--strict-config",
        action="store_true",
        help="Falha diante de chaves desconhecidas ou não utilizadas (obsoletas/removidas) no runtime.",
    )
    parser.add_argument("--reward-api-key", default=None, help="Substitui a chave da API de recompensa.")
    parser.add_argument("--reward-api-base-url", default=None, help="Substitui a URL base da API de recompensa.")
    parser.add_argument("--reward-api-model", default=None, help="Substitui o modelo da API de recompensa.")
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
    rft_cfg = load_rft_config(str(root / args.rft_config))

    runtime_cfg = _apply_runtime_overrides(
        runtime_cfg,
        resume_override=args.resume,
        overwrite_override=args.overwrite,
        concurrency_override=args.concurrency,
        save_dir_override=args.save_dir,
    )
    baseline_cfg = _apply_baseline_runtime_overrides(baseline_cfg, runtime_cfg)
    rft_cfg = _apply_rft_overrides(rft_cfg, args)

    logger = logging.getLogger("psychagent_rft")
    logger.info("Auditoria da configuração de runtime: %s", runtime_audit.to_dict())
    logger.info("Configuração efetiva de runtime: %s", runtime_cfg.to_dict())
    logger.info("Configuração efetiva de baseline: %s", baseline_cfg.to_dict())
    dataset_loader = DatasetLoader(dataset_cfg, logger=logger)
    cases = dataset_loader.load_cases(seed=runtime_cfg.random_seed)

    logger.info("%s caso(s) carregado(s) de %s", len(cases), str(root / args.dataset))
    logger.info("Configuração do RFT: %s", rft_cfg.to_dict())

    runner = RFTPsychAgentRunner(
        baseline_config=baseline_cfg,
        runtime_config=runtime_cfg,
        prompt_root=root / "prompts",
        rft_runtime_config=rft_cfg,
        logger=logger,
    )
    try:
        result = await runner.run_cases(cases)
    finally:
        await runner.close()

    logger.info("Resumo da execução: %s", result.to_dict())
    print("Resumo da execução")
    print(f"  total_cases: {result.total_cases}")
    print(f"  succeeded: {result.succeeded}")
    print(f"  partially_completed: {result.partially_completed}")
    print(f"  failed_due_to_retries: {result.failed_due_to_retries}")
    print(f"  crashed: {result.crashed}")
    print(f"  skipped_completed: {result.skipped_completed}")
    return 0 if result.crashed == 0 else 1


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
    max_turns = (
        runtime_cfg.max_counselor_turns
        if runtime_cfg.max_counselor_turns is not None
        else baseline_cfg.max_counselor_turns
    )
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


def _apply_rft_overrides(cfg: RFTRuntimeConfig, args: argparse.Namespace) -> RFTRuntimeConfig:
    return replace(
        cfg,
        rollout_n=args.rollout_n if args.rollout_n is not None else cfg.rollout_n,
        rollout_concurrency=(
            args.rollout_concurrency if args.rollout_concurrency is not None else cfg.rollout_concurrency
        ),
        reward_method_concurrency=(
            args.reward_method_concurrency
            if args.reward_method_concurrency is not None
            else cfg.reward_method_concurrency
        ),
        reward_api_key=args.reward_api_key if args.reward_api_key is not None else cfg.reward_api_key,
        reward_api_base_url=(
            args.reward_api_base_url if args.reward_api_base_url is not None else cfg.reward_api_base_url
        ),
        reward_api_model=args.reward_api_model if args.reward_api_model is not None else cfg.reward_api_model,
    ).validated()


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    return asyncio.run(run_from_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
