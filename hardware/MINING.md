# Reading list - what still has to be mined for hardware/

Marks: `[x]` done, `[~]` partly, `[ ]` open (worth reading), `[!]` blocked - needs a person (a PDF, a forum login, a unit), `[-]` deliberately not pursued, `[->]` moved to [RESEARCH-MAP.md](../RESEARCH-MAP.md) as a research task. Status 2026-11-02: every project in the catalogue has at least been scanned; what remains open below is depth, not coverage.

Ordered by expected value for an agent that builds mods. Tick off and fold the result into the matching device file.

## Digitone II (highest value)
- [x] complex-ping/digitone-2-modding-skill: SKILL.md + references/{setup,firmware,coldfire,sharc,emulators,workflow}.md (-> devices/digitone-2-os111-reference.md, common/agent-workflow.md); [x] examples, hwrules.py, script docstrings (git clone works where the tree page was blocked)
- [x] angellinares/dn2_firmware_explore: `docs/flashing.md` (-> common/flash-procedure.md); [x] `docs/mainos-image.md`, `docs/ele3-format.md` (keys dn2-ele3, dn2-memory-map)
- [x] naturarum/dn2-cfw: `docs/parameter-table-growth.md` (-> devices/digitone-2.md); [x] T1.4/T1.5 notes (-> common/recovery.md), T1.7 brickcheck note; [ ] the brickcheck tool source
- [x] De-Pattern/dn2mk2-firmware: `docs/SAFETY.md` (-> common/flash-procedure.md); [x] `docs/emulator.md`, `docs/user-reports.md`, `docs/dsp-time.md`, `docs/dsp-cost.md`; [ ] FIRMWARE.md v0.20 and older
- [x] complex-ping/overtone README (the repo publishes no further docs; the ~160 checks are not public) (-> recovery, B7)
- [x] nzimas/digirust: `docs/FEATURES.md` and `docs/VALIDATION.md` read 2026-11-02: generators, Control All macros, drone latch; hardware evidence is a developer statement (12 Oct 2026); nothing for hardware/

## Digitakt mk1 / Digitone mk1
- [x] elekloader `docs/DEVICES.md` (-> common/memory-maps.md, key elekloader-devices); [ ] `mods/core/mod.json` (all core-owned sites), `mods/core-dn1`
- [x] machine-ID registry in `devices/digitakt.md`: ids 4, 5, 6, 7, 9, 10, 27, 69, 77 (digistring is not a machine; digidrum unreachable)
- [x] Digitone mk1 recovery buttons: FUNC + TRIG 4 over DIN, used on a unit (digitone-arp-mod) -> devices/digitone.md

