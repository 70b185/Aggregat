#!/usr/bin/env python3
"""Export the whole repository as one queryable database for agents and tools.

Writes export/aggregat.sqlite and export/aggregat.json from:
  data/projects.yml, data/candidates.yml, data/devices.yml   -> projects, devices, relations
  hardware/AGENT-RULES.md                                     -> rules
  hardware/SOURCES.md                                         -> sources
  hardware/CONFLICTS.md                                       -> conflicts
  hardware/devices/*.md, hardware/common/*.md                 -> facts (one row per top-level bullet)

Facts are extracted automatically: each top-level bullet with its sub-bullets is one fact, tagged with the
device (from the file name or the text), the heading path, the evidence tags ([hw] [emu] [doc] [?]) and the
source keys ({key}) it cites or that its heading cites. The prose files stay the source of truth; this is
an index over them, rebuilt on every run.

Usage: python3 scripts/export_db.py        (needs PyYAML; sqlite3 is in the standard library)
"""
from pathlib import Path
import json
import re
import sqlite3
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "export"
OUT.mkdir(exist_ok=True)

projects = yaml.safe_load((ROOT / "data/projects.yml").read_text(encoding="utf-8"))
checked = str(projects.get("checked"))
plist = projects["projects"]
cand = ROOT / "data/candidates.yml"
if cand.exists():
    plist = plist + (yaml.safe_load(cand.read_text(encoding="utf-8"))["projects"] or [])
devices = yaml.safe_load((ROOT / "data/devices.yml").read_text(encoding="utf-8"))["devices"]
slugs = [d["slug"] for d in devices]

KIND_LIST = {"mod": "mods", "firmware": "mods", "loader": "mods", "emulator": "dev", "research": "dev",
             "library": "dev", "agent-skill": "dev", "tool": "dev", "editor": "musician"}

# ---------------------------------------------------------------- devices named in a file or a text
FILE_DEVICE = {
    "digitakt.md": ["digitakt"], "digitakt-2.md": ["digitakt-2"], "digitakt-2-sharc-measured.md": ["digitakt-2"],
    "digitakt-2-dsp-optimizing.md": ["digitakt-2"], "digitone.md": ["digitone"], "digitone-2.md": ["digitone-2"],
    "digitone-2-internals.md": ["digitone-2"], "digitone-2-machines-sampler-sharc.md": ["digitone-2"],
    "digitone-2-os111-firmware-map.md": ["digitone-2"], "digitone-2-os111-reference.md": ["digitone-2"],
    "syntakt.md": ["syntakt"], "analog-heat.md": ["analog-heat"], "octatrack.md": ["octatrack"],
    "analog-rytm.md": ["analog-rytm"], "analog-four-keys.md": ["analog-four-keys"],
    "model-cycles-samples.md": ["model-cycles", "model-samples"],
    "machinedrum-monomachine.md": ["machinedrum", "monomachine"],
    "dt2-dn2-limits-and-audio-chain.md": ["digitakt-2", "digitone-2"],
}
TEXT_DEVICE = [
    (r"\bDigitakt II\b|\bDT2\b", "digitakt-2"), (r"\bDigitone II\b|\bDN2\b", "digitone-2"),
    (r"\bDigitakt (mk1|MKI)\b|\bDT1\b|\bDT mk1\b", "digitakt"), (r"\bDigitone (mk1|MKI)\b|\bDN1\b|\bDigitone Keys\b", "digitone"),
    (r"\bSyntakt\b", "syntakt"), (r"\bAnalog Heat\b|\bHeat \+FX\b", "analog-heat"), (r"\bOctatrack\b", "octatrack"),
    (r"\bRytm\b", "analog-rytm"), (r"\bAnalog Four\b|\bA4\b|\bAnalog Keys\b", "analog-four-keys"),
    (r"\bModel:Cycles\b", "model-cycles"), (r"\bModel:Samples\b", "model-samples"),
    (r"\bMachinedrum\b", "machinedrum"), (r"\bMonomachine\b", "monomachine"),
]
EVID = re.compile(r"`\[(hw|emu|doc|\?)\]`")
KEYS = re.compile(r"\{([a-z0-9][a-z0-9-]*)\}")
ADDR = re.compile(r"0x[0-9a-fA-F]{5,8}")


