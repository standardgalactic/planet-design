#!/usr/bin/env python3
"""Collection runner for the generate.py supplied earlier. Standard library only."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def slug(value):
    value = re.sub(r'[^a-zA-Z0-9_-]+', '-', str(value)).strip('-').lower()
    if not value:
        raise ValueError('Names must contain at least one ASCII letter or number')
    return value


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
    temporary.replace(path)


def plan(config, selected):
    root = slug(config['name'])
    shared = config['shared_prompt'].strip()
    defaults = config.get('defaults', {})
    seen = set()
    for category, group in config['categories'].items():
        if selected and category not in selected:
            continue
        for entry in group['items']:
            settings = {**defaults, **group.get('settings', {}), **entry.get('settings', {})}
            variations = int(settings.get('variations', 1))
            batch = int(settings.get('batch', 4))
            if variations < 1 or batch < 1:
                raise ValueError('variations and batch must be positive')
            folder = f"{root}/{slug(category)}/{slug(entry['name'])}"
            if folder in seen:
                raise ValueError(f'Duplicate output folder: {folder}')
            seen.add(folder)
            # Distinction always precedes category context and the shared prompt.
            positive = ', '.join(p for p in [entry['prompt'].strip(), group.get('prompt', '').strip(), shared] if p)
            negative = ', '.join(p for p in [settings.get('negative', '').strip(), entry.get('negative', '').strip()] if p)
            base_seed = int(settings.get('seed', 1000))
            for variant in range(1, variations + 1):
                stable_offset = int(hashlib.sha256(folder.encode()).hexdigest()[:12], 16)
                seed = (base_seed + stable_offset + variant - 1) % (2**48)
                job = {'prefix': f'{folder}/variant-{variant:03d}', 'prompt': positive,
                       'negative': negative, 'seed': seed, 'batch': batch}
                job['key'] = hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest()
                yield job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', nargs='?', default='collection.json')
    parser.add_argument('--generator', default='generate.py')
    parser.add_argument('--workflow', default='workflow.json')
    parser.add_argument('--url', default='http://127.0.0.1:7860')
    parser.add_argument('--category', action='append', help='Repeat to select multiple categories')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--retry-incomplete', action='store_true', help='Explicitly resubmit interrupted/failed jobs; may duplicate images')
    parser.add_argument('--timeout', type=float, default=1800)
    args = parser.parse_args()
    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if args.category:
        unknown = set(args.category) - set(config['categories'])
        if unknown:
            raise ValueError(f'Unknown categories: {sorted(unknown)}')
    jobs = list(plan(config, args.category))
    if not jobs:
        raise ValueError('No jobs selected')
    workflow_path = Path(args.workflow)
    # Workflow content belongs to job identity, so changed settings regenerate.
    workflow_hash = hashlib.sha256(workflow_path.read_bytes()).hexdigest()
    for job in jobs:
        job['key'] = hashlib.sha256((job['key'] + workflow_hash + args.url).encode()).hexdigest()
    print(f"{len(jobs)} jobs; {sum(j['batch'] for j in jobs)} images", flush=True)
    if args.dry_run:
        for job in jobs:
            print(f"\n{job['prefix']} | seed={job['seed']} | batch={job['batch']}\n{job['prompt']}\nNegative: {job['negative']}")
        return
    if not Path(args.generator).is_file():
        raise ValueError(f'Cannot find {args.generator}; use the generate.py created earlier')
    manifest = config_path.with_name(config_path.stem + '.progress.json')
    state = json.loads(manifest.read_text()) if manifest.exists() else {'jobs': {}}
    for index, job in enumerate(jobs, 1):
        previous = state['jobs'].get(job['key'], {})
        if previous.get('status') == 'completed':
            print(f"[{index}/{len(jobs)}] Already completed: {job['prefix']}", flush=True)
            continue
        if previous and not args.retry_incomplete:
            raise ValueError(f"Incomplete job: {job['prefix']}. Check ComfyUI before using --retry-incomplete, since it may still be running.")
        command = [sys.executable, args.generator, job['prompt'], '--workflow', args.workflow,
                   '--url', args.url, '--seed', str(job['seed']), '--batch', str(job['batch']),
                   '--prefix', job['prefix'], '--negative', job['negative'], '--timeout', str(args.timeout)]
        state['jobs'][job['key']] = {**job, 'status': 'running'}
        save(manifest, state)
        print(f"\n[{index}/{len(jobs)}] {job['prefix']}", flush=True)
        try:
            result = subprocess.run(command, check=False)
        except KeyboardInterrupt:
            state['jobs'][job['key']]['status'] = 'interrupted'
            save(manifest, state)
            print('\nInterrupted. The server may still finish this job.', file=sys.stderr)
            return 130
        state['jobs'][job['key']]['status'] = 'completed' if result.returncode == 0 else 'failed'
        save(manifest, state)
        if result.returncode:
            print('Stopped after a failed job; progress was saved.', file=sys.stderr)
            return 1
    print('\nCollection complete.', flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
