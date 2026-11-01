#!/usr/bin/env python3
"""Generate new images from the base images in images/ through a local ComfyUI server.

Each file in images/ supplies a base prompt. The prompt comes from a sidecar
text file with the same stem (tidal-causeway.png -> tidal-causeway.txt) when one
exists, and otherwise from the file name itself, so
"tidal-causeway-and-material-memory.png" becomes
"tidal causeway and material memory".

Two modes:
  txt2img  (default) renders fresh images from the prompt alone.
  img2img  starts from the base image and reworks it; --denoise sets how far
           the result may drift (0.3 stays close, 0.8 changes a lot).

Only the standard library is used. Defaults follow the repo README: Stable
Diffusion 1.5, 512x512, 20 steps, CFG 8, Euler, normal scheduler, server at
http://127.0.0.1:7860. If workflow.json (ComfyUI API format) sits next to this
script it is used for txt2img, with only the prompt, seed and output prefix
replaced.

Examples:
  python3 generate_from_images.py --dry-run
  python3 generate_from_images.py --count 4
  python3 generate_from_images.py --mode img2img --denoise 0.55 --count 2
  python3 generate_from_images.py --only tidal --suffix "dusk, long shadows"
"""

import argparse
import copy
import json
import mimetypes
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

DEFAULT_SUFFIX = (
    "original futuristic planet, scenery and set design, cinematic concept art, "
    "highly detailed, atmospheric lighting"
)
DEFAULT_NEGATIVE = (
    "text, watermark, signature, logo, people, blurry, low quality, "
    "deformed, oversaturated"
)


def prompt_from_filename(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    stem = re.sub(r"[_-]?\d{3,5}_?$", "", stem)  # _00001_ style counters
    stem = re.sub(r"[-_]\d{1,2}$", "", stem)  # -01 style counters
    words = re.sub(r"[-_]+", " ", stem).strip()
    return words


def base_prompt(path):
    sidecar = os.path.splitext(path)[0] + ".txt"
    if os.path.isfile(sidecar):
        with open(sidecar, encoding="utf-8") as fh:
            text = fh.read().strip()
        if text:
            return text
    return prompt_from_filename(path)


def collect_images(folder, only):
    found = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTS and os.path.isfile(path):
            if only and only.lower() not in name.lower():
                continue
            found.append(path)
    return found


# ---------------------------------------------------------------- HTTP helpers

def http_json(url, data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def upload_image(server, path):
    boundary = uuid.uuid4().hex
    filename = os.path.basename(path)
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        payload = fh.read()
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
        f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n".encode(),
        payload,
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; "
        f"name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode(),
    ]
    req = urllib.request.Request(
        server + "/upload/image",
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))["name"]


# ------------------------------------------------------------------- workflows

def builtin_graph(a, positive, negative, seed, prefix, uploaded=None):
    graph = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": a.checkpoint}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": positive, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": negative, "clip": ["1", 1]}},
        "6": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"images": ["6", 0], "filename_prefix": prefix}},
    }
    if uploaded is None:
        graph["4"] = {"class_type": "EmptyLatentImage",
                      "inputs": {"width": a.width, "height": a.height,
                                 "batch_size": 1}}
        latent, denoise = ["4", 0], 1.0
    else:
        graph["8"] = {"class_type": "LoadImage", "inputs": {"image": uploaded}}
        graph["9"] = {"class_type": "ImageScale",
                      "inputs": {"image": ["8", 0],
                                 "upscale_method": "lanczos",
                                 "width": a.width, "height": a.height,
                                 "crop": "center"}}
        graph["4"] = {"class_type": "VAEEncode",
                      "inputs": {"pixels": ["9", 0], "vae": ["1", 2]}}
        latent, denoise = ["4", 0], a.denoise
    graph["5"] = {"class_type": "KSampler",
                  "inputs": {"model": ["1", 0], "positive": ["2", 0],
                             "negative": ["3", 0], "latent_image": latent,
                             "seed": seed, "steps": a.steps, "cfg": a.cfg,
                             "sampler_name": "euler", "scheduler": "normal",
                             "denoise": denoise}}
    return graph


