# Aggregat

**A metadata index and agent knowledge base for unofficial firmware and tooling on Elektron's small boxes** - Digitakt (MKI/II), Digitone (MKI/Keys/II), Syntakt and Analog Heat (MKI/MKII/+FX).

> **Deutsch, kurz:** Dieses Repo sammelt *nur Metadaten* zu Community-Projekten rund um Elektron-Firmware: wo liegt welches Projekt, für welches Gerät und welche OS-Version, und wie ist der aktuelle Stand. Dazu kommt mit [`hardware/`](hardware/) eine Wissensbasis, die KI-Agenten beim Entwickeln lesen sollen, statt jedes Mal alle Repos zu durchsuchen. Es enthält keine Firmware, keine Binärdateien und keinen fremden Code.

---

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
| [`scripts/build.py`](scripts/build.py) | Regenerates `INDEX.md` and `devices/*.md` from `data/` | maintainers |

Snapshot (2026-10-31): 63 verified project entries, 2 unverified candidates, 6 devices; `hardware/` holds about 23 files with ~30,000 words drawn from more than 40 repositories, two directories, official release notes and forum threads.

## Using it with an AI agent

Point the agent at this repo and tell it to read, in this order:

1. [`hardware/README.md`](hardware/README.md) - the ten things to know first
2. [`hardware/AGENT-RULES.md`](hardware/AGENT-RULES.md) - safety, legal, process and coding rules
3. [`hardware/common/recovery.md`](hardware/common/recovery.md) and [`hardware/common/flash-procedure.md`](hardware/common/flash-procedure.md)
4. the device file under [`hardware/devices/`](hardware/devices/)
5. [`INDEX.md`](INDEX.md) / [`devices/`](devices/) to find the project it builds on

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

- **Phase 1 (now):** Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX.
- **Phase 2 (later):** Octatrack, Analog Four/Rytm/Keys, Model:Cycles/Samples, Tonverk, Machinedrum/Monomachine - candidates are listed in [`docs/BACKLOG.md`](docs/BACKLOG.md).
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
