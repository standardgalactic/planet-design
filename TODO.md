# TODO

Carried over from issue #1 of the previous repository ("Image Feedback UI & Functionality Roadmap", opened 25 May 2025), then extended with the open work on the catalogue and the image pipeline.

## Image feedback (from issue #1)

The old viewer was a Picbreeder-style rater for a 4,999-image set, with ratings and comments stored in Supabase. The new site is static and has no backend, so most feedback items are not planned. Status against the new `index.html`:

| Item | Status |
|---|---|
| Store filenames exactly as written (`ComfyUI_00003_.png`, not corrupted names) | Done by design. The site reads exact paths from `index.jsonl` and no longer stores names by hand. |
| Log click coordinates on images | Not planned. Needs a backend. |
| Show a marker where an image was clicked | Not planned. Only useful with click logging. |
| Tooltip with existing comments and ratings on hover | Not planned. Needs stored feedback. |
| Heatmap of popular click areas | Not planned. |
| Indicator for images that have comments | Not planned. |
| Paginate in batches of 100 | Done differently. Experiments are browsed by run, the archive by contact sheet (400 images each), and described images by page (10 each). |
| Sort by rating, votes, comments or delete flags | Not planned. Needs stored feedback. |
| Session or user tracking, moderation, admin dashboard | Not planned. |

If feedback comes back, the simplest static route is to let visitors open a pre-filled GitHub issue from the image viewer, with the image path in the title. That needs no database.

## Image pipeline

- [ ] Fix `01.01-register-overlay.svg`: widen the registration slip as the visual bible describes (0.3, 0.6, 1.0 mm and up), draw each register's rear strip as specified, and add a separated version with seven sheets side by side for Scene 14.
- [ ] Draw the brass plate "3R" as a vector asset for 01.01.
- [ ] Add exact lettering (dialogue, ledger hands, stamped notices) as a compositing step after generation.
- [ ] Write a script that places generated images inside `03.01-reconstruction-marker.svg`.
- [ ] Build a casting and location sheet from the best v3 and v4 picks, one page per project.
- [ ] Decide how Ilse's age and tape measure are shown. The generator has not produced either reliably.
- [ ] Turn the two catalogue audits into a script in `tools/`.
- [ ] Add the 1,000-image sets and other old archives to the contact sheets if they are missing.

## Catalogue

- [ ] 04.01 The Society for Perfect Endings: treatment, scene outline, screenplay, visual bible.
- [ ] 07.01 Whale Beneath the Railway: same four steps.
- [ ] 08.01 Seven Minutes of Summer: same four steps.
- [ ] 11.01 A Country Made of Footnotes: same four steps.
- [ ] Sample images for each new project, using a new manifest category.
- [ ] Hand-code the 162 graphic treatments that name no medium.
- [ ] Differentiate the eight clusters of near-duplicate treatments before developing those projects.

## Site and repository

- [ ] Rebuild `thumbs/comfy` at 512 px (`--size 512 --quality 80`) so the image viewer is sharp.
- [ ] Commit the contact sheets for `output/old`, and attach the full archive to a release.
- [ ] Move files into `catalogue/`, `projects/`, `manifests/` and `tools/`, and update the paths in the README.
- [ ] Decide whether to keep `image-rater.html` or remove it.
