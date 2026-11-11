#!/usr/bin/env python3
"""Aggregat MCP server: the Aggregat database as query tools for coding agents.

Standard library only (no `pip install`): speaks the Model Context Protocol over stdio (newline-delimited JSON-RPC 2.0)
and reads export/aggregat.sqlite. Read-only; it never writes to the database or the repository.

Run:   python3 mcp/aggregat_mcp.py                  (from a clone of the repo)
Env:   AGGREGAT_DB=/path/to/aggregat.sqlite         (default: ../export/aggregat.sqlite next to this file)
Test:  python3 mcp/aggregat_mcp.py --call search_facts '{"query": "reverb", "device": "digitone-2"}'
"""
from pathlib import Path
import json
import os
import re
import sqlite3
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB = Path(os.environ.get("AGGREGAT_DB", ROOT / "export" / "aggregat.sqlite"))
SERVER = {"name": "aggregat", "version": "1.0.0"}
PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"]
EV_RANK = "CASE WHEN {c} LIKE '%hw%' THEN 0 WHEN {c} LIKE '%emu%' THEN 1 WHEN {c} LIKE '%doc%' THEN 2 ELSE 3 END"
HEX = re.compile(r"^(0x)?[0-9a-fA-F]{5,8}$")


def db():
    if not DB.exists():
        raise RuntimeError(f"database not found at {DB}; run python3 scripts/export_db.py or set AGGREGAT_DB")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def rows(sql, *args):
    with db() as con:
        return [dict(r) for r in con.execute(sql, args)]


def devices():
    return {r["slug"]: r["name"] for r in rows("SELECT slug, name FROM devices")}


def dev_slug(device):
    """Accept a slug ('digitone-2') or a common name ('Digitone II', 'DN2'); None for empty."""
    if not device:
        return None
    d = str(device).strip().lower()
    alias = {"dt2": "digitakt-2", "dn2": "digitone-2", "dt1": "digitakt", "dn1": "digitone", "dt": "digitakt",
             "dn": "digitone", "st": "syntakt", "ot": "octatrack", "a4": "analog-four-keys", "ar": "analog-rytm",
             "heat": "analog-heat", "md": "machinedrum", "mnm": "monomachine", "m:c": "model-cycles", "m:s": "model-samples"}
    if d in alias:
        return alias[d]
    devs = devices()
    if d in devs:
        return d
    d2 = re.sub(r"[^a-z0-9]+", "-", d.replace(" ii", "-2").replace(" mk2", "-2")).strip("-")
    if d2 in devs:
        return d2
    for slug, name in devs.items():
        if d in name.lower():
            return slug
    raise ValueError(f"unknown device {device!r}; known: {', '.join(devs)}")


def dev_clause(col, slug):
    # list columns are comma-separated slugs; match whole items so 'digitakt' does not match 'digitakt-2'
    return (f" AND (','||{col}||',') LIKE ?", [f"%,{slug},%"]) if slug else ("", [])


def fts_query(q):
    """Quote each word so user input never breaks FTS5 syntax; all words must match."""
    words = re.findall(r"[\w.:+-]+", q)
    return " ".join('"' + w.replace('"', '') + '"' for w in words)


def link(file, line=None):
    return f"{file}:{line}" if line else file


# ------------------------------------------------------------------ tools
def search_facts(query: str, device: str = None, evidence: str = None, limit: int = 20):
    """Full-text search over the hardware facts, best evidence first. An address (0x...) searches the address index."""
    slug = dev_slug(device)
    limit = max(1, min(int(limit or 20), 100))
    if HEX.match(query.strip()):
        return check_address(query.strip(), device=device)
    dc, da = dev_clause("f.devices", slug)
    ec, ea = ((" AND f.evidence LIKE ?", [f"%{evidence}%"]) if evidence else ("", []))
    sql = (f"SELECT f.fid, f.file, f.line, f.section, f.evidence, f.devices, f.text FROM facts f "
           f"WHERE f.id IN (SELECT rowid FROM facts_fts WHERE facts_fts MATCH ?){dc}{ec} "
           f"ORDER BY {EV_RANK.format(c='f.evidence')}, f.file, f.line LIMIT ?")
    found = rows(sql, fts_query(query), *da, *ea, limit)
    return {"query": query, "device": slug, "count": len(found),
            "facts": [{"id": r["fid"], "where": link(r["file"], r["line"]), "evidence": r["evidence"] or "untagged",
                       "section": r["section"], "devices": r["devices"], "text": r["text"]} for r in found]}