## Digitakt II
- [x] lalzart/digitakt-ii-firmware-research-public (architecture notes) (-> devices/digitakt-2.md); [x] lalzart/dt2-machine-lab (README, COLDFIRE-FIX, UPLOAD-PREFLIGHT head, FLEX-DSP-MEMORY-INVESTIGATION 1-2 and 7; the ~160 other docs are recorder/BUF feature work)
- [x] karigardarsson/digitakt-ii-research: RECOVERY.md, KNOWN_LIMITATIONS.md (-> RESEARCH-MAP DT2 recovery row; the route is Elektron's official one)

## Syntakt
- [x] karigardarsson/Synthack-OS `RECOVERY.md` (already in devices/syntakt.md); [x] mods README, modarea, kitstore, projstore, master-comp (-> devices/syntakt.md, S13)
- [~] Syntakt container: sections known (SyntHack, digikit f70); signing still conflict O1 (needs a file-level check, research map T5)

## Analog Heat
- [x] (2026-11-02) The only public Heat firmware knowledge is the owner's +FX research (devices/analog-heat.md); the daily search finds no Heat firmware project. Original note: Candidate first steps: check whether the elektron-firmware-tool README/issues mention Heat results; search Elektronauts-adjacent communities and GitHub topics for "analog heat" firmware; ask the user whether they own Heat OS files to inspect.

## Cross-checks
- [x] altstrument.org device pages cross-checked (phase-2 import 2026-11-01 and the daily fingerprint check)
- [ ] Lapin list: re-read weekly for new Elektron entries
- [x] Spot-check 2026-11-02: `scripts/factcheck_addresses.py` checked 997 hex addresses against the local clones of their cited sources: all found (2 are written-out range ends that the source abbreviates). Earlier run 2026-11-01: 117 on lines citing a locally cloned source verbatim in that source; sizes checked by hand (in-place margins, 2 MiB buffer, voice records, expansion region). Lines that cite only remote sources (READMEs, web pages) are not covered.

## Added 2026-10-31 (knowledge-source search)
- [-] **Deliberately not pursued:** mzero/elk-herd: new home (README obfuscates the address) - the protocol reference several projects port from; respect its no-AI-issues rule
- [x] xrcstrecords/syxgrid-digitone-ii `sysexmap/` (read via git clone; the 23 level-A mappings -> common/sysex-and-midi.md)
- [-] zerubeus/dn-deobfuscator is unreachable (catalogue status); emnyeca/digitone-syx-toolkit scanned in the phase-1 sweep. Remaining: Elektronauts "Digitone 2 pattern manager" thread; emnyeca/digitone-syx-toolkit `docs/`
- [x] ElekLabs/digikit `docs/TOOLS.md` (-> common/toolchain-and-emulators.md); [ ] `docs/FINDINGS.md`, `docs/findings/*`, newest `HANDOVER-*.md`; naturarum/digikit and Bezronczek/digikit for divergences
- [x] (2026-11-02: the fork is a mirror of elekloader 0.9.0, `DEVICES.md` identical to upstream; elekloader's SHARC-BOOT, SHARC-DN2-ABI and MACHINES-DN2-VOICE/FILTER mined into firmware-container.md and digitone-2-machines-sampler-sharc.md) simonjohansson/elekloader `docs/DEVICES.md` and the Digitakt II / Digitone II core docs (control-side hook bus on DT2/DN2)
- [!] **Needs a person with the PDF** (research map T13): Elektron manuals: MIDI implementation tables (CC/NRPN) for Digitakt II and Digitone II - official numbers instead of the MCP project's list
- [!] **Needs a person with the PDF or a unit** (T13): Analog Heat +FX: manual (MIDI implementation, modulation matrix), Overbridge 2 USB protocol via Overwitch source; no teardown exists in what we found - ask whether anyone has opened one
- [->] moved to RESEARCH-MAP T22: libanalogrytm `sysex.c` as the best-documented Elektron container/encoding reference (Rytm) to compare against Digitakt II dumps

## Blocked or skipped (2026-10-31)
- xrcstrecords/syxgrid-digitone-ii `sysexmap/` and complex-ping/digitone-2-modding-skill `skills/.../` tree pages: our fetcher is refused by the site's robots.txt (`robots_disallowed`). Not worked around. Options: the maintainer pastes the files, or the upstream authors publish them elsewhere.
- mzero/elk-herd new home: the README obfuscates the address on purpose and asks that AI-generated issues/PRs are not sent; not decoded, not contacted.
- [x] naturarum/dn2-cfw `ROADMAP.md`, `HANDOFF.md` (keys dn2-cfw-roadmap, -handoff); [ ] `notes/` (addresses with [verified]/[inferred]), `analysis/` (RTTI class hierarchy), `tools/brickcheck` source (the 12 checks)
- [x] karigardarsson/digitakt-ii-research `docs/RECOVERY.md`, KNOWN_LIMITATIONS; [x] `research/` (heap, startup hook, hook ABI -> devices/digitakt-2.md); [ ] `docs/INSTALLATION.md`, `coldfire/` source, `tools/midisniff.py`
- [->] moved to RESEARCH-MAP T21: Cross-check the two Digitakt II routes: digitakt-ii-research (trampoline + startup allocation, 1.16/1.17) vs. dt2-machine-lab (profile dt2-1.16) vs. elekloader fork (core, 1.17)
- [->] moved to RESEARCH-MAP T8: Verify the skill's OS 1.11 addresses against 1.12 (Overtone, dn2-cfw use 1.12: parameter table `0x401f83a4`, `pg_boot` call `0x40000568`) - build an address-translation note once both sets are confirmed
- [x] CPU naming for DN2: settled as MCF5441x (CONFLICTS S3); the Rytm MKII naming is still open (O14)

## Needs approval / not retried (2026-10-31)
- [~] elektron.se support pages: Digitakt II and Digitone II read; Analog Heat +FX at `https://www.elektron.se/en/download-support-analog-heat-fx`, Digitakt II, Digitone II) and the +FX explorer/spec page - for current OS dates, manual links (MIDI implementation tables, OS upgrade steps), FAQ answers. The fetch was blocked on a permission prompt nobody answered; retry when the user is present.
- [x] Remaining characters of elektronmods thread 27 (nothing new).
- [!] Forum reading (Elektronauts pages load only partly for our fetcher): Elektronauts "Digitone 2 pattern manager" and "Introducing Digitakt II / Analog Heat +FX" threads for hardware chatter on the Heat +FX (the +FX thread is at `elektronauts.com/t/introducing-analog-heat-fx/193814`).
- [~] Official manuals (PDF) for Digitakt II OS 1.17 and Digitone II OS 1.12: first ~95,000 characters read; **appendix B/C (CC/NRPN tables) and the startup-menu chapter are beyond what the fetch tool extracts** - needs the PDF attached to a chat or a local text extraction.
- [!] Analog Heat +FX manual (URL truncated in a forum post: `cdn.www.elektron.se/media/downl...230510.pdf`). Search 2026-11-02 found no reachable copy: **needs the PDF from someone** (research map T13).
- [~] dn2-cfw `notes/` beyond T1.7, T2.2 and the release history; dnfw `docs/` beyond flashing, ele3-format, mainos-image, bootstrap, memory-map, os-versions. 2026-11-02: dnfw dn1-dsp-comparison (superseded on DN2, CONFLICTS S16), sharc-accelerators/-plan, coldfire-tasks, old-project-load mined into digitone-2-internals.md; dn2-cfw overlap-dnfw and T2.8 (Deja Vu on DN2, already in FEATURE-OVERLAP) read. Still unread: the waverider-*/lfo4-* design series, sharc-selache, T3.1/T3.6, T5.5/T5.6, T6.4

## Next from the 2026-10-31 clones (not yet read)
- [x] digikit `MIDI-SYSEX-RPC.md`, `ARCHITECTURE.md`, `SHARC-ADDRESS-MAP.md`, `SAMPLES.md`; findings 14, 16, 25, 45, 47, 48, 51, 53, 57, 60, 73, 76, 77, 91, 100
- [x] digikit findings 01, 03, 04, 09, 15, 19, 31, 41, 46, 52, 58, 78, 101-103
- [x] digikit findings 37 (exception handler), 42, 49 (rung C), 59, 72 read 2026-11-02; [ ] still unread, scanned as emulator/runtime internals: 02, 05, 10-13, 17, 20-24, 26-30, 32-36, 38-40, 43-44, 50, 54-56, 61-69, 71, 74
- [x] dnfw docs: hardware, PRINCIPLES, mod-memory-regions, code-caves, version-gate, os-update-path, service-commands, mods-compatibility, sharc-load/-cycle-model/-stall-probe/-ddr, waverider-dsp-silence
- [x] dnfw midi-rpc, usbprobe, audio-dma, dsp-control-block, sharc-voice-path, dt2-machine-port, lalzart-dt2-crosscheck
- [x] dnfw waverider-performance and waverider-loadmap (unit load calibration, per-stage meter); waverider-dsp-silence earlier (S9); [ ] the rest of the waverider-* and lfo4-* series (feature design), flashing.md beyond the procedure
- [x] Digiwerk DEVELOPERS.md, notes T1.3, T1.4, T1.5, OB01, T1.11, DT01, DC01/DC02, SC01, SP02, release 0.2.1
- [x] Digiwerk USB01, T1.7/T1.7b, T2.1, T2.4a-c, T3.2, T3.3, prior-art-2026-10
- [x] Digiwerk T3.8 (DSP splice: 'nothing ran on the unit', encoding audit), T5.3, T6.3 cmp2f/cmp4 (code only where it ran on the unit), T6.5, PB01 scanned/read; [ ] T2.x arp, T2.8 dejavu, T3.1/T3.4-T3.6, T5.5/T5.6 effect design
- [x] Overtone: README and release notes v1.0-v1.2 read 2026-11-02 (v1.2 instant pattern switch, v1.1 GROOVE rework, v1.0.1 Transfer-install fix; no technical causes given)

## Phase-1 sweep of the remaining 51 projects (2026-11-02)
All 48 reachable repos cloned; their docs scanned for unit results, measurements, crashes and recovery, then read where it paid off.
- [x] Mined: digitone-arp-mod (DN1 recovery used on a unit, A42 second case, startup caches), taktone (DN1 board, second ColdFire, FPGA, SysEx addressing), RingTone/Tone+FX (DN1 load lessons), emu-elektron (Unicorn bugs), digitakt-sidecar (DT1 Overbridge stream), digigrain (DT1 render path and tables), machine ids for the DT1 registry (digigrain, reslicer, vawt, sayit, elektrob-1, Vampire Manga OS).
- [x] Scanned, nothing new for hardware/: the elekloader DN1 effect mods (digihalo, digitriad, digitide, digihoard, digireel: "tested on a Digitone mk1 by its author"), digi-macro (emulator only), elektron-mods-rumorismo (setup), keyframer-lab (web tool), digitone-syx-toolkit, the small DT1/DN1 mods, splash screens.
- [ ] Deeper reads that could still pay: digigrain's nine other skills (hook bus, recorder, audio input, testing), [x] taktone-extended DEVELOPMENT/MACHINE-DEVELOPMENT (-> digitone.md), elektrob-1 `docs/dsp.md` (sound model only), digigrain skills (-> toolchain ColdFire C notes); [ ] digitone-arp-mod's ~100 other reviews (arp internals).

## Phase-2 sweep of 57 more projects (2026-11-02)
All cloned and scanned like the phase-1 sweep.
- [x] Mined: kitbasher FIRMWARE-SAFETY (Machinedrum failure register), rytm-mods-src HAZARDS and compressor notes, analog-rytm-mkii-research (hardware profile, BR characterization), rytm1_mods HAZARDS (MK1 vs MKII data), octatrack-kyoti-fw (load ceiling, memory map), octamax (CF-card logging, DSP feeding), Supermodel notes 23 and 35 (Model:Cycles load and USB).
- [x] Scanned, nothing new for hardware/: octa-panel and passos (octabam forks, same trap register), model27 and cycles-mod-standard (read earlier), model-tg, cycles-one-shot, model-machinedrum, plaits-on-models, spokes, the emulator ports (MModule, Machinemodule, Monomodule ports, OP-XY), the small Octatrack tools.
- [x] Supermodel notes 30, 36, 211, 217 (load governor, EMAC wrapper cost, worst-block profiling) read 2026-11-02; the other ~200 are feature logs. [ ] Could still pay: [x] KYOTI caves.md, techniques.md, NOTES DSP quirks; [ ] KYOTI handoffs, [x] MModule's DSP-memory research (-> machinedrum-monomachine.md).

