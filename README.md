# Aggregat

**One place to find Elektron mods, and everything you need to build your own.** Community firmware, mods and tools
are spread across many repos, threads and Discords; Aggregat lists them all with how far each was tested, and keeps a
knowledge base for the people who build them. Metadata and short notes only, never firmware; every entry links to the
original project.

**[Open the website](https://70b185.github.io/Aggregat/)**

## Looking for a mod

Pick your device:

[Digitakt](https://70b185.github.io/Aggregat/?t=mods&d=digitakt) · [Digitakt II](https://70b185.github.io/Aggregat/?t=mods&d=digitakt-2) · [Digitone / Keys](https://70b185.github.io/Aggregat/?t=mods&d=digitone) · [Digitone II](https://70b185.github.io/Aggregat/?t=mods&d=digitone-2) · [Syntakt](https://70b185.github.io/Aggregat/?t=mods&d=syntakt) · [Analog Heat](https://70b185.github.io/Aggregat/?t=mods&d=analog-heat) · [Octatrack](https://70b185.github.io/Aggregat/?t=mods&d=octatrack) · [Analog Rytm](https://70b185.github.io/Aggregat/?t=mods&d=analog-rytm) · [Analog Four / Keys](https://70b185.github.io/Aggregat/?t=mods&d=analog-four-keys) · [Model:Cycles](https://70b185.github.io/Aggregat/?t=mods&d=model-cycles) · [Model:Samples](https://70b185.github.io/Aggregat/?t=mods&d=model-samples) · [Machinedrum](https://70b185.github.io/Aggregat/?t=mods&d=machinedrum) · [Monomachine](https://70b185.github.io/Aggregat/?t=mods&d=monomachine)

Each card says how far the mod was tested (on a real unit, emulator only, not yet), which OS it needs and how it
installs. Read the project's own instructions before you flash anything: custom firmware can brick a unit and may
affect your warranty.

Also: [what's new](https://70b185.github.io/Aggregat/?t=news) ([feed](https://70b185.github.io/Aggregat/feed.xml)) · [musician tools](catalog/MUSICIAN-TOOLS.md) (editors, sample
and project managers, nothing that changes firmware) · the same lists as Markdown in [`catalog/`](catalog/README.md).

## Building a mod

- **How the hardware works:** [`hardware/`](hardware/README.md) (the ten things to know first, then one page per
  device), with about 1,100 facts, each with an evidence tag and a source.
- **What went wrong before:** [incidents on real units](hardware/INCIDENTS.md) and
  [bugs in Elektron's own OS](hardware/STOCK-BUGS.md) (check before you blame your mod).
- **What exists already:** [features built elsewhere and shared building blocks](research/FEATURE-OVERLAP.md),
  [developer tools](catalog/DEV-TOOLS.md) (toolchains, emulators, unpackers), and
  [which memory other mods use](hardware/RAM-TENANCY.md).
- **Before you release:** the [mod-author checklist](docs/MOD-AUTHOR-CHECKLIST.md), with a status block for your README.
- **With a coding agent:** see [below](#using-it-with-an-ai-agent).

## Help out

No flashing needed: run a [five-minute test on your stock unit](https://70b185.github.io/Aggregat/?t=stock_tests), pick an issue labelled
[good first test](https://github.com/70b185/Aggregat/labels/good%20first%20test), or correct the entry for your own
project. More in [CONTRIBUTING.md](.github/CONTRIBUTING.md) and the [research map](research/RESEARCH-MAP.md) (what is
known and open per device).

## Using it with an AI agent

Point the agent at this repo; it will find [AGENTS.md](AGENTS.md). The short version:

1. **One file per device:** [`export/context/<device>-brief.md`](export/context/README.md) holds the safety rules,
   recovery, stock bugs, incidents and open questions for that device (2k-11k tokens); `<device>.md` adds every fact.
2. **Or ask instead of reading:** the [MCP server](mcp/README.md) answers `preflight("DN2", "1.12")`,
   `search_facts("reverb", "DN2")`, `check_address("0x46800000")` from the same data. A clone has a `.mcp.json`, so
   Claude Code offers it by itself; other clients need one line of config.
3. **For open-ended research**, start with the prompt in [RESEARCH-MAP.md](research/RESEARCH-MAP.md).
4. **For scripts:** [`export/`](export/README.md) holds everything as one SQLite/JSON database (full-text search,
   stable fact ids); [llms.txt](llms.txt) is the short index for language models.

The long way, file by file: [`hardware/README.md`](hardware/README.md) (the ten things to know first), then
[`AGENT-RULES.md`](hardware/AGENT-RULES.md), [`INCIDENTS.md`](hardware/INCIDENTS.md),
[`STOCK-BUGS.md`](hardware/STOCK-BUGS.md), [`common/recovery.md`](hardware/common/recovery.md) and
[`common/flash-procedure.md`](hardware/common/flash-procedure.md), the device file under
[`hardware/devices/`](hardware/devices/), and [`catalog/`](catalog/README.md) for the project you build on.

Evidence tags: `[hw]` seen on a real unit, `[emu]` emulator only, `[doc]` stated without a test result, `[?]` unclear
or inferred. Everything is second-hand: check addresses and byte patterns against the original source. Source keys
like `{dn2-ele3}` resolve in [`hardware/SOURCES.md`](hardware/SOURCES.md).

**Starting a new project?** Copy [`research/AGGREGAT_RESEARCH.md`](research/AGGREGAT_RESEARCH.md) into its root on
day one and let your agent keep its results table. It holds the shared goals, tasks and tests as of that day; we merge
results back by hand, with credit.

## Contributing

- **Start with [CONTRIBUTING.md](.github/CONTRIBUTING.md).** The smallest useful thing takes five minutes: run a
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
[`schema/projects.schema.json`](data/projects.schema.json)), run `python3 scripts/validate.py` and then
`python3 scripts/rebuild.py`; generated files carry a marker, so edit the YAML or the Markdown they come from. The full
procedure, including finding new projects and merging research results, is in [`docs/UPDATING.md`](docs/UPDATING.md).

## What is where

| Folder | What |
|---|---|
| [`catalog/`](catalog/README.md) | the project lists, generated from `data/`: [index](catalog/README.md), [mods](catalog/MODS.md), [developer tools](catalog/DEV-TOOLS.md), [musician tools](catalog/MUSICIAN-TOOLS.md), [project families](catalog/PROJECT-FAMILIES.md), one page per device |
| [`hardware/`](hardware/README.md) | the knowledge base: rules, incidents, stock bugs, RAM tenancy, device pages |
| [`research/`](research/RESEARCH-MAP.md) | the research map, feature overlap, participants |
| [`data/`](data/projects.yml) | the sources of the catalogue: projects, devices, candidates, ignore list, schema |
| [`export/`](export/README.md) | database, JSON and per-device context packs for agents and scripts |
| [`mcp/`](mcp/README.md), [`scripts/`](scripts/), [`tests/`](tests/) | MCP server, generators and checks |
| [`docs/`](docs/UPDATING.md), [`state/`](state/CHANGES.md) | how updates work, and the change reports they produce |
| `index.html`, `assets/`, `p/`, `feed.xml`, `sitemap.xml`, `llms.txt` | the website |

## Related directories

[Awesome Music Gear Firmware](https://github.com/Lapin/awesome-music-gear-firmware) (19 brands),
[altstrument](https://altstrument.org) (structured directory of alternative firmware),
[elektronmods.com](https://elektronmods.com) (community forum). Aggregat goes deeper on fewer devices: the current
version and OS per project, and a hardware knowledge base for agents.

## Licence

Everything in this repository (texts, data and scripts) is dedicated to the public domain under
[CC0 1.0 Universal](LICENSE). The linked projects keep their own licences.

---

Vibecoded with love ♥
