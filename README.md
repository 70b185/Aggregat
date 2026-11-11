# Aggregat

**An index and agent knowledge base for community firmware, mods and tools on Elektron devices.** In depth for
Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt and Analog Heat MKI/MKII/+FX; as a catalogue for Octatrack, Analog
Rytm/Four/Keys, Model:Cycles/Samples, Machinedrum and Monomachine.

**[Website](https://70b185.github.io/Aggregat/)** (search everything) ·
[Mod finder](https://70b185.github.io/Aggregat/?t=finder) (what fits your unit, and how far it was tested) ·
[New](https://70b185.github.io/Aggregat/?t=news) ([feed](https://70b185.github.io/Aggregat/feed.xml)) ·
[Test your unit](https://70b185.github.io/Aggregat/?t=stock_tests) (five-minute tests, no flashing) ·
[Network map](https://70b185.github.io/Aggregat/?t=network) (how the projects relate) ·
[Community](https://70b185.github.io/Aggregat/?t=community) ·
[Stock bugs](hardware/STOCK-BUGS.md) ·
[Incidents](hardware/INCIDENTS.md) ·
[Research map](RESEARCH-MAP.md)

## Start here

| You are | Read |
|---|---|
| **Musician** looking for a mod or a tool | the [mod finder](https://70b185.github.io/Aggregat/?t=finder) (pick your device and OS, see each mod with a risk light) · [MODS.md](MODS.md) (mods, custom firmware, loaders) · [MUSICIAN-TOOLS.md](MUSICIAN-TOOLS.md) (editors, sample and project managers, nothing that changes firmware) · [INDEX.md](INDEX.md) and [catalog/](catalog/) (everything per device) |
| **Developer** writing a mod | [hardware/](hardware/README.md) (how the hardware works) · [AGENT-RULES.md](hardware/AGENT-RULES.md) (rules, grown from tests) · [INCIDENTS.md](hardware/INCIDENTS.md) (what went wrong on real units) · [STOCK-BUGS.md](hardware/STOCK-BUGS.md) (bugs in Elektron's own OS, check before you blame your mod) · [DEV-TOOLS.md](DEV-TOOLS.md) (toolchains, emulators, unpackers) · [FEATURE-OVERLAP.md](FEATURE-OVERLAP.md) (features already built elsewhere, and shared building blocks to start from) · [RAM-TENANCY.md](hardware/RAM-TENANCY.md) (which platform uses which memory: check before you pick an address, and declare yours) · [ADDRESS-MAP.md](hardware/ADDRESS-MAP.md) |
| **Researcher**, or want to help | [CONTRIBUTING.md](CONTRIBUTING.md) (five ways to help, from five minutes up) · [RESEARCH-MAP.md](RESEARCH-MAP.md) (what is known and open per device, shared goals, tests that take minutes on a stock unit) · [research/PARTICIPANTS.md](research/PARTICIPANTS.md) (take part with your project) |
| **Agent or script** | [AGENTS.md](AGENTS.md) (start here) · [context packs](export/context/README.md): one file per device, brief or full · the [MCP server](mcp/README.md) (`preflight`, `search_facts`, `check_address` and more; no install) · [export/](export/README.md): one SQLite/JSON database with projects, relations, rules, incidents, stock bugs, sources, conflicts and about 1,100 hardware facts, with full-text search and stable fact ids · [llms.txt](llms.txt) |

The lists are generated from [`data/projects.yml`](data/projects.yml); [PROJECT-FAMILIES.md](PROJECT-FAMILIES.md)
shows which entries are forks, ports or copies of each other, so nothing is counted twice.

## Using it with an AI agent

Point the agent at this repo; it will find [AGENTS.md](AGENTS.md). The short version:

1. **One file per device:** [`export/context/<device>-brief.md`](export/context/README.md) holds the safety rules,
   recovery, stock bugs, incidents and open questions for that device (2k-11k tokens); `<device>.md` adds every fact.
2. **Or ask instead of reading:** the [MCP server](mcp/README.md) answers `preflight("DN2", "1.12")`,
   `search_facts("reverb", "DN2")`, `check_address("0x46800000")` from the same data. A clone has a `.mcp.json`, so
   Claude Code offers it by itself; other clients need one line of config.
3. **For open-ended research**, start with the prompt in [RESEARCH-MAP.md](RESEARCH-MAP.md).

The long way, file by file: [`hardware/README.md`](hardware/README.md) (the ten things to know first), then
[`AGENT-RULES.md`](hardware/AGENT-RULES.md), [`INCIDENTS.md`](hardware/INCIDENTS.md),
[`STOCK-BUGS.md`](hardware/STOCK-BUGS.md), [`common/recovery.md`](hardware/common/recovery.md) and
[`common/flash-procedure.md`](hardware/common/flash-procedure.md), the device file under
[`hardware/devices/`](hardware/devices/), and [`INDEX.md`](INDEX.md) for the project you build on.

Evidence tags: `[hw]` seen on a real unit, `[emu]` emulator only, `[doc]` stated without a test result, `[?]` unclear
or inferred. Everything is second-hand: check addresses and byte patterns against the original source. Source keys
like `{dn2-ele3}` resolve in [`hardware/SOURCES.md`](hardware/SOURCES.md).

**Starting a new project?** Copy [`research/AGGREGAT_RESEARCH.md`](research/AGGREGAT_RESEARCH.md) into its root on
day one and let your agent keep its results table. It holds the shared goals, tasks and tests as of that day; we merge
results back by hand, with credit.

## Contributing

- **Start with [CONTRIBUTING.md](CONTRIBUTING.md).** The smallest useful thing takes five minutes: run a
  [stock test](https://70b185.github.io/Aggregat/?t=stock_tests) on your unit and report what you saw.
- **Pull requests** are welcome: correct a fact about your project, add evidence, declare your mod's RAM in
  [RAM-TENANCY.md](hardware/RAM-TENANCY.md), fix the tooling. Every pull request is checked automatically
  (`scripts/validate.py` and the tests); a maintainer reviews and merges by hand ([credits](research/PARTICIPANTS.md)).
- **Issue forms:** [test result](https://github.com/70b185/Aggregat/issues/new?template=test-result.yml) for a test
  from the research map, [stock bug](https://github.com/70b185/Aggregat/issues/new?template=stock-bug.yml) for a bug in
  Elektron's OS.
- **Ground rules:** metadata only (names, links, status, short notes in our own words); never firmware, extracted
  sections, built images or copied code. Every entry has a source and a date. Do not post firmware-mod links on
  Elektronauts (Elektron's policy since 2026-09-16), and read each project's contribution rules before opening issues
  there.
- **Not affiliated with Elektron.** Custom firmware can brick a unit and may affect warranty. This repo points to
  projects; it does not endorse or test them.

## Keeping it current

A daily GitHub Action checks every catalogued repo for changes and writes [`state/CHANGES.md`](state/CHANGES.md).
To update by hand: edit [`data/projects.yml`](data/projects.yml) (fields are documented at its top; the schema is
[`schema/projects.schema.json`](schema/projects.schema.json)), run `python3 scripts/validate.py` and then
`python3 scripts/rebuild.py`; generated files carry a marker, so edit the YAML or the Markdown they come from. The full
procedure, including finding new projects and merging research results, is in [`docs/UPDATING.md`](docs/UPDATING.md).

## Scope

- **Phase 1, in depth:** Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX: catalogue plus the
  knowledge base in [`hardware/`](hardware/).
- **Phase 2, catalogue:** Octatrack, Analog Rytm, Analog Four/Keys, Model:Cycles/Samples, Machinedrum, Monomachine,
  with device profiles in `hardware/devices/` where projects have published research.
- **Every Elektron device that custom firmware or mods are written for belongs in the catalogue.** A device gets an
  entry in [`data/devices.yml`](data/devices.yml) as soon as the first such project appears, and a loader lists every
  device it supports. Tonverk is not listed yet: so far there are research notes and requests, no mod.
- Not covered: other brands ([`docs/BACKLOG.md`](docs/BACKLOG.md)).

Related directories: [Awesome Music Gear Firmware](https://github.com/Lapin/awesome-music-gear-firmware) (19 brands),
[altstrument](https://altstrument.org) (structured directory of alternative firmware),
[elektronmods.com](https://elektronmods.com) (community forum). Aggregat goes deeper on fewer devices: the current
version and OS per project, and a hardware knowledge base for agents.

## Licence

Everything in this repository (texts, data and scripts) is dedicated to the public domain under
[CC0 1.0 Universal](LICENSE). The linked projects keep their own licences.

---

Vibecoded with love ♥
