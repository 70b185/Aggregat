#!/usr/bin/env python3
"""Cheap change detection for every watched GitHub repo.

Stage 1 (always, ~1 network call per repo, no file content):
    git ls-remote  -> default-branch HEAD + tag set.  Same as stored?  -> "unchanged", done.
Stage 2 (only when HEAD moved):
    blobless depth-1 clone -> `git ls-tree` -> blob hashes of watched paths -> added / changed / removed.
Optional (--diff):
    fetch the old HEAD (blobless) and print `git diff` of the changed watched files only.

State lives in state/fingerprints.json (compact, one entry per repo).
The human/agent-readable result is written to state/CHANGES.md and printed.

Usage:
    python3 scripts/check_updates.py              # report only, state untouched
    python3 scripts/check_updates.py --update     # report and store the new fingerprints
    python3 scripts/check_updates.py --diff       # also print text diffs of changed watched files
    python3 scripts/check_updates.py --only overtone digikit
Needs: git, PyYAML.  No GitHub API, no token.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import fnmatch
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "fingerprints.json"
REPORT = ROOT / "state" / "CHANGES.md"
GH = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+?)(?:\.git)?/?$")


def git(*args, cwd=None, timeout=180):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def load_targets():
    watch = yaml.safe_load((ROOT / "data" / "watch.yml").read_text(encoding="utf-8"))
    default, overrides = watch["default_watch"], watch.get("overrides") or {}
    targets = {}
    for f in ("projects.yml", "candidates.yml"):
        p = ROOT / "data" / f
        if not p.exists():
            continue
        for e in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("projects") or []:
            repo = (e.get("repo") or "").strip()
            if GH.match(repo):
                targets[e["id"]] = {"repo": repo, "watch": overrides.get(e["id"], default), "kind": "project"}
    for d in watch.get("directories") or []:
        targets[d["id"]] = {"repo": d["repo"], "watch": d["watch"], "kind": "directory"}
    return targets


def remote_state(repo):
    out = git("ls-remote", "--symref", repo, "HEAD", timeout=60)
    head = next(l.split()[0] for l in out.splitlines() if l.endswith("\tHEAD") and not l.startswith("ref:"))
    tags = sorted({l.split("\t")[1][len("refs/tags/"):].removesuffix("^{}")
                   for l in git("ls-remote", "--tags", repo, timeout=60).splitlines() if "\trefs/tags/" in l})
    return head, tags


def watched_files(repo, globs, old_head=None, want_diff=False):
    tmp = Path(tempfile.mkdtemp(prefix="agg-"))
    try:
        git("clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", repo, str(tmp))
        files = {}
        for line in git("ls-tree", "-r", "HEAD", cwd=tmp).splitlines():
            meta, path = line.split("\t", 1)
            if any(fnmatch.fnmatch(path, g) for g in globs):
                files[path] = meta.split()[2][:12]
        diff = ""
        if want_diff and old_head:
            try:
                git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", old_head, cwd=tmp)
                diff = git("diff", "--stat", "-p", old_head, "HEAD", "--", *globs, cwd=tmp, timeout=300)
            except RuntimeError as e:
                diff = f"(diff unavailable: {e})"
        return files, diff
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check(tid, t, prev, want_diff):
    res = {"id": tid, "kind": t["kind"], "repo": t["repo"]}
    try:
        head, tags = remote_state(t["repo"])
    except Exception as e:  # repo gone, renamed, private, network
        res["status"] = "error"
        res["error"] = str(e)[:200]
        return res
    res.update(head=head, tags=tags)
    if prev and prev.get("head") == head and prev.get("watch") == t["watch"]:
        res["status"] = "unchanged"
        res["files"] = prev.get("files", {})
        return res
    files, diff = watched_files(t["repo"], t["watch"], prev.get("head") if prev else None, want_diff)
    res["files"] = files
    res["diff"] = diff
    if not prev:
        res["status"] = "new"
        return res
    old = prev.get("files", {})
    res["added"] = sorted(set(files) - set(old))
    res["removed"] = sorted(set(old) - set(files))
    res["changed"] = sorted(p for p in files if p in old and files[p] != old[p])
    res["new_tags"] = sorted(set(tags) - set(prev.get("tags", [])))
    res["status"] = "changed" if (res["added"] or res["removed"] or res["changed"] or res["new_tags"]) else "code-only"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true", help="store new fingerprints")
    ap.add_argument("--diff", action="store_true", help="print diffs of changed watched files")
    ap.add_argument("--only", nargs="*", help="limit to these ids")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    targets = load_targets()
    if a.only:
        targets = {k: v for k, v in targets.items() if k in a.only}
    state = json.loads(STATE.read_text()) if STATE.exists() else {}

    with cf.ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(lambda kv: check(kv[0], kv[1], state.get(kv[0]), a.diff), sorted(targets.items())))

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by = {s: [r for r in results if r["status"] == s] for s in ("changed", "code-only", "new", "error", "unchanged")}
    lines = [f"# Change report {now}", "",
             f"changed {len(by['changed'])} | code-only {len(by['code-only'])} | new {len(by['new'])} | "
             f"errors {len(by['error'])} | unchanged {len(by['unchanged'])}", ""]
    for r in by["changed"]:
        bits = []
        if r["new_tags"]:
            bits.append("tags +" + ",".join(r["new_tags"]))
        bits += ["+" + p for p in r["added"]] + ["~" + p for p in r["changed"]] + ["-" + p for p in r["removed"]]
        lines.append(f"- **{r['id']}** ({r['kind']}) {r['repo']}: " + " ".join(bits))
    if by["code-only"]:
        lines.append("- code-only (HEAD moved, no watched file or tag changed): " + ", ".join(r["id"] for r in by["code-only"]))
    if by["new"]:
        lines.append("- new baseline: " + ", ".join(r["id"] for r in by["new"]))
    for r in by["error"]:
        lines.append(f"- ERROR {r['id']} {r['repo']}: {r['error']}")
    if not (by["changed"] or by["code-only"] or by["error"]):
        lines.append("Nothing to do.")
    report = "\n".join(lines) + "\n"
    print(report)
    for r in by["changed"]:
        if r.get("diff"):
            print(f"\n===== diff {r['id']} =====\n{r['diff'][:20000]}")

    if a.update:
        for r in results:
            if r["status"] == "error":
                continue
            state[r["id"]] = {"repo": r["repo"], "head": r["head"], "tags": r["tags"],
                              "files": r["files"], "watch": targets[r["id"]]["watch"],
                              "checked": now if r["status"] != "unchanged" else state.get(r["id"], {}).get("checked", now),
                              "seen": now}
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        REPORT.write_text(report)


if __name__ == "__main__":
    main()
