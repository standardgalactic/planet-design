#!/usr/bin/env python3
"""Ollama screenplay + shot list -> existing ComfyUI generate.py. Standard library."""
import argparse
import hashlib
import json
from fractions import Fraction
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib import request,error

PREMISE='At dawn in a futuristic coastal city, a maintenance worker discovers that an abandoned botanical station is still sending a signal. A quiet three-minute mystery with a clear ending, no violence, at most two characters.'
STYLE='1970s science fiction matte painting, monumental concrete architecture, curved glass, muted earth colors, restrained contrast, warm amber light'
NEGATIVE='text, watermark, logo, blurry, distorted, oversaturated, neon'


def api(url,path,payload=None,timeout=1800):
    data=None if payload is None else json.dumps(payload).encode()
    req=request.Request(url.rstrip('/')+path,data=data,headers={'Content-Type':'application/json'})
    try:
        with request.urlopen(req,timeout=timeout) as response:
            body=response.read()
            return json.loads(body) if body.strip() else {}
    except error.HTTPError as exc:
        raise RuntimeError(f'{url}{path}: HTTP {exc.code}: {exc.read().decode(errors="replace")}') from exc


def save(path,obj):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)


def schema(count):
    text={'type':'string','minLength':1}
    return {'type':'object','additionalProperties':False,
      'properties':{'title':text,'logline':text,'screenplay':text,'shots':{'type':'array','minItems':count,'maxItems':count,
      'items':{'type':'object','additionalProperties':False,'properties':{'number':{'type':'integer'},'location':text,'duration_seconds':{'type':'integer','minimum':1},'action':text,'camera':text,'visual_prompt':text},'required':['number','location','duration_seconds','action','camera','visual_prompt']}}},
      'required':['title','logline','screenplay','shots']}


def validate(plan,count,duration):
    if not isinstance(plan,dict):raise ValueError('Plan must be a JSON object')
    for field in ('title','logline','screenplay'):
        if not isinstance(plan.get(field),str) or not plan[field].strip():raise ValueError('Missing text field: '+field)
    shots=plan.get('shots')
    if not isinstance(shots,list) or len(shots)!=count:raise ValueError(f'Need exactly {count} shots')
    for i,shot in enumerate(shots,1):
        if not isinstance(shot,dict):raise ValueError('Shot must be an object')
        if type(shot.get('number')) is not int or shot['number']!=i:raise ValueError('Shot numbers must be consecutive from 1')
        if type(shot.get('duration_seconds')) is not int or shot['duration_seconds']<=0:raise ValueError('Invalid shot duration')
        for field in ('location','action','camera','visual_prompt'):
            if not isinstance(shot.get(field),str) or not shot[field].strip():raise ValueError(f'Shot {i}: missing {field}')
        if len(shot['visual_prompt'])>1200:raise ValueError(f'Shot {i}: shorten visual prompt below 1200 characters')
        if '<think>' in shot['visual_prompt'].lower():raise ValueError('Unexpected think markup in visual prompt')
    if sum(s['duration_seconds'] for s in shots)!=duration:raise ValueError(f'Shot durations must sum to {duration}')


def normalize_durations(plan,count,duration):
    # Validate structure before modifying anything. Preserve the raw writer reply.
    original=sum(s.get('duration_seconds',0) for s in plan.get('shots',[]) if isinstance(s,dict) and type(s.get('duration_seconds')) is int)
    validate(plan,count,original)
    if original==duration:return
    remaining=duration-count
    scaled=[Fraction(remaining*s['duration_seconds'],original) for s in plan['shots']]
    values=[1+int(x) for x in scaled]
    order=sorted(range(count),key=lambda i:scaled[i]-int(scaled[i]),reverse=True)
    for i in order[:duration-sum(values)]:values[i]+=1
    plan['timing_adjustment']={'original_seconds':original,'target_seconds':duration,'method':'proportional allocation with at least one second per shot'}
    for shot,value in zip(plan['shots'],values):shot['duration_seconds']=value
    print(f'Adjusted editing durations: {original} → {duration} seconds',flush=True)