def devices_in(text):
    return sorted({slug for rx, slug in TEXT_DEVICE if re.search(rx, text)})


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- facts from the prose
def extract_facts(path):
    rel = path.relative_to(ROOT).as_posix()
    lines = path.read_text(encoding="utf-8").split("\n")
    intro = []
    for l in lines[1:]:
        if l.startswith("## "):
            break
        intro.append(l)
    file_keys = set(KEYS.findall("\n".join(intro)))
    file_evid = set(EVID.findall("\n".join(intro)))
    heads = []          # (level, text)
    sec = {"keys": set(), "evid": set()}   # keys/tags in prose lines right under the current heading
    facts = []
    block = None

    def flush():
        nonlocal block
        if block:
            body = "\n".join(block["lines"])
            text = clean(re.sub(r"^\s*-\s+", "", body, flags=re.M).replace("**", ""))
            head_text = " / ".join(h for _, h in heads)
            head_keys = KEYS.findall(head_text)
            keys = set(KEYS.findall(body)) | set(head_keys) | sec["keys"]
            keys = sorted(keys or file_keys)
            # evidence: the bullet's own tag, else a tag in the section's prose, its headings, or the file intro
            evid = sorted(set(EVID.findall(body)) or sec["evid"] or set(EVID.findall(head_text)) or file_evid)
            devs = FILE_DEVICE.get(path.name) or devices_in(text + " " + head_text)
            if len(text) > 25:
                facts.append({
                    "file": rel, "line": block["line"], "section": clean(KEYS.sub("", head_text)),
                    "text": text, "evidence": ",".join(evid), "sources": ",".join(keys),
                    "devices": ",".join(devs), "addresses": ",".join(sorted(set(ADDR.findall(body)))),
                })
        block = None

    in_code = False
    for n, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            flush()
            lvl = len(m.group(1))
            heads = [h for h in heads if h[0] < lvl] + [(lvl, m.group(2).strip())]
            sec = {"keys": set(), "evid": set()}
            continue
        if line.startswith("- ") or line.startswith("* "):
            flush()
            block = {"line": n, "lines": [line]}
        elif block and (line.startswith("  ") or (line.strip() and not line.startswith("|") and not line.startswith("#"))):
            if line.strip() == "":
                continue
            block["lines"].append(line)
        elif line.strip() == "":
            if block and block["lines"][-1].strip() != "":
                block["lines"].append("")
        else:
            flush()
            if line.strip() and not line.startswith("|") and n > len(intro) + 1:
                sec["keys"] |= set(KEYS.findall(line))
                sec["evid"] |= set(EVID.findall(line))
    flush()
    return facts


fact_files = sorted((ROOT / "hardware/devices").glob("*.md")) + sorted((ROOT / "hardware/common").glob("*.md"))
facts = []
for f in fact_files:
    facts += extract_facts(f)
for i, f in enumerate(facts, 1):
    f["id"] = i

# ---------------------------------------------------------------- rules, sources, conflicts
rules = []
rtext = (ROOT / "hardware/AGENT-RULES.md").read_text(encoding="utf-8")
section = ""
cur = None
for line in rtext.split("\n") + [""]:
    m = re.match(r"^##\s+(.*)", line)
    if m:
        section = m.group(1).strip()
        continue
    m = re.match(r"^\*\*([A-Z][0-9]+)\.\s*(.*)", line)
    if m:
        if cur:
            rules.append(cur)
        cur = {"id": m.group(1), "section": section, "lines": [line]}
    elif cur is not None:
        if line.startswith("## "):
            rules.append(cur)
            cur = None
        else:
            cur["lines"].append(line)
if cur:
    rules.append(cur)
for r in rules:
    body = "\n".join(r.pop("lines"))
    t = re.match(r"^\*\*[A-Z][0-9]+\.\s*(.*?)\*\*", body, re.S)
    r["title"] = clean(t.group(1)) if t else ""
    r["text"] = clean(body.replace("**", ""))
    r["evidence"] = ",".join(sorted(set(EVID.findall(body))))
    r["sources"] = ",".join(sorted(set(KEYS.findall(body))))
    r["devices"] = ",".join(devices_in(body))

sources = []
for line in (ROOT / "hardware/SOURCES.md").read_text(encoding="utf-8").split("\n"):
    m = re.match(r"^\|\s*([a-z0-9][a-z0-9-]*)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", line)
    if m and m.group(1) != "key":
        sources.append({"key": m.group(1), "what": m.group(2), "url": m.group(3)})

