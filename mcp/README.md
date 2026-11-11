# Aggregat MCP server

Query tools over the Aggregat database for coding agents. One Python file, **standard library only**: no
`pip install`, works with Python 3.9 and later. Read-only. It speaks the
[Model Context Protocol](https://modelcontextprotocol.io) over stdio and reads `export/aggregat.sqlite`.

## Set up

Clone the repository (or `git pull` to refresh the data), then register the server with your agent.

**Claude Code**: a clone already contains [`.mcp.json`](../.mcp.json); Claude Code offers the server when you open the
folder. From any other folder:

```sh
claude mcp add aggregat -- python3 /path/to/Aggregat/mcp/aggregat_mcp.py
```

**Claude Desktop, Cursor, Windsurf and other clients with a JSON config:**

```json
{
  "mcpServers": {
    "aggregat": { "command": "python3", "args": ["/path/to/Aggregat/mcp/aggregat_mcp.py"] }
  }
}
```

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.aggregat]
command = "python3"
args = ["/path/to/Aggregat/mcp/aggregat_mcp.py"]
```

To use a database somewhere else, set `AGGREGAT_DB=/path/to/aggregat.sqlite` in the server's environment.

## Tools

| tool | what it answers |
|---|---|
| `preflight(device, os_version?)` | Before flashing: checklist, key safety rules, recovery facts (and whether recovery is proven on a unit), stock bugs, incidents, mods for that OS |
| `context_pack(device, brief?)` | The device's context pack as Markdown ([export/context/](../export/context/README.md)) |
| `search_facts(query, device?, evidence?, limit?)` | Full-text search over about 1,100 hardware facts, `[hw]` first; an address searches the address index |
| `get_fact(id)` | One fact by its stable id, with the sources it cites |
| `check_address(address, device?, window?)` | Facts at and near an address, and which mod platforms claim that RAM ([RAM-TENANCY.md](../hardware/RAM-TENANCY.md)) |
| `rules_for(device?, section?, full_text?)` | Safety rules plus the rules that name the device |
| `list_stock_bugs(device?)` | Bugs in Elektron's own OS |
| `list_incidents(device?, query?)` | What went wrong on real units, cause, fix, rule |
| `find_projects(query?, device?, kind?, tested?)` | Catalogued mods, firmware, loaders, tools |
| `open_questions(device?)` | Open conflicts, tests and tasks, with the link to report a result |
| `what_changed(since?)` | The latest change report; commits to the knowledge base since a date |
| `sql_query(sql)` | One read-only `SELECT` (tables: [export/README.md](../export/README.md)) |

Devices are slugs (`digitone-2`) or names and short forms (`Digitone II`, `DN2`).

## Try it without an agent

```sh
python3 mcp/aggregat_mcp.py --call preflight '{"device": "DN2", "os_version": "1.12"}'
python3 mcp/aggregat_mcp.py --call check_address '{"address": "0x46800000"}'
```

Everything the server returns is second-hand. It points to the Markdown line each fact comes from; check the cited
source before you rely on an address.
