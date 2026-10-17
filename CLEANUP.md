# Cleanup steps for steel-sky

Run from the repo root. Review each step before you commit.

## 1. Move files into folders

```
mkdir -p catalogue projects/03.01/assets projects/01.01/assets manifests tools
git mv 03.01-*.md projects/03.01/
git mv 03.01-reconstruction-marker.svg projects/03.01/assets/
git mv 01.01-*.md projects/01.01/
git mv 01.01-register-overlay.svg projects/01.01/assets/
git mv framework-family-* graphic-treatment-* catalogue/
git mv slate-samples*.json collection.json manifests/
git mv make-json.py check-image.py test-check-image.py test-grok.sh test-samples.sh tools/
```

Move `catalogue.md` into `catalogue/` too (it was never in the tree you sent, so it may be outside the repo).
Delete `README.txt` after its content is merged into `README.md`.
The `*.progress.json` files are run state. Add them to `.gitignore` instead of committing them.

## 2. Stop tracking raw output

Your current rules only cover PNGs directly inside the two folders:

```
/output/comfy/*.png
/output/comfy/cache/
/output/old/*.png
/output/old/*.png        (duplicate line)
```

They do not match the run subfolders (`output/comfy/slate-samples-v4/03-01/...`), so `git add -A` would commit those images. Replace the output rules with:

```
# raw generator output stays local; thumbs/ and samples/ are committed
/output/
*.progress.json
```

Keep your other lines (`/.devcontainer`, `/docker-compose.override.yml`, `*.code-workspace`, `/.vscode`).

Anything already committed under `output/` stays tracked even after the ignore rule. Check with `git ls-files output | head` and, if there are files, run:

```
git rm -r --cached output
```

If the PNGs are already in history, the clone size will not shrink until history is rewritten (for example `git filter-repo --path output --invert-paths`). That rewrites history, so only do it if clone size matters.

## 3. Build previews

```
pip install pillow
python tools/make_thumbs.py output/comfy output/old --dst thumbs
```

Expect about 40 MB of WebP for 12,000 images. Check with `du -sh thumbs` before committing.

## 4. Pick samples

Copy the chosen full-size images into `samples/` (a few dozen at most) and convert them to WebP at quality 85 with
`python -c "from PIL import Image;import sys;[Image.open(p).convert('RGB').save(p.rsplit('.',1)[0]+'.webp','WEBP',quality=85) for p in sys.argv[1:]]" samples/*.png`
then delete the PNG copies.

## 5. Commit

```
git add -A
git commit -m "Reorganise repository, add catalogue and pilot documentation, add thumbnail tooling"
```

If GitHub Pages serves `index.html`, check that it does not reference paths you moved.
