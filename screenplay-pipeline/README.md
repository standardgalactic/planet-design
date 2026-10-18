# Planet screenplay season

Copy `season.py` and `storyboard.py` into the repository root alongside your existing `generate.py` and `workflow.json`. This replaces the earlier storyboard.py; keep a backup if desired. Python standard library only. Ollama and ComfyUI must already be running.

## Default collection

Twelve distinct premises, eight scenes per screenplay, three image variants per scene: **288 images**. Each scene has one representative still composition; the three images are variations of that prompt, not three consecutive action beats. Screenplay continuity and scene alignment are model instructions, not guaranteed by validation. Review the drafts before rendering. No video is assembled.

Write everything first:

```bash
python season.py --model granite4.1:3b --write-only
```

Review `storyboards/planet-season-01/README.md` and each screenplay/prompts file, then render:

```bash
python season.py --model granite4.1:3b --render-only
```

Or write and render in one run:

```bash
python season.py --model granite4.1:3b
```

A smaller trial:

```bash
python season.py --count 2 --scenes 6 --images-per-scene 2 --out storyboards/trial --write-only
python season.py --count 2 --scenes 6 --images-per-scene 2 --out storyboards/trial --render-only
```

Repeat the same options when resuming; saved season settings are checked to avoid silently changing a production. Choose a new output folder for a different collection. Saved valid plans and completed render jobs are skipped. On an interrupted or failed image job, inspect its log and ComfyUI queue before explicitly adding `--retry-incomplete` (it can duplicate a server job that finished after the client stopped). Stop at the first failure; rerun to continue. Avoid simultaneous runs targeting the same folder.

Writing runs sequentially, then rendering runs sequentially. The writer uses keep_alive=0; ComfyUI is asked to release models before writing. `--cpu-writer` runs Granite on CPU instead. If three images exhaust GPU memory, start a new output collection with `--images-per-scene 1`.

## Output locations

Text, plans, raw writer requests/responses, logs, timing adjustments and render progress stay beneath `storyboards/planet-season-01/`.

PNG files stay on the ComfyUI server, normally:

```text
output/comfy/planet-design/storyboards/planet-season-01-01-tidal-signal/shot-01_00001_.png
```

Other films use numbered folder names, and shot-01 through shot-08 correspond to the scene prompts. ComfyUI chooses the final numeric filename suffix. Existing gallery tooling is not changed automatically.

The updated storyboard.py proportionally normalizes positive integer shot durations to the requested total instead of rejecting an otherwise valid draft for bad arithmetic. Raw writer-response.txt is unchanged; plan.json records any timing adjustment. Those durations are editorial suggestions, not animated output. Other structural errors still stop the run, preserving the raw response for inspection.
