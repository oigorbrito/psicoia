#!/usr/bin/env python3
"""Local, resumable PsicoIA catalog PT-BR draft translation via Ollama.

Drafts go to a separate directory. Existing locale sidecars and originals
are never overwritten. Clinical/behavioral translation requires review.
No paid services or cloud APIs are used.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CJK = re.compile(r'[\u3400-\u9fff]')
PLACEHOLDER = re.compile(r'\{\{.*?\}\}|\$\{[^{}]+\}|\{[A-Za-z_][A-Za-z0-9_.-]*\}')
ALLOWED_FIELDS = ('skill_name', 'skill_description')


class OllamaUnavailable(RuntimeError):
    """The local Ollama endpoint could not serve a request after bounded retries."""


def catalogs(root):
    for source in sorted((root / 'assets/skills/sect').glob('*/stage*/*_skills.json')):
        target = source.with_name(source.stem + '.pt-BR.json')
        if not target.exists():
            yield source, target


def call_ollama(url, model, batch, timeout, attempts):
    entries = [{'id': str(k), 'skill_name': v['skill_name'],
                'skill_description': v['skill_description']} for k, v in batch]
    user = json.dumps({'entries': entries}, ensure_ascii=False)
    system = (
        'Você é um tradutor técnico de chinês para português brasileiro (pt-BR) de um catálogo de psicologia. '
        'Traduza fielmente o nome e a descrição de cada entrada, sem acrescentar fatos, interpretações, diagnósticos ou recomendações. '
        'Preserve o sentido, números, instrumentos citados, cautelas e terminologia. '
        'Preserve cada placeholder exatamente, incluindo delimitadores, espaços e nome da variável. '
        'Não responda à tarefa clínica; apenas traduza o texto. '
        'Retorne EXCLUSIVAMENTE um objeto JSON com a chave entries: lista de objetos com id, skill_name e skill_description. '
        'Retorne cada id original uma única vez. Não inclua campos extras, comentários ou texto de raciocínio.'
    )
    payload = json.dumps({'model': model, 'stream': False, 'think': False,
                          'format': 'json', 'options': {'temperature': 0.0},
                          'messages': [{'role': 'system', 'content': system},
                                       {'role': 'user', 'content': user}]}, ensure_ascii=False).encode('utf-8')
    err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url.rstrip('/') + '/api/chat', payload,
                                         {'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = json.load(response)
            raw = body.get('message', {}).get('content', '')
            if not raw.strip():
                raise ValueError('Ollama devolveu resposta pública vazia')
            result = json.loads(raw)
            if isinstance(result, list):
                translated = result
            else:
                translated = result['entries']
            if not isinstance(translated, list):
                raise ValueError('JSON não contém lista de entradas')
            expected = {str(k) for k, _ in batch}
            received = [str(x.get('id')) for x in translated]
            if len(received) != len(expected) or set(received) != expected:
                raise ValueError('IDs da tradução não correspondem ao lote')
            source_by_id = {str(k): v for k, v in batch}
            clean = {}
            for x in translated:
                tid = str(x['id'])
                if tid in clean:
                    raise ValueError('ID duplicado')
                for field in ALLOWED_FIELDS:
                    value = x.get(field)
                    if not isinstance(value, str) or not value.strip() or CJK.search(value):
                        raise ValueError(f'Campo ausente, vazio ou com CJK: {tid}.{field}')
                    expected_placeholders = PLACEHOLDER.findall(source_by_id[tid][field])
                    actual_placeholders = PLACEHOLDER.findall(value)
                    if actual_placeholders != expected_placeholders:
                        raise ValueError(f'Placeholder alterado ou ausente: {tid}.{field}')
                clean[tid] = {f: x[f].strip() for f in ALLOWED_FIELDS}
            return clean
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as e:
            err = e
            print(f'  tentativa {i+1}/{attempts} falhou: {type(e).__name__}: {e}', file=sys.stderr)
            if i + 1 < attempts:
                time.sleep(1)
    message = f'Lote rejeitado após {attempts} tentativas: {err}'
    if isinstance(err, (urllib.error.URLError, TimeoutError)):
        raise OllamaUnavailable(message) from err
    raise RuntimeError(message) from err


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    try:
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def verify(source, draft):
    if set(source) != set(draft):
        raise ValueError('IDs ausentes ou extras')
    for key, row in source.items():
        trans = draft[key]
        if set(row) != set(trans):
            raise ValueError(f'Campos alterados em {key}')
        for field in row:
            if field in ALLOWED_FIELDS:
                if not isinstance(trans[field], str) or not trans[field] or CJK.search(trans[field]):
                    raise ValueError(f'Tradução inválida em {key}.{field}')
                if PLACEHOLDER.findall(row[field]) != PLACEHOLDER.findall(trans[field]):
                    raise ValueError(f'Placeholder alterado ou ausente em {key}.{field}')
            elif trans[field] != row[field]:
                raise ValueError(f'Campo estrutural alterado em {key}.{field}')
    return len(draft)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path, default=None, help='Saída de rascunhos (padrão: <root>/ptbr-drafts)')
    p.add_argument('--url', default='http://127.0.0.1:11434')
    p.add_argument('--model', default='qwen3.5:4b')
    p.add_argument('--batch-size', type=int, default=8)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--attempts', type=int, default=2)
    p.add_argument('--max-records', type=int, default=0, help='0 processa todos os registros restantes')
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    out = (args.output or root / 'ptbr-drafts').resolve()
    if args.batch_size < 1 or args.batch_size > 25:
        p.error('--batch-size deve estar entre 1 e 25')
    if args.attempts < 1:
        p.error('--attempts deve ser pelo menos 1')
    if not (root / 'assets/skills/sect').exists():
        p.error('Raiz do projeto inválida: assets/skills/sect ausente')
    files = list(catalogs(root))
    print(f'Catálogos PT-BR ausentes: {len(files)}; registros: {sum(len(json.loads(a.read_text(encoding="utf-8"))) for a,_ in files)}')
    processed = 0
    attempted = 0
    failed_records = []
    incomplete_drafts = False
    for src, final_target in files:
        rel = src.relative_to(root)
        draft_path = out / rel.parent / final_target.name
        source = json.loads(src.read_text(encoding='utf-8'))
        draft = json.loads(draft_path.read_text(encoding='utf-8')) if draft_path.exists() else {}
        if not isinstance(source, dict) or not isinstance(draft, dict):
            raise ValueError(f'Formato de catálogo inválido: {src}')
        if any(k not in source for k in draft):
            raise ValueError(f'Rascunho com IDs extras: {draft_path}')
        for k,v in draft.items():
            verify({k:source[k]}, {k:v})
        if args.verify_only:
            if len(draft) == len(source):
                print(f'{rel}: COMPLETO; {len(draft)}/{len(source)} rascunhos validados')
            else:
                missing = len(source) - len(draft)
                print(f'{rel}: INCOMPLETO; {len(draft)}/{len(source)} rascunhos validados ({missing} pendentes)')
                incomplete_drafts = True
            continue
        pending = [(k,v) for k,v in source.items() if k not in draft]
        print(f'\n{rel}: {len(draft)}/{len(source)} concluídos')
        for start in range(0,len(pending),args.batch_size):
            if args.max_records and attempted >= args.max_records:
                break
            batch = pending[start:start+args.batch_size]
            if args.max_records:
                batch = batch[:args.max_records-attempted]
            if not batch:
                break
            attempted += len(batch)

            def translate_and_save(current_batch):
                nonlocal processed
                try:
                    translated = call_ollama(args.url,args.model,current_batch,args.timeout,args.attempts)
                except OllamaUnavailable:
                    raise
                except Exception as e:
                    if len(current_batch) == 1:
                        failed_id = str(current_batch[0][0])
                        failed_records.append((rel, failed_id, str(e)))
                        print(f'PENDING {rel} id={failed_id}: {e}', file=sys.stderr)
                        return
                    midpoint = len(current_batch) // 2
                    print(f'  Lote rejeitado ({len(current_batch)} registros); isolando falhas e continuando.', file=sys.stderr)
                    translate_and_save(current_batch[:midpoint])
                    translate_and_save(current_batch[midpoint:])
                    return
                for k,v in current_batch:
                    draft[k] = {**v, **translated[str(k)]}
                atomic_json(draft_path,draft)
                processed += len(current_batch)
                print(f'  {len(draft)}/{len(source)} traduções verificadas; total desta execução: {processed}',flush=True)

            try:
                translate_and_save(batch)
            except OllamaUnavailable as e:
                print(f'FALHA GLOBAL do endpoint Ollama em {rel}: {e}', file=sys.stderr)
                print('Checkpoint preservado; execução interrompida porque o serviço local não está disponível.', file=sys.stderr)
                return 2
        if len(draft) == len(source):
            verify(source,draft)
            print(f'  COMPLETO: {draft_path} (rascunho, requer revisão humana)')
        elif args.max_records and attempted >= args.max_records:
            print(f'  INCOMPLETO: {draft_path} ({len(draft)}/{len(source)}; somente rascunho retomável, não é catálogo válido)')
        elif len(draft) < len(source):
            print(f'  PENDING: {draft_path} ({len(draft)}/{len(source)}; registros restantes preservados para retomada)')
        if args.max_records and attempted >= args.max_records:
            break
    print(f'\nTotal tentado nesta execução: {attempted}; traduzido e salvo: {processed}; registros com falha isolada: {len(failed_records)}. Rascunhos em: {out}')
    print('ATENÇÃO: não copiar automaticamente para assets/skills sem revisão de tradução e validação de comportamento.')
    return 2 if failed_records else (1 if args.verify_only and incomplete_drafts else 0)

if __name__=='__main__':
    raise SystemExit(main())
