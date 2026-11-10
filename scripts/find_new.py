#!/usr/bin/env python3
"""List GitHub repos that match Elektron search terms and are not in the catalogue yet.

Uses `gh search repos` (needs the GitHub CLI; works without a token for public search, rate-limited).
Prints one line per unknown repo, newest push first. It decides nothing: read the README, then add the
project to data/projects.yml by hand (or ignore it). Repos listed in data/ignore.yml are skipped.

Usage: python3 scripts/find_new.py [--since 2026-10-01] [--limit 60] [--code] [--authors] [--report state/NEW.md]

--authors also lists repos that authors already in the catalogue created since --since whose name or description
points at Elektron gear (forks only when their description differs from every catalogued repo's). --report writes the result as Markdown; the daily GitHub Action runs
it, and the update run works through that file (docs/UPDATING.md).
"""
import argparse
import json
import re
import subprocess
import time
from datetime import date
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


# Name or description must point at Elektron gear for a catalogued author's new repo to be listed (their other
# repos - other brands, games, tools - are noise). "digi" catches names like Digi2Core with an empty description.
ELEKTRON = re.compile(r"elektron|digitakt|digitone|syntakt|octatrack|rytm|analog[ _-]?(four|keys|heat)|"
                      r"model[ :_-]?(cycles|samples)|machinedrum|monomachine|elekloader|elemod|overbridge|tonverk|"
                      r"(^|[^a-z])(digi|dt[12]|dn[12]|ot[ _-]?mk|ar[12]|a4)", re.I)


def catalogue_owners():
    """GitHub owners of the repos in projects.yml (repo URL only)."""
    owners = set()
    for e in (yaml.safe_load((ROOT / "data" / "projects.yml").read_text(encoding="utf-8")) or {}).get("projects") or []:
        u = (e.get("repo") or "").lower()
        if "github.com/" in u:
            owners.add(u.split("github.com/")[1].split("/")[0])
    return owners


