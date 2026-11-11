#!/usr/bin/env python3
"""Check the data before it is committed: schema, cross-references, generated files in sync.

  python3 scripts/validate.py            schema + cross-references (fast; needs PyYAML and jsonschema)
  python3 scripts/validate.py --sync     also rebuild everything and warn about generated files that changed (a
                                         warning, not an error: the scheduled Action regenerates them on master, and
                                         the feed and "new" dates depend on the commit itself)

Checks
  - data/projects.yml and data/candidates.yml against schema/projects.schema.json
  - ids unique across both files; every device slug is in data/devices.yml; every relation target exists
  - mods, firmware and loaders in projects.yml say what was tested (`tested`)
  - every {source-key} cited in hardware/ resolves in hardware/SOURCES.md
  - every rule an incident names exists in hardware/AGENT-RULES.md; incident and stock-bug ids are unique
  - no firmware-like binaries are tracked (the repository holds metadata only)
Exit code 1 on any error; warnings do not fail.
"""
from pathlib import Path
import datetime
import json
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def load_yaml(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def to_json(o):
    """YAML dates -> ISO strings, so the JSON schema sees what the scripts see."""
    if isinstance(o, dict):
        return {k: to_json(v) for k, v in o.items()}
    if isinstance(o, list):
        return [to_json(v) for v in o]
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    return o


def check_schema(data, rel, relaxed=()):
    try:
        import jsonschema
    except ImportError:
        warn("jsonschema not installed (pip install jsonschema); schema check skipped")
        return
    schema = json.loads((ROOT / "schema" / "projects.schema.json").read_text(encoding="utf-8"))
    req = schema["$defs"]["project"]["required"]
    schema["$defs"]["project"]["required"] = [r for r in req if r not in relaxed]
    v = jsonschema.Draft202012Validator(schema)
    for e in sorted(v.iter_errors(to_json(data)), key=lambda e: list(e.absolute_path)):
        path = list(e.absolute_path)
        where = rel
        if len(path) >= 2 and path[0] == "projects":
            pid = (data["projects"][path[1]] or {}).get("id", f"#{path[1]}")
            where += f" [{pid}] " + ".".join(str(p) for p in path[2:])
        err(f"{where}: {e.message}")


def main(sync=False):
    devices = {d["slug"] for d in load_yaml("data/devices.yml")["devices"]}
    proj = load_yaml("data/projects.yml")
    cand = load_yaml("data/candidates.yml")
    check_schema(proj, "data/projects.yml")
    check_schema(cand, "data/candidates.yml", relaxed=("sources",))   # candidates are unverified by definition
    entries = [(p, "data/projects.yml") for p in proj["projects"] or []] + [(p, "data/candidates.yml") for p in cand["projects"] or []]
    ids = {}
    for p, rel in entries:
        if p["id"] in ids:
            err(f"{rel}: duplicate id {p['id']} (also in {ids[p['id']]})")
        ids[p["id"]] = rel
    for p, rel in entries:
        for d in p.get("devices") or []:
            if d not in devices:
                err(f"{rel} [{p['id']}]: unknown device {d!r} (add it to data/devices.yml)")
        for m in p.get("own_mods") or []:
            for d in m.get("devices") or []:
                if d not in devices:
                    err(f"{rel} [{p['id']}] own_mods {m['name']}: unknown device {d!r}")
            if m.get("origin") and m["origin"] not in ids:
                err(f"{rel} [{p['id']}] own_mods {m['name']}: origin {m['origin']!r} is not a catalogue id")
        for r in p.get("relations") or []:
            if r["id"] not in ids:
                err(f"{rel} [{p['id']}]: relation {r['type']} -> {r['id']!r}, which is not in the catalogue")
            if r["id"] == p["id"]:
                err(f"{rel} [{p['id']}]: relation to itself")
        if not p.get("devices"):
            warn(f"{rel} [{p['id']}]: no devices; it will not show under any device filter")
        if rel == "data/projects.yml" and p["kind"] in ("mod", "firmware", "loader") and not p.get("tested") and not p.get("own_mods"):
            err(f"{rel} [{p['id']}]: a {p['kind']} needs `tested` (unit | partly | emulator | not-stated)")
        if p.get("status") == "unverified" and rel == "data/projects.yml":
            err(f"{rel} [{p['id']}]: status unverified belongs in data/candidates.yml")

    ignore = load_yaml("data/ignore.yml").get("ignore") or []
    lower_repos = {re.sub(r"^https?://github\.com/", "", (p.get("repo") or "").lower()).rstrip("/") for p, _ in entries}
    for r in ignore:
        if str(r).lower() in lower_repos:
            warn(f"data/ignore.yml: {r} is ignored and catalogued at the same time")

    # source keys
    src = (ROOT / "hardware" / "SOURCES.md").read_text(encoding="utf-8")
    known = set(re.findall(r"^\|\s*([a-z0-9][a-z0-9-]*)\s*\|", src, re.M)) - {"key"}
    known |= set(ids)   # a catalogue id is a valid source key too: it points to the entry and its repo
    gen = ("DUPLICATES.md", "WEAK-EVIDENCE.md", "ADDRESS-MAP.md")
    for f in sorted((ROOT / "hardware").rglob("*.md")):
        if f.name in gen or f.name == "SOURCES.md":
            continue
        text = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)          # inline code may contain braces
        for n, line in enumerate(text.splitlines(), 1):
            for k in re.findall(r"(?<![\w$]){([a-z0-9][a-z0-9-]*)}", line):
                if k not in known:
                    err(f"{f.relative_to(ROOT)}:{n}: source key {{{k}}} is not in hardware/SOURCES.md")

    # incidents, stock bugs, rules
    rules = set(re.findall(r"^\*\*([A-G]\d+)\.", (ROOT / "hardware" / "AGENT-RULES.md").read_text(encoding="utf-8"), re.M))
    inc = (ROOT / "hardware" / "INCIDENTS.md").read_text(encoding="utf-8")
    inc_ids = re.findall(r"^### (I\d+)\.", inc, re.M)
    for i in {x for x in inc_ids if inc_ids.count(x) > 1}:
        err(f"hardware/INCIDENTS.md: duplicate incident id {i}")
    for block in re.split(r"^(?=### )", inc, flags=re.M):
        h = re.match(r"^### (I\d+)\.", block)
        m = re.search(r"^- \*\*Rule[^:]*:\*\* (.+)$", block, re.M)
        if h and m:
            for r in re.findall(r"\b([A-G]\d+)\b", m.group(1)):
                if r not in rules:
                    err(f"hardware/INCIDENTS.md {h.group(1)}: names rule {r}, which is not in AGENT-RULES.md")
    sb = re.findall(r"^### (SB\d+)\.", (ROOT / "hardware" / "STOCK-BUGS.md").read_text(encoding="utf-8"), re.M)
    for i in {x for x in sb if sb.count(x) > 1}:
        err(f"hardware/STOCK-BUGS.md: duplicate id {i}")

    # metadata only: no binaries that look like firmware
    try:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        tracked = []
    for t in tracked:
        if re.search(r"\.(syx|bin|hex|elf|img|fw|dfu|ldr)$", t, re.I):
            err(f"{t}: binary file types that could be firmware do not belong in this repository")

    if sync and not errors:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "rebuild.py")], check=True)
        diff = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
        noisy = ("feed.xml", "export/web/news.json", "state/first_seen.json")
        changed = [l[3:] for l in diff.splitlines() if l[3:] not in noisy]
        if changed:
            warn("generated files differ after a rebuild (run python3 scripts/rebuild.py and commit them, or let the "
                 "scheduled Action do it): " + ", ".join(changed[:20]) + (" ..." if len(changed) > 20 else ""))

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    print(f"validate: {len(entries)} entries, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sync="--sync" in sys.argv))
