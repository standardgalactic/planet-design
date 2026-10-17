#!/usr/bin/env python3
"""Rebuild a repository's history as many small, cumulative commits.

The history has two parts.

1. Upstream base. The upstream project is cloned and its real commits are kept
   exactly as they are (authors, dates, messages). Upstream files that you did
   not touch are never re-committed, so their credit stays with the real authors.
2. Reconstruction. Every other file in your finished working tree is added on top
   with `git fast-import`. Text files grow line by line (or N lines at a time),
   binary files and very large files go in whole. Commit times are the real
   times at which the script runs. Nothing is back-dated. The intermediate states
   are reconstructions of the finished files, and PROVENANCE.md says so.

Every file is classified before anything is written:

    upstream            identical to the upstream file (ignoring line endings): no commit
    upstream-modified   started from an upstream file and differs from it
    steel-sky           not in upstream
    upstream-removed    in upstream, absent from your folder (deleted, or kept with --removed keep)

Commits that touch an upstream-modified file carry trailers. The authors named are
those whose upstream lines are still present in the final file, found by matching
the final file against `git blame` of the upstream version. It is a count of
surviving lines, not a statement about who wrote the changes:

    Upstream-Origin: https://github.com/AbdBarho/stable-diffusion-webui-docker
    Upstream-Path: docker-compose.yml
    Upstream-Authors: AbdBarho (40 lines retained), PassiveLemon (14 lines retained)
    Upstream-Lines-Retained: 55 of 63
    Provenance: upstream-modified

Emails are never written. Authors are named, not impersonated: the commit author
is you.

Bytes are preserved, with two exceptions that are reported. Files are read and
written as raw bytes (no decoding, no line-ending changes) unless you pass `--eol lf`.

  1. A file whose only difference from upstream is CRLF versus LF counts as identical
     to upstream, so the repository keeps upstream's LF bytes and your CRLF copy is
     not re-committed. The dry run lists these files.
  2. Symbolic links are not imported. They are listed as skipped.

Binary files get no line matching. Their trailers name the authors of the upstream
version ("not line-matched"), which is not a statement about what survives.

File modes: a path that exists upstream keeps its upstream mode. A new file is
100755 only when it starts with a `#!` line, otherwise 100644. The source folder's
own permission bits are not used, so the result is the same on Windows and Linux.

Verification: after the import the script reads every file back out of the new
repository's object database (not the working tree, so autocrlf cannot disturb the
check) and compares its SHA-256 and its mode with the plan. It also checks that the
set of tracked files is exactly the planned set. It refuses to push on any mismatch.

Branch: the whole history, upstream commits included, lives on one branch,
`archdaemon` by default (`--branch NAME` to change it). After the first push, set
that branch as the default branch in the GitHub repository settings.

Typical use, from the finished project folder (needs a .gitignore beside it):

    python tools/monotonic_commit.py --source . --dest ../steel-sky-new --dry-run
    python tools/monotonic_commit.py --source . --dest ../steel-sky-new
    python tools/monotonic_commit.py --source . --dest ../steel-sky-new \\
        --remote https://github.com/standardgalactic/steel-sky --push

Requires git and Python 3.8 or newer. Standard library only.
"""
import argparse
import collections
import csv
import difflib
import fnmatch
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

UPSTREAM_URL = "https://github.com/AbdBarho/stable-diffusion-webui-docker"
ALIASES = {"abdullah barhoum": "AbdBarho", "abdullah": "AbdBarho", "abdbarho": "AbdBarho"}
WHOLE_EXT = (".webp", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".mp3", ".mp4", ".zip", ".woff", ".woff2")

