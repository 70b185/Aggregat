#!/usr/bin/env python3
"""Cheap change detection for every watched GitHub repo.

Stage 1 (always, ~1 network call per repo, no file content):
    git ls-remote  -> default-branch HEAD + tag set.  Same as stored?  -> "unchanged", done.
Stage 2 (only when HEAD moved):
    blobless depth-1 clone -> `git ls-tree` -> blob hashes of watched paths -> added / changed / removed.
Optional (--diff):
    fetch the old HEAD (blobless) and print `git diff` of the changed watched files only.
Forum threads (entries without a GitHub repo but with links.forum on a host in PAGE_HOSTS):
    one HTTP GET of the thread page -> post ids, page count and GitHub links in the posts. A new post, a new page or
    a new GitHub link is reported like a changed file ("+post 123", "+link github.com/x/y"); nothing else on the
    page (online users, view counts) counts. This is how forum-only projects (such as heatfx-multimode) get watched.

State lives in state/fingerprints.json (compact, one entry per repo).
The human/agent-readable result is written to state/CHANGES.md and printed.

Usage:
    python3 scripts/check_updates.py              # report only, state untouched
    python3 scripts/check_updates.py --update     # report and store the new fingerprints
    python3 scripts/check_updates.py --diff       # also print text diffs of changed watched files
    python3 scripts/check_updates.py --only overtone digikit
Needs: git, PyYAML.  No GitHub API, no token.  Forum threads need plain HTTPS to the forum.
"""
from __future__ import annotations

import argparse
import os
import concurrent.futures as cf
import datetime as dt
import fnmatch
import json
import re
import shutil
import subprocess
import tempfile
import hashlib
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "fingerprints.json"
REPORT = ROOT / "state" / "CHANGES.md"
GH = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+?)(?:\.git)?/?$")
# Forums whose thread pages we can fingerprint (MyBB: every post carries id="post_<n>").
PAGE_HOSTS = ("elektronmods.com",)
POST_ID = re.compile(r'id="post_(\d+)"')
GH_LINK = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
GH_NOT_REPO = {"orgs", "users", "settings", "login", "about", "features", "topics", "sponsors", "marketplace"}


def git(*args, cwd=None, timeout=180):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def load_targets():
    """Return (targets, gone): the repos to poll, and the GitHub repos of entries marked unreachable."""
    watch = yaml.safe_load((ROOT / "data" / "watch.yml").read_text(encoding="utf-8"))
    default, overrides = watch["default_watch"], watch.get("overrides") or {}
    targets, gone = {}, {}
    for f in ("projects.yml", "candidates.yml"):
        p = ROOT / "data" / f
        if not p.exists():
            continue
        for e in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("projects") or []:
            repo = (e.get("repo") or "").strip()
            forum = str((e.get("links") or {}).get("forum") or "").strip()
            if not GH.match(repo) and is_page(forum) and str(e.get("status", "")).lower() != "unreachable":
                targets[e["id"]] = {"repo": forum, "watch": ["posts"], "kind": "page"}
                continue
            # Repos we already know are gone (deleted or private) are not polled in full; one cheap
            # ls-remote per run tells whether they are back (reported as "back online"). Set their
            # status back to something else to watch them again.
            if not GH.match(repo):
                continue
            if str(e.get("status", "")).lower() == "unreachable":
                gone[e["id"]] = repo
            else:
                targets[e["id"]] = {"repo": repo, "watch": overrides.get(e["id"], default), "kind": "project"}
    for d in watch.get("directories") or []:
        targets[d["id"]] = {"repo": d["repo"], "watch": d["watch"], "kind": "directory"}
    return targets, gone


def is_page(url):
    """True for a forum thread URL we know how to fingerprint."""
    m = re.match(r"^https://([^/]+)/thread-\d+", url or "")
    return bool(m) and m.group(1).lower().removeprefix("www.") in PAGE_HOSTS


def page_fingerprint(html, url):
    """What counts on a MyBB thread page: its posts, how many pages it has, and GitHub links in it.

    Returns a dict shaped like a watched-file listing, so the usual added/removed logic reports changes."""
    posts = sorted(set(POST_ID.findall(html)), key=int)
    if not posts:
        raise RuntimeError("no posts found on the page (layout changed, or the thread is gone)")
    tid = re.search(r"thread-(\d+)", url).group(1)
    # pagination links to the same thread: thread-92-...html?page=3 or showthread.php?tid=92&page=3
    pages = [int(n) for n in re.findall(rf"(?:thread-{tid}[^\"'\s]*?|tid={tid}[^\"'\s]*?)[?&](?:amp;)?page=(\d+)", html)]
    files = {f"post {p}": "" for p in posts}
    files[f"pages {max(pages + [1])}"] = ""
    for owner, name in GH_LINK.findall(html):
        if owner.lower() not in GH_NOT_REPO:
            files[f"link github.com/{owner}/{name.removesuffix('.git')}".lower()] = ""
    return files


