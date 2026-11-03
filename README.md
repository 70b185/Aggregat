# Aggregat

**A metadata index and agent knowledge base for unofficial firmware and tooling on Elektron devices** - in depth for the small boxes (Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX), as a catalogue for Octatrack, Analog Rytm/Four/Keys, Model:Cycles/Samples, Machinedrum and Monomachine.

---

## Looking for something?

| You want | Read |
|---|---|
| **Mods and custom firmware** for your device, and the loaders that install them | [MODS.md](MODS.md) |
| **Development tools**: toolchains, emulators, firmware unpackers, protocol libraries, research | [DEV-TOOLS.md](DEV-TOOLS.md) |
| **Tools for musicians**: editors, sample/project managers, Overbridge audio, screen mirrors - nothing that changes firmware | [MUSICIAN-TOOLS.md](MUSICIAN-TOOLS.md) |
| **The same feature built more than once** (engines carried between boxes, compressors, scales, direct jump, load meters): where to start instead of from zero | [FEATURE-OVERLAP.md](FEATURE-OVERLAP.md) |
| Which entries are forks, copies, ports or builds of each other (so nothing is counted twice) | [PROJECT-FAMILIES.md](PROJECT-FAMILIES.md) |
| Everything for one device, with full notes | [INDEX.md](INDEX.md) |
| How the hardware works, for writing mods | [hardware/](hardware/README.md) |
| **What is known and what is still open, per device, plus a shared to-do and a prompt to start a research session** | [RESEARCH-MAP.md](RESEARCH-MAP.md) |
| **Help the research:** tests that take minutes on a stock unit, open tasks and shared goals, and how to take part with your own project | [RESEARCH-MAP.md](RESEARCH-MAP.md#help-with-a-test-no-flashing-needed), [research/](research/PARTICIPANTS.md) |
| **Everything as one database** (projects, relations, rules, sources, conflicts, ~900 hardware facts with full-text search), for agents and scripts | [export/](export/README.md), or search it in the browser: [70b185.github.io/Aggregat](https://70b185.github.io/Aggregat/) |

All three lists are generated from [`data/projects.yml`](data/projects.yml); an entry's `kind` (or an explicit `list:` field) decides where it goes.

## What is in here

| Path | What it is | Who it is for |
|---|---|---|
| [`INDEX.md`](INDEX.md) | Overview: projects per device, verified vs. unverified | everyone |
| [`devices/`](devices/) | One generated page per device: table of projects with kind, status, OS, last activity, links | developers looking for a tool or mod |
| [`data/projects.yml`](data/projects.yml) | The source of truth: one entry per project (repo, links, status, base OS, version, notes, sources) | contributors, scripts |
| [`data/candidates.yml`](data/candidates.yml) | Entries seen in other directories but not yet checked against their repo | contributors |
| [`data/devices.yml`](data/devices.yml) | Device catalogue and scope phases | scripts |
| [`hardware/`](hardware/) | **Knowledge base for AI agents**: rules, recovery, firmware container, memory maps, toolchains, per-device internals - every fact with an evidence tag and a source | agents and humans writing mods |
| [`state/CHANGES.md`](state/CHANGES.md) | Latest change report from the fingerprint check - **read this first when updating** | agents, maintainers |
| [`docs/UPDATING.md`](docs/UPDATING.md) | Token-cheap update procedure (fingerprints, diffs, daily GitHub Action) | agents, maintainers |
| [`docs/BACKLOG.md`](docs/BACKLOG.md) | Research backlog and phase-2 devices | maintainers |
| [`scripts/build.py`](scripts/build.py) | Regenerates `INDEX.md`, `devices/*.md` and the three lists from `data/` | maintainers |

Snapshot (2026-11-02): 199 project entries for 13 devices (115 mods/firmware/loaders, 53 development tools, 27 musician tools); `hardware/` holds about 35 files with rules A1-A38, drawn from more than 70 repositories, two directories, official release notes and forum threads.

## Using it with an AI agent

Point the agent at this repo and tell it to read, in this order (for open-ended research, start with the ready-made prompt in [RESEARCH-MAP.md](RESEARCH-MAP.md) instead):

1. [`hardware/README.md`](hardware/README.md) - the ten things to know first
2. [`hardware/AGENT-RULES.md`](hardware/AGENT-RULES.md) - safety, legal, process and coding rules
3. [`hardware/common/recovery.md`](hardware/common/recovery.md) and [`hardware/common/flash-procedure.md`](hardware/common/flash-procedure.md)
4. the device file under [`hardware/devices/`](hardware/devices/)
5. [`INDEX.md`](INDEX.md) / [`devices/`](devices/) to find the project it builds on

**Starting a new project with this repo?** Copy [`research/AGGREGAT_RESEARCH.md`](research/AGGREGAT_RESEARCH.md) into the root of the new project on day one, and have your agent keep its results table up to date. It holds a copy of the shared goals, tasks and tests as of the day you started, so your findings stay comparable, and we merge your results back (by hand, with credit) when we update. Optional, but it is how one project's finding helps all the others. See [research/PARTICIPANTS.md](research/PARTICIPANTS.md).

Evidence tags used throughout `hardware/`: `[hw]` reported working on a real unit, `[emu]` emulator only, `[doc]` stated without a test result, `[?]` unclear or inferred. Everything is **second-hand** - verify addresses and byte patterns against the original source before relying on them. Source keys like `{dn2-ele3}` resolve in [`hardware/SOURCES.md`](hardware/SOURCES.md); what was read and how deeply is in [`hardware/READING-LEDGER.md`](hardware/READING-LEDGER.md).

## Ground rules

- **Metadata only.** Names, links, status, short paraphrased notes. No Elektron firmware, no extracted sections, no built images, no binaries, no copied third-party code. Never commit a `.syx`.
- **Every entry has a source and a date.** Status words follow the authors' own wording; where sources disagree, the note says so.
- **Respect the communities.** Elektron does not allow firmware-mod links or files on Elektronauts (policy of 2026-09-16) - do not post there. Some projects reject AI-generated issues or pull requests; read each project's contribution rules first.
- **Not affiliated with Elektron.** Custom firmware can brick a unit and may affect warranty. This repo only points to projects; it does not endorse or test them.

## Updating the data

```bash
pip install pyyaml
# edit data/projects.yml (or move an entry from data/candidates.yml once checked)
python3 scripts/build.py      # regenerates INDEX.md and devices/*.md
```

Entry fields are documented at the top of `data/projects.yml`. To find out *what* needs updating, run `python3 scripts/check_updates.py` (or read `state/CHANGES.md`, written daily by the GitHub Action) - see [`docs/UPDATING.md`](docs/UPDATING.md). Generated files carry a marker - edit the YAML, not the Markdown.

## Status and scope

- **Phase 1 (in depth):** Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX: project catalogue plus the agent knowledge base in [`hardware/`](hardware/).
- **Phase 2 (catalogue, since 2026-11-01):** Octatrack, Analog Rytm, Analog Four/Keys, Model:Cycles, Model:Samples, Machinedrum, Monomachine: 45 projects imported from altstrument as facts with our own short notes, watched daily; repos not yet read, no hardware notes yet. Tonverk and non-Elektron gear: see [`docs/BACKLOG.md`](docs/BACKLOG.md).
- **Known gap:** no community firmware work exists for the Analog Heat yet; only official facts, Overbridge channel layout and tool support lists are collected.
- **Open reading list:** [`hardware/MINING.md`](hardware/MINING.md) (e.g. the MIDI appendices of the official manuals, which our tooling could not extract).

## Related directories

- [Awesome Music Gear Firmware](https://github.com/Lapin/awesome-music-gear-firmware) - curated link list across 19 brands (CC0)
- [altstrument](https://altstrument.org) / [repo](https://github.com/philmillman/altstrument) - structured directory of alternative firmware (CC-BY-4.0 data)
- [elektronmods.com](https://elektronmods.com) - community forum and GitHub mod list for Elektron devices

Aggregat differs from these by focusing on a few devices in depth: current version and OS per project, and an agent-readable hardware knowledge base.

## Licence

Everything in this repository - texts, data and scripts - is dedicated to the public domain under
[CC0 1.0 Universal](LICENSE). Use it for anything, no attribution required (a mention is welcome).
The linked projects are not part of this repository and keep their own licences; check those before
you reuse their code.
