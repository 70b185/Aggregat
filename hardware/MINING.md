# Reading list - what still has to be mined for hardware/

Ordered by expected value for an agent that builds mods. Tick off and fold the result into the matching device file.

## Digitone II (highest value)
- [x] complex-ping/digitone-2-modding-skill: SKILL.md + references/{setup,firmware,coldfire,sharc,emulators,workflow}.md (-> devices/digitone-2-os111-reference.md, common/agent-workflow.md); [x] examples, hwrules.py, script docstrings (git clone works where the tree page was blocked)
- [x] angellinares/dn2_firmware_explore: `docs/flashing.md` (-> common/flash-procedure.md); [ ] `docs/mainos-image.md`, `docs/ele3-format.md`
- [x] naturarum/dn2-cfw: `docs/parameter-table-growth.md` (-> devices/digitone-2.md); [ ] T1.4/T1.5 notes (flash-write audit, STARTUP independence), `tools/brickcheck` (the 12 checks)
- [x] De-Pattern/dn2mk2-firmware: `docs/SAFETY.md` (-> common/flash-procedure.md); [ ] `docs/emulator.md`, `docs/user-reports.md`, FIRMWARE.md v0.20 and older
- [ ] complex-ping/overtone: `docs/` and the patcher's ~160 checks
- [ ] nzimas/digirust: `docs/FEATURES.md` (Digitone II OS 1.12)

## Digitakt mk1 / Digitone mk1
- [ ] elekloader `docs/DEVICES.md` (maturity per device), `mods/core/mod.json` (all core-owned sites), `mods/core-dn1`
- [ ] machine-ID usage of digisophie, DT-FM, digigrain, digidrum, digistring (fill the registry in `devices/digitakt.md`)
- [ ] Digitone mk1 recovery buttons (not stated in anything we read)

## Digitakt II
- [ ] lalzart/digitakt-ii-firmware-research-public (architecture notes), lalzart/dt2-machine-lab
- [ ] karigardarsson/digitakt-ii-research: install and recovery docs

## Syntakt
- [ ] karigardarsson/Synthack-OS: `RECOVERY.md`, `patch.json` examples, protected-section list
- [ ] Syntakt container: signed or not? sections?

## Analog Heat
- [ ] Anything at all. Candidate first steps: check whether the elektron-firmware-tool README/issues mention Heat results; search Elektronauts-adjacent communities and GitHub topics for "analog heat" firmware; ask the user whether they own Heat OS files to inspect.

## Cross-checks
- [ ] altstrument.org device pages (Digitakt 12, Digitakt II 3, Digitone 5, Digitone II 3, Syntakt 4 firmwares listed) against `data/projects.yml`
- [ ] Lapin list: re-read weekly for new Elektron entries
- [x] Spot-check 2026-11-02: `scripts/factcheck_addresses.py` checked 997 hex addresses against the local clones of their cited sources: all found (2 are written-out range ends that the source abbreviates). Earlier run 2026-11-01: 117 on lines citing a locally cloned source verbatim in that source; sizes checked by hand (in-place margins, 2 MiB buffer, voice records, expansion region). Lines that cite only remote sources (READMEs, web pages) are not covered.

## Added 2026-10-31 (knowledge-source search)
- [ ] mzero/elk-herd: new home (README obfuscates the address) - the protocol reference several projects port from; respect its no-AI-issues rule
- [ ] xrcstrecords/syxgrid-digitone-ii `sysexmap/` in full (45 mappings with evidence) -> fold level-A mappings into `common/sysex-and-midi.md`
- [ ] zerubeus/dn-deobfuscator (`.dn2prj` project-file research); Elektronauts "Digitone 2 pattern manager" thread; emnyeca/digitone-syx-toolkit `docs/`
- [x] ElekLabs/digikit `docs/TOOLS.md` (-> common/toolchain-and-emulators.md); [ ] `docs/FINDINGS.md`, `docs/findings/*`, newest `HANDOVER-*.md`; naturarum/digikit and Bezronczek/digikit for divergences
- [ ] simonjohansson/elekloader `docs/DEVICES.md` and the Digitakt II / Digitone II core docs (control-side hook bus on DT2/DN2)
- [ ] Elektron manuals: MIDI implementation tables (CC/NRPN) for Digitakt II and Digitone II - official numbers instead of the MCP project's list
- [ ] Analog Heat +FX: manual (MIDI implementation, modulation matrix), Overbridge 2 USB protocol via Overwitch source; no teardown exists in what we found - ask whether anyone has opened one
- [ ] libanalogrytm `sysex.c` as the best-documented Elektron container/encoding reference (Rytm) to compare against Digitakt II dumps

