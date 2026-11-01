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
| elektron.se support pages Digitakt II and Digitone II | full (second attempt) | devices/digitakt-2.md, devices/digitone-2.md, common/recovery.md |
| elektron.se Analog Heat +FX support and explorer pages | **site error (client_error) on the second attempt**; unread | - |
| Lapin list beyond the Elektron section, altstrument pages of non-Elektron brands, Elektron Octatrack/Rytm/Four/Model projects | out of phase-1 scope, not read in detail | - |
| ElekLabs/digikit `docs/findings/01-51`, dn2-cfw `notes/`, `analysis/`, `docs/`, dnfw other docs, Overtone `docs/`, elekloader `docs/ADAPTING.md` update, DigiAlchemy CHANGELOGs, mod `docs/` folders | **not read yet** (README/index level only) | - |
| dnfw `docs/bootstrap.md`, `docs/memory-map.md`, `docs/os-versions.md`; dn2-cfw `notes/dn2-release-history.md`, `notes/T1.7-redteam.md`, `notes/T2.2-arp-midi-v2.md` | full | devices/digitone-2-internals.md, common/agent-workflow.md, AGENT-RULES |
| elekloader `docs/ADAPTING.md` (current, both parts) | full (second part only covers Octatrack USB) | AGENT-RULES D10b |
| elektronmods thread 27 remainder (offset 100000) | full (no further content) | - |
| Digitone II manual (OS 1.12) and Digitakt II manual (OS 1.17), PDF | **partial** - text extraction yields ~95,000 characters and stops before the startup-menu chapter and the MIDI appendices | devices/digitone-2.md, devices/digitakt-2.md |
| Analog Heat +FX manual | not found by URL (a forum post shows a truncated CDN link); KVR/Equipboard snippets only | devices/analog-heat.md |
| digitone-2-modding-skill **full git clone**: references/*.md raw, all scripts' docstrings, hwrules.py and bootblocks.py in full, examples | full (emulator sources sim.py/simc_core.c/emu.py not read line by line) | devices/digitone-2-os111-firmware-map.md |


## Pass 2026-10-31 (developer docs, from git clones)
| Source | Depth | Folded into |
|---|---|---|
| digikit findings 70 (Syntakt 1.42), 75 (OS upgrade receive path) | full | devices/syntakt.md, common/os-update-protocol.md, common/firmware-container.md, A22, A23 |
| digikit findings 08 (hardware/Ghidra), 42 (USB routes), 59 (card regions) | sections on platform, USB, card | common/memory-maps.md, common/overbridge-usb.md, A24 |
| digikit AGENTS.md | full | common/agent-workflow.md |
| owner's private DT2 DSP notes (device findings in full; state, long-sample and load notes; firmware facts) | full / sections | devices/digitakt-2-sharc-measured.md, A25, A26 |
| owner's private Heat +FX research notes (device facts, research, test log, environment, status) | full | devices/analog-heat.md, common/memory-maps.md, common/firmware-container.md, A27 |
| digikit `docs/MIDI-SYSEX-RPC.md`, `SHARC-ADDRESS-MAP.md`, `ARCHITECTURE.md`, `SAMPLES.md` | full / key sections | sysex-and-midi, machines-sampler-sharc, agent-workflow, memory-maps |
| digikit findings 45, 47, 48, 51, 53, 57, 60, 73, 76, 77, 91, 100 | results and key sections | digitakt-2, dt2-dn2-limits-and-audio-chain, A28, A29 |
| Digiwerk notes T1.3, T1.4, T1.5, OB01, DT01, DC01/DC02, SC01, release 0.2.1 | answers and key sections | recovery, overbridge-usb, digitone-2-internals, A30 |
| dnfw docs: PRINCIPLES, hardware, code-caves, mod-memory-regions, os-update-path, version-gate, sharc-load, sharc-cycle-model, sharc-stall-probe, sharc-ddr, waverider-dsp-silence, for-digikit-waverider-dsp-stop | full / key sections | digitone-2, memory-maps, os-update-protocol, machines-sampler-sharc, A31, A32 |
| digikit findings 14, 16, 25; dnfw service-commands, mods-compatibility | key sections | sysex-and-midi, agent-workflow |
| Digiwerk notes T1.7, T1.7b, T2.1, T2.4a-c, T3.2, T3.3, USB01, prior-art-2026-10 | answers and key sections | agent-workflow (brick checker), digitone-2-internals, digitakt, digitone |
| karigardarsson/digitakt-ii-research: research/*.md, PLAITS OPTIMIZING.md and HARDWARE-TEST.md (headings + key entries), VALIDATION, KNOWN_LIMITATIONS | full / key sections | digitakt-2, digitakt-2-dsp-optimizing, A33 |
| Angelo-politek/Synthack-OS docs (memory-map, firmware-format, audio-path, emulation, modding-guide), README, RECOVERY; SY FM4 DESIGN; machine45 DSP_ABI; syntakt-firmware-workbench README | full | devices/syntakt, A34 |
| digikit findings 78, 101, 102, 103 (new 2026-11-01); dnfw AGENTS.md, audio-dma, dsp-control-block, sharc-voice-path, lalzart-dt2-crosscheck, midi-rpc, usbprobe, dt2-machine-port | full / key sections | digitakt-2-dsp-optimizing, digitone-2-internals, sysex-and-midi, A35 |
| digikit findings 01, 03, 04, 09, 15, 19, 31, 41, 46, 52, 58 | headings + key sections | digitakt-2-sharc-measured, sysex-and-midi, memory-maps |
| SynCrackd MEMORY_MAP + README; Synfact README + transfer readme | full / key sections | devices/syntakt (CPU #2) |
