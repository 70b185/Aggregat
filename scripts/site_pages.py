#!/usr/bin/env python3
"""Share pages: p/<id>/index.html for every catalogue entry, plus sitemap.xml (no robots.txt: crawlers read it only at a
domain root, not under /Aggregat/; submit the sitemap in a search console instead).

The website is one page that draws everything in the browser, so a link like ?p=overtone shows no preview when it is
pasted into a forum or a chat: the crawler sees only the generic page. Each share page is a small static file with
the entry's own title and description (Open Graph tags) that sends a human visitor on to ?p=<id>.
Deterministic. Usage: python3 scripts/site_pages.py   (run by scripts/rebuild.py)
"""
from html import escape
from pathlib import Path
import re
import shutil

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://70b185.github.io/Aggregat/"
OUT = ROOT / "p"
KIND = {"mod": "Mod", "firmware": "Custom OS", "loader": "Mod loader", "emulator": "Emulator", "editor": "Editor",
        "tool": "Tool", "research": "Research", "library": "Library", "agent-skill": "Agent skill", "resource": "Resource",
        "request": "Request"}
TESTED = {"unit": "tested on a unit", "partly": "partly tested on a unit", "emulator": "emulator only",
          "not-stated": "tests not stated"}
TABS = ["mods", "finder", "news", "stock_tests", "network", "community", "facts", "addresses", "projects", "rules",
        "incidents", "stock_bugs"]


def short(text, n):
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + " …"


def main():
    devs = {d["slug"]: d["name"].split(" (")[0] for d in yaml.safe_load((ROOT / "data/devices.yml").read_text(encoding="utf-8"))["devices"]}
    projects = yaml.safe_load((ROOT / "data/projects.yml").read_text(encoding="utf-8"))["projects"]
    if OUT.exists():
        shutil.rmtree(OUT)          # entries that left the catalogue lose their page
    for p in projects:
        pid = p["id"]
        names = ", ".join(devs.get(s, s) for s in p.get("devices") or [])
        title = f"{p['name']} - {KIND.get(p['kind'], p['kind'])}" + (f" for {names}" if names else "")
        bits = [TESTED.get(p.get("tested"), ""), f"needs {short(p['base_os'], 60)}" if p.get("base_os") else ""]
        desc = short(" · ".join(b for b in bits if b) + (". " if any(bits) else "") + str(p.get("notes") or ""), 260)
        url = f"{SITE}?p={pid}"
        d = OUT / pid
        d.mkdir(parents=True)
        (d / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)} - Aggregat</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{escape(url)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Aggregat - Elektron mods and hardware knowledge">
<meta property="og:title" content="{escape(short(title, 90))}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{SITE}p/{escape(pid)}/">
<meta property="og:image" content="{SITE}assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url=../../?p={escape(pid)}">
<script>location.replace("../../?p={escape(pid)}");</script>
</head>
<body><p><a href="../../?p={escape(pid)}">{escape(title)}</a> on Aggregat.</p></body>
</html>
""", encoding="utf-8")
    urls = [SITE] + [f"{SITE}?t={t}" for t in TABS] + [f"{SITE}p/{p['id']}/" for p in projects]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    print(f"site_pages: {len(projects)} share pages, sitemap with {len(urls)} urls")


if __name__ == "__main__":
    main()