## Blocked or skipped (2026-10-31)
- xrcstrecords/syxgrid-digitone-ii `sysexmap/` and complex-ping/digitone-2-modding-skill `skills/.../` tree pages: our fetcher is refused by the site's robots.txt (`robots_disallowed`). Not worked around. Options: the maintainer pastes the files, or the upstream authors publish them elsewhere.
- mzero/elk-herd new home: the README obfuscates the address on purpose and asks that AI-generated issues/PRs are not sent; not decoded, not contacted.
- [ ] naturarum/dn2-cfw: `ROADMAP.md`, `HANDOFF.md`, `notes/` (addresses with [verified]/[inferred]), `analysis/` (RTTI class hierarchy), `tools/brickcheck` source (the 12 checks)
- [ ] karigardarsson/digitakt-ii-research: `docs/INSTALLATION.md`, `docs/RECOVERY.md`, `research/` (byte-backed findings), `coldfire/` trampoline and startup-allocation source, `tools/midisniff.py`
- [ ] Cross-check the two Digitakt II routes: digitakt-ii-research (trampoline + startup allocation, 1.16/1.17) vs. dt2-machine-lab (profile dt2-1.16) vs. elekloader fork (core, 1.17)
- [ ] Verify the skill's OS 1.11 addresses against 1.12 (Overtone, dn2-cfw use 1.12: parameter table `0x401f83a4`, `pg_boot` call `0x40000568`) - build an address-translation note once both sets are confirmed
- [ ] Resolve the CPU naming discrepancy: skill says MCF5445x, digikit says MCF54415 (and coldfire-rs covers MCF5441x)

## Needs approval / not retried (2026-10-31)
- [~] elektron.se support pages: Digitakt II and Digitone II read; Analog Heat +FX at `https://www.elektron.se/en/download-support-analog-heat-fx`, Digitakt II, Digitone II) and the +FX explorer/spec page - for current OS dates, manual links (MIDI implementation tables, OS upgrade steps), FAQ answers. The fetch was blocked on a permission prompt nobody answered; retry when the user is present.
- [x] Remaining characters of elektronmods thread 27 (nothing new).
- [ ] Elektronauts "Digitone 2 pattern manager" and "Introducing Digitakt II / Analog Heat +FX" threads for hardware chatter on the Heat +FX (the +FX thread is at `elektronauts.com/t/introducing-analog-heat-fx/193814`).
- [~] Official manuals (PDF) for Digitakt II OS 1.17 and Digitone II OS 1.12: first ~95,000 characters read; **appendix B/C (CC/NRPN tables) and the startup-menu chapter are beyond what the fetch tool extracts** - needs the PDF attached to a chat or a local text extraction.
- [ ] Analog Heat +FX manual (URL truncated in a forum post: `cdn.www.elektron.se/media/downl...230510.pdf`).
- [ ] dn2-cfw `notes/` beyond T1.7, T2.2 and the release history; dnfw `docs/` beyond flashing, ele3-format, mainos-image, bootstrap, memory-map, os-versions.

## Next from the 2026-10-31 clones (not yet read)
- [x] digikit `MIDI-SYSEX-RPC.md`, `ARCHITECTURE.md`, `SHARC-ADDRESS-MAP.md`, `SAMPLES.md`; findings 14, 16, 25, 45, 47, 48, 51, 53, 57, 60, 73, 76, 77, 91, 100
- [x] digikit findings 01, 03, 04, 09, 15, 19, 31, 41, 46, 52, 58, 78, 101-103
- [ ] digikit findings still unread: 02, 05, 10-13, 17, 20-24, 26-30, 32-40, 42-44 (partly), 49, 50, 54-56, 61-69, 71, 72, 74 (mostly emulator/runtime internals)
- [x] dnfw docs: hardware, PRINCIPLES, mod-memory-regions, code-caves, version-gate, os-update-path, service-commands, mods-compatibility, sharc-load/-cycle-model/-stall-probe/-ddr, waverider-dsp-silence
- [x] dnfw midi-rpc, usbprobe, audio-dma, dsp-control-block, sharc-voice-path, dt2-machine-port, lalzart-dt2-crosscheck
- [ ] dnfw docs still unread: the waverider-* series, lfo4-*, flashing.md (43 KB), bootstrap (partly)
- [x] Digiwerk DEVELOPERS.md, notes T1.3, T1.4, T1.5, OB01, T1.11, DT01, DC01/DC02, SC01, SP02, release 0.2.1
- [x] Digiwerk USB01, T1.7/T1.7b, T2.1, T2.4a-c, T3.2, T3.3, prior-art-2026-10
- [ ] Digiwerk notes still unread: T2.2 arp, T2.8 dejavu, T3.1/T3.4-T3.11, T5.x/T6.x effect notes
- [ ] Overtone v1.2 release notes