# Phase order matters. First matching rule wins.
RULES = [
    ("pipeline", ["generate.py", "workflow.json", "generate_collection.py", "tools/*", "check-image.py",
                  "make-json.py", "test-*", "docker-compose.yml"]),
    ("catalogue", ["catalogue/*", "catalogue.md", "framework-family-*", "graphic-treatment-*"]),
    ("manifests", ["manifests/*", "slate-samples*.json", "collection.json"]),
    ("samples", ["samples/*", "thumbs/*", "assets/*", "*.webp"]),
    ("site", ["index.html", "image-rater.html", "image_descriptions.json"]),
    ("docs", ["README*", "CONTRIBUTORS.md", "TODO.md", "CLEANUP.md", "LICENSE", ".gitignore"]),
]
PROJECT_RE = re.compile(r"^(?:projects/)?(\d\d\.\d\d)[-/]")


def run(args, cwd=None, inp=None, check=True):
    r = subprocess.run(args, cwd=cwd, input=inp, capture_output=True)
    if check and r.returncode:
        sys.exit("git error: %s\n%s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
    return r.stdout


def git(dest, *a, **k):
    return run(["git"] + list(a), cwd=dest, **k)


def norm_author(name):
    name = name.strip()
    return ALIASES.get(name.lower(), name)


def is_binary(b):
    return b"\0" in b[:8192]


def to_lf(b):
    return b if is_binary(b) else b.replace(b"\r\n", b"\n")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def hash_object(dest, data):
    return git(dest, "hash-object", "--stdin", inp=data).decode().strip()


def fi_path(p):
    """Path bytes as fast-import wants them (C-quoted only when it has to be)."""
    b = os.fsencode(p)
    if b.startswith(b'"') or b"\n" in b:
        b = b'"' + b.replace(b"\\", b"\\\\").replace(b'"', b'\\"').replace(b"\n", b"\\n") + b'"'
    return b


def list_source_files(source):
    """Files git would track, honouring the source .gitignore, without touching the source."""
    tmp = tempfile.mkdtemp()
    try:
        run(["git", "init", "--bare", "-q", tmp])
        out = run(["git", "-c", "core.excludesFile=", "--git-dir=" + tmp, "--work-tree=" + source,
                   "ls-files", "-co", "--exclude-standard", "-z"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    files, skipped = [], []
    for raw in out.split(b"\0"):
        if not raw:
            continue
        p = os.fsdecode(raw)
        full = os.path.join(source, p)
        if p.startswith(".git/"):
            continue
        if os.path.islink(full):
            skipped.append((p, "symlink"))
        elif os.path.isfile(full):
            files.append(p)
    return sorted(files), skipped


def phase_of(path, cls):
    if cls in ("upstream-modified", "upstream-removed"):
        return "upstream-changes"
    m = PROJECT_RE.match(path)
    if m:
        return "project-" + m.group(1)
    for name, pats in RULES:
        for p in pats:
            if fnmatch.fnmatch(path, p):
                return name
    return "misc"


def split_lines(data):
    out = data.split(b"\n")
    if out and out[-1] == b"":
        out.pop()
    return out


def blame_lines(dest, path):
    out = git(dest, "blame", "--line-porcelain", "-w", "HEAD", "--", path)
    return [norm_author(l[7:].decode("utf-8", "replace")) for l in out.split(b"\n") if l.startswith(b"author ")]


def retained_authors(dest, path, new_data):
    """Authors of upstream lines still present in new_data. Returns (Counter, retained, total)."""
    up = git(dest, "cat-file", "blob", "HEAD:" + path)
    names = blame_lines(dest, path)
    if is_binary(up) or is_binary(new_data):
        c = collections.Counter(names)  # upstream version only: no line matching was done
        return c, None, sum(c.values())
    up_l, new_l = split_lines(up), split_lines(new_data)
    c = collections.Counter()
    sm = difflib.SequenceMatcher(None, up_l, new_l, autojunk=False)
    for i, _j, n in sm.get_matching_blocks():
        for k in range(n):
            if i + k < len(names):
                c[names[i + k]] += 1
    return c, sum(c.values()), len(up_l)


def describe(line, n, ext):
    s = line.decode("utf-8", "replace").strip()
    short = (s[:60] + "...") if len(s) > 60 else s
    if ext == ".md":
        if s.startswith("#"):
            return "Add heading: " + s.lstrip("# ").strip()[:60]
        if s.startswith("|"):
            cell = s.strip("| ").split("|")[0].strip()
            return "Add table row: " + (cell[:50] or "row")
        if s[:2] in ("- ", "* ") or re.match(r"^\d+\. ", s):
            return "Add list item: " + re.sub(r"^([-*]|\d+\.)\s+", "", s)[:50]
        if s.startswith("```"):
            return "Add code block"
        return "Add text: " + short
    if ext == ".py":
        m = re.match(r"\s*(def|class)\s+(\w+)", s)
        if m:
            return "Add %s %s" % (m.group(1), m.group(2))
        if s.startswith(("import ", "from ")):
            return "Add import: " + short
        if s.startswith("#"):
            return "Add comment: " + short
        return "Add code line %d" % n
    if ext in (".json", ".csv", ".jsonl"):
        return "Add data entry %d" % n
    if ext in (".html", ".svg", ".xml", ".css"):
        return "Add markup line %d" % n
    return "Add line %d" % n


def group_lines(data):
    """Raw-byte lines; blank lines are attached to the next non-blank line."""
    groups, cur = [], []
    for ln in data.splitlines(keepends=True):  # bytes: splits on \n, \r\n, \r only
        cur.append(ln)
        if ln.strip():
            groups.append(cur)
            cur = []
    if cur:
        if groups:
            groups[-1].extend(cur)
        else:
            groups.append(cur)
    return groups


class Plan:
    def __init__(self):
        self.items = []

    def add(self, **k):
        k.setdefault("data", None)
        self.items.append(k)


def load(it, source, args):
    """The bytes this file should have in the new repository."""
    if it.get("data") is not None:
        return it["data"]
    raw = open(os.path.join(source, it["path"]), "rb").read()
    return to_lf(raw) if args.eol == "lf" else raw


def per_commit(groups, args):
    return max(args.lines, -(-groups // args.max_commits_per_file))


def commit_count(it, args):
    if it["cls"] == "upstream-removed" or it["whole"] or it["groups"] == 0:
        return 1
    return -(-it["groups"] // per_commit(it["groups"], args))


def build_plan(source, dest, args):
    files, skipped = list_source_files(source)
    base = {}
    for e in git(dest, "ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if e:
            meta, p = e.split(b"\t", 1)
            mode, _t, blob = meta.decode().split()
            base[os.fsdecode(p)] = (mode, blob)
    plan = Plan()
    plan.skipped = skipped
    seen = set()
    for p in files:
        seen.add(p)
        full = os.path.join(source, p)
        raw = open(full, "rb").read()
        data = to_lf(raw) if args.eol == "lf" else raw
        item = dict(path=p, size=len(data), sha=sha(data), phase=None, authors=None, retained=None,
                    total=None, whole=True, groups=0, eol_only=False)
        if p in base:
            bmode, bblob = base[p]
            item["mode"] = bmode
            lf = to_lf(data)
            if hash_object(dest, data) == bblob:
                item.update(cls="upstream")
            elif lf != data and hash_object(dest, lf) == bblob:
                item.update(cls="upstream", eol_only=True, sha=sha(lf))
            else:
                a, ret, tot = retained_authors(dest, p, data)
                item.update(cls="upstream-modified", authors=a, retained=ret, total=tot)
        else:
            item.update(cls="steel-sky", mode="100755" if data.startswith(b"#!") else "100644")
        if item["cls"] != "upstream":
            item["phase"] = phase_of(p, item["cls"])
            ext = os.path.splitext(p)[1].lower()
            item["whole"] = (item["cls"] == "upstream-modified" or is_binary(data)
                             or len(data) > args.max_line_bytes or ext in WHOLE_EXT)
            if not item["whole"]:
                item["groups"] = len(group_lines(data))
        plan.add(**item)
    for p, (mode, _b) in sorted(base.items()):
        if p in seen:
            continue
        if os.path.lexists(os.path.join(source, p)):
            plan.add(path=p, cls="upstream-ignored", phase=None, mode=mode, base_blob=_b, sha=None, whole=True, groups=0)
        elif args.removed == "delete":
            c = collections.Counter(blame_lines(dest, p))
            plan.add(path=p, cls="upstream-removed", phase="upstream-changes", mode=mode, sha=None,
                     whole=True, groups=0, authors=c, retained=None, total=sum(c.values()))
        else:
            plan.add(path=p, cls="upstream-removed", phase=None, mode=mode, base_blob=_b, sha=None,
                     whole=True, groups=0)
    return plan


def provenance_files(plan, base_count):
    rows = [("path", "class", "phase", "upstream_lines_retained", "upstream_authors")]
    for it in sorted(plan.items, key=lambda x: x["path"]):
        a = ""
        if it.get("authors"):
            a = "; ".join("%s (%d)" % (k, v) for k, v in it["authors"].most_common())
        ret = "" if it.get("retained") is None else "%d of %d" % (it["retained"], it["total"])
        rows.append((it["path"], it["cls"], it.get("phase") or "", ret, a))
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    counts = collections.Counter(it["cls"] for it in plan.items)
    md = ["# Provenance", "",
          "This repository continues from the real history of %s." % UPSTREAM_URL, "",
          "- The first %d commits are upstream's own, unchanged, with their original authors and dates." % base_count,
          "- Every later commit was made by the repository owner with `tools/monotonic_commit.py`. "
          "Upstream authors are named in commit trailers and are never impersonated.",
          "- The later commits are a reconstruction. Each file was built up in small steps from its "
          "finished form. The steps show how the file can be assembled, not how it was first written.",
          "- Timestamps on those commits are the times the script ran, not the times the work was done.",
          "", "| Class | Files | Meaning |", "|---|---|---|",
          "| upstream | %d | Identical to the upstream file, or identical apart from CRLF versus LF (the repository then keeps upstream's LF bytes). Not re-committed. Authorship is in the upstream commits. |" % counts["upstream"],
          "| upstream-modified | %d | Started from an upstream file and differs from it. Trailers name the upstream authors whose lines are still present, counted by matching the final file against the upstream version. That is a count of surviving lines. It says nothing about who wrote the changes. Binary files are not line-matched, and their trailers name the authors of the upstream version. |" % counts["upstream-modified"],
          "| steel-sky | %d | Not in upstream. |" % counts["steel-sky"],
          "| upstream-removed | %d | In upstream, absent from this project. Deleted in a commit that names the upstream authors, unless the history was built with `--removed keep`. |" % counts["upstream-removed"],
          "| upstream-ignored | %d | In upstream, present in the author's folder but excluded by its `.gitignore`. Left exactly as upstream has it, and checked to be unchanged. |" % counts["upstream-ignored"],
          "", "Counts do not include `PROVENANCE.md` and `provenance.csv` themselves.",
          "The per-file table is in `provenance.csv`.", ""]
    return [("provenance.csv", buf.getvalue().encode()), ("PROVENANCE.md", "\n".join(md).encode())]


def trailers(it):
    if it["cls"] in ("upstream-modified", "upstream-removed"):
        if it["authors"]:
            if it["cls"] == "upstream-removed":
                word = "removed"
            elif it.get("retained") is None:
                word = "in the upstream version, not line-matched"
            else:
                word = "retained"
            a = ", ".join("%s (%d lines %s)" % (k, v, word) for k, v in it["authors"].most_common())
        else:
            a = "none retained (file rewritten)"
        t = ("\n\nUpstream-Origin: %s\nUpstream-Path: %s\nUpstream-Authors: %s\n"
             % (UPSTREAM_URL, it["path"], a))
        if it["cls"] == "upstream-modified" and it.get("retained") is not None:
            t += "Upstream-Lines-Retained: %d of %d\n" % (it["retained"], it["total"])
        return t + "Provenance: %s\n" % it["cls"]
    return "\n\nProvenance: steel-sky\n"


def commits_for(it, source, args):
    """Yield (message, bytes or None) per commit for one file. None means delete."""
    path, scope, tr = it["path"], it["phase"], trailers(it)
    if it["cls"] == "upstream-removed":
        yield "%s: Remove upstream file %s%s" % (scope, path, tr), None
        return
    data = load(it, source, args)
    if it["whole"]:
        verb = "Update upstream file" if it["cls"] == "upstream-modified" else "Add"
        yield "%s: %s %s (%d bytes)%s" % (scope, verb, path, len(data), tr), data
        return
    groups = group_lines(data)
    if not groups:
        yield "%s: Add empty %s%s" % (scope, path, tr), data
        return
    per = per_commit(len(groups), args)
    ext = os.path.splitext(path)[1].lower()
    base = os.path.basename(path)
    acc = []
    for i in range(0, len(groups), per):
        chunk = groups[i:i + per]
        for g in chunk:
            acc.extend(g)
        first = next((x for x in chunk[0] if x.strip()), chunk[0][0])
        if per > 1:
            what = "Add lines %d to %d of %s" % (i + 1, min(i + per, len(groups)), base)
        else:
            what = describe(first, i + 1, ext)
        yield "%s: %s (%s)%s" % (scope, what, base, tr), b"".join(acc)


def schedule(plan, source, args):
    """Yield (path, message, data, mode) commits in order, lazily, so memory stays small."""
    by_phase = collections.OrderedDict()
    for it in plan.items:
        if it["phase"]:
            by_phase.setdefault(it["phase"], []).append(it)
    names = [n for n in ("upstream-changes", "pipeline", "catalogue") if n in by_phase]
    names += sorted(n for n in by_phase if n.startswith("project-"))
    names += [n for n in ("manifests", "samples", "site", "docs", "misc") if n in by_phase]
    for name in names:
        streams = [(it, iter(commits_for(it, source, args)))
                   for it in sorted(by_phase[name], key=lambda x: x["path"])]
        if args.interleave:
            live = streams
            while live:
                nxt = []
                for it, gen in live:
                    s = next(gen, None)
                    if s:
                        yield it["path"], s[0], s[1], it["mode"]
                        nxt.append((it, gen))
                live = nxt
        else:
            for it, gen in streams:
                for msg, data in gen:
                    yield it["path"], msg, data, it["mode"]


def fast_import(dest, commits, ident, branch):
    """Stream commits into git fast-import. Returns the number written."""
    name, email = ident
    tip = git(dest, "rev-parse", "HEAD").decode().strip()
    tz = time.strftime("%z")
    proc = subprocess.Popen(["git", "fast-import", "--quiet"], cwd=dest, stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    w = proc.stdin
    first, n = True, 0
    try:
        for path, msg, data, mode in commits:
            m = msg.encode("utf-8")
            w.write(b"commit refs/heads/" + branch.encode() + b"\n")
            w.write(("committer %s <%s> %d %s\n" % (name, email, int(time.time()), tz)).encode("utf-8"))
            w.write(b"data %d\n%s\n" % (len(m), m))
            if first:
                w.write(("from %s\n" % tip).encode())
                first = False
            if data is None:
                w.write(b"D " + fi_path(path) + b"\n")
            else:
                w.write(b"M " + mode.encode() + b" inline " + fi_path(path) + b"\n")
                w.write(b"data %d\n" % len(data))
                w.write(data + b"\n")
            n += 1
        w.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read()
    if proc.wait():
        sys.exit("fast-import failed:\n" + err.decode("utf-8", "replace"))
    return n


def read_blobs(dest, ids):
    """Yield (blob id, sha256 of its content) through one `git cat-file --batch` process.

    Requests are object IDs, never paths, so file names with newlines or quotes cannot
    split a request or desynchronise the replies."""
    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=dest, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    try:
        for oid in ids:
            proc.stdin.write(oid.encode() + b"\n")
            proc.stdin.flush()
            head = proc.stdout.readline().split()
            if len(head) < 3 or head[1] != b"blob":
                yield oid, None
                continue
            body = proc.stdout.read(int(head[2]))
            proc.stdout.read(1)
            yield oid, sha(body)
    finally:
        proc.stdin.close()
        proc.wait()


def verify(dest, plan):
    """Return a list of problems. Compares committed content, modes and the file set to the plan.

    Planned files: content (SHA-256 of the committed blob) and mode must match.
    Inherited upstream files (ignored here, or kept with --removed keep): the committed blob
    and mode must still be exactly what upstream has."""
    tree = {}
    for e in git(dest, "ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if e:
            meta, p = e.split(b"\t", 1)
            mode, _t, oid = meta.decode().split()
            tree[os.fsdecode(p)] = (mode, oid)
    expect, inherited = {}, {}
    for it in plan.items:
        if it["cls"] == "upstream-ignored" or (it["cls"] == "upstream-removed" and it["phase"] is None):
            inherited[it["path"]] = it
        elif it["cls"] != "upstream-removed":
            expect[it["path"]] = it
    problems = []
    for p, it in expect.items():
        if p not in tree:
            problems.append("missing: " + p)
        elif tree[p][0] != it["mode"]:
            problems.append("mode %s, expected %s: %s" % (tree[p][0], it["mode"], p))
    for p, it in inherited.items():
        if p not in tree:
            problems.append("inherited file disappeared: " + p)
        elif tree[p] != (it["mode"], it["base_blob"]):
            problems.append("inherited file changed: " + p)
    for p in tree:
        if p not in expect and p not in inherited:
            problems.append("unexpected file: " + p)
    check = [p for p in expect if p in tree]
    ids = [tree[p][1] for p in check]
    for p, (_oid, h) in zip(check, read_blobs(dest, ids)):
        want = expect[p].get("data")
        want = sha(want) if want is not None else expect[p]["sha"]
        if h != want:
            problems.append("content differs: " + p)
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=".", help="finished working tree (needs a .gitignore)")
    ap.add_argument("--dest", required=True, help="new repository folder (must not exist)")
    ap.add_argument("--upstream", default=UPSTREAM_URL, help="upstream URL or local clone")
    ap.add_argument("--lines", type=int, default=1, help="lines per commit for text files (default 1)")
    ap.add_argument("--max-commits-per-file", type=int, default=1500)
    ap.add_argument("--max-line-bytes", type=int, default=2_000_000, help="bigger text files go in whole")
    ap.add_argument("--eol", choices=["keep", "lf"], default="keep",
                    help="keep bytes exactly as they are (default) or convert CRLF to LF in text files")
    ap.add_argument("--removed", choices=["delete", "keep"], default="delete",
                    help="upstream files missing from your folder: delete them in a commit that credits "
                         "upstream (default), or leave them as upstream has them")
    ap.add_argument("--branch", default="archdaemon", help="branch name for the whole history (default: archdaemon)")
    ap.add_argument("--interleave", action="store_true", help="alternate between files within a phase")
    ap.add_argument("--name", help="commit author name (default: git config user.name)")
    ap.add_argument("--email", help="commit author email (default: git config user.email)")
    ap.add_argument("--remote", help="URL of the new, empty GitHub repository")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--push-every", type=int, default=0, help="push in batches of N commits (default: once at the end)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    source = os.path.abspath(args.source)
    if not os.path.exists(os.path.join(source, ".gitignore")):
        sys.exit("No .gitignore in the source folder. Create it first so output/ is not committed.")
    if os.path.exists(args.dest):
        sys.exit("Destination already exists: " + args.dest)

    name = args.name or run(["git", "config", "user.name"], check=False).decode().strip()
    email = args.email or run(["git", "config", "user.email"], check=False).decode().strip()
    if not name or not email:
        sys.exit("Set git user.name and user.email, or pass --name and --email.")

    print("Cloning upstream base ...")
    run(["git", "clone", "-q", args.upstream, args.dest])
    dest = args.dest
    default = git(dest, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    git(dest, "checkout", "-q", "-B", args.branch, default)
    git(dest, "config", "user.name", name)
    git(dest, "config", "user.email", email)
    for b in git(dest, "for-each-ref", "--format=%(refname:short)", "refs/heads").decode().split():
        if b != args.branch:
            git(dest, "branch", "-q", "-D", b)
    git(dest, "remote", "remove", "origin")  # also drops refs/remotes/origin/*
    for b in git(dest, "for-each-ref", "--format=%(refname)", "refs/tags").decode().split():
        git(dest, "update-ref", "-d", b)
    base_count = int(git(dest, "rev-list", "--count", "HEAD").decode())

    plan = build_plan(source, dest, args)
    for p, data in provenance_files(plan, base_count):
        plan.add(path=p, cls="steel-sky", phase="docs", data=data, mode="100644", sha=sha(data),
                 whole=False, groups=len(group_lines(data)), authors=None, retained=None)

    counts = collections.Counter(it["cls"] for it in plan.items)
    per_phase = collections.Counter()
    for it in plan.items:
        if it.get("phase"):
            per_phase[it["phase"]] += commit_count(it, args)
    total_commits = sum(per_phase.values())
    print("\nFiles: " + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())))
    print("Upstream base commits kept: %d" % base_count)
    print("Reconstruction commits: %d" % total_commits)
    for k, v in sorted(per_phase.items()):
        print("  %-18s %6d" % (k, v))
    eol = [it["path"] for it in plan.items if it.get("eol_only")]
    if eol:
        print("\nIdentical to upstream apart from line endings (not re-committed): %d" % len(eol))
    for p, why in plan.skipped:
        print("Skipped %s: %s" % (why, p))
    for label, cls in (("removed", "upstream-removed"), ("ignored here but present in upstream", "upstream-ignored")):
        lst = [it["path"] for it in plan.items if it["cls"] == cls]
        if lst:
            act = ("deleted" if args.removed == "delete" else "kept") if cls == "upstream-removed" else "kept"
            print("\nUpstream files %s (%s): %d" % (label, act, len(lst)))
            for p in lst[:15]:
                print("   " + p)
    if args.dry_run:
        shutil.rmtree(dest, ignore_errors=True)
        print("\nDry run only. Nothing was kept.")
        return

    print("\nImporting ...")
    written = fast_import(dest, schedule(plan, source, args), (name, email), args.branch)
    print("  %d commits written" % written)
    git(dest, "reset", "-q", "--hard", args.branch)

    print("Verifying content, modes and file set from the object database ...")
    problems = verify(dest, plan)
    if problems:
        print("PROBLEMS: %d" % len(problems))
        for b in problems[:30]:
            print("   " + b)
        sys.exit("Not pushing. Fix the cause and run again with a new --dest.")
    total = int(git(dest, "rev-list", "--count", "HEAD").decode())
    n_files = sum(1 for i in plan.items if i["cls"] not in ("upstream-removed", "upstream-ignored"))
    print("All %d files match in content and mode. History: %d commits." % (n_files, total))
    git(dest, "gc", "-q", "--aggressive", "--prune=now")

    if args.remote:
        git(dest, "remote", "add", "origin", args.remote)
    if args.push:
        if not args.remote:
            sys.exit("--push needs --remote")
        if args.push_every > 0:
            shas = git(dest, "rev-list", "--reverse", "HEAD").decode().split()
            step = args.push_every
            marks = shas[step - 1::step]
            if not marks or marks[-1] != shas[-1]:
                marks.append(shas[-1])
            for i, s in enumerate(marks, 1):
                git(dest, "push", "-q", "origin", "%s:refs/heads/%s" % (s, args.branch))
                print("pushed batch %d/%d" % (i, len(marks)))
        else:
            git(dest, "push", "-u", "origin", args.branch)
        print("Pushed.")
    else:
        print("Not pushed. Review with: git -C %s log --oneline | head" % dest)


if __name__ == "__main__":
    main()