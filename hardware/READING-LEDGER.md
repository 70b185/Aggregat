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
| octabam docs (CHIP, ARCHITECTURE, PLACEMENT, TRAPS headings, guide/BUILDING); Modded-Cycles (RECOVERY, os-map, free-space, notes heads); rytm-fw-re (STATUS, flash-driver, usb-reflash) | key sections | devices/octatrack, devices/model-cycles-samples, devices/analog-rytm, A36, CONFLICTS O8 |
| elekloader SHARC-DN2 "The DSP peek", ADAPTING (DSP peek, selache pitfalls), dspbusy-dn2 README (new 2026-11-02) | key sections | digitone-2-internals, toolchain, A37 |
| hugz202 A4 mods (HAZARDS, FLASHING, digital-path findings, README); analog-emu A4-PORT (1-3, 11-14), MK1-PORT (summary, 5); analoghealth README | full / key sections | devices/analog-four-keys, A38 |
| machinedrum-kit docs 01, 05, 08 (timing, slot floor), 13 (toolchain, arithmetic), 16 (emulator limits), 02 (DSP1/P:0x400); em's MD/MnM READMEs + CHANGELOG head; Monomodule README | key sections | devices/machinedrum-monomachine, A38 |
| hugz202 Rytm MK1 mods: HAZARDS, MANUAL (0011 CPU probe), re/fx-engine, re/hidden-machines, 0010 design head | full / key sections | devices/analog-rytm (MK1), A38, O14 |
| octabam TRAPS (assembler, rep/DMA, r7 scratch, init r1, window clear, host mask, write-watch, EP0) and FAILURE_MODES headings; Modwerk OCTATRACK_HARDWARE_TRAPS (USB and EP0, RAM boot, NOR over USB, load, cold starts) | key sections | devices/octatrack, A39-A41 |
| Digiwerk notes T6.5 (table growth on the unit), T5.3 (tape echo), PB01 (DSP memory candidates), ROADMAP (SC01 L2 stop, CMP2 forbidden range, load targets); dn2mk2 user-reports (v0.26-v0.30), dsp-time, dsp-cost; digitakt-ii-research RECOVERY, KNOWN_LIMITATIONS; lalzart DT2 architecture (README + 6 architecture docs) | key sections | digitone-2, digitone-2-internals, digitone-2-machines-sampler-sharc, digitakt-2, O15, RESEARCH-MAP |
| lalzart dt2-machine-lab: README, STATUS head, COLDFIRE-FIX, UPLOAD-PREFLIGHT head, FLEX-DSP-MEMORY-INVESTIGATION (answer, memory map, estimates) | key sections | digitakt-2 (recovery used, memory map), recovery, A42, RESEARCH-MAP |
| SyntHack mods/README, modarea, kitstore, projstore, master-comp; digikit finding 42 (USB EP0), 59 (storage regions, already folded earlier) | key sections | devices/syntakt, S13, A39 note, RESEARCH-MAP |
| Overtone README (DSP load, install, recovery, compatibility, limits, testing) | full | recovery, B7 |
| digikit finding 72 (stock SHARC kernels, idioms, own vs stock), finding 53 line on unchanged DSP images | key sections | digitakt-2-dsp-optimizing, RESEARCH-MAP G5 |
| Phase-1 sweep: digitone-arp-mod (E04 incident, recovery plan, instruction review, cache assessment), taktone (README, recovery, changelog, ARCHITECTURE, SECONDARY-CPU), RingTone (DSP, AGENTS, CHANGELOG, CPU-OPT-PLAN, OPTIMIZATION-ROUND), emu-elektron patches README, digitakt-sidecar H01, digigrain skills (firmware-map) and CLAUDE.md; 40 more scanned | key sections / scan | digitone, digitakt, toolchain, overbridge-usb, recovery, A34, A42, RESEARCH-MAP |
| Phase-2 sweep: kitbasher FIRMWARE-SAFETY; rytm-mods-src HAZARDS + compressor-hardware; analog-rytm-mkii-research (3 docs); rytm1_mods HAZARDS; KYOTI memory-map + LOAD_AUDIT; octamax HOTCHANGE_FINDINGS + NOTES excerpt; Supermodel notes 23, 35; 49 more scanned | key sections / scan | machinedrum-monomachine, analog-rytm, octatrack, model-cycles-samples, A29, A42, A43 |
| Supermodel notes 30, 36 (load governor), 211 (EMAC/reverb comparisons), 217 (worst-block profiling) | full | model-cycles-samples, A44 |