def gh_json(args, tries=3):
    """Run gh and parse its JSON; on a rate limit (HTTP 429/403 "try again in N s") wait as told and retry."""
    for _ in range(tries):
        r = subprocess.run(["gh"] + args, capture_output=True, text=True)
        if not r.returncode:
            return json.loads(r.stdout or "[]"), ""
        m = re.search(r"try again in ([0-9.]+)s|rate limit", r.stderr, re.I)
        if not m:
            break
        time.sleep(min(70.0, float(m.group(1) or 60) + 2))
    return None, r.stderr.strip()[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="", help="only repos pushed on or after this date (YYYY-MM-DD)")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--code", action="store_true",
                    help="also search file contents for OS file names and Elektron constants (finds repos whose name and "
                         "description say nothing about Elektron; prints repo names only, no dates)")
    ap.add_argument("--authors", action="store_true",
                    help="also list repos that catalogued authors created since --since (forks marked)")
    ap.add_argument("--report", default="", help="write the result as Markdown to this file")
    a = ap.parse_args()
    lines = []                                   # Markdown report
    out = (lambda t: lines.append(t)) if a.report else print
    seen = {}
    for q in QUERIES:
        res, err = gh_json(["search", "repos", q, "--sort", "updated", "--limit", str(a.limit), "--json",
                            "fullName,updatedAt,createdAt,description,stargazersCount,isFork"])
        time.sleep(2.5)                          # search API: 30 requests a minute
        if res is None:
            out(f"- search failed: `{q}`: {err}")
            continue
        for x in res:
            seen[x["fullName"].lower()] = x
    known = known_repos()
    code_hits = {}
    if a.code:
        for q in CODE_QUERIES:
            res, err = gh_json(["search", "code", q, "--limit", "60", "--json", "repository"])
            time.sleep(7)                        # code search: 10 requests a minute
            if res is None:
                out(f"- code search failed: `{q}`: {err}")
                continue
            for x in res:
                code_hits.setdefault(x["repository"]["nameWithOwner"].lower(), set()).add(q)
    # The catalogue owner's own repos are never listed (some are private work notes); skip them by owner.
    url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"], capture_output=True, text=True).stdout
    owner = url.split("github.com")[-1].lstrip(":/").split("/")[0].lower() if "github.com" in url else ""
    new = [x for k, x in seen.items() if k not in known and not x["isFork"] and x["updatedAt"][:10] >= a.since
           and not (owner and k.startswith(owner + "/"))]
    by_author = []
    if a.authors:
        # a fork that keeps a catalogued repo's description (or has none) is taken as unchanged and skipped
        known_desc = {(x["description"] or "").strip() for k, x in seen.items() if k in known} - {""}
        owners = sorted(catalogue_owners() - {owner})
        for i in range(0, len(owners), 20):          # one search per 20 authors, forks included
            batch = owners[i:i + 20]
            args = ["search", "repos", "--include-forks", "true", "--limit", "200", "--json",
                    "fullName,createdAt,description,isFork,url"] + [f"--owner={o}" for o in batch]
            if a.since:
                args.append(f"--created=>={a.since}")
            res, err = gh_json(args)
            time.sleep(2.5)
            if res is None:
                out(f"- author check failed: `{batch[0]}`..`{batch[-1]}`: {err}")
                continue
            for x in res:
                k = x["fullName"].lower()
                desc = (x["description"] or "").strip()
                if k in known or k in seen or not ELEKTRON.search(f"{x['fullName'].split('/')[1]} {desc}"):
                    continue
                if x["isFork"] and (not desc or desc in known_desc):
                    continue
                by_author.append({"full_name": x["fullName"], "created_at": x["createdAt"], "fork": x["isFork"],
                                  "description": x["description"], "html_url": x["url"]})
    if not a.report:
        for x in sorted(new, key=lambda x: x["updatedAt"], reverse=True):
            print(f"{x['updatedAt'][:10]}  created {x['createdAt'][:10]}  *{x['stargazersCount']:<3} "
                  f"{x['fullName']}  | {(x['description'] or '')[:100]}")
        print(f"# {len(seen)} hits, {len(new)} not in the catalogue or ignore list")
        for x in by_author:
            print(f"author {x['created_at'][:10]}  {x['full_name']}{'  (fork)' if x['fork'] else ''}  | {(x['description'] or '')[:100]}")
        if a.code:
            extra = {k: v for k, v in code_hits.items() if k not in known and k not in seen
                     and not (owner and k.startswith(owner + "/"))}
            for k, v in sorted(extra.items()):
                print(f"code  {k}  | {'; '.join(sorted(v))}")
            print(f"# code search: {len(code_hits)} repos, {len(extra)} not in the catalogue or ignore list "
                  "(generic queries also hit unrelated repos: read before adding)")
        return
    cell = lambda t: (t or "").replace("|", "/").replace("\n", " ")[:110]
    extra = {k: v for k, v in code_hits.items() if k not in known and k not in seen
             and not (owner and k.startswith(owner + "/"))} if a.code else {}
    head = [f"# New repos to triage ({date.today()})", "",
            f"Found by `scripts/find_new.py --since {a.since or 'any'}{' --code' if a.code else ''}{' --authors' if a.authors else ''}`. "
            "Only repos that are in neither `data/projects.yml`, `data/candidates.yml` nor `data/ignore.yml`; an entry "
            "disappears once it is added or ignored. Triage: docs/UPDATING.md, \"Finding new projects\".", "",
            f"{len(new)} from the keyword search, {len(by_author)} new repos of catalogued authors, "
            f"{len(extra)} from the code search.", ""]
    if new:
        head += ["## Keyword search", "", "| pushed | created | repo | description |", "|---|---|---|---|"]
        head += [f"| {x['updatedAt'][:10]} | {x['createdAt'][:10]} | [{x['fullName']}](https://github.com/{x['fullName']}) | {cell(x['description'])} |"
                 for x in sorted(new, key=lambda x: x["updatedAt"], reverse=True)] + [""]
    if by_author:
        head += ["## New repos of catalogued authors", "", "| created | repo | fork | description |", "|---|---|---|---|"]
        head += [f"| {x['created_at'][:10]} | [{x['full_name']}]({x['html_url']}) | {'yes' if x['fork'] else ''} | {cell(x['description'])} |"
                 for x in sorted(by_author, key=lambda x: x["created_at"], reverse=True)] + [""]
    if extra:
        head += ["## Code search (generic queries also hit unrelated repos)", "", "| repo | matched |", "|---|---|"]
        head += [f"| [{k}](https://github.com/{k}) | {cell('; '.join(sorted(v)))} |" for k, v in sorted(extra.items())] + [""]
    if lines:
        head += ["## Problems", ""] + lines + [""]
    Path(a.report).write_text("\n".join(head), encoding="utf-8")
    print(f"{a.report}: {len(new)} search, {len(by_author)} author, {len(extra)} code")

if __name__ == "__main__":
    main()
