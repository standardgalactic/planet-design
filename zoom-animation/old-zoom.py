#!/usr/bin/env python3
"""Iterative ComfyUI image-to-image zoom. Requires Pillow; MP4 needs ffmpeg."""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from urllib import request, error, parse
from PIL import Image, ImageOps

DEFAULT_PROMPT = 'futuristic coastal city, concrete terraces, curved glass, ocean mist, 1970s science fiction matte painting'
DEFAULT_NEGATIVE = 'text, watermark, logo, blurry, distorted, low quality'


def crop_zoom(image, scale, x, y):
    w,h=image.size
    cw,ch=w/scale,h/scale
    left=(w-cw)*x;top=(h-ch)*y
    return image.resize((w,h),Image.Resampling.LANCZOS,box=(left,top,left+cw,top+ch))


def save_state(path, state):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(state,indent=2)+'\n')
    temp.replace(path)


class Client:
    def __init__(self,url):self.url=url.rstrip('/')
    def call(self,path,data=None,ctype='application/json',raw=False):
        if isinstance(data,dict):data=json.dumps(data).encode()
        req=request.Request(self.url+path,data=data,headers={'Content-Type':ctype})
        try:
            with request.urlopen(req,timeout=60) as response:body=response.read()
        except error.HTTPError as exc:
            raise RuntimeError(f'HTTP {exc.code}: {exc.read().decode(errors="replace")}') from exc
        return body if raw else json.loads(body)
    def upload(self,image):
        buf=io.BytesIO();image.save(buf,format='PNG')
        boundary='zoom-'+uuid.uuid4().hex
        name=uuid.uuid4().hex+'.png'
        body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: image/png\r\n\r\n'.encode()+buf.getvalue()+f'\r\n--{boundary}--\r\n'.encode())
        r=self.call('/upload/image',body,'multipart/form-data; boundary='+boundary)
        return (r.get('subfolder','').strip('/')+'/' +r['name']).lstrip('/')
    def wait(self,prompt_id,timeout):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            result=self.call('/history/'+prompt_id).get(prompt_id)
            if result:
                status=result.get('status',{})
                if status.get('status_str')=='error':
                    raise RuntimeError('ComfyUI execution failed: '+json.dumps(status))
                images=result.get('outputs',{}).get('9',{}).get('images',[])
                if images:
                    item=images[0]
                    query=parse.urlencode({k:item.get(k,'') for k in ('filename','subfolder','type')})
                    raw=self.call('/view?'+query,raw=True)
                    with Image.open(io.BytesIO(raw)) as image:return image.convert('RGB'),item
                if status.get('completed'):raise RuntimeError('Job completed without an image')
            time.sleep(1)
        raise TimeoutError('Job is still unconfirmed. Rerun the same command to resume waiting; do not submit a duplicate.')


def graph(image,args,checkpoint,prefix):
    return {
      '4':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':checkpoint}},
      '6':{'class_type':'CLIPTextEncode','inputs':{'text':args.prompt,'clip':['4',1]}},
      '7':{'class_type':'CLIPTextEncode','inputs':{'text':args.negative,'clip':['4',1]}},
      '10':{'class_type':'LoadImage','inputs':{'image':image}},
      '11':{'class_type':'VAEEncode','inputs':{'pixels':['10',0],'vae':['4',2]}},
      '3':{'class_type':'KSampler','inputs':{'seed':args.seed,'steps':args.steps,'cfg':args.cfg,'sampler_name':'euler','scheduler':'normal','denoise':args.denoise,'model':['4',0],'positive':['6',0],'negative':['7',0],'latent_image':['11',0]}},
      '8':{'class_type':'VAEDecode','inputs':{'samples':['3',0],'vae':['4',2]}},
      '9':{'class_type':'SaveImage','inputs':{'filename_prefix':prefix,'images':['8',0]}}
    }