def get_fact(id: str):
    """One fact by its stable id (e.g. 'digitone-2#3f9a01bc'), with the sources it cites."""
    r = rows("SELECT * FROM facts WHERE fid = ?", id)
    if not r:
        raise ValueError(f"no fact {id!r}")
    f = r[0]
    keys = [k for k in (f["sources"] or "").split(",") if k]
    src = rows(f"SELECT key, what, url FROM sources WHERE key IN ({','.join('?' * len(keys))})", *keys) if keys else []
    return {"id": f["fid"], "where": link(f["file"], f["line"]), "section": f["section"], "evidence": f["evidence"],
            "devices": f["devices"], "addresses": f["addresses"], "text": f["text"], "sources": src}


def rules_for(device: str = None, section: str = None, full_text: bool = True):
    """Agent rules: every safety rule (section A) plus the rules that name the device. section: a letter A-G to filter."""
    slug = dev_slug(device)
    rs = rows("SELECT id, section, title, text, evidence, devices FROM rules")
    out = []
    for r in rs:
        letter = r["section"][:1]
        if section and letter != section.upper()[:1]:
            continue
        if slug and letter != "A" and slug not in (r["devices"] or "").split(","):
            continue
        out.append({"id": r["id"], "section": r["section"], "evidence": r["evidence"],
                    **({"text": r["text"]} if full_text else {"title": r["title"]})})
    out.sort(key=lambda r: (r["id"][0], int(re.sub(r"\D", "", r["id"]) or 0)))
    return {"device": slug, "count": len(out), "rules": out}


def check_address(address: str, device: str = None, window: int = 0x100):
    """What is known at and near an address: facts that name it, facts within +-window bytes, RAM tenancy claims."""
    slug = dev_slug(device)
    a = address.strip().lower()
    v = int(a, 16)
    window = max(0, min(int(window or 0), 0x100000))
    dc, da = dev_clause("devices", slug)
    hits = rows(f"SELECT address, value, fid, file, line, section, devices, evidence FROM addresses "
                f"WHERE value BETWEEN ? AND ?{dc} ORDER BY ABS(value - ?), {EV_RANK.format(c='evidence')}",
                v - window, v + window, *da, v)
    exact = [h for h in hits if h["value"] == v]
    near = [h for h in hits if h["value"] != v]
    fmt = lambda h: {"address": f"0x{h['value']:08x}", "fact": h["fid"], "where": link(h["file"], h["line"]),
                     "evidence": h["evidence"], "devices": h["devices"], "section": h["section"]}
    tenancy = [t for t in ram_tenancy() if t["start"] <= v < t["end"] and (not slug or t["device"] == slug)]
    return {"address": f"0x{v:08x}", "device": slug, "exact": [fmt(h) for h in exact],
            "nearby": [fmt(h) for h in near[:30]], "ram_tenancy": tenancy,
            "note": "Addresses differ between OS versions; read the fact text for the version. All second-hand."}


def ram_tenancy():
    """Rows of hardware/RAM-TENANCY.md (table ram_tenancy): device, space, start, end (None = start only), user, use, os."""
    out = []
    for r in rows('SELECT device, space, start, "end", user, use, os, evidence, sources FROM ram_tenancy'):
        r["end"] = r["end"] if r["end"] is not None else r["start"] + 1
        r["range"] = f"0x{r['start']:08x}-" + (f"0x{r['end']:08x}" if r["end"] > r["start"] + 1 else "?")
        out.append(r)
    return out


