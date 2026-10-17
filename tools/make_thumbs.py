#!/usr/bin/env python3
"""Build small WebP thumbnails, a prompt index and contact sheets from ComfyUI output.

Standard library plus Pillow. Run from the repo root:

    python tools/make_thumbs.py output/comfy output/old --dst thumbs

For every PNG under each source folder it writes:
  thumbs/<source-name>/<relative path>.webp      small preview (default 192 px, quality 60)
  thumbs/<source-name>/index.jsonl               one line per image: path, size, seed, prompt, negative
  thumbs/<source-name>/sheets/sheet-NN.webp      contact sheets, 400 images each (20 x 20)

Existing thumbnails are skipped, so the script can be re-run after new generations.
The index keeps the prompt that ComfyUI embeds in each PNG, so the thumbnail
copy of the project does not lose how an image was made.
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image


def read_prompt(img):
    """Return (positive, negative, seed) from the ComfyUI 'prompt' chunk, or blanks."""
    raw = img.info.get("prompt")
    if not raw:
        return "", "", None
    try:
        graph = json.loads(raw)
    except Exception:
        return "", "", None
    pos = neg = ""
    seed = None
    for node in graph.values():
        if node.get("class_type") in ("KSampler", "KSamplerAdvanced"):
            inp = node.get("inputs", {})
            seed = inp.get("seed", inp.get("noise_seed"))

            def text_of(link):
                try:
                    return graph[str(link[0])]["inputs"].get("text", "")
                except Exception:
                    return ""

            pos = text_of(inp.get("positive", [None]))
            neg = text_of(inp.get("negative", [None]))
            break
    return pos, neg, seed


def one(job):
    src, dst, root, size, quality = job
    rel = src.relative_to(root)
    out = dst / (str(rel) + ".webp")
    try:
        with Image.open(src) as img:
            pos, neg, seed = read_prompt(img)
            w, h = img.size
            if not out.exists():
                out.parent.mkdir(parents=True, exist_ok=True)
                t = img.convert("RGB")
                t.thumbnail((size, size), Image.LANCZOS)
                t.save(out, "WEBP", quality=quality, method=6)
        return {"path": rel.as_posix(), "w": w, "h": h, "seed": seed,
                "prompt": pos, "negative": neg}
    except Exception as e:  # keep going on a bad file
        return {"path": rel.as_posix(), "error": str(e)}


def make_sheets(rows, thumb_root, sheet_dir, cell=96, cols=20, per_sheet=400, quality=70):
    sheet_dir.mkdir(parents=True, exist_ok=True)
    ok = [r for r in rows if "error" not in r]
    for n in range(0, len(ok), per_sheet):
        chunk = ok[n:n + per_sheet]
        rows_n = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rows_n * cell), (20, 20, 20))
        for i, r in enumerate(chunk):
            p = thumb_root / (r["path"] + ".webp")
            try:
                with Image.open(p) as t:
                    t = t.convert("RGB")
                    t.thumbnail((cell, cell), Image.LANCZOS)
                    sheet.paste(t, ((i % cols) * cell, (i // cols) * cell))
            except Exception:
                pass
        sheet.save(sheet_dir / f"sheet-{n // per_sheet + 1:02d}.webp", "WEBP", quality=quality)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+", help="folders of PNGs, e.g. output/comfy output/old")
    ap.add_argument("--dst", default="thumbs")
    ap.add_argument("--size", type=int, default=192)
    ap.add_argument("--quality", type=int, default=60)
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()

    for s in a.sources:
        root = Path(s)
        if not root.is_dir():
            print("skip, not a folder:", s, file=sys.stderr)
            continue
        dst = Path(a.dst) / root.name
        files = sorted(root.rglob("*.png"))
        print(f"{root}: {len(files)} PNGs")
        jobs = [(f, dst, root, a.size, a.quality) for f in files]
        with Pool(a.workers) as pool:
            rows = pool.map(one, jobs, chunksize=32)
        dst.mkdir(parents=True, exist_ok=True)
        with open(dst / "index.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        if not a.no_sheets:
            make_sheets(rows, dst, dst / "sheets")
        size = sum(p.stat().st_size for p in dst.rglob("*.webp"))
        print(f"  wrote {dst}  ({size / 1e6:.1f} MB of WebP)")


if __name__ == "__main__":
    main()
