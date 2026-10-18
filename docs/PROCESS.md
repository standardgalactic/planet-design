# Process record

## Scope

This session took place on 17 October 2026. The task was exploratory scenery and set design for a futuristic planet with the atmosphere of seventies speculative cinema, beginning with references to Logan's Run and Planet of the Apes. The work sought a visually coherent world without determining its story, politics or geography in advance. Prompts were proposed in conversation, run locally, and the user reported that the resulting batches looked good. The complete image collection was not available for independent visual review while this documentation was prepared.

## Project separation

The source repository was /home/flyxion/steel-sky on archdaemon, with origin pointing to standardgalactic/steel-sky.git and 22,180 commits reported at that time. A new /home/flyxion/planet-design directory was copied with rsync, excluding .git/, samples/, thumbs/, output/, data/, .cleanup-backups/, __pycache__/ and *.progress.json. A fresh repository was then initialized separately. No new GitHub repository URL has been established in this record.

The purpose was to work with fewer than 20,000 files. The supplied new tree has 200 files and 46 directories, including 137 planet images. Repository file count and Git commit count are different quantities.

## Bringing the service back

The old sd-comfy:7 container, webui-docker-comfy-1, was stopped. It was restarted directly with docker start, preserving its original mounts. The first client attempt received a connection reset while initialization was underway. Subsequent logs showed an RTX 3060, 12 GB VRAM, PyTorch 2.3.0, CUDA device initialization, and then a running prompt. GPU usage was initially low while RAM usage increased; the logs later reported BaseModel and SD1ClipModel loading. The job eventually completed. No specific disk or model-loading fault was conclusively diagnosed.

The container's data and output mounts point to the old Windows OneDrive project rather than the new Linux project. HTTP clients submit work to that server; their working directory does not control the server's save destination. The first successful output was reported as planet-design/city-test_00001_.png and was located under the original output tree. Samples were later copied into the new repository.

## Prompt progression

The first job requested a wide establishing shot of a domed city with concrete terraces, curved glass, gardens and forest, using a seventies film-set and matte-painting treatment. One image established the direction. Four calls with batch size four then tested variation around exactly that prompt, producing sixteen further city images.

The next six jobs tested whether this direction could extend to distinct settings: a residential atrium, transit station, botanical garden, industrial complex, forest ruins and reservoir. Each specific subject preceded a shared material and medium description. All six used batch size four, producing 24 images.

The final 24 jobs expanded the geography and social infrastructure, again generating four images per setting. This pass introduced tidal settlements, a crater capital, public baths, government and archival interiors, transport megastructures, agriculture, alien migration, adaptive reuse, an eclipse court and oceanic arrival. It used a longer shared production-design prompt and a revised negative prompt that blocked picture frames and gallery walls.

The complete session therefore comprises 35 jobs and 137 images. The exact strings are preserved in PROMPTS.md and manifests/planet-design.json. The manifest's local file lists follow the supplied tree; the server prefixes include planet-design/ while the copied repository paths do not.

## Settings and evidence

The submitted graph used v1-5-pruned-emaonly.ckpt, EmptyLatentImage at 512 × 512, KSampler with 20 steps, CFG 8, Euler sampler, normal scheduler and denoise 1, CLIP text encoding, VAE decoding and SaveImage. City and initial location studies inherited the workflow negative prompt: text, watermark, ugly, amateur, distorted, garish, gawdy, abstract. World expansion supplied its own negative prompt explicitly.

No seed ledger was captured for the complete session. Known seeds should be extracted from individual PNG prompt graphs rather than inferred or fabricated. Every image in a batch can carry the same graph seed, which is not evidence of a separately recorded seed for each batch position. The local indexer reads ordinary PNG tEXt prompt chunks from ComfyUI SaveImage outputs. If metadata is absent, compressed, unsupported or does not match this simple graph, it keeps the documented prompt and marks its source accordingly. It never rewrites the PNGs.

A shared prompt encourages common materials, lighting and medium; it does not impose a consistent planetary map, engineering design, character identity or object geometry. Current outputs are location concepts, not construction drawings. The user selected this stage as sufficient for now; no further generation is required to install this documentation and viewer.

## Gallery maintenance

index.html embeds its own gallery data, uses only relative image URLs, and runs without external libraries. tools/build_planet_gallery.py refreshes that data by scanning real city PNGs, locations/ and world-expansion/. It reads known PNG metadata when present. It deliberately excludes inherited Ankara previews and historical sample runs. Generated thumbnails are unnecessary for the current 512-pixel collection, reducing file duplication.

When adding new image directories, extend the scanner and job manifest. Existing directory labels are retained. The page uses a filterable grid and an accessible native dialog with original-file links, prompt copying and arrow navigation. Static gallery data does not prove files exist until rebuilt locally or loaded by a browser. Rebuild after copying new images, then test over python -m http.server 8000 before publishing.
