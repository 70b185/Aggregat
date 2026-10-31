# Reading ledger - what was read, how deep, and what was blocked

Updated as the "read everything" pass proceeds (started 2026-10-31; paused when an elektron.se fetch needed an approval nobody answered). Depth: **full** = whole page/file read through the fetch tool (the tool summarises long pages, so very long files may be cut); **index** = only a table of contents or listing was available; **blocked** = refused by robots.txt or unreachable (not worked around).

| Source | Depth | Folded into |
|---|---|---|
| altstrument.org: Digitakt, Digitakt II, Digitone, Digitone II, Syntakt, Elektron tools pages | full | data/projects.yml (`latest_seen`, new entries) |
| elektronmods.com mods.php (59 entries), device filters 2, 5, 9, 86, recent changes | full | data/projects.yml, devices/analog-heat.md |
| elektronmods mods.php?id=39 (DNX) | full | data/projects.yml |
| elekloader/elekloader README + releases page (first 10 releases) | full / first 10 | data/projects.yml (elekloader) |
| xerydian/elektron-emu, Angelo-politek/Synthack-OS, Humgic/syntakt-machine45-research READMEs | full | data/projects.yml |
| dnfw `docs/mainos-image.md`, `docs/ele3-format.md` | full | common/firmware-container.md, devices/digitone-2-internals.md |
| dn2-cfw `ROADMAP.md`, `HANDOFF.md` (part dated 2026-10-06), `FIRMWARE.md` | full / part | devices/digitone-2-internals.md |
| ElekLabs/digikit `docs/FINDINGS.md` | index (findings 01-51 are separate files, not read) | devices/digitone-2-internals.md |
| nzimas/digirust README + `docs/FEATURES.md` | full | devices/digitone-2-internals.md |
| digitone-2-modding-skill SKILL.md + 6 references | full | devices/digitone-2-os111-reference.md, common/agent-workflow.md |
| De-Pattern dn2mk2 `docs/SAFETY.md`, README, `FIRMWARE.md` (up to v0.20) | full / part | common/flash-procedure.md |
| angellinares dnfw `docs/flashing.md` | full | common/flash-procedure.md |
| naturarum `docs/parameter-table-growth.md` | full | devices/digitone-2.md |
| xrcstrecords/syxgrid-digitone-ii `sysexmap/` tree page | **blocked (robots.txt)** | - |
| digitone-2-modding-skill `/tree/main` pages | **blocked (robots.txt)**; blob pages worked | - |
| naturarum/dn2-cfw `/tree/main#install` | **blocked (robots.txt)**; repo root worked | - |
| mzero/elk-herd new home | skipped on purpose (address obfuscated by the author) | - |
| dn2mk2 `docs/emulator.md`, `docs/sampler.md`, `docs/user-reports.md` (report CSV "B01-B19" not included), `docs/CHANGES-FROM-UPSTREAM.md`, `FIRMWARE.md` table v0.1-v0.20 | full | devices/digitone-2-machines-sampler-sharc.md |
| elekloader `docs/DEVICES.md`, `docs/MACHINES-DN2.md`, `docs/SHARC-DN2.md` | full | common/memory-maps.md, devices/digitone-2-machines-sampler-sharc.md |
| elekloader repo-root `AGENTS.md`, `docs/CORES.md`, `docs/FORMAT.md`, `docs/BUILDING.md` | full | common/agent-workflow.md, common/recovery.md, devices/digitakt-2.md |
| digitakt-ii-research `docs/RECOVERY.md`, `docs/INSTALLATION.md` | full | common/recovery.md, devices/digitakt-2.md |
| SyntHack OS `RECOVERY.md`; syntakt-machine45-research handoff | full | common/recovery.md, devices/syntakt.md |
| dagargo/overwitch README, dagargo/elektroid README | full (no USB protocol tables in either) | common/overbridge-usb.md, common/sysex-and-midi.md |
| digiemu, digislicer, DigiFilter, Tone-FX, digi1_mods, digisophie, DigiPrism, DigiSwarm READMEs; SY FM4 README; elektronmods DigiPools entry | full (READMEs only; their `docs/` and CHANGELOG files not opened) | devices/digitakt.md, devices/digitone.md, devices/syntakt.md |
| elektronmods threads 25, 27 (first 100,000 of 116,789 characters), 8; Dubspot article; Elektronauts policy post and DT2 teardown thread; Elektron-manual and Heat +FX web searches (snippets only) | full / partial / snippets | common/ecosystem-lessons.md, devices/analog-heat.md, common/sysex-and-midi.md |
| elektron.se support pages for Analog Heat +FX, Digitakt II, Digitone II and the +FX explorer page | **not read - the fetch needed an approval nobody answered (2026-10-31); not retried** | - |
| Lapin list beyond the Elektron section, altstrument pages of non-Elektron brands, Elektron Octatrack/Rytm/Four/Model projects | out of phase-1 scope, not read in detail | - |
| ElekLabs/digikit `docs/findings/01-51`, dn2-cfw `notes/`, `analysis/`, `docs/`, dnfw other docs, Overtone `docs/`, elekloader `docs/ADAPTING.md` update, DigiAlchemy CHANGELOGs, mod `docs/` folders | **not read yet** (README/index level only) | - |