def fetch_page(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "aggregat-check-updates (+https://github.com/70b185/Aggregat)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def check_page(tid, t, prev, fetch=fetch_page):
    res = {"id": tid, "kind": "page", "repo": t["repo"], "tags": []}
    try:
        files = page_fingerprint(fetch(t["repo"]), t["repo"])
    except Exception as e:  # network, blocked, layout changed: report, keep the old baseline
        res["status"] = "error"
        res["error"] = str(e)[:200]
        return res
    res["files"] = files
    res["head"] = hashlib.sha1("\n".join(sorted(files)).encode()).hexdigest()[:12]
    if not prev:
        res["status"] = "new"
        return res
    if prev.get("head") == res["head"]:
        res["status"] = "unchanged"
        return res
    old = prev.get("files", {})
    res["added"] = sorted(set(files) - set(old))
    res["removed"] = sorted(set(old) - set(files))
    res["changed"], res["new_tags"] = [], []
    res["status"] = "changed"
    return res


def is_back(repo):
    """True when a repo catalogued as unreachable answers again with at least one commit."""
    try:
        return bool(git("ls-remote", repo, "HEAD", timeout=60).strip())
    except Exception:
        return False


def remote_state(repo):
    out = git("ls-remote", "--symref", repo, "HEAD", timeout=60)
    head = next((l.split()[0] for l in out.splitlines() if l.endswith("\tHEAD") and not l.startswith("ref:")), None)
    if head is None:  # ls-remote succeeded but listed no HEAD: the repo exists and has no commits yet
        raise RuntimeError("repo is empty (no commits yet)")
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
    if t["kind"] == "page":
        return check_page(tid, t, prev)
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
    try:
        files, diff = watched_files(t["repo"], t["watch"], prev.get("head") if prev else None, want_diff)
    except Exception as e:  # clone timed out or failed: report it, keep the old baseline, go on with the others
        res["status"] = "error"
        res["error"] = f"listing files failed: {str(e)[:180]}"
        return res
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
    ap.add_argument("--update", action="store_true", help="store new fingerprints (and write state/CHANGES.md)")
    ap.add_argument("--report", action="store_true",
                    help="write state/CHANGES.md without storing fingerprints: the report then lists every change since "
                         "the last processed baseline (the daily Action; the update run stores baselines for what it read)")
    ap.add_argument("--diff", action="store_true", help="print diffs of changed watched files")
    ap.add_argument("--only", nargs="*", help="limit to these ids")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    targets, gone = load_targets()
    if a.only:
        targets = {k: v for k, v in targets.items() if k in a.only}
        gone = {k: v for k, v in gone.items() if k in a.only}
    state = json.loads(STATE.read_text()) if STATE.exists() else {}

    with cf.ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(lambda kv: check(kv[0], kv[1], state.get(kv[0]), a.diff), sorted(targets.items())))
        back = [k for k, ok in zip(sorted(gone), ex.map(lambda k: is_back(gone[k]), sorted(gone))) if ok]

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by = {s: [r for r in results if r["status"] == s] for s in ("changed", "code-only", "new", "error", "unchanged")}
    lines = [f"# Change report {now}", "",
             f"changed {len(by['changed'])} | code-only {len(by['code-only'])} | new {len(by['new'])} | "
             f"errors {len(by['error'])} | unchanged {len(by['unchanged'])} | back online {len(back)}", ""]
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
    for k in back:
        lines.append(f"- BACK ONLINE {k} {gone[k]}: catalogued as unreachable, answers again; reread it, set its "
                     "status and fields from the README, then store a baseline with --only")
    if not (by["changed"] or by["code-only"] or by["error"] or back):
        lines.append("Nothing to do.")
    report = "\n".join(lines) + "\n"
    print(report)
    for r in by["changed"]:
        if r.get("diff"):
            print(f"\n===== diff {r['id']} =====\n{r['diff']}")

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
    if (a.update and not a.only) or a.report:
        REPORT.write_text(report)


if __name__ == "__main__":
    main()
