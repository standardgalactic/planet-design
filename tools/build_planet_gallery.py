#!/usr/bin/env python3
"""Refresh embedded gallery data from real PNG files; no external packages."""
import argparse
import json
import re
import struct
from pathlib import Path


def png_prompt(path):
    # ComfyUI SaveImage stores its API graph in a PNG tEXt field named prompt.
    with path.open('rb') as stream:
        if stream.read(8) != b'\x89PNG\r\n\x1a\n':
            return None
        while True:
            head=stream.read(8)
            if len(head)!=8: break
            size,kind=struct.unpack('>I4s',head)
            if kind == b'tEXt' and size<=16_000_000:
                data=stream.read(size)
                key,sep,value=data.partition(b'\0')
                if key==b'prompt' and sep:
                    return json.loads(value.decode('utf-8'))
            else: stream.seek(size,1)
            stream.read(4)
            if kind==b'IEND':break
    return None


def metadata(graph):
    # Read only this project's simple sampler/CLIP/latent/checkpoint graph.
    samplers=[n for n in graph.values() if n.get('class_type')=='KSampler']
    if len(samplers)!=1:raise ValueError('Expected one KSampler')
    s=samplers[0]['inputs']
    def inputs(link):return graph[str(link[0])]['inputs']
    positive=inputs(s['positive'])['text'];negative=inputs(s['negative'])['text']
    model=inputs(s['model']);latent=inputs(s['latent_image'])
    return dict(prompt=positive,negative=negative,seed=s.get('seed'),settings={
        'checkpoint':model.get('ckpt_name'),'width':latent.get('width'),'height':latent.get('height'),
        'steps':s.get('steps'),'cfg':s.get('cfg'),'sampler':s.get('sampler_name'),
        'scheduler':s.get('scheduler'),'denoise':s.get('denoise')},
        metadata_source='Recovered from PNG prompt graph. Seed is the sampler batch seed, not a separately verified per-image seed.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=ap.parse_args()
    root=args.root.resolve();manifest=json.loads((root/'manifests/planet-design.json').read_text())
    jobs=manifest['jobs'];exact={f:j for j in jobs for f in j['files']}
    files=list(root.glob('city-test_*.png'))+list(root.glob('city-batch-*.png'))
    for folder in ('locations','world-expansion'):
        files.extend((root/folder).rglob('*.png'))
    rows=[];recovered=0;order={j['id']:i for i,j in enumerate(jobs)}
    for file in files:
        path=file.relative_to(root).as_posix();job=exact.get(path)
        if not job:
            local_prefix=path.rsplit('_',2)[0]
            job=next((j for j in jobs if j['prefix'].removeprefix('planet-design/')==local_prefix),None)
        row=dict(path=path,title=job['title'] if job else file.parent.name.replace('-',' ').title(),
                 category=job['category'] if job else 'Uncatalogued',job=job['id'] if job else '',
                 prompt=job['prompt'] if job else '',negative=job['negative'] if job else '',
                 settings=manifest['settings'],seed=None,metadata_source='Recorded session prompt; no readable PNG prompt metadata found.')
        try:
            graph=png_prompt(file)
            if graph:
                row.update(metadata(graph));recovered+=1
        except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
            print(f'Metadata warning: {path}: {exc}')
        rows.append(row)
    rows.sort(key=lambda r:(order.get(r['job'],999),r['path']))
    if not rows:raise SystemExit('No matching planet images found; index.html was not modified.')
    page=root/'index.html';html=page.read_text();payload=json.dumps(rows,ensure_ascii=True).replace('<','\\u003c')
    pattern=r'(<script id="gallery-data" type="application/json">).*?(</script>)'
    updated,n=re.subn(pattern,lambda m:m[1]+payload+m[2],html,flags=re.S)
    if n!=1:raise SystemExit('Expected exactly one embedded gallery-data block; no changes made.')
    page.write_text(updated)
    print(f'Indexed {len(rows)} real PNGs; recovered metadata for {recovered}.')

if __name__=='__main__':main()
