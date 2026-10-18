#!/usr/bin/env python3
"""Write a collection of screenplays, then render each scene with generate.py."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import storyboard as sb

IDEAS = [
 ('tidal-signal', 'A tidal monitoring engineer finds an old distress signal beneath a coastal city; following it restores a forgotten public warning system.'),
 ('last-tram', 'A tram operator runs the final service to a deserted botanical district and discovers why a single passenger returns every evening.'),
 ('rain-archive', 'An archivist discovers a reservoir contains recordings of vanished rainfall and must choose which recording to release into the city.'),
 ('glass-orchard', 'A gardener investigates fruit ripening overnight in a sealed glass orchard and finds a hidden community maintaining its ancient machinery.'),
 ('eclipse-court', 'A caretaker prepares an empty ceremonial court for an eclipse and learns that its moving shadows unlock a buried observatory.'),
 ('salt-terminal', 'A courier reaches a terminal stranded in a salt desert with a parcel addressed to a station that no longer exists.'),
 ('underwater-window', 'An observatory technician sees a light moving outside a submerged window and follows its pattern to locate a stranded maintenance vessel.'),
 ('mountain-clock', 'A planetarium attendant notices the mechanical sky is running one day ahead and traces the fault to a forgotten astronomical event.'),
 ('fungus-library', 'A preservation worker enters a fungus-lit archive where living shelves have begun arranging records into an unexpected message.'),
 ('bridge-house', 'A bridge inspector discovers a small inhabited room within a vast migration bridge and must restore its failing water connection.'),
 ('storm-garden', 'Two workers shelter in an abandoned weather station and discover that its courtyard still protects the last surviving native plants.'),
 ('departure-hall', 'A cleaner at an orbital departure hall finds a ticket issued for today by a transport line closed decades ago and investigates its destination.'),
]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',default='granite4.1:3b')
    p.add_argument('--count',type=int,default=12)
    p.add_argument('--scenes',type=int,default=8)
    p.add_argument('--images-per-scene',type=int,default=3)
    p.add_argument('--duration',type=int,default=180)
    p.add_argument('--seed',type=int,default=20261018)
    p.add_argument('--out',type=Path,default=Path('storyboards/planet-season-01'))
    p.add_argument('--ollama',default='http://127.0.0.1:11434')
    p.add_argument('--comfy',default='http://127.0.0.1:7860')
    p.add_argument('--generator',type=Path,default=Path('generate.py'))
    p.add_argument('--workflow',type=Path,default=Path('workflow.json'))
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--write-only',action='store_true')
    mode.add_argument('--render-only',action='store_true')
    p.add_argument('--retry-incomplete',action='store_true')
    p.add_argument('--cpu-writer',action='store_true')
    a=p.parse_args()
    if not 1<=a.count<=12 or not 1<=a.scenes<=20 or not 1<=a.images_per_scene<=4 or a.duration<a.scenes:
        p.error('count 1–12, scenes 1–20, images-per-scene 1–4, duration >= scenes')
    if not 0<=a.seed<2**48-12000:p.error('Seed out of range')
    a.out.mkdir(parents=True,exist_ok=True)
    cfgpath=a.out/'season.json'
    config={k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items() if k not in ('write_only','render_only','retry_incomplete','out')}
    if cfgpath.exists():
        if json.loads(cfgpath.read_text())!=config:
            raise ValueError('Settings differ from saved season. Repeat the original settings or choose a new --out folder.')
    else:
        if a.render_only:raise ValueError('No saved season. Write it first.')
        sb.save(cfgpath,config)
    print(f'{a.count} screenplays × {a.scenes} scenes × {a.images_per_scene} variants = {a.count*a.scenes*a.images_per_scene} images',flush=True)
    runner=Path(__file__).with_name('storyboard.py')
    jobs=[]
    for i,(slug,idea) in enumerate(IDEAS[:a.count],1):
        folder=a.out/f'{a.out.name}-{i:02d}-{slug}'
        premise=(idea+' Write a complete standalone story, not an episode requiring a sequel. '
                 f'Use exactly {a.scenes} numbered scenes in the screenplay, each with its own scene heading. '
                 'Give exactly one representative storyboard shot per scene, in matching order. '
                 'Vary establishing views, medium compositions and object details across scenes. '
                 'At most two characters, restrained dialogue, no violence, a resolved ending.')
        cmd=[sys.executable,str(runner),'--model',a.model,'--premise',premise,
             '--shots',str(a.scenes),'--duration',str(a.duration),'--batch',str(a.images_per_scene),
             '--seed',str(a.seed+i*1000),'--out',str(folder),'--ollama',a.ollama,'--comfy',a.comfy,
             '--generator',str(a.generator),'--workflow',str(a.workflow)]
        if a.cpu_writer:cmd.append('--cpu-writer')
        if a.retry_incomplete:cmd.append('--retry-incomplete')
        jobs.append((folder,cmd))
    # All writing precedes all rendering: avoid swapping models between stories.
    if not a.render_only:
        for i,(folder,cmd) in enumerate(jobs,1):
            print(f'\nWriting screenplay {i}/{len(jobs)}: {folder.name}',flush=True)
            subprocess.run(cmd+['--write-only'],check=True)
    for folder,_ in jobs:
        if not (folder/'plan.json').exists():raise ValueError(f'Missing plan: {folder}; write the season first.')
    lines=['# Planet screenplay collection','',f'{a.count} films; {a.scenes} scenes each; {a.images_per_scene} image variants per scene.','']
    for folder,_ in jobs:
        plan=json.loads((folder/'plan.json').read_text())
        lines.extend([f"## {plan['title']}",'',plan['logline'],'',f'[Screenplay]({folder.name}/screenplay.md) · [Scene prompts]({folder.name}/prompts.md)',''])
    (a.out/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    if a.write_only:
        print(f'\nWriting complete. Review {a.out}/README.md, then repeat with --render-only.',flush=True)
        return
    for i,(folder,cmd) in enumerate(jobs,1):
        print(f'\nRendering screenplay {i}/{len(jobs)}: {folder.name}',flush=True)
        subprocess.run(cmd+['--render-only'],check=True)
    print('Season complete. Images remain in the ComfyUI server output directory.',flush=True)

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:raise SystemExit(130)
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        print(f'Error: {exc}',file=sys.stderr);raise SystemExit(1)