def write_documents(out,plan,style,negative):
    (out/'screenplay.md').write_text('# '+plan['title']+'\n\n'+plan['logline']+'\n\n'+plan['screenplay']+'\n')
    parts=['# Shot prompts','',f'Shared style: {style}','',f'Negative: {negative}','']
    for shot in plan['shots']:
        parts.extend([f"## Shot {shot['number']:02d}: {shot['location']}",'',f"Duration: {shot['duration_seconds']} seconds. Camera: {shot['camera']}",'',shot['action'],'',shot['visual_prompt']+', '+style,''])
    (out/'prompts.md').write_text('\n'.join(parts))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',default='granite4.1:3b')
    p.add_argument('--premise',default=PREMISE)
    p.add_argument('--style',default=STYLE)
    p.add_argument('--negative',default=NEGATIVE)
    p.add_argument('--shots',type=int,default=8)
    p.add_argument('--duration',type=int,default=180)
    p.add_argument('--batch',type=int,default=1)
    p.add_argument('--seed',type=int,default=20261018)
    p.add_argument('--ollama',default='http://127.0.0.1:11434')
    p.add_argument('--comfy',default='http://127.0.0.1:7860')
    p.add_argument('--generator',type=Path,default=Path('generate.py'))
    p.add_argument('--workflow',type=Path,default=Path('workflow.json'))
    p.add_argument('--out',type=Path,default=Path('storyboards/signal-at-dawn'))
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--write-only',action='store_true')
    modes.add_argument('--render-only',action='store_true')
    p.add_argument('--dry-run',action='store_true',help='Print saved shot prompts; never call a model')
    p.add_argument('--retry-incomplete',action='store_true',help='Explicitly resubmit interrupted image jobs, possibly duplicating outputs')
    p.add_argument('--cpu-writer',action='store_true',help='Run Ollama on CPU and skip ComfyUI model-release request')
    a=p.parse_args()
    if not 1<=a.shots<=40 or a.duration<a.shots or not 1<=a.batch<=4:p.error('Use shots 1–40, duration >= shots, batch 1–4')
    if not 0<=a.seed<2**48-a.shots:p.error('Seed outside supported range')
    out=a.out;planpath=out/'plan.json'
    if not planpath.exists():
        if a.render_only or a.dry_run:raise ValueError('No saved plan. Run --write-only first.')
        out.mkdir(parents=True,exist_ok=True)
        if not a.cpu_writer:
            queue=api(a.comfy,'/queue',timeout=30)
            if queue.get('queue_running') or queue.get('queue_pending'):raise ValueError('ComfyUI has active jobs. Let them finish before releasing models.')
            api(a.comfy,'/free',{'unload_models':True,'free_memory':True},timeout=30)
            time.sleep(2)
        structure=schema(a.shots)
        prompt=(f'Write an original short science-fiction screenplay and exactly {a.shots} storyboard shots. '
          f'Total planned shot duration must be exactly {a.duration} seconds. Premise: {a.premise}\n'
          'Use at most two characters. A beginning, discovery, consequence and resolved ending. '
          'Screenplay text must include scene headings, visible action and brief dialogue. '
          'The shot list must cover that screenplay in order. A still image represents each shot; durations are an editing plan, not generated motion. '
          'Each visual_prompt must describe ONE visible instant, with the concrete subject and camera framing first, in 25–60 words. '
          'Repeat visible character clothing/appearance whenever needed; prefer environment shots and silhouettes over face-dependent continuity. '
          'Do not put dialogue, written labels, camera movement, reasoning, or invisible backstory in visual_prompt. '
          f'Shared visual world: {a.style}\nReturn only JSON matching this schema:\n'+json.dumps(structure))
        (out/'writer-prompt.txt').write_text(prompt)
        options={'temperature':.5,'seed':a.seed,'num_ctx':8192,'num_predict':5500}
        if a.cpu_writer:options['num_gpu']=0
        payload={'model':a.model,'prompt':prompt,'stream':False,'format':structure,'keep_alive':0,'options':options}
        save(out/'writer-request.json',payload)
        print('Granite is writing the screenplay and shot list...',flush=True)
        reply=api(a.ollama,'/api/generate',payload)
        (out/'writer-response.txt').write_text(reply.get('response',''))
        if reply.get('done_reason')=='length':raise ValueError('Writer hit the token limit; use fewer shots and a new output folder')
        plan=json.loads(reply.get('response',''))
        normalize_durations(plan,a.shots,a.duration)
        validate(plan,a.shots,a.duration)
        save(planpath,plan)
        save(out/'production.json',{'model':a.model,'premise':a.premise,'style':a.style,'negative':a.negative,'shots':a.shots,'duration':a.duration})
    else:
        plan=json.loads(planpath.read_text())
        config=json.loads((out/'production.json').read_text())
        a.style=config['style'];a.negative=config['negative'];a.model=config['model']
        validate(plan,config['shots'],config['duration'])
    write_documents(out,plan,a.style,a.negative)
    print(f"Saved: {out/'screenplay.md'} and {out/'prompts.md'}",flush=True)
    if a.dry_run:
        print((out/'prompts.md').read_text());return
    if a.write_only:return
    if not a.generator.is_file() or not a.workflow.is_file():raise ValueError('Need existing generate.py and workflow.json in this working directory')
    # Explicitly unload the writer even when rendering a plan created earlier.
    api(a.ollama,'/api/generate',{'model':a.model,'keep_alive':0},timeout=120)
    workflow_hash=hashlib.sha256(a.workflow.read_bytes()).hexdigest()
    ledgerpath=out/'render.progress.json'
    ledger=json.loads(ledgerpath.read_text()) if ledgerpath.exists() else {}
    run=out.resolve().name
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',run):raise ValueError('Output folder basename must contain only letters, numbers, hyphens or underscores')
    for shot in plan['shots']:
        i=shot['number'];positive=shot['visual_prompt']+', '+a.style
        prefix=f'planet-design/storyboards/{run}/shot-{i:02d}'
        identity={'positive':positive,'negative':a.negative,'seed':a.seed+i-1,'batch':a.batch,'workflow':workflow_hash,'url':a.comfy,'prefix':prefix}
        key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        previous=ledger.get(key)
        if previous and previous['status']=='completed':
            print(f'Shot {i}: already completed',flush=True);continue
        if previous and not a.retry_incomplete:raise ValueError(f'Shot {i} is incomplete. Inspect its log and queue before using --retry-incomplete.')
        ledger[key]={**identity,'shot':i,'status':'running'};save(ledgerpath,ledger)
        command=[sys.executable,str(a.generator),positive,'--negative',a.negative,'--seed',str(a.seed+i-1),'--batch',str(a.batch),'--prefix',prefix,'--workflow',str(a.workflow),'--url',a.comfy]
        print(f'\nRendering shot {i}/{len(plan["shots"])}',flush=True)
        with (out/f'shot-{i:02d}.log').open('a') as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        print((out/f'shot-{i:02d}.log').read_text(),flush=True)
        ledger[key]['status']='completed' if result.returncode==0 else 'failed';save(ledgerpath,ledger)
        if result.returncode:raise RuntimeError(f'Shot {i} failed; see its log. No later shots submitted.')
    print('Storyboard generation complete. Images are in the ComfyUI server output directory under '+f'planet-design/storyboards/{run}/')


if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('\nInterrupted. Check the current server job before retrying.');raise SystemExit(130)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:print(f'Error: {exc}',file=sys.stderr);raise SystemExit(1)