def patched_workflow(template, positive, negative, seed, prefix):
    """Patch an API-format workflow.json. Returns None if it cannot be patched."""
    if not isinstance(template, dict):
        return None
    graph = copy.deepcopy(template)
    samplers = [n for n in graph.values()
                if isinstance(n, dict) and n.get("class_type") == "KSampler"]
    saves = [n for n in graph.values()
             if isinstance(n, dict) and n.get("class_type") == "SaveImage"]
    if not samplers or not saves:
        return None
    for node in samplers:
        node["inputs"]["seed"] = seed
        for key, text in (("positive", positive), ("negative", negative)):
            link = node["inputs"].get(key)
            if isinstance(link, list) and link and str(link[0]) in graph:
                target = graph[str(link[0])]
                if target.get("class_type") == "CLIPTextEncode":
                    target["inputs"]["text"] = text
    for node in saves:
        node["inputs"]["filename_prefix"] = prefix
    return graph


def load_template(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(data, dict) and "nodes" in data:  # editor format, not API format
        return None
    return data


# ------------------------------------------------------------------- execution

def wait_for_result(server, prompt_id, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = http_json(f"{server}/history/{prompt_id}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(1.5)
    raise TimeoutError(f"no result after {timeout} seconds")


def download_outputs(server, entry, out_dir, stem, index):
    saved = []
    for node_output in entry.get("outputs", {}).values():
        for img in node_output.get("images", []):
            query = urllib.parse.urlencode({
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })
            with urllib.request.urlopen(f"{server}/view?{query}", timeout=120) as r:
                data = r.read()
            ext = os.path.splitext(img["filename"])[1] or ".png"
            dest = os.path.join(out_dir, f"{stem}_v{index:02d}{ext}")
            with open(dest, "wb") as fh:
                fh.write(data)
            saved.append(dest)
    return saved


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", default="images", help="folder of base images")
    p.add_argument("--out", default="default", help="folder for downloaded results")
    p.add_argument("--server", default="http://127.0.0.1:7860")
    p.add_argument("--mode", choices=["txt2img", "img2img"], default="txt2img")
    p.add_argument("--count", type=int, default=2, help="variations per base image")
    p.add_argument("--only", default="", help="only base images whose name contains this")
    p.add_argument("--suffix", default=DEFAULT_SUFFIX, help="appended to every prompt")
    p.add_argument("--negative", default=DEFAULT_NEGATIVE)
    p.add_argument("--denoise", type=float, default=0.6, help="img2img strength")
    p.add_argument("--seed", type=int, default=None, help="fixed first seed")
    p.add_argument("--checkpoint", default="v1-5-pruned-emaonly.ckpt")
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=512)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--cfg", type=float, default=8.0)
    p.add_argument("--workflow", default=os.path.join(here, "workflow.json"))
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--dry-run", action="store_true", help="print prompts and exit")
    a = p.parse_args()

    if not os.path.isdir(a.images):
        sys.exit(f"base image folder not found: {a.images}")
    bases = collect_images(a.images, a.only)
    if not bases:
        sys.exit("no base images matched")

    template = load_template(a.workflow) if a.mode == "txt2img" else None
    if a.dry_run:
        for path in bases:
            full = f"{base_prompt(path)}, {a.suffix}" if a.suffix else base_prompt(path)
            print(f"{os.path.basename(path)}\n    {full}")
        return

    server = a.server.rstrip("/")
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(a.seed)
    total, failed = 0, 0

    for path in bases:
        stem = os.path.splitext(os.path.basename(path))[0]
        positive = base_prompt(path)
        if a.suffix:
            positive = f"{positive}, {a.suffix}"
        uploaded = None
        if a.mode == "img2img":
            try:
                uploaded = upload_image(server, path)
            except (urllib.error.URLError, OSError) as exc:
                print(f"upload failed for {stem}: {exc}", file=sys.stderr)
                failed += 1
                continue
        for i in range(1, a.count + 1):
            seed = rng.randrange(2**32)
            prefix = f"planet-design/base-{stem}"
            graph = None
            if template is not None:
                graph = patched_workflow(template, positive, a.negative, seed, prefix)
            if graph is None:
                graph = builtin_graph(a, positive, a.negative, seed, prefix, uploaded)
            try:
                reply = http_json(f"{server}/prompt",
                                  {"prompt": graph, "client_id": uuid.uuid4().hex})
                entry = wait_for_result(server, reply["prompt_id"], a.timeout)
                saved = download_outputs(server, entry, a.out, stem, i)
            except (urllib.error.URLError, TimeoutError, KeyError, OSError) as exc:
                print(f"failed {stem} variation {i}: {exc}", file=sys.stderr)
                failed += 1
                continue
            total += len(saved)
            for dest in saved:
                print(f"{dest}  seed={seed}")

    print(f"done: {total} images saved to {a.out}, {failed} failures")


if __name__ == "__main__":
    main()