conflicts = []
for line in (ROOT / "hardware/CONFLICTS.md").read_text(encoding="utf-8").split("\n"):
    m = re.match(r"^\|\s*([OS][0-9]+)\s*\|(.*)\|\s*$", line)
    if m:
        cells = [c.strip() for c in m.group(2).split("|")]
        conflicts.append({"id": m.group(1), "status": "open" if m.group(1)[0] == "O" else "settled",
                          "topic": cells[0], "a": cells[1] if len(cells) > 1 else "",
                          "b": cells[2] if len(cells) > 2 else "", "details": " | ".join(cells[3:]),
                          "devices": ",".join(devices_in(" ".join(cells)))})

# ---------------------------------------------------------------- projects, relations
prow, rrow = [], []
for p in plist:
    prow.append({
        "id": p["id"], "name": p["name"], "author": p.get("author"), "kind": p["kind"],
        "list": p.get("list") or KIND_LIST.get(p["kind"]), "devices": ",".join(p.get("devices") or []),
        "repo": p.get("repo"), "status": p.get("status"), "base_os": p.get("base_os"),
        "version": p.get("version"), "last_activity": str(p.get("last_activity") or ""),
        "notes": clean(str(p.get("notes") or "")), "links": json.dumps(p.get("links") or {}),
        "sources": json.dumps(p.get("sources") or []),
    })
    for r in p.get("relations") or []:
        rrow.append({"project": p["id"], "type": r["type"], "target": r["id"], "evidence": r.get("evidence", "")})

# ---------------------------------------------------------------- research: goals, tasks, hypotheses, participants
def md_rows(path, first_cell):
    """(section heading, cells) for table rows whose first cell matches first_cell."""
    out, head = [], ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            head = line[3:].strip()
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if re.fullmatch(first_cell, cells[0]):
                out.append((head, cells))
    return out


IDS = re.compile(r"\b([GTHO]\d+)(?:\s*-\s*[GTHO]?(\d+))?\b")


def id_list(text):
    """All research ids in a text, with ranges like H12-H15 or H8-H11 expanded."""
    found = []
    for m in IDS.finditer(text):
        first = m.group(1)
        found.append(first)
        if m.group(2):
            for n in range(int(first[1:]) + 1, int(m.group(2)) + 1):
                found.append(f"{first[0]}{n}")
    return list(dict.fromkeys(found))


rmap = ROOT / "RESEARCH-MAP.md"
goals, tasks, hyps, links = [], [], [], []
for _, c in md_rows(rmap, r"G\d+"):
    goals.append({"id": c[0], "goal": clean(c[1].replace("**", "")), "status": clean(c[2]), "moved_by": clean(c[3])})
    for item in id_list(c[3]):
        links.append({"item": item, "goal": c[0], "via": "goal table"})
for _, c in md_rows(rmap, r"T\d+"):
    done = c[1].startswith("~~") or "**done" in c[1]
    tasks.append({"id": c[0], "task": clean(c[1].replace("**", "")), "devices": clean(c[2]), "needs": clean(c[3]),
                  "effort": clean(c[4]), "value": clean(c[5]) if len(c) > 5 else "", "status": "done" if done else "open"})
for head, c in md_rows(ROOT / "hardware" / "HYPOTHESES.md", r"H\d+"):
    kind = "stock" if head.startswith("1.") else "probe" if head.startswith("2.") else "build" if head.startswith("3.") else ""
    hyps.append({"id": c[0], "goals": ",".join(id_list(c[1])), "inference": clean(c[2]), "derived_from": clean(c[3]),
                 "devices": clean(c[4]), "test": clean(c[5]), "kind": kind, "status": "open"})
    for g in id_list(c[1]):
        links.append({"item": c[0], "goal": g, "via": "hypothesis goal column"})
merged = {}
for l in links:
    merged.setdefault((l["goal"], l["item"]), []).append(l["via"])
links = [{"item": i, "goal": g, "via": "; ".join(sorted(set(v)))} for (g, i), v in sorted(merged.items())]
participants = []
part = ROOT / "research" / "PARTICIPANTS.md"
if part.exists():
    for m in re.finditer(r"^## (.+?) \((https?://[^)]+)\)\s*$", part.read_text(encoding="utf-8"), re.M):
        participants.append({"project": m.group(1), "repo": m.group(2)})