## Pass 2026-11-06 (working-state and sampler UI lifecycle)
| Source | Depth | Folded into |
|---|---|---|
| armio `docs/research/2026-11-06-autosave.md`, `releases/r022.json`, and sampler-fixes helpers `r021_source_route.py` / `r022_sample_mirror.py` | full research note and helpers; native replay results reported by the source, no independent hardware test | digitone-2, I51-I52, C8, E5; R022 candidate listing with R012 stable retained |

## Pass 2026-11-08 (change report: digikit, modwerk, rytm-mods-src, model27 copy)
| Source | Depth | Folded into |
|---|---|---|
| digikit findings 116 and 117, `docs/DEVELOPMENT.md` "Boot screens", `devices/fw/rtos.toml` and `draw.toml` diffs, port anchors for DT2 1.17 / DN2 1.11 / 1.12 (af0ef08) | full | devices/digitakt-2, devices/digitone-2, CONFLICTS O20, INCIDENTS I53/I54, A29, C10, D13, common/agent-workflow, FEATURE-OVERLAP, projects.yml |
| modwerk `docs/verification/2026-11-08-beta-diagnostics.md`, Rytm MKII SDK README (machine list, mod machines), changelogs 2026-11-05 to 11-08 (93270f5) | full / key sections | devices/analog-rytm, devices/octatrack, D6c |
| rytm-mods-src README, `docs/MANUAL.md` (0017, 0018), `mods/0018-scene-mutes/design.md`, `re/subsystems/control-inputs.md`, `scenes-mutes.md`, first parts of `loosened-scopes.md` and `loosened-sound.md` (cd4ded4) | full / key sections | devices/analog-rytm, projects.yml |
| nicolai-creates/model27 README and LOST_CHANGES.md diff | full | candidates.yml (model27-restored) |
| dn2_firmware_explore and altstrument changes of 2026-11-08 | not re-read: the fingerprint baseline had already moved, so no diff was available; the earlier run of the same day judged them doc changes | - |
| **2026-11-10 run** (baselines since the 2026-11-08 evening update; the daily Action had already moved some, so diffs were taken against c85f263's fingerprints) | | |
| digikit findings 118 and 119, README rewrite, MODULE-AUTHORING / sdk README knob slots, device profile diffs, core/overdrive and tb303 READMEs (56fbc11) | full (119, module READMEs) / key sections | devices/digitakt-2, projects.yml |
| modwerk changelogs 2026-11-08 to 11-10, Rytm MKII guide, module manifests and TESTING files (comp-preview, ctrl-in-perf, improved-machine-browser, kit-ab, lfo-rnd, midi-mute, scene-mutes, voice-dac, silent-pad-trig, control-in-actions), octabam bbd / ring-sc / sidechain-compressor evidence, `docs/verification/2026-11-09-octatrack-base-options.md`, DT2 elekloader/modwerk README; OCTATRACK_API and Zoom docs skimmed (74c9eb2) | full / key sections | devices/analog-rytm, octatrack, digitakt-2, I55, I56, SB18, S18, H20, H21, projects.yml |
| octabam CHANGELOG, DEMAND_LOADER, FAILURE_MODES (8-9 Nov soak), HARDWARE_TESTING, STEM_REC, modules wavecf / xfcurve / keybus / sc-keybus-bridge / dlcopy (1adbd49) | diff, key sections | devices/octatrack, I57, I58, O22, H22, projects.yml |
| octamax NOTES (2f-2h), README, sysex README (560c848) | diff | devices/octatrack, I59, SB17, O23, projects.yml |
| octatrack-kyoti-fw NOTES, FLASHING, BUILD_KYOTI, START_HERE, README, reload-from-project README (f22c22b); octatrack-step-view README (068ed91) | diff | devices/octatrack, I60, O23, projects.yml |
| elekloader README, CORES, FORMAT, SDK, SHARC-DN2, MACHINES-DN2, TESTS, mods core / core-dn1 / core-dn2 / core-ar2 / machine-pages / machines-dn1 READMEs, commit 4115937 (8daa2ea); elekloader/shop catalog.json (b3d687d): no uncatalogued repos | diff / full | devices/digitakt, digitone, digitone-2-internals, digitakt-2, analog-rytm, I61, projects.yml |
| synfact-dev SAFE-BOOT-SMZ4-07-16, core-st README / SMZ4 / STORAGE / CHANGELOG, mod CHANGELOGs and mod.json, chorus / poly / arp READMEs, MACHINE-REFERENCE (30e2707) | full / key sections | devices/syntakt, I62, I63, I64, projects.yml |
| Tone-FX releases/4.1a, CHANGELOG, README, HANDOFF, Digitakt port README, docs/PATTERN-STORAGE (785c219); RingTone mod.json (28298f8) | full | devices/digitone, digitakt, O21, projects.yml |
| dn2mk2 FIRMWARE.md, releases/v0.45-v0.47, docs/after-v045, leds, fascia, fascia-integration-plan, ping (01113e6) | full / key sections | devices/digitone-2-internals, I65, I66, projects.yml |
| dn2_firmware_explore README, CONTRIBUTING, docs/references (ef8948e); DNX KNOWN-ISSUES, samples (dba9069) | key sections | devices/digitone-2-internals, H23, projects.yml |
| sidecar-expander RELEASE-NOTES 0.4.3, KNOWN-ISSUES, what-works-now (7f717fe); ems-monomachine-firmware CHANGELOG 26B09 (d3dc702) | key sections / full | devices/analog-rytm, machinedrum-monomachine, projects.yml |
| sample-shepherd roadmap and CLI docs (094c59d); SPOKES, Supermodel and whiplash commit logs; Lapin README diff (39936b2); altstrument firmwares diff (dee0272); model27 README and log (eda85fc, public again) | scan | projects.yml, ignore.yml (repeat98/octamachine) |

## Pass 2026-11-10 (user's tip: gdeo607's Digi2 family)
| Source | Depth | Folded into |
|---|---|---|
| gdeo607 Digi2Core, Digi2MacroOSC, Digi2ElixirPotionsDRUM, Digi2String, Digi2Sophie, Digi2Digiseq: READMEs, LICENSE, file lists | full | projects.yml (six entries), INCIDENTS I67, A42 |

## Pass 2026-11-10 afternoon (change report 13:29 UTC, diffs against the 10 Nov morning baselines)
| Source | Depth | Folded into |
|---|---|---|
| digikit `docs/TESTING.md` | diff | nothing (test infrastructure only) |
| naturarum/dn2-cfw HANDOFF, ROADMAP, notes MR01-MR03, SP02 sections 7-8, R1.17 | diff, full new notes | INCIDENTS I68, A16, devices/digitone-2, projects.yml (personal paths in HANDOFF not taken) |
| elekloader `mods/core-ar2/README.md`, `docs/FORMAT.md`, `docs/CORES.md`, examples (ar2) | diff | devices/analog-rytm, D6c, projects.yml |
| DigiAlchemydsp/Flex-Plus README, RELEASE-NOTES 1.1 | diff | projects.yml |
| repeat98/modwerk changelogs 9-10 Nov, `docs/verification/2026-11-10-*`, Zoom docs (skimmed: not Elektron) | diff | devices/octatrack, INCIDENTS I69, C12, projects.yml |

## Pass 2026-11-10 (state/NEW.md triage, 40 repos)
| Source | Depth | Folded into |
|---|---|---|
| READMEs of 40 repos; forks compared commit by commit with their originals | README start, history | projects.yml (9 new entries, digiemu and digihealth moved to the elekloader organisation), ignore.yml (28 with reasons), candidates.yml (1) |

## Pass 2026-11-10 evening (check_updates after the triage)
| Source | Depth | Folded into |
|---|---|---|
| model27 README and AGENTS (uploader 0.57/0.58) | diff | projects.yml, devices/model-cycles-samples |
| modwerk changelog 2026-11-10 (macOS check workers) | diff | nothing (development only) |
| sidecar-digitakt README and mod.json (0.3) | diff | projects.yml |
| sidecar-expander README, RELEASE-NOTES, INSTALL-PI, KNOWN-ISSUES (0.4.4) | diff | projects.yml (sidecar-expander, sidecar-mods) |
| synfact-dev docs/ADAPTING, MACHINE-REFERENCE, core-st, recorder, probes (core 1.8.0) | diff | projects.yml, devices/syntakt |
| altstrument directory (CyclesEmu, Sidecar, dn2mk2, DNX entries) | diff | nothing new (CyclesEmu catalogued today) |

## Pass 2026-11-11 (daily update run)
| Source | Depth | Folded into |
|---|---|---|
| digikit findings 42 (4a), 43 (hardware section), 120; plans usb-fast and usb-fast-hardware; CONTROL, store and upload designs, handover | diff, finding 120 whole | projects.yml, devices/digitone-2-internals, devices/digitakt-2, INCIDENTS I70, AGENT-RULES A39 |
| dn2mk2 v0.48 release, FIRMWARE.md, coupled-emulator, flex-design, bounce-removal-plan, v048-plan, ROADMAP | diff | projects.yml, devices/digitone-2-internals, INCIDENTS I66 (update), I71, AGENT-RULES A44 |
| elekloader drive-loader-ar2 README and PAGE, docs DRIVE, FORMAT, WEB, ADAPTING (core-a4 renamed core-a4mk2) | diff | projects.yml (own_mods Drive Loader), devices/analog-rytm, STOCK-BUGS SB19, HYPOTHESES H24 |
| modwerk Rytm machine guide (queued trigs), QPER Live Rec rename, Zoom pedal docs and changelog | diff | projects.yml, devices/analog-rytm; Zoom pedals out of scope |
| octabam DRUMMER (INVESTIGATION, README), CX OSC README and MORPH, CHIP.md DSP forms, TRAPS, pages, modulation, reload and rec-trig-mute READMEs | diff | projects.yml, devices/octatrack, INCIDENTS I72, AGENT-RULES G8 |
| octatrack-kyoti-fw NOTES (RELOAD beside FREE LOOP) | diff | projects.yml |
| octatrack-step-view README (audio tracks in Split and Pages) | diff | projects.yml |
| elkbench README (cached flash gates) | diff | projects.yml |
| sample-shepherd CLI docs and daily log | diff | projects.yml (log content left out: personal) |
| dn2_firmware_explore ideas backlog (#39 keyboard hold), usbprobe doc | diff | projects.yml (last activity only; the LFO4 memory fault is already in CONFLICTS S17 and common/memory-maps) |

## Pass 2026-11-12 (daily update run)
| Source | Depth | Folded into |
|---|---|---|
| digikit findings 121-125, usb-fast and usb-bulk READMEs, card-info fixture, hardware handover 2026-11-11 | diff + new files | devices/digitakt-2.md, RAM-TENANCY, CONFLICTS O25, projects.yml (handover's personal details left out) |
| dn2mk2 releases/v0.49.md, FIRMWARE.md, ROADMAP | diff | devices/digitone-2-internals.md, INCIDENTS I71 (fixed in v0.49) and I73, projects.yml |
| dn2_firmware_explore docs/os-versions.md (1.12 port) | diff | devices/digitone-2-internals.md, projects.yml |
| armio README, docs/sem-filter.md (R023-R027) | diff + new file | devices/digitone-2.md, INCIDENTS I74, projects.yml |
| Modwerk changelog 2026-11-11, Octatrack docs, SYNTIZ, Pattern Sample Locks, Analog BD, Rytm modules, Digi Perform | diff + moved files | devices/octatrack.md, analog-rytm.md, digitakt.md, INCIDENTS I75-I77, CONFLICTS S19, RAM-TENANCY, AGENT-RULES A54, projects.yml (Zoom pedal work out of scope) |
| octabam FREE LOOP README and INVESTIGATION, FAILURE_MODES, DRUMMER README | diff | devices/octatrack.md, INCIDENTS I78, projects.yml |
| octamax NOTES 2i, README | diff | STOCK-BUGS SB17, projects.yml |
| model27 notes 65, 71-73, README (release 0.60, SOLID) | diff + new file | devices/model-cycles-samples.md, RAM-TENANCY, projects.yml |
| whiplash CHANGELOG, README, docs/digitakt-ii/reference.md, clock-jitter.md | diff + new files | devices/digitakt-2.md, CONFLICTS O24, HYPOTHESES H25, projects.yml (hackathon and plan files skipped) |
| synfact mod changelogs and READMEs (arp 1.9, poly 1.5, samplers 1.4) | diff | projects.yml (the Unicorn EMAC pitfall is already in syntakt.md and octatrack.md) |
| op-xy-mnmd README v1.3.2, machinemodule-mpc tags, octatrack-manager v0.50.0 docs, octatrack-step-view README, elkbench config example, sample-shepherd CLI docs | diff | projects.yml (sample-shepherd daily log left out) |
| altstrument data folder (version bumps only), dn2-tools-depattern, dnx, spokes (code only) | report | nothing to fold |
| dn2mk2 FIRMWARE.md v0.50, ROADMAP, docs/gate-speed.md | diff + new file | common/toolchain-and-emulators.md, projects.yml |
| elekloader core-a4mk2 README 0.6, ADAPTING, DEVICES, FORMAT, CORES, AGENTS | diff | devices/analog-four-keys.md, common/memory-maps.md, projects.yml |
| elkbench docs/emulator-timing.md, README, config example | diff + new file | common/toolchain-and-emulators.md, RESEARCH-MAP G4, projects.yml |
| modwerk changelogs 2026-11-11/12, README, new module READMEs and TESTING (crossfader, live-looper, amiga); the sdk/octabam to sdk/octatrack move read as a rename | diff | devices/octatrack.md, INCIDENTS I79, AGENT-RULES A34, projects.yml (own_mods) |
| octabam HOOKS ui_tick, hooks-reload remix; octatrack-step-view README; OpenBridge README; altstrument data (sidecar 0.4.4, model27, octatrack-manager, digikit, dn2mk2 patcher) | diff | devices/octatrack.md, projects.yml |
| octatrack-step-view README (later the same day: lengths at the row end) | diff | projects.yml |
| digicmi CHANGELOG, README, CLAUDE.md, mod.json (0.19-0.26) | diff | devices/digitakt.md, INCIDENTS I81, AGENT-RULES A34, projects.yml |
| digikit findings 120/123 (update), 126 (new), sdhc-large and usb-bulk READMEs, storage and port TOMLs, MODULE-AUTHORING and the SDK/runtime design docs (runtime 0.6.0), handover | diff + new file | devices/digitakt-2.md, INCIDENTS I80, AGENT-RULES A55, projects.yml |
| dn2mk2 FIRMWARE.md v0.51/v0.52, releases, mnm-trim, flex-design, stereo-assessment, leds, ROADMAP, HANDOFF-second-firmware (private repo names left out) | diff + new files | devices/digitone-2-internals.md, projects.yml (dn2mk2, dn2-rift) |
| model27 README, notes/14, 60 section 24, 66 section 37, 73, PROVENANCE, REGISTRY | diff | devices/model-cycles-samples.md, projects.yml (model27, cycles-one-shot) |
| modwerk changelog 2026-11-12 machine stack, ADD_A_MACHINE, MACHINE_RECIPE, Improved SMPL 0.5.0 README, TESTING and verification, Rytm machine README | diff + new file | devices/analog-rytm.md, projects.yml (own_mods) |
| octabam frame-guard README (new), TRAPS, FAILURE_MODES, MIDI_SCENES, midi-scenes README, remix READMEs | diff + new files | devices/octatrack.md, INCIDENTS I82, AGENT-RULES A56, projects.yml |
| mpc-tributary README, AGENTS, CAPTURE.md; octatrack-step-view README; OP-XY-MNMD README, DEVICE, SCREEN; sample-shepherd README and docs | diff | projects.yml |
| new repos femifleming/AERIA-OS (README, aeria-os/HARDWARE.md start, aeria-fx/STATUS.md) and De-Pattern/DN2-Rift (README, docs/rift.md) | blobless clone, text only | projects.yml (aeria-os, dn2-rift) |
| digikit findings 123 (rewrite), 128, 129, usb-bulk-audio README, plan usb-fast-audio-bulk, MODULES.md, ADDRMAP.md | diff + new files | devices/digitakt-2.md, digitone-2-internals.md, common/overbridge-usb.md, INCIDENTS I80, AGENT-RULES A55, A61, STOCK-BUGS SB20, projects.yml |
| AERIA-OS tags v0.9.2/v0.9.3, README, docs/CHANGELOG.md and docs/LOG.md (new; by sections) | diff + new files | devices/octatrack.md, INCIDENTS I83-I86, AGENT-RULES A57-A58, projects.yml |
| modwerk changelog 2026-11-11..13, docs/verification, MODULE_PERFORMANCE, OCTATRACK_* docs, Rytm machine README, analog-bd and improved-amp README/TESTING, vector and digiperform README/TESTING | diff + new files | devices/octatrack.md, analog-rytm.md, digitakt.md, digitakt-2.md, INCIDENTS I77, I95-I101, STOCK-BUGS SB22, AGENT-RULES A60, A62, A63, RAM-TENANCY, projects.yml |
| digicmi CHANGELOG, README, notes, mod.json (0.27-0.37); Tone-FX 4.3b release files; dt2-machine-lab README, STATUS, SKETCH-117-TRIAL and other docs | diff + new files | devices/digitakt.md, digitakt-2.md, INCIDENTS I81, I89-I94, AGENT-RULES A34, A59, CONFLICTS S20-S21, RAM-TENANCY, projects.yml |
| dn2_firmware_explore README, STATUS, flashing, mod-memory-regions, mods.md, os-versions; DN2-Rift FIRMWARE.md, rift.md, fascia.md, roadmap, release draft; dn2mk2 v0.53; model27 README, notes/60, PROVENANCE | diff + blobless clone | devices/digitone-2-internals.md, model-cycles-samples.md, RAM-TENANCY, CONFLICTS S22 and O26, INCIDENTS I87-I88, AGENT-RULES A64, projects.yml |
| elekloader README, DEVICES.md (Rytm MKI), TESTS.md, ADAPTING.md (core-ot 0.9-0.40), seqrows-ot README; octabam usage pages; octatrack-step-view README; sample-shepherd docs/cli | diff | devices/analog-rytm.md, octatrack.md, INCIDENTS I102, STOCK-BUGS SB21, RAM-TENANCY, projects.yml |
| elkflash README 0.7 and elkbench elklock README (A4 MKII restart stall); OP-XY-MNMD, mpc-tributary, sidecar-expander, kyoti NOTES; altstrument entries | diff | devices/analog-four-keys.md, STOCK-BUGS SB23, INCIDENTS I103, AGENT-RULES A23, projects.yml |
| new repos ClaidArremer/digitakt-mashup, digitakt-gestalt, digitone-gestalt (history compared with digitone-pump), Hteah/ot-mods, bento909/mds-harness, irpina/dirtyloader, seren-a/ot-dpo-4ms-ensemble-folding-acid-style, ClaidArremer/digitakt-glide (empty); mbreilly/Modded_cycles_techno_edition (same HEAD as the catalogued repo) | blobless clone, text only | projects.yml, candidates.yml, ignore.yml |
| 2026-11-14 (second pass): digikit (runtime 0.8.0, devices.md, profiling, INSTRUMENTATION, device toml), synfact-dev MAIN optimisation docs and mod CHANGELOGs, modwerk changelog 11-13/14, MODULE_PERFORMANCE, OCTATRACK_TWO_SLOT_BASE, track-names, amiga/poly8/synth TESTING; mdmm 0.9.1 release docs, BUGS B-133/B-210; dn2mk2 name-screen, md-mm-rewrite, full-sweep; Tone-FX PATTERN-STORAGE, HANDOFF; octatrack-step-view v0.9.1 README; elkbench README; octabam AGENTS (process only); new repos ClaidArremer/digitakt-glide (now with code), ycmdynp9vw-coder/terrain-dn2, Spunkmeyer77/MONO2K-M4L | diff (subagent digests) + blobless clone | devices/syntakt.md, octatrack.md, digitakt.md, digitakt-2.md, digitone-2.md, digitone-2-internals.md, machinedrum-monomachine.md, common/dt2-dn2-limits-and-audio-chain.md, common/sysex-and-midi.md, INCIDENTS I104-I107 (and I75), STOCK-BUGS SB24, AGENT-RULES A42, C10, A65, RAM-TENANCY (Syntakt), projects.yml, candidates.yml, ignore.yml |
