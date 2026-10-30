"""CLI entrypoint for PsicoIA evaluation workflows."""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import replace
from pathlib import Path
from typing import List, Optional

from .core.schemas import EvalRuntimeConfig
from .io.config_loader import load_eval_config

try:
    from src.shared.file_utils import project_root
except ModuleNotFoundError:  # pragma: no cover - supports PYTHONPATH=src execution style
    from shared.file_utils import project_root


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute os fluxos de avaliação do PsicoIA (base de pesquisa PsychAgent).")
    parser.add_argument(
        "--config",
        default="configs/runtime/eval_default.yaml",
        help="Caminho do arquivo YAML de configuração do runtime de avaliação.",
    )
    parser.add_argument(
        "--input-format",
        default=None,
        choices=["auto", "eval_case", "sample"],
        help="Formato de entrada: detecção automática, eval_case nativo ou artefatos de demonstração.",
    )
    parser.add_argument("--data-root", default=None, help="Substitui a raiz dos dados de entrada da avaliação.")
    parser.add_argument("--output-root", default=None, help="Substitui a raiz dos resultados da avaliação.")
    parser.add_argument("--modalities", default=None, help="Abordagens a executar, separadas por vírgulas.")
    parser.add_argument("--methods", default=None, help="Nomes dos métodos a executar, separados por vírgulas.")
    parser.add_argument("--selected-files", default=None, help="Nomes dos arquivos a executar, separados por vírgulas.")
    parser.add_argument("--case-limit", type=int, default=None, help="Limita a quantidade de arquivos de casos.")

    parser.add_argument("--resume", dest="resume", action="store_true", help="Força a opção resume=True.")
    parser.add_argument("--no-resume", "--no_resume", dest="resume", action="store_false", help="Força a opção resume=False.")
    parser.set_defaults(resume=None)
    parser.add_argument("--overwrite", action="store_true", help="Força a substituição dos resultados existentes.")

    parser.add_argument("--file-concurrency", type=int, default=None, help="Substitui a concorrência por arquivo.")
    parser.add_argument("--method-concurrency", type=int, default=None, help="Substitui a concorrência por método.")
    parser.add_argument("--api-concurrency", type=int, default=None, help="Substitui a concorrência máxima da API.")
    parser.add_argument("--api-rps", type=int, default=None, help="Substitui o limite de solicitações da API por segundo.")
    parser.add_argument("--api-rps-period", type=float, default=None, help="Substitui o período do limite de taxa da API.")
    parser.add_argument("--api-key", default=None, help="Substitui a chave da API.")
    parser.add_argument("--api-base-url", default=None, help="Substitui a URL base da API.")
    parser.add_argument("--api-model", default=None, help="Substitui o nome do modelo da API.")

    parser.add_argument("--log-level", default="INFO", help="Nível de registro de eventos (logging).")
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


async def run_from_args(args: argparse.Namespace) -> int:
    from .manager.evaluation_orchestrator import EvaluationOrchestrator

    root = project_root()
    config_path = _resolve_config_path(root, args.config)
    runtime_cfg = load_eval_config(config_path)
    runtime_cfg = _apply_overrides(runtime_cfg, args, root)

    logger = logging.getLogger("psychagent_eval")
    logger.info("Configuração da execução de avaliação: %s", runtime_cfg.to_dict())

    orchestrator = EvaluationOrchestrator(runtime_cfg)
    try:
        summary = await orchestrator.run()
    finally:
        await orchestrator.close()

    logger.info("Resumo da avaliação: %s", summary.__dict__)
    print("Resumo da avaliação")
    print(f"  total_files: {summary.total_files}")
    print(f"  completed: {summary.completed}")
    print(f"  failed: {summary.failed}")
    print(f"  output_root: {runtime_cfg.output_root}")
    return 0 if summary.failed == 0 else 1


def _resolve_config_path(root: Path, config_arg: str) -> Path:
    path = Path(config_arg).expanduser()
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _apply_overrides(cfg: EvalRuntimeConfig, args: argparse.Namespace, root: Path) -> EvalRuntimeConfig:
    resume_value = cfg.resume if args.resume is None else bool(args.resume)
    overwrite_value = bool(args.overwrite or cfg.overwrite)
    if overwrite_value:
        resume_value = False

    data_root = cfg.data_root
    if args.data_root:
        data_root = _resolve_runtime_path(root, args.data_root)
    output_root = cfg.output_root
    if args.output_root:
        output_root = _resolve_runtime_path(root, args.output_root)

    merged = replace(
        cfg,
        data_root=data_root,
        output_root=output_root,
        input_format=args.input_format if args.input_format is not None else cfg.input_format,
        resume=resume_value,
        overwrite=overwrite_value,
        case_limit=args.case_limit if args.case_limit is not None else cfg.case_limit,
        modalities=_csv_to_list(args.modalities) if args.modalities else cfg.modalities,
        method_names=_csv_to_list(args.methods) if args.methods else cfg.method_names,
        selected_files=_csv_to_list(args.selected_files) if args.selected_files else cfg.selected_files,
        file_concurrency=args.file_concurrency if args.file_concurrency is not None else cfg.file_concurrency,
        method_concurrency=args.method_concurrency if args.method_concurrency is not None else cfg.method_concurrency,
        api_concurrency=args.api_concurrency if args.api_concurrency is not None else cfg.api_concurrency,
        api_rps=args.api_rps if args.api_rps is not None else cfg.api_rps,
        api_rps_period=args.api_rps_period if args.api_rps_period is not None else cfg.api_rps_period,
        api_key=args.api_key if args.api_key is not None else cfg.api_key,
        api_base_url=args.api_base_url if args.api_base_url is not None else cfg.api_base_url,
        api_model=args.api_model if args.api_model is not None else cfg.api_model,
    )
    return merged.validated()


def _resolve_runtime_path(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (root / path).resolve()


def _csv_to_list(raw: str) -> List[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    return asyncio.run(run_from_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
