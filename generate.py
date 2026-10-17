#!/usr/bin/env python3
import argparse
import json
import secrets
import sys
import time
from pathlib import Path
from urllib import request, error

parser = argparse.ArgumentParser(description="Generate images through local ComfyUI.")
parser.add_argument("prompt", nargs="?", help="Defaults to the workflow's prompt")
parser.add_argument("--workflow", default="workflow.json")
parser.add_argument("--url", default="http://127.0.0.1:7860")
parser.add_argument("--negative")
parser.add_argument("--seed", type=int)
parser.add_argument("--batch", type=int)
parser.add_argument("--prefix")
parser.add_argument("--timeout", type=float, default=1800)
args = parser.parse_args()

# Widget order for the specific node types in your supplied workflow.
widget_names = {
    "CheckpointLoaderSimple": ["ckpt_name"],
    "EmptyLatentImage": ["width", "height", "batch_size"],
    "CLIPTextEncode": ["text"],
    "KSampler": [
        "seed", "_seed_control", "steps", "cfg",
        "sampler_name", "scheduler", "denoise",
    ],
    "SaveImage": ["filename_prefix"],
    "VAEDecode": [],
}

def api(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(
        args.url.rstrip("/") + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc

def main():
    workflow = json.loads(Path(args.workflow).read_text(encoding="utf-8"))
    links = {link[0]: link for link in workflow["links"]}
    graph = {}

    for node in workflow["nodes"]:
        kind = node["type"]
        if kind not in widget_names:
            raise ValueError(f"Unsupported node type: {kind}")
        inputs = {}
        for name, value in zip(widget_names[kind], node.get("widgets_values", [])):
            if not name.startswith("_"):
                inputs[name] = value
        for socket in node.get("inputs", []):
            if socket.get("link") is not None:
                link = links[socket["link"]]
                inputs[socket["name"]] = [str(link[1]), link[2]]
        graph[str(node["id"])] = {"class_type": kind, "inputs": inputs}

    # These node IDs match your supplied workflow.
    if args.prompt is not None:
        graph["6"]["inputs"]["text"] = args.prompt
    if args.negative is not None:
        graph["7"]["inputs"]["text"] = args.negative
    if args.batch is not None:
        if args.batch < 1:
            raise ValueError("--batch must be at least 1")
        graph["5"]["inputs"]["batch_size"] = args.batch
    if args.prefix is not None:
        graph["9"]["inputs"]["filename_prefix"] = args.prefix

    seed = args.seed if args.seed is not None else secrets.randbits(48)
    graph["3"]["inputs"]["seed"] = seed

    submitted = api("/prompt", {"prompt": graph})
    if submitted.get("node_errors"):
        raise RuntimeError(json.dumps(submitted["node_errors"], indent=2))
    prompt_id = submitted["prompt_id"]
    print(f"Queued {prompt_id}; seed={seed}", flush=True)

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        history = api(f"/history/{prompt_id}")
        if prompt_id in history:
            result = history[prompt_id]
            status = result.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, indent=2))
            images = [
                image
                for output in result.get("outputs", {}).values()
                for image in output.get("images", [])
                if image.get("type") == "output"
            ]
            if images:
                for image in images:
                    relative = Path(image.get("subfolder", "")) / image["filename"]
                    print(f"Saved on server: {relative}")
                return
            if status.get("completed"):
                raise RuntimeError("Generation completed without saved images")
        time.sleep(1)
    raise TimeoutError(
        f"Stopped waiting after {args.timeout:g}s; job {prompt_id} may still be running"
    )

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, TimeoutError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