snap = ROOT / "research" / "AGGREGAT_RESEARCH.md"
snapshot = re.search(r"snapshot `([0-9a-f]+)`", snap.read_text(encoding="utf-8")).group(1) if snap.exists() else ""

meta = {"checked": checked, "generator": "scripts/export_db.py",
        "counts": {"projects": len(prow), "devices": len(devices), "relations": len(rrow), "rules": len(rules),
                   "sources": len(sources), "conflicts": len(conflicts), "facts": len(facts),
                   "goals": len(goals), "tasks": len(tasks), "hypotheses": len(hyps), "research_links": len(links),
                   "participants": len(participants)},
        "research_snapshot": snapshot}

# ---------------------------------------------------------------- write SQLite and JSON
db = OUT / "aggregat.sqlite"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
SCHEMA = {
    "meta": "key TEXT PRIMARY KEY, value TEXT",
    "devices": "slug TEXT PRIMARY KEY, name TEXT, family TEXT, phase INTEGER",
    "projects": "id TEXT PRIMARY KEY, name TEXT, author TEXT, kind TEXT, list TEXT, devices TEXT, repo TEXT, "
                "status TEXT, base_os TEXT, version TEXT, last_activity TEXT, notes TEXT, links TEXT, sources TEXT",
    "relations": "project TEXT, type TEXT, target TEXT, evidence TEXT",
    "rules": "id TEXT PRIMARY KEY, section TEXT, title TEXT, text TEXT, evidence TEXT, sources TEXT, devices TEXT",
    "sources": "key TEXT PRIMARY KEY, what TEXT, url TEXT",
    "conflicts": "id TEXT PRIMARY KEY, status TEXT, topic TEXT, a TEXT, b TEXT, details TEXT, devices TEXT",
    "facts": "id INTEGER PRIMARY KEY, file TEXT, line INTEGER, section TEXT, text TEXT, evidence TEXT, "
             "sources TEXT, devices TEXT, addresses TEXT",
    "goals": "id TEXT PRIMARY KEY, goal TEXT, status TEXT, moved_by TEXT",
    "tasks": "id TEXT PRIMARY KEY, task TEXT, devices TEXT, needs TEXT, effort TEXT, value TEXT, status TEXT",
    "hypotheses": "id TEXT PRIMARY KEY, goals TEXT, inference TEXT, derived_from TEXT, devices TEXT, test TEXT, "
                  "kind TEXT, status TEXT",
    "research_links": "item TEXT, goal TEXT, via TEXT",
    "participants": "project TEXT, repo TEXT",
}
for t, cols in SCHEMA.items():
    con.execute(f"CREATE TABLE {t} ({cols})")


def ins(table, rows):
    if not rows:
        return
    cols = list(rows[0].keys())
    con.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                    [[r.get(c) for c in cols] for r in rows])


ins("meta", [{"key": k, "value": json.dumps(v) if not isinstance(v, str) else v} for k, v in meta.items()])
ins("devices", [{"slug": d["slug"], "name": d["name"], "family": d.get("family"), "phase": d.get("phase")} for d in devices])
ins("projects", prow)
ins("relations", rrow)
ins("rules", rules)
ins("sources", sources)
ins("conflicts", conflicts)
ins("goals", goals)
ins("tasks", tasks)
ins("hypotheses", hyps)
ins("research_links", links)
ins("participants", participants)
ins("facts", [{k: f[k] for k in ("id", "file", "line", "section", "text", "evidence", "sources", "devices", "addresses")} for f in facts])
# full-text search over facts and rules, if this SQLite has FTS5
try:
    con.execute("CREATE VIRTUAL TABLE facts_fts USING fts5(text, section, devices, content='facts', content_rowid='id')")
    con.execute("INSERT INTO facts_fts(rowid, text, section, devices) SELECT id, text, section, devices FROM facts")
except sqlite3.OperationalError:
    pass
con.commit()
con.execute("VACUUM")
con.close()

(OUT / "aggregat.json").write_text(json.dumps({
    "meta": meta, "devices": devices, "projects": prow, "relations": rrow, "rules": rules,
    "sources": sources, "conflicts": conflicts, "facts": facts,
    "goals": goals, "tasks": tasks, "hypotheses": hyps, "research_links": links, "participants": participants}, ensure_ascii=False, indent=1), encoding="utf-8")
print("export:", meta["counts"])
