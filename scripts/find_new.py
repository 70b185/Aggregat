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
           "elektron transfer", "octatrack", "analog rytm", "analog four", "model:cycles", "model cycles",
           "model:samples", "machinedrum", "monomachine", "topic:digitakt", "topic:digitone", "topic:elektron"]


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
    new = [x for k, x in seen.items() if k not in known and not x["isFork"] and x["updatedAt"][:10] >= a.since]
    for x in sorted(new, key=lambda x: x["updatedAt"], reverse=True):
        print(f"{x['updatedAt'][:10]}  created {x['createdAt'][:10]}  *{x['stargazersCount']:<3} "
              f"{x['fullName']}  | {(x['description'] or '')[:100]}")
    print(f"# {len(seen)} hits, {len(new)} not in the catalogue or ignore list")


if __name__ == "__main__":
    main()
