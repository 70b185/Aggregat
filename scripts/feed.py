#!/usr/bin/env python3
"""What is new: feed.xml (Atom, for feed readers) and export/web/news.json (the website's "New" tab).

Two kinds of entry:
  - a catalogue entry appeared (date from state/first_seen.json, written by scripts/first_seen.py)
  - the knowledge base changed (commits that touch hardware/, the research map or data/, from git history; the
    automatic check-updates commits are left out, they only move generated files)
Deterministic for a given commit: no "now" timestamps. Usage: python3 scripts/feed.py
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://70b185.github.io/Aggregat/"
GH = "https://github.com/70b185/Aggregat"
# a project in the mods list is a mod, whatever its repo calls itself (research notebook, custom OS, ...)
IN_MODS = lambda p: (p.get("list") or {"mod": "mods", "loader": "mods"}.get(p["kind"], "")) == "mods" or "mods" in (p.get("also_lists") or [])
KIND = {"mod": "Mod", "loader": "Loader", "emulator": "Emulator", "editor": "Editor",
        "tool": "Tool", "research": "Research", "library": "Library", "agent-skill": "Agent skill", "resource": "Resource",
        "request": "Request"}


def short(text, n=280):
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + " …"


def project_entries():
    first = json.loads((ROOT / "state" / "first_seen.json").read_text()) if (ROOT / "state" / "first_seen.json").exists() else {}
    devs = {d["slug"]: d["name"] for d in yaml.safe_load((ROOT / "data" / "devices.yml").read_text(encoding="utf-8"))["devices"]}
    projects = yaml.safe_load((ROOT / "data" / "projects.yml").read_text(encoding="utf-8"))["projects"]
    out = []
    for p in projects:
        d = first.get(p["id"])
        if not d:
            continue
        names = ", ".join(devs.get(s, s).split(" (")[0] for s in p.get("devices") or [])
        out.append({"date": d, "type": "project", "id": f"project-{p['id']}",
                    "title": f"New in the catalogue: {p['name']} ({'Mod' if IN_MODS(p) and p['kind'] != 'loader' else KIND.get(p['kind'], p['kind'])}{', ' + names if names else ''})",
                    "link": f"{SITE}?p={p['id']}", "project": p["id"], "kind": p["kind"],
                    "devices": p.get("devices") or [], "tested": p.get("tested") or "", "text": short(p.get("notes"))})
    return out


def commit_entries(limit=150):
    try:
        log = subprocess.run(["git", "-C", str(ROOT), "log", f"-{limit * 3}", "--format=%H%x09%ad%x09%s", "--date=short",
                              "--", "hardware", "research/RESEARCH-MAP.md", "RESEARCH-MAP.md", "data"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    out = []
    for line in log.splitlines():
        h, d, s = line.split("\t", 2)
        if s.startswith(("check-updates:", "Merge ")):
            continue
        out.append({"date": d, "type": "update", "id": f"commit-{h[:12]}", "title": s, "link": f"{GH}/commit/{h}",
                    "text": ""})
        if len(out) >= limit:
            break
    return out


def main():
    entries = sorted(project_entries() + commit_entries(), key=lambda e: (e["date"], e["id"]), reverse=True)
    web = ROOT / "export" / "web"
    web.mkdir(parents=True, exist_ok=True)
    (web / "news.json").write_text(json.dumps(entries[:300], ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    latest = entries[:60]
    updated = (latest[0]["date"] if latest else "2026-01-01") + "T00:00:00Z"
    xml = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom">',
           "  <title>Aggregat: new Elektron mods, tools and hardware knowledge</title>",
           f'  <link href="{SITE}"/>', f'  <link rel="self" href="{SITE}feed.xml"/>', f"  <id>{SITE}</id>",
           f"  <updated>{updated}</updated>", "  <author><name>Aggregat</name></author>",
           "  <rights>CC0 1.0; linked projects keep their own licences</rights>"]
    for e in latest:
        xml += ["  <entry>", f"    <title>{escape(e['title'])}</title>", f'    <link href="{escape(e["link"])}"/>',
                f"    <id>{SITE}#{escape(e['id'])}</id>", f"    <updated>{e['date']}T00:00:00Z</updated>",
                f"    <category term=\"{e['type']}\"/>"]
        if e["text"]:
            xml.append(f"    <summary>{escape(e['text'])}</summary>")
        xml.append("  </entry>")
    xml.append("</feed>")
    (ROOT / "feed.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print(f"feed: {len(entries)} entries ({sum(e['type'] == 'project' for e in entries)} projects), feed.xml has {len(latest)}")


if __name__ == "__main__":
    main()
