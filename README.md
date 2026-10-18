# Planet Design

Scenery and set-design studies for an original futuristic planet, developed through a local Stable Diffusion image pipeline. The initial direction draws on the atmosphere of *Logan’s Run* and *Planet of the Apes*: monumental spaces, enclosed technological societies, and older worlds persisting beyond their boundaries. These are cinematic references for exploration rather than a claim that the images reproduce either film's designs.

The emerging vocabulary combines concrete terraces, curved glass, gardens, amber illumination, practical miniature scenery and matte-painted horizons. The collection moves from a domed city to its inhabited interiors, infrastructure, reclaimed ruins and more speculative landscapes. There is no settled screenplay or authoritative planetary geography yet.

## Browse the collection

Open [index.html](index.html) directly, or serve the repository:

```bash
python -m http.server 8000
```

Visit http://localhost:8000. The gallery has collection filters, prompt search, larger tiles and a detail viewer. Click an image to inspect its prompt and generation settings. Left and right arrows navigate the filtered collection; Escape closes the viewer. Original files and downloads are linked in the viewer. The gallery uses system fonts and has no CDN, framework, analytics or remote font dependencies.

The supplied index contains the 137 image paths reported in the current project tree. To discover actual files, include later runs and recover PNG metadata, rebuild it:

```bash
python tools/build_planet_gallery.py
```

This updates the JSON embedded in index.html, so the gallery also works without a web server. It reads the PNGs already present; it does not generate thumbnails or duplicate images. Missing images are reported in the gallery. The indexer recognizes the present city filenames and the locations/ and world-expansion/ directories, leaving the inherited Ankara images out of this collection.

## Current collection

| Collection | Jobs | Images | Local paths |
|---|---:|---:|---|
| City test and studies | 5 | 17 | city-test_*.png and city-batch-*.png |
| Locations | 6 | 24 | locations/<location>/study_*.png |
| World expansion | 24 | 96 | world-expansion/<location>/study_*.png |
| Total | 35 | 137 | 31 distinct settings, including the city |

The four city batches repeat one visual direction. Other settings include residential atria, botanical gardens, transit stations, tidal cities, public baths, archives, a submerged observatory, a fungus vault and settlements inside obsolete infrastructure. Image counts describe the tree supplied on 17 October 2026; the indexer reports the actual count after subsequent changes.

## Process and prompts

[Process notes](docs/PROCESS.md) record the workflow, output mounts, storage distinction and practical observations. [The prompt record](docs/PROMPTS.md) contains the complete positive and negative prompts for every job. [The job manifest](manifests/planet-design.json) stores those prompts, batch sizes, server prefixes and initial local filenames in machine-readable form.

The current setup is Stable Diffusion 1.5, checkpoint v1-5-pruned-emaonly.ckpt, at 512 × 512, with 20 steps, CFG 8, Euler sampling, normal scheduling and denoise 1. No reference images or LoRAs were configured. The active machine reported an NVIDIA RTX 3060 with 12 GB VRAM. Generation is headless through generate.py and ComfyUI's HTTP endpoint at http://127.0.0.1:7860.

The recorded batches used random seeds. A seed must be recovered from the PNG's prompt graph to associate it with an existing output. A KSampler seed is a batch seed; the gallery does not invent an independent seed for each image in that batch. Matching prompts and seeds alone do not guarantee identical output across changed workflows or software environments.

## Run another study

The existing service can be started without rebuilding or changing its mounts:

```bash
docker start webui-docker-comfy-1
docker logs --since 2m -f webui-docker-comfy-1
```

Wait for the server-ready message. Press Ctrl+C to leave the log viewer; this does not stop the container. Test the service:

```bash
curl -fsS http://127.0.0.1:7860/system_stats
```

Preview a recorded category and then generate it:

```bash
python tools/run_planet.py --category "Locations" --dry-run
python tools/run_planet.py --category "Locations"
```

Select one job with --job locations/forest-ruins, or supply --seed 12345 to choose a new deterministic base seed. Without --seed, generate.py selects a fresh random seed per job. The runner is sequential and stops after a failure. It has no resume manifest and rerunning it submits those jobs again. This job manifest belongs to tools/run_planet.py; it is not interchangeable with generate_collection.py's older manifest schema. The latter remains available for separately authored collections.

The replay tool uses workflow.json for actual model and sampling settings. Settings stored in the job manifest document the session and do not override that workflow. Check it before comparing results.

## Where the generated files go

The active container still mounts the original Windows data and output directories. Running a client from ~/planet-design does not change the server's output location:

```text
/mnt/c/Users/nateg/OneDrive/Documentos/GitHub/stable-diffusion/data   -> /data
/mnt/c/Users/nateg/OneDrive/Documentos/GitHub/stable-diffusion/output -> /output
```

New files from the documented commands normally appear under the original output/comfy/planet-design/. Inspect the actual mount if this changes:

```bash
docker inspect webui-docker-comfy-1 \
  --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
```

Copy those outputs into this repository before rebuilding the gallery:

```bash
rsync -av \
  /mnt/c/Users/nateg/OneDrive/Documentos/GitHub/stable-diffusion/output/comfy/planet-design/ \
  ~/planet-design/
python tools/build_planet_gallery.py
```

The project was copied without data/, so launching Compose here without configuring models will not automatically reuse the old model directory. Both projects also inherit the same Compose project name; use the existing container until intentionally configuring a separate service. The observed cold start took many minutes; later jobs reused loaded models. Windows/OneDrive-backed model storage is a possible source of slow disk access, not a proven explanation of the delay.

## Repository scope and inheritance

Planet Design began as a small working copy of Steel Sky. Its .git history, large samples, thumbnails, raw output, local models and cleanup backups were excluded when the copy was made. The local project is ~/planet-design, with archdaemon chosen as the initial branch name. This gallery and README describe the new planet project rather than the earlier 440-screenplay programme.

The catalogue/, projects/, older manifests, Ankara previews, image-rater.html and other historical utilities remain inherited reference material. In particular, PROVENANCE.md and provenance.csv describe the earlier Steel Sky reconstruction; they do not certify this new repository's commit history or the new planet images. They have been retained rather than silently rewritten. See [inheritance notes](docs/INHERITANCE.md).

Docker services and infrastructure originated in [AbdBarho/stable-diffusion-webui-docker](https://github.com/AbdBarho/stable-diffusion-webui-docker), with the image graph executed by [ComfyUI](https://github.com/comfyanonymous/ComfyUI). Retain LICENSE and CONTRIBUTORS.md. This update does not establish a new license or remove inherited restrictions; consult the existing LICENSE and applicable model terms before redistribution.