def ram_users(device: str, os_version: str = None):
    """The RAM tenancy table for a device: which platform or mod uses which range, and the overlaps between them."""
    slug = dev_slug(device)
    rs = [r for r in ram_tenancy() if r["device"] == slug and (not os_version or r["os"] in (os_version, "both"))]
    clashes = []
    for i, a in enumerate(rs):
        for b in rs[i + 1:]:
            if a["space"] == b["space"] and a["user"] != b["user"] and a["start"] < b["end"] and b["start"] < a["end"] \
                    and (a["os"] == b["os"] or "both" in (a["os"], b["os"])):
                clashes.append({"a": f"{a['user']} {a['range']}", "b": f"{b['user']} {b['range']}", "os": a["os"]})
    return {"device": slug, "os_version": os_version, "ranges": rs, "overlaps": clashes,
            "source": "hardware/RAM-TENANCY.md; add your ranges there"}


def preflight(device: str, os_version: str = None):
    """Checklist before flashing anything to a unit: recovery path, safety rules, stock bugs, incidents, mods for the OS."""
    slug = dev_slug(device)
    if not slug:
        raise ValueError("device is required")
    dc, da = dev_clause("devices", slug)
    recovery = rows(f"SELECT fid, file, line, evidence, text FROM facts WHERE (file LIKE '%recovery.md' OR file LIKE "
                    f"'%flash-procedure.md'){dc} ORDER BY {EV_RANK.format(c='evidence')}", *da)
    bugs = rows(f"SELECT id, title, device_os, status, workaround FROM stock_bugs WHERE 1=1{dc}", *da)
    inc = rows(f"SELECT id, title, cause, fix, rules FROM incidents WHERE 1=1{dc}", *da)
    mods = rows(f"SELECT name, kind, status, tested, base_os, repo FROM projects WHERE kind IN ('mod','firmware','loader'){dc}", *da)
    if os_version:
        osv = os_version.lower()
        bugs = [b for b in bugs if not b["device_os"] or osv in b["device_os"].lower() or "all" in b["device_os"].lower()] or bugs
        mods = [m for m in mods if m["base_os"] and osv in str(m["base_os"]).lower()]
    safety = rows("SELECT id, title FROM rules WHERE section LIKE 'A.%'")
    must = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A11", "A12", "A18", "A36"]
    return {
        "device": slug, "os_version": os_version,
        "checklist": [
            "Back up projects, sounds and the +Drive with Elektron Transfer (A3).",
            "Have the stock OS file for this exact OS at hand, and a DIN MIDI interface: startup-menu recovery listens to DIN MIDI only (A2, A36).",
            "Rehearse recovery with the stock file before the first modified flash (A11).",
            "Verify the image: checksums, only intended sections differ, size limits, never a higher bootstrap version (A1, A5, A6, A9).",
            "Flash one change at a time; never power off during an upgrade, including the restart after it (A4, A12).",
            "First run of a new DSP or audio build: volume down (A7).",
            "Read the stock bugs below first, so you do not blame the mod for them.",
        ],
        "key_rules": [r for r in safety if r["id"] in must],
        "recovery_facts": [{"id": r["fid"], "where": link(r["file"], r["line"]), "evidence": r["evidence"], "text": r["text"]} for r in recovery],
        "recovery_status": (rows("SELECT recovery, recovery_note FROM devices WHERE slug = ?", slug) or [{}])[0],
        "stock_bugs": bugs, "incidents": inc,
        "mods_for_this_os" if os_version else "mods": mods,
    }


def find_projects(query: str = None, device: str = None, kind: str = None, tested: str = None, limit: int = 30):
    """Catalogued projects. kind: mod|firmware|loader|emulator|editor|tool|research|library; tested: unit|partly|emulator|not-stated."""
    slug = dev_slug(device)
    dc, da = dev_clause("devices", slug)
    sql, args = f"SELECT id, name, author, kind, status, tested, base_os, version, devices, repo, notes FROM projects WHERE 1=1{dc}", list(da)
    if kind:
        sql += " AND kind = ?"; args.append(kind)
    if tested:
        sql += " AND COALESCE(tested,'not-stated') = ?"; args.append(tested)
    for w in (query or "").split():
        sql += " AND (name || ' ' || COALESCE(notes,'') || ' ' || COALESCE(author,'') || ' ' || id) LIKE ?"; args.append(f"%{w}%")
    sql += " ORDER BY COALESCE(pushed, last_activity) DESC LIMIT ?"; args.append(max(1, min(int(limit or 30), 200)))
    found = rows(sql, *args)
    return {"count": len(found), "projects": found}


