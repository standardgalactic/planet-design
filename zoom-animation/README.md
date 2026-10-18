# Iterative scenery zoom

Copy zoom.py into ~/planet-design beside template.png and workflow.json. Keep ComfyUI running and make sure a normal generate.py job succeeds first. This tool submits a separate image-to-image graph and does not modify generate.py, workflow.json, the original template or container configuration.

Install Pillow:

```bash
python -m pip install pillow
```

Optional MP4 encoder:

```bash
sudo apt install ffmpeg
```

A short first trial:

```bash
python zoom.py template.png --frames 8 --out zoom-output/first-test
```

A longer run with your own scene description:

```bash
python zoom.py template.png \
  --prompt "wide view of a futuristic domed city, monumental concrete terraces, curved glass roofs, lush enclosed gardens, distant forest, 1970s science fiction film set, matte painting, warm amber light" \
  --frames 40 --zoom 1.03 --denoise 0.25 \
  --out zoom-output/city-zoom
```

The default prompt describes a coastal city. Match it to the actual template, especially whether the scene is interior, forested, coastal or industrial. More scene-specific prompts should retain the atmosphere better than contradictory descriptions. The default negative prompt is text, watermark, logo, blurry, distorted, low quality; override it with --negative.

## Outputs

Each run saves keyframes/00000.png as its prepared starting image, a regenerated PNG per AI step, rendered playback frames in frames/, zoom.gif, and zoom.mp4 when ffmpeg is installed. progress.json records settings, pending server job IDs and completed steps. workflow-last.json records the last submitted API graph. Server-side output copies also remain under the unique prefix planet-design/zoom/<run-id>/ on the ComfyUI server.

The input is center-cropped and resized to a 512-pixel square by default, matching the SD1.5 setup. Original template.png remains unchanged. --size changes the square resolution and must be a multiple of 64; 512 is the recommended trial size.

The script uses the single CheckpointLoaderSimple model from workflow.json, or an explicit --checkpoint name. It uses its own 20-step Euler/normal sampler, CFG 8 and denoise 0.25 rather than importing every setting from the text-to-image workflow. Checkpoint availability is checked before submitting. A missing checkpoint or CUDA/model-loading failure must be fixed in ComfyUI first.

## Animation method

Each step crops the previous regenerated image by a factor of 1.03, resizes it back to the working resolution, uploads it to ComfyUI and passes it through LoadImage, VAEEncode, KSampler, VAEDecode and SaveImage. A fixed seed is reused at all steps by default; --seed changes it. Low denoise encourages continuity but cannot enforce geometric consistency. These are invented details, not recovered information from the source photograph.

Six rendered playback frames connect each pair of AI keyframes. They use a smooth digital crop and a smooth crossfade toward regenerated detail. This is not optical-flow interpolation; ghosting and slow morphing are possible. The last frame of each interval is exactly the next regenerated keyframe. The default 24 AI steps produce 145 playback frames, about twelve seconds at the requested 12 fps, and a nominal 2.03x total zoom. GIF timing is rounded to centiseconds and may play slightly differently from MP4.

Use --focus-x and --focus-y between 0 and 1 to place each crop: 0 is left/top, 1 is right/bottom, 0.5 is centered. The point is a fixed normalized crop position throughout the run, not a tracked object. --inbetweens changes playback frames per AI step and --fps changes playback speed.

GIF uses one shared 256-color palette derived from the first frame, which helps avoid per-frame palette jumps but can distort later colors. MP4 preserves gradients better and is usually smaller. The script keeps frames in memory for GIF encoding and rejects very large frame/resolution combinations. Long runs also consume disk space because PNG frames and server-side keyframes are retained.

## Resuming and changing settings

Rerun the identical command after a normal interruption or polling timeout. Completed AI steps are skipped, and a recorded pending prompt ID is polled again rather than submitted again. Changing generation settings or the template requires a different --out directory. The server URL is part of those settings. Do not run simultaneous copies against the same output directory.

There is a small unavoidable acknowledgement window: if the server accepts a job but the client loses its response before recording its ID, a subsequent run may submit that step again. Inspect ComfyUI's queue after an ambiguous submission error. If recorded history has been cleared or the server restarted before a pending result can be retrieved, the script will keep waiting and eventually time out; it does not silently resubmit or clear pending state. A failed recorded job similarly needs inspection before a fresh run.

To reassemble saved keyframes without generating:

```bash
python zoom.py template.png --frames 8 --out zoom-output/first-test \
  --assemble-only --ping-pong
```

Keep the original generation arguments, including custom prompt/size/zoom/denoise/seed, when resuming or assembling. fps, inbetweens and ping-pong can change without regenerating. Ping-pong reverses the journey so it returns to the beginning; the direction reversal remains visible. Ordinary output loops with a jump from the final zoom to the beginning, not a seamless infinite inward zoom.

To keep experimental outputs out of Git, add /zoom-output/ to .gitignore. This package does not change ignore rules or commit anything.

## Validation

The tool was tested against a local simulated ComfyUI service for multipart upload, graph construction, history polling, image download, GIF creation, pending-job resume, completed-run resume, reverse playback and settings mismatch refusal. A real diffusion run and its visual temporal coherence still need verification on your GPU. ComfyUI's HTTP implementation is documented by its source at https://github.com/comfyanonymous/ComfyUI/blob/master/server.py .
