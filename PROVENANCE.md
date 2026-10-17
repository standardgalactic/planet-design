# Provenance

This repository continues from the real history of https://github.com/AbdBarho/stable-diffusion-webui-docker.

- The first 237 commits are upstream's own, unchanged, with their original authors and dates.
- Every later commit was made by the repository owner with `tools/monotonic_commit.py`. Upstream authors are named in commit trailers and are never impersonated.
- The later commits are a reconstruction. Each file was built up in small steps from its finished form. The steps show how the file can be assembled, not how it was first written.
- Timestamps on those commits are the times the script ran, not the times the work was done.

| Class | Files | Meaning |
|---|---|---|
| upstream | 24 | Identical to the upstream file, or identical apart from CRLF versus LF (the repository then keeps upstream's LF bytes). Not re-committed. Authorship is in the upstream commits. |
| upstream-modified | 3 | Started from an upstream file and differs from it. Trailers name the upstream authors whose lines are still present, counted by matching the final file against the upstream version. That is a count of surviving lines. It says nothing about who wrote the changes. Binary files are not line-matched, and their trailers name the authors of the upstream version. |
| steel-sky | 12356 | Not in upstream. |
| upstream-removed | 1 | In upstream, absent from this project. Deleted in a commit that names the upstream authors, unless the history was built with `--removed keep`. |
| upstream-ignored | 1 | In upstream, present in the author's folder but excluded by its `.gitignore`. Left exactly as upstream has it, and checked to be unchanged. |

Counts do not include `PROVENANCE.md` and `provenance.csv` themselves.
The per-file table is in `provenance.csv`.
