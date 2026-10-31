# Reading list - what still has to be mined for hardware/

Ordered by expected value for an agent that builds mods. Tick off and fold the result into the matching device file.

## Digitone II (highest value)
- [x] complex-ping/digitone-2-modding-skill: SKILL.md + references/{setup,firmware,coldfire,sharc,emulators,workflow}.md (-> devices/digitone-2-os111-reference.md, common/agent-workflow.md); [ ] `examples/` code, `scripts/hwrules.py` source, THIRD-PARTY.md
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
- [ ] Hardware facts above were extracted from READMEs by summarising tools; spot-check numbers (addresses, sizes) against the original files before depending on them.

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

