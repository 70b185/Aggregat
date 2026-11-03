#!/usr/bin/env python3
"""List GitHub repos that match Elektron search terms and are not in the catalogue yet.

Uses `gh search repos` (needs the GitHub CLI; works without a token for public search, rate-limited).
Prints one line per unknown repo, newest push first. It decides nothing: read the README, then add the
project to data/projects.yml by hand (or ignore it). Repos listed in data/ignore.yml are skipped.

Usage: python3 scripts/find_new.py [--since 2026-10-01] [--limit 60]
"""
import argparse
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ["digitakt", "digitone", "syntakt", "analog heat elektron", "elektron firmware", "elektron mod",
           "elektron sysex", "digitakt ii", "digitone ii", "elekloader", "elektron os", "overbridge",
           "elektron transfer", "octatrack", "analog rytm", "analog four", "elektron model", "modded-cycles",
           "model:cycles mod", "model:samples mod", "machinedrum", "monomachine", "topic:digitakt", "topic:digitone", "topic:elektron"]


# File contents only Elektron projects carry: stock OS file names and addresses from the device pages.
CODE_QUERIES = ["Digitakt_II_OS1", "Digitone_II_OS1", "Syntakt_OS1", "Digitakt_OS1", "Digitone_OS1",
                "Model_Cycles_OS", "Model_Samples_OS", "Analog_Heat_OS", "Octatrack_OS", "0x403117c4", "elemod",
                "filename:AGGREGAT_RESEARCH.md"]   # projects that take part in the research (research/PARTICIPANTS.md)


def known_repos():
    known = set()
    for f in ("projects.yml", "candidates.yml"):
        p = ROOT / "data" / f
        if not p.exists():
            continue
        for e in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("projects") or []:
            urls = [e.get("repo") or ""] + [v for v in (e.get("links") or {}).values() if isinstance(v, str)]
            for u in urls:
                u = u.lower().rstrip("/")
                if "github.com/" in u:
                    known.add("/".join(u.split("github.com/")[1].split("/")[:2]))
    ign = ROOT / "data" / "ignore.yml"
    if ign.exists():
        known |= {x.lower() for x in (yaml.safe_load(ign.read_text()) or {}).get("ignore") or []}
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="", help="only repos pushed on or after this date (YYYY-MM-DD)")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--code", action="store_true",
                    help="also search file contents for OS file names and Elektron constants (finds repos whose name and "
                         "description say nothing about Elektron; prints repo names only, no dates)")
    a = ap.parse_args()
    seen = {}
    for q in QUERIES:
        r = subprocess.run(["gh", "search", "repos", q, "--sort", "updated", "--limit", str(a.limit), "--json",
                            "fullName,updatedAt,createdAt,description,stargazersCount,isFork"],
                           capture_output=True, text=True)
        if r.returncode:
            print(f"# search failed: {q}: {r.stderr.strip()[:100]}")
            continue
        for x in json.loads(r.stdout):
            seen[x["fullName"].lower()] = x
    known = known_repos()
    code_hits = {}
    if a.code:
        for q in CODE_QUERIES:
            r = subprocess.run(["gh", "search", "code", q, "--limit", "60", "--json", "repository"],
                               capture_output=True, text=True)
            if r.returncode:
                print(f"# code search failed: {q}: {r.stderr.strip()[:100]}")
                continue
            for x in json.loads(r.stdout):
                code_hits.setdefault(x["repository"]["nameWithOwner"].lower(), set()).add(q)
    # The catalogue owner's own repos are never listed (some are private work notes); skip them by owner.
    url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"], capture_output=True, text=True).stdout
    owner = url.split("github.com")[-1].lstrip(":/").split("/")[0].lower() if "github.com" in url else ""
    new = [x for k, x in seen.items() if k not in known and not x["isFork"] and x["updatedAt"][:10] >= a.since
           and not (owner and k.startswith(owner + "/"))]
    for x in sorted(new, key=lambda x: x["updatedAt"], reverse=True):
        print(f"{x['updatedAt'][:10]}  created {x['createdAt'][:10]}  *{x['stargazersCount']:<3} "
              f"{x['fullName']}  | {(x['description'] or '')[:100]}")
    print(f"# {len(seen)} hits, {len(new)} not in the catalogue or ignore list")
    if a.code:
        extra = {k: v for k, v in code_hits.items() if k not in known and k not in seen
                 and not (owner and k.startswith(owner + "/"))}
        for k, v in sorted(extra.items()):
            print(f"code  {k}  | {'; '.join(sorted(v))}")
        print(f"# code search: {len(code_hits)} repos, {len(extra)} not in the catalogue or ignore list "
              "(generic queries also hit unrelated repos: read before adding)")


if __name__ == "__main__":
    main()