def list_stock_bugs(device: str = None):
    """Bugs in Elektron's own OS that projects found: symptom, trigger, workaround."""
    slug = dev_slug(device)
    dc, da = dev_clause("devices", slug)
    return {"device": slug, "stock_bugs": rows(f"SELECT * FROM stock_bugs WHERE 1=1{dc}", *da)}


def list_incidents(device: str = None, query: str = None):
    """What went wrong on real units, the cause, the fix and the rule it taught."""
    slug = dev_slug(device)
    dc, da = dev_clause("devices", slug)
    sql, args = f"SELECT * FROM incidents WHERE 1=1{dc}", list(da)
    for w in (query or "").split():
        sql += " AND (title||' '||cause||' '||fix||' '||seen) LIKE ?"; args.append(f"%{w}%")
    return {"device": slug, "incidents": rows(sql, *args)}


def open_questions(device: str = None):
    """Open conflicts, untested hypotheses and open tasks: where a result would move the community forward."""
    slug = dev_slug(device)
    dc, da = dev_clause("devices", slug)
    conf = rows(f"SELECT id, topic, a, b FROM conflicts WHERE status='open'{dc}", *da)
    hyps = rows("SELECT id, kind, inference, devices, test FROM hypotheses WHERE status='open'")
    tasks = rows("SELECT id, task, devices, needs, effort, value FROM tasks WHERE status='open'")
    if slug:
        name = devices()[slug]
        keys = {slug, name.split(" (")[0].lower(), {"digitakt-2": "dt2", "digitone-2": "dn2", "digitakt": "dt1",
                                                     "digitone": "dn mk1", "analog-heat": "heat"}.get(slug, "~")}
        hit = lambda s: any(k in (s or "").lower() for k in keys)
        hyps = [h for h in hyps if hit(h["devices"])]
        tasks = [t for t in tasks if hit(t["devices"])]
    return {"device": slug, "conflicts": conf, "hypotheses": hyps, "tasks": tasks,
            "report": "https://github.com/70b185/Aggregat/issues/new?template=test-result.yml"}


def context_pack(device: str, brief: bool = True):
    """The generated context pack for a device as Markdown (brief: rules, recovery, bugs, incidents; full: plus all facts)."""
    slug = dev_slug(device)
    f = ROOT / "export" / "context" / (f"{slug}-brief.md" if brief else f"{slug}.md")
    if not f.exists():
        raise RuntimeError(f"{f} missing; run python3 scripts/agent_packs.py")
    return f.read_text(encoding="utf-8")


def what_changed(since: str = None):
    """Recent changes: the daily change report and, in a git clone, commits since a date (YYYY-MM-DD) to data and knowledge."""
    out = {}
    ch = ROOT / "state" / "CHANGES.md"
    if ch.exists():
        out["change_report_head"] = "\n".join(ch.read_text(encoding="utf-8").splitlines()[:40])
    meta = {r["key"]: r["value"] for r in rows("SELECT key, value FROM meta")}
    out["checked"], out["research_snapshot"] = meta.get("checked"), meta.get("research_snapshot")
    if since:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", since):
            raise ValueError("since must be YYYY-MM-DD")
        try:
            log = subprocess.run(["git", "-C", str(ROOT), "log", f"--since={since}", "--format=%ad %s", "--date=short",
                                  "--", "data", "hardware", "research/RESEARCH-MAP.md", "RESEARCH-MAP.md"], capture_output=True, text=True, timeout=20)
            out["commits"] = log.stdout.strip().splitlines()[:100]
        except (OSError, subprocess.SubprocessError) as e:
            out["commits_error"] = str(e)
    return out


def sql_query(sql: str):
    """Read-only SQL against the database (SELECT/WITH only, max 200 rows). Tables: see export/README.md."""
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*(select|with)\b", s) or ";" in s:
        raise ValueError("only a single SELECT or WITH statement is allowed")
    with db() as con:
        cur = con.execute(s)
        cols = [c[0] for c in cur.description]
        return {"columns": cols, "rows": [list(r) for r in cur.fetchmany(200)]}


