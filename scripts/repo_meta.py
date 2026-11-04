#!/usr/bin/env python3
"""Fetch public GitHub metadata (creation date, stars, forks, last push, language, fork flag, owner, detected licence)
for every catalogued GitHub repo and store it in state/repo_meta.json.

Uses GitHub's repository search (several `repo:` qualifiers per query) through the `gh` CLI, so it
needs `gh` with a token (GH_TOKEN in CI). Read-only; nothing is cloned or run.

    python3 scripts/repo_meta.py            # refresh all
    python3 scripts/repo_meta.py --missing  # only repos not in the file yet

Repos that search cannot find (renamed, deleted, private) keep their old record with "missing": true.
"""
import json, re, subprocess, sys, time, datetime, pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "state" / "repo_meta.json"
GH = re.compile(r"^https?://github\.com/([^/\s]+)/([^/\s#?]+)", re.I)
BATCH = 6          # repo: qualifiers per query (the query must stay short)
PAUSE = 2.3        # seconds between queries: the search API allows 30 per minute


def repos():
    data = yaml.safe_load(open(ROOT / "data" / "projects.yml"))
    out = {}
    for p in data["projects"]:
        m = GH.match(p.get("repo") or "")
        if m:
            name = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
            out.setdefault(name.lower(), name)
    return out


def search(names):
    q = " ".join(f"repo:{n}" for n in names) + " fork:true"
    r = subprocess.run(["gh", "api", "-X", "GET", "search/repositories", "-f", f"q={q}", "-f", "per_page=100"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout).get("items", [])


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    want = repos()
    todo = [n for k, n in want.items() if "--missing" not in sys.argv or k not in old]
    today = datetime.date.today().isoformat()
    found, errors = {}, 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        for attempt in range(3):
            try:
                items = search(chunk)
                break
            except Exception as e:
                print(f"query failed ({e}); retrying", file=sys.stderr)
                time.sleep(20)
        else:
            errors += 1
            continue
        for it in items:
            found[it["full_name"].lower()] = {
                "full_name": it["full_name"], "created": it["created_at"][:10], "pushed": (it.get("pushed_at") or "")[:10],
                "stars": it["stargazers_count"], "forks": it["forks_count"], "language": it.get("language"),
                "fork": it.get("fork", False), "license": ((it.get("license") or {}).get("spdx_id") or None), "owner_type": it["owner"]["type"], "archived": it.get("archived", False),
                "seen": today}
        time.sleep(PAUSE)
    merged = {}
    for k in want:
        if k in found:
            merged[k] = found[k]
        elif k in old:
            merged[k] = dict(old[k], missing=True) if k in [n.lower() for n in todo] and not errors else old[k]
    OUT.write_text(json.dumps(dict(sorted(merged.items())), indent=1, ensure_ascii=False) + "\n")
    print(f"repo meta: {len(want)} GitHub repos, {len(found)} fetched, {len(merged)} stored, {errors} failed queries -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
