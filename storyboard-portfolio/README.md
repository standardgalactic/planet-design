# Storyboard portfolio

Put both files in the repository root next to generate.py:

build_storyboard_portfolio.py
storyboard_portfolio.template.html

Build from your local ComfyUI outputs and screenplay plans:

```bash
python build_storyboard_portfolio.py
explorer.exe storyboard-portfolio.html
```

On native desktop Linux use `xdg-open storyboard-portfolio.html` instead. Open the generated HTML directly; no web server or dependencies are required. It does not overwrite your existing index.html.

Default image root is `output/comfy/planet-design/storyboards` and default plan root is `storyboards`. If Docker mounts output elsewhere, point to that host directory:

```bash
python build_storyboard_portfolio.py --images /path/to/output/comfy/planet-design/storyboards --plans storyboards
```

It scans every screenplay folder under the image root, including partially completed films. It matches folder names to plan.json and production.json for titles, screenplay text, scene action, camera, editing duration and prompts. Images without matching plans remain viewable with their folder/file names. Shot numbers are treated as scene numbers, matching season.py's one-shot-per-scene convention. Seeds and individual image metadata are not extracted.

Run the same build command again after more images finish, then reload the browser. The viewer is a snapshot; it does not auto-scan or poll. A file currently being written might be incomplete; rebuild and reload after rendering finishes.

Filter by screenplay or scene, search descriptions, resize thumbnails, and click an image to inspect it. Left/right arrow keys navigate within current filters; Escape closes the viewer. The original link opens the full image. Favourites stay in browser storage where available, and Export favourites saves JSON with file paths and prompt information. Browser storage policies can prevent persistence for local files, so export selections you want to keep. Keep the generated HTML at its original location relative to the image folders; images are linked, not embedded or copied. Existing website/gallery deployment is not changed.
