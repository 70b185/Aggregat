"""Tests for the generators and the MCP server. Run: python3 -m pytest -q tests

The generators work on the whole repository, so most tests run them on a copy in a temporary folder and look at the
output. Nothing here needs the network.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(script, cwd, *args):
    r = subprocess.run([PY, str(cwd / "scripts" / script), *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"{script} failed:\n{r.stdout}\n{r.stderr}"
    return r.stdout


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    """A copy of the repository without git history, with a fresh export."""
    dst = tmp_path_factory.mktemp("repo") / "Aggregat"
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    run("export_db.py", dst)
    run("agent_packs.py", dst)
    return dst


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def facts(repo):
    con = sqlite3.connect(repo / "export" / "aggregat.sqlite")
    rows = con.execute("SELECT fid, text, file, line FROM facts").fetchall()
    con.close()
    return rows


# ------------------------------------------------------------------ export_db
def test_export_is_deterministic(repo):
    before = {p: sha(repo / p) for p in ("export/aggregat.json", "export/aggregat.sqlite", "export/web/core.json", "export/web/facts.json")}
    run("export_db.py", repo)
    after = {p: sha(repo / p) for p in before}
    assert before == after


def test_fact_ids_unique_and_well_formed(repo):
    rows = facts(repo)
    fids = [r[0] for r in rows]
    assert len(rows) > 500
    assert len(fids) == len(set(fids))
    assert all("#" in f and len(f.split("#")[1]) >= 8 for f in fids)


def test_fact_ids_survive_moved_lines(tmp_path, repo):
    """Inserting text above a fact moves its line number but must not change its id."""
    copy = tmp_path / "Aggregat"
    shutil.copytree(repo, copy)
    target = copy / "hardware" / "devices" / "digitone-2.md"
    lines = target.read_text(encoding="utf-8").split("\n")
    first_h2 = next(i for i, l in enumerate(lines) if l.startswith("## "))
    lines[first_h2:first_h2] = ["## Inserted section", "", "Some prose without bullets.", ""]
    target.write_text("\n".join(lines), encoding="utf-8")
    run("export_db.py", copy)
    old = {r[0]: r[3] for r in facts(repo) if r[2].endswith("digitone-2.md")}
    new = {r[0]: r[3] for r in facts(copy) if r[2].endswith("digitone-2.md")}
    assert set(old) == set(new)
    moved = [f for f in old if old[f] > first_h2]
    assert moved and all(new[f] == old[f] + 4 for f in moved)


def test_address_index_matches_facts(repo):
    con = sqlite3.connect(repo / "export" / "aggregat.sqlite")
    n = con.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]
    bad = con.execute("SELECT COUNT(*) FROM addresses a LEFT JOIN facts f ON f.fid = a.fid WHERE f.fid IS NULL").fetchone()[0]
    sample = con.execute("SELECT address, value FROM addresses LIMIT 50").fetchall()
    con.close()
    assert n > 100 and bad == 0
    assert all(int(a, 16) == v for a, v in sample)


def test_web_split_has_everything_but_facts(repo):
    core = json.loads((repo / "export" / "web" / "core.json").read_text(encoding="utf-8"))
    full = json.loads((repo / "export" / "aggregat.json").read_text(encoding="utf-8"))
    assert "facts" not in core
    assert set(full) - set(core) == {"facts"}
    assert len(json.loads((repo / "export" / "web" / "facts.json").read_text(encoding="utf-8"))) == len(full["facts"])


# ------------------------------------------------------------------ agent_packs
def test_context_pack_per_device(repo):
    import yaml
    slugs = [d["slug"] for d in yaml.safe_load((repo / "data" / "devices.yml").read_text())["devices"]]
    for s in slugs:
        brief = (repo / "export" / "context" / f"{s}-brief.md").read_text(encoding="utf-8")
        full = (repo / "export" / "context" / f"{s}.md").read_text(encoding="utf-8")
        assert "## 1. Safety rules" in brief and "**A1**" in brief
        assert len(full) >= len(brief)
        assert "](../" not in full.replace("[`../", "")   # relative links are resolved to absolute URLs


def test_agent_packs_deterministic(repo):
    files = sorted((repo / "export" / "context").glob("*.md")) + [repo / "llms.txt", repo / "hardware" / "ADDRESS-MAP.md"]
    before = {f: sha(f) for f in files}
    run("agent_packs.py", repo)
    assert before == {f: sha(f) for f in files}


def test_llms_txt_format(repo):
    t = (repo / "llms.txt").read_text(encoding="utf-8")
    assert t.startswith("# Aggregat\n\n> ")
    assert "## Context packs" in t and "-brief.md" in t


# ------------------------------------------------------------------ validate
def test_validate_passes_on_repo():
    r = subprocess.run([PY, str(ROOT / "scripts" / "validate.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_validate_catches_bad_data(tmp_path):
    copy = tmp_path / "Aggregat"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "export"))
    p = copy / "data" / "projects.yml"
    t = p.read_text(encoding="utf-8")
    t = t.replace("devices: [digitakt, digitone, digitakt-2", "devices: [no-such-device, digitone, digitakt-2", 1)
    t = t.replace("  - id: elekloader\n", "  - id: elekloader\n    colour: red\n", 1)
    p.write_text(t, encoding="utf-8")
    r = subprocess.run([PY, str(copy / "scripts" / "validate.py")], capture_output=True, text=True)
    assert r.returncode == 1
    assert "no-such-device" in r.stdout and "colour" in r.stdout


# ------------------------------------------------------------------ MCP server
def mcp_session(messages, db):
    env = {"AGGREGAT_DB": str(db), "PATH": "/usr/bin:/bin"}
    inp = "\n".join(json.dumps(m) for m in messages) + "\n"
    r = subprocess.run([PY, str(ROOT / "mcp" / "aggregat_mcp.py")], input=inp, capture_output=True, text=True, env=env, timeout=60)
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


def test_mcp_protocol(repo):
    db = repo / "export" / "aggregat.sqlite"
    out = mcp_session([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                                       "clientInfo": {"name": "t", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_facts", "arguments": {"query": "recovery", "device": "DN2"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "sql_query", "arguments": {"sql": "DROP TABLE facts"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "nope"},
    ], db)
    by_id = {m["id"]: m for m in out}
    assert set(by_id) == {1, 2, 3, 4, 5}            # the notification gets no answer
    assert by_id[1]["result"]["protocolVersion"] == "2025-06-18"
    names = {t["name"] for t in by_id[2]["result"]["tools"]}
    assert {"search_facts", "preflight", "check_address", "context_pack"} <= names
    res = json.loads(by_id[3]["result"]["content"][0]["text"])
    assert res["device"] == "digitone-2" and res["count"] > 0
    assert by_id[4]["result"]["isError"] is True
    assert by_id[5]["error"]["code"] == -32601


@pytest.mark.parametrize("name,slug", [("DN2", "digitone-2"), ("Digitakt II", "digitakt-2"), ("digitakt", "digitakt"),
                                       ("Syntakt", "syntakt"), ("A4", "analog-four-keys")])
def test_mcp_device_names(repo, monkeypatch, name, slug):
    monkeypatch.setenv("AGGREGAT_DB", str(repo / "export" / "aggregat.sqlite"))
    sys.path.insert(0, str(ROOT / "mcp"))
    import importlib
    import aggregat_mcp
    importlib.reload(aggregat_mcp)
    assert aggregat_mcp.dev_slug(name) == slug


def test_mcp_device_filter_is_exact(repo, monkeypatch):
    """'digitakt' must not match facts that only name 'digitakt-2'."""
    monkeypatch.setenv("AGGREGAT_DB", str(repo / "export" / "aggregat.sqlite"))
    sys.path.insert(0, str(ROOT / "mcp"))
    import importlib
    import aggregat_mcp
    importlib.reload(aggregat_mcp)
    res = aggregat_mcp.search_facts("SHARC", device="digitakt", limit=100)
    assert all("digitakt" in f["devices"].split(",") for f in res["facts"])