S, I, B = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}
DEV = {"type": "string", "description": "device slug (digitakt, digitakt-2, digitone, digitone-2, syntakt, analog-heat, "
                                        "octatrack, analog-rytm, analog-four-keys, model-cycles, model-samples, machinedrum, "
                                        "monomachine) or a name like 'Digitone II' / 'DN2'"}
TOOLS = {
    "search_facts": (search_facts, {"query": {**S, "description": "words (all must match) or an address like 0x40000400"},
                                    "device": DEV, "evidence": {**S, "enum": ["hw", "emu", "doc", "?"]}, "limit": I}, ["query"]),
    "get_fact": (get_fact, {"id": {**S, "description": "stable fact id, e.g. digitone-2#3f9a01bc"}}, ["id"]),
    "rules_for": (rules_for, {"device": DEV, "section": {**S, "description": "A safety, B legal, C process, D writing mods, "
                                                                            "E parameter tables, F SysEx, G working method"},
                              "full_text": B}, []),
    "check_address": (check_address, {"address": {**S, "description": "hex address, e.g. 0x46800000"}, "device": DEV,
                                      "window": {**I, "description": "also list facts within +- this many bytes (default 256)"}}, ["address"]),
    "ram_users": (ram_users, {"device": DEV, "os_version": {**S, "description": "e.g. 1.11"}}, ["device"]),
    "preflight": (preflight, {"device": DEV, "os_version": {**S, "description": "e.g. 1.12"}}, ["device"]),
    "find_projects": (find_projects, {"query": S, "device": DEV, "kind": S, "tested": S, "limit": I}, []),
    "list_stock_bugs": (list_stock_bugs, {"device": DEV}, []),
    "list_incidents": (list_incidents, {"device": DEV, "query": S}, []),
    "open_questions": (open_questions, {"device": DEV}, []),
    "context_pack": (context_pack, {"device": DEV, "brief": B}, ["device"]),
    "what_changed": (what_changed, {"since": {**S, "description": "YYYY-MM-DD"}}, []),
    "sql_query": (sql_query, {"sql": {**S, "description": "one read-only SELECT"}}, ["sql"]),
}


def tool_list():
    return [{"name": n, "description": (f.__doc__ or "").strip(),
             "inputSchema": {"type": "object", "properties": props, "required": req},
             "annotations": {"readOnlyHint": True, "openWorldHint": False}}
            for n, (f, props, req) in TOOLS.items()]


def call(name, args):
    if name not in TOOLS:
        raise ValueError(f"unknown tool {name}")
    f, props, _ = TOOLS[name]
    args = {k: v for k, v in (args or {}).items() if k in props}
    return f(**args)


# ------------------------------------------------------------------ JSON-RPC over stdio
def handle(msg):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if mid is None:          # notification (notifications/initialized, cancelled, ...): no answer
        return None
    try:
        if method == "initialize":
            want = params.get("protocolVersion")
            result = {"protocolVersion": want if want in PROTOCOLS else PROTOCOLS[0],
                      "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER,
                      "instructions": "Aggregat: second-hand knowledge about Elektron hardware for mod developers. "
                                      "Start with preflight or context_pack for the device; follow safety rules A1-A49; "
                                      "prefer [hw] evidence; cite facts by their id."}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": tool_list()}
        elif method == "tools/call":
            try:
                out = call(params.get("name"), params.get("arguments"))
                text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False, indent=1)
                result = {"content": [{"type": "text", "text": text}], "isError": False}
            except Exception as e:   # tool errors go back to the model, not as protocol errors
                result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
        elif method in ("resources/list", "prompts/list"):
            result = {method.split("/")[0]: []}
        else:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    except Exception as e:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": str(e)}}


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            out = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            out = [r for r in map(handle, msg) if r] if isinstance(msg, list) else handle(msg)
        if out:
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--call":
        res = call(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {})
        print(res if isinstance(res, str) else json.dumps(res, ensure_ascii=False, indent=1))
    else:
        serve()
