#!/usr/bin/env python3
"""Replay selected documented jobs using the existing generate.py."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--category',choices=['City studies','Locations','World expansion'])
p.add_argument('--job',help='Exact job ID in manifests/planet-design.json')
p.add_argument('--dry-run',action='store_true')
p.add_argument('--seed',type=int,help='Optional new base seed; historical seeds require PNG metadata')
p.add_argument('--url',default='http://127.0.0.1:7860')
a=p.parse_args();root=Path(__file__).resolve().parents[1]
m=json.loads((root/'manifests/planet-design.json').read_text())
jobs=[j for j in m['jobs'] if (not a.category or j['category']==a.category) and (not a.job or j['id']==a.job)]
if not jobs:raise SystemExit('No matching jobs')
print(f"{len(jobs)} jobs, {sum(j['batch'] for j in jobs)} images",flush=True)
for i,j in enumerate(jobs):
    command=[sys.executable,str(root/'generate.py'),j['prompt'],'--negative',j['negative'],
             '--batch',str(j['batch']),'--prefix',j['prefix'],'--url',a.url,'--workflow',str(root/'workflow.json')]
    if a.seed is not None:command.extend(['--seed',str(a.seed+i)])
    print('\n'+j['id']+'\n'+j['prompt'],flush=True)
    if not a.dry_run:subprocess.run(command,cwd=root,check=True)
