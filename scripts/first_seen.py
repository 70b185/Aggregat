#!/usr/bin/env python3
"""Record the date each catalogue entry first appeared, from the git history of the data files.

Writes state/first_seen.json ({id: YYYY-MM-DD}). Entries not yet committed get today's date.
A date already in the file only ever moves earlier: in a shallow clone the oldest visible commit would otherwise
re-date every older entry to that commit (this happened on 2026-11-06 and made every mod "new" on the website).
build.py and export_db.py read it for "new" markers. Usage: python3 scripts/first_seen.py
"""
import datetime
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state" / "first_seen.json"
FILES = ["data/projects.yml", "data/candidates.yml"]
ID = re.compile(r"^  - (?:id: |\{id: )([A-Za-z0-9._-]+)[\s,]", re.M)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout


seen = {}
for line in git("log", "--reverse", "--format=%H %cs", "--", *FILES).splitlines():
    sha, day = line.split()
    for f in FILES:
        for i in ID.findall(git("show", f"{sha}:{f}")):
            seen.setdefault(i, day)
if git("rev-parse", "--is-shallow-repository").strip() == "true":
    print("first seen: shallow clone, keeping the recorded dates of older entries")
old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
for i, day in old.items():
    if i not in seen or day < seen[i]:
        seen[i] = day
today = datetime.date.today().isoformat()
for f in FILES:
    p = ROOT / f
    if p.exists():
        for i in ID.findall(p.read_text(encoding="utf-8")):
            seen.setdefault(i, today)
OUT.write_text(json.dumps(dict(sorted(seen.items())), indent=1) + "\n", encoding="utf-8")
print(f"first seen: {len(seen)} ids -> {OUT.relative_to(ROOT)}")
