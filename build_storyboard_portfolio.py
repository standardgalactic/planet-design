#!/usr/bin/env python3
"""Build an offline HTML portfolio from local ComfyUI outputs. Standard library only."""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import quote


def build(images,plans,output,template):
    records=[];metadata={};warnings=[]
    if plans.exists():
        for path in sorted(plans.rglob('plan.json')):
            try:
                plan=json.loads(path.read_text(encoding='utf-8'))
                configpath=path.with_name('production.json')
                config=json.loads(configpath.read_text(encoding='utf-8')) if configpath.exists() else {}
                metadata[path.parent.name]=(plan,config)
            except (OSError,ValueError) as exc:warnings.append(f'{path}: {exc}')
    for path in sorted(images.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.png','.webp','.jpg','.jpeg'):continue
        rel=path.relative_to(images)
        film=rel.parts[0] if len(rel.parts)>1 else 'ungrouped'
        plan,config=metadata.get(film,({},{}))
        match=re.search(r'shot-(\d+)',path.stem)
        number=int(match.group(1)) if match else 0
        shot=next((s for s in plan.get('shots',[]) if s.get('number')==number),{})
        href=quote(Path(os.path.relpath(path.resolve(),output.parent.resolve())).as_posix(),safe='/')
        records.append({'id':rel.as_posix(),'url':href,'film':film,
            'title':plan.get('title',film.replace('-',' ')),'logline':plan.get('logline',''),
            'screenplay':plan.get('screenplay',''),'scene':number,'location':shot.get('location',''),
            'action':shot.get('action',''),'camera':shot.get('camera',''),
            'duration':shot.get('duration_seconds',''),'prompt':shot.get('visual_prompt',''),
            'style':config.get('style',''),'negative':config.get('negative',''),'filename':path.name})
    records.sort(key=lambda r:(r['film'],r['scene'],r['filename']))
    data=json.dumps(records,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    html=template.read_text(encoding='utf-8').replace('/*PORTFOLIO_DATA*/[]',data)
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix(output.suffix+'.tmp');temp.write_text(html,encoding='utf-8');temp.replace(output)
    print(f'Built {output}: {len(records)} images across {len(set(r["film"] for r in records))} screenplays')
    for warning in warnings:print('Warning:',warning)
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images',type=Path,default=Path('output/comfy/planet-design/storyboards'))
    p.add_argument('--plans',type=Path,default=Path('storyboards'))
    p.add_argument('--out',type=Path,default=Path('storyboard-portfolio.html'))
    a=p.parse_args()
    if not a.images.is_dir():p.error(f'Image directory does not exist: {a.images}. Use --images with the host output folder.')
    build(a.images,a.plans,a.out,Path(__file__).with_name('storyboard_portfolio.template.html'))

if __name__=='__main__':main()