def assemble(out,args):
    render=out/'frames';render.mkdir(exist_ok=True)
    keys=[out/'keyframes'/f'{i:05d}.png' for i in range(args.frames+1)]
    count=0
    with Image.open(keys[0]) as image:previous=image.convert('RGB')
    previous.save(render/f'{count:06d}.png');count+=1
    for key in keys[1:]:
        with Image.open(key) as image:following=image.convert('RGB')
        for j in range(1,args.inbetweens+1):
            t=j/args.inbetweens
            frame=crop_zoom(previous,args.zoom**t,args.focus_x,args.focus_y)
            # Crossfade introduces regenerated detail; it is not optical flow.
            alpha=t*t*(3-2*t)
            Image.blend(frame,following,alpha).save(render/f'{count:06d}.png');count+=1
        previous=following
    if args.ping_pong:
        for i in range(count-2,0,-1):
            shutil.copyfile(render/f'{i:06d}.png',render/f'{count:06d}.png');count+=1
    # One shared palette avoids independently quantized frame palettes.
    with Image.open(render/'000000.png') as image:palette=image.convert('RGB').quantize(colors=256)
    frames=[]
    for i in range(count):
        with Image.open(render/f'{i:06d}.png') as image:
            frames.append(image.convert('RGB').quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG))
    duration=max(10,round(100/args.fps)*10)
    frames[0].save(out/'zoom.gif',save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=2,optimize=False)
    for frame in frames:frame.close()
    palette.close()
    print(f'Saved {out / "zoom.gif"} ({count} frames, approximately {1000/duration:.2f} fps)',flush=True)
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg:
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str(args.fps),'-i',str(render/'%06d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'zoom.mp4')],check=True)
        print(f'Saved {out / "zoom.mp4"}',flush=True)
    else:print('ffmpeg not found; GIF is ready. Install ffmpeg and rerun to also create MP4.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',nargs='?',type=Path,default=Path('template.png'))
    p.add_argument('--prompt',default=DEFAULT_PROMPT)
    p.add_argument('--negative',default=DEFAULT_NEGATIVE)
    p.add_argument('--url',default='http://127.0.0.1:7860')
    p.add_argument('--checkpoint',help='Defaults to checkpoint in workflow.json')
    p.add_argument('--workflow',type=Path,default=Path('workflow.json'))
    p.add_argument('--frames',type=int,default=24,help='Number of AI regeneration steps')
    p.add_argument('--zoom',type=float,default=1.03,help='Zoom factor per AI step')
    p.add_argument('--denoise',type=float,default=.25)
    p.add_argument('--steps',type=int,default=20)
    p.add_argument('--cfg',type=float,default=8)
    p.add_argument('--seed',type=int,default=12345,help='Fixed sampler seed reused at every step')
    p.add_argument('--size',type=int,default=512,help='Square working resolution')
    p.add_argument('--focus-x',type=float,default=.5,help='0 left, 1 right; crop position')
    p.add_argument('--focus-y',type=float,default=.5,help='0 top, 1 bottom; crop position')
    p.add_argument('--inbetweens',type=int,default=6,help='Rendered frames per AI step')
    p.add_argument('--fps',type=int,default=12)
    p.add_argument('--ping-pong',action='store_true',help='Reverse after reaching the deepest frame')
    p.add_argument('--timeout',type=float,default=1800)
    p.add_argument('--out',type=Path,default=Path('zoom-output/test'))
    p.add_argument('--assemble-only',action='store_true',help='Rebuild animation from saved keyframes without contacting ComfyUI')
    a=p.parse_args()
    if not 1<=a.frames<=300 or not 1<=a.inbetweens<=30 or not 1<=a.fps<=50: p.error('Use frames 1–300, inbetweens 1–30 and fps 1–50')
    if not 1<a.zoom<=1.5 or not 0<a.denoise<=1:p.error('zoom must be >1 and <=1.5; denoise must be >0 and <=1')
    if a.size<64 or a.size%64 or not 0<=a.focus_x<=1 or not 0<=a.focus_y<=1:p.error('size must be a multiple of 64; focus coordinates must be 0–1')
    if a.steps<1 or a.cfg<0 or not 0<=a.seed<2**64 or a.timeout<=0:p.error('Invalid sampling or timeout setting')
    estimated=(1+a.frames*a.inbetweens)*(2 if a.ping_pong else 1)*a.size*a.size
    if estimated>256_000_000:p.error('GIF would use too much memory; reduce frames, inbetweens or size')
    checkpoint=a.checkpoint
    if not checkpoint:
        workflow=json.loads(a.workflow.read_text())
        if isinstance(workflow.get('nodes'),list):
            checkpoints=[n['widgets_values'][0] for n in workflow['nodes'] if n['type']=='CheckpointLoaderSimple']
        else:checkpoints=[n['inputs']['ckpt_name'] for n in workflow.values() if isinstance(n,dict) and n.get('class_type')=='CheckpointLoaderSimple']
        if len(checkpoints)!=1:raise ValueError('Use --checkpoint to select one model explicitly')
        checkpoint=checkpoints[0]
    source=a.image.read_bytes()
    settings={k:v for k,v in vars(a).items() if k not in ('out','timeout','assemble_only','fps','inbetweens','ping_pong','workflow','image','checkpoint')}
    settings.update(checkpoint=checkpoint,source_sha256=hashlib.sha256(source).hexdigest())
    out=a.out;statepath=out/'progress.json'
    if statepath.exists():
        state=json.loads(statepath.read_text())
        if state['settings']!=settings:raise ValueError('Generation settings or source changed. Use a new --out folder.')
    else:
        if a.assemble_only:raise ValueError('No saved run at this --out folder')
        if out.exists() and any(out.iterdir()):raise ValueError('Output folder is nonempty without a progress file; choose a new --out')
        (out/'keyframes').mkdir(parents=True,exist_ok=True)
        with Image.open(io.BytesIO(source)) as image:
            image=ImageOps.exif_transpose(image)
            image=ImageOps.fit(image.convert('RGB'),(a.size,a.size),method=Image.Resampling.LANCZOS)
            image.save(out/'keyframes/00000.png')
        state={'settings':settings,'run_id':uuid.uuid4().hex,'completed':0,'pending':None,'outputs':[]}
        save_state(statepath,state)
    if not a.assemble_only and state['completed']<a.frames:
        client=Client(a.url)
        info=client.call('/object_info/CheckpointLoaderSimple')
        available=info['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]
        if checkpoint not in available:raise ValueError(f'Checkpoint {checkpoint!r} not available; available={available}')
        for i in range(state['completed']+1,a.frames+1):
            target=out/'keyframes'/f'{i:05d}.png'
            if state['pending'] is None:
                with Image.open(out/'keyframes'/f'{i-1:05d}.png') as image:
                    cropped=crop_zoom(image.convert('RGB'),a.zoom,a.focus_x,a.focus_y)
                upload=client.upload(cropped)
                prefix=f'planet-design/zoom/{state["run_id"]}/step-{i:04d}'
                workflow=graph(upload,a,checkpoint,prefix)
                (out/'workflow-last.json').write_text(json.dumps(workflow,indent=2))
                submitted=client.call('/prompt',{'prompt':workflow})
                if submitted.get('node_errors'):raise RuntimeError(json.dumps(submitted['node_errors']))
                state['pending']={'step':i,'prompt_id':submitted['prompt_id']}
                save_state(statepath,state)
            if state['pending']['step']!=i:raise ValueError('Pending step does not match progress')
            print(f'[{i}/{a.frames}] queued {state["pending"]["prompt_id"]}',flush=True)
            image,remote=client.wait(state['pending']['prompt_id'],a.timeout)
            if image.size!=(a.size,a.size):raise ValueError(f'Unexpected server image size {image.size}')
            temp=target.with_suffix('.tmp');image.save(temp,format='PNG');temp.replace(target)
            state['outputs'].append({'step':i,'prompt_id':state['pending']['prompt_id'],'remote':remote})
            state['completed']=i;state['pending']=None;save_state(statepath,state)
            print(f'  saved {target}',flush=True)
    if state['completed']<a.frames:raise ValueError('Not all required keyframes exist yet')
    assemble(out,a)
    print(f'Total nominal zoom: {a.zoom**a.frames:.2f}x')


if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('\nStopped waiting. The server job may still run. Rerun the same command to resume.');raise SystemExit(130)
    except (OSError,ValueError,KeyError,RuntimeError,TimeoutError,subprocess.CalledProcessError) as exc:
        print(f'Error: {exc}');raise SystemExit(1)
