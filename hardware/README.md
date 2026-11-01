# hardware/ - what we know about the boxes, written as rules for AI agents

Purpose: an agent that develops mods/tools for Elektron's small boxes should read **this folder** instead of
combing through dozens of repos. Everything here is distilled from public repos, READMEs and
manufacturer pages. It contains **no firmware, no binaries and no dumps** - only facts, addresses as
published by the authors, and rules.

## How to use

1. Read [`AGENT-RULES.md`](AGENT-RULES.md) first (safety and process rules, valid for every device), and check [`CONFLICTS.md`](CONFLICTS.md) for numbers that sources disagree on.
2. Read [`common/firmware-container.md`](common/firmware-container.md), [`common/recovery.md`](common/recovery.md), [`common/flash-procedure.md`](common/flash-procedure.md) before any flash, and - if you only talk to a unit over MIDI/SysEx - [`common/sysex-and-midi.md`](common/sysex-and-midi.md).
3. Read the file for your device in [`devices/`](devices/).
4. Look up the project you build on in [`../INDEX.md`](../INDEX.md) (who maintains what, which OS, which state).

## Evidence levels (every fact carries one)

| Tag | Meaning |
|---|---|
| `[hw]` | The author reports it worked on a real unit. We did not test anything ourselves. |
| `[emu]` | Only checked in an emulator (digikit/digiemu). Not proof for real hardware, audio is not emulated. |
| `[doc]` | Stated in a README/doc/manufacturer page, no test result given. |
| `[?]` | Unclear, contradictory or inferred - treat as a question, not a fact. |

Every fact also names its source key in brackets, e.g. `{elekloader-adapting}`. Keys are resolved in
[`SOURCES.md`](SOURCES.md). All of it is **second-hand**: re-check against the source before you
rely on an address or a byte pattern.

## A finer evidence ladder to adopt when a source uses it
digitakt-ii-research grades its own statements as SOURCE/STATIC -> HOST -> SYNTHETIC UNICORN -> NATURAL EMULATED -> HARDWARE. Our `emu` tag lumps the middle three together; when a source draws that distinction, keep it in the note.

## Ten things every agent should know first (details and sources inside)
1. **Never touch the bootstrap/updater**; recovery is the startup menu (FUNC at power-on, TRIG 4) - **DIN MIDI only on Digitakt II, Digitone II, Syntakt**; avoid TRIG 2/3 (erase data). Prove the recovery once with a stock file before the first modified flash. (`AGENT-RULES` A1-A5, A11, A17; `common/recovery.md`, `common/flash-procedure.md`)
2. **Nothing Elektron ships in the repo**; the user supplies the stock `.syx`, you identify it by SHA-256; keep stock files - old OS versions are no longer offered. (B1, B2, B6; `common/ecosystem-lessons.md`)
3. **One mod = one exact OS build.** Digitone II is split between 1.11 (dn2mk2, skill) and 1.12 (Overtone, Digiwerk, DigiRust); Digitakt II 1.16/1.17; Syntakt 1.40A/1.41/1.42. (C1, A10)
4. **Size limits bite before flash limits:** 2 MiB USB receive limit and the in-place unpack margin on DT2/DN2 (DN2 stock +31,182 B; a default-level recompress is -39,318 B); on the Syntakt a zero-padded image with -8,751 B of margin did not boot. Section 7 must stay under 1 MiB. (A9, A14, A30; `devices/digitone-2-internals.md`, `devices/syntakt.md`)
5. **Emulators lie, and silicon has the last word.** Code that ran bit-exactly in the emulator hung real units: a same-DAG store, SIMD moves into L2, compressed loop ends, code copied without a cache write-back, negative shift immediates, 8n+4 boot blocks. **Silence means a DSP trap; a stuck tone means a stalled task.** (A28, A33, G9; `devices/digitakt-2-dsp-optimizing.md`, `devices/digitone-2-machines-sampler-sharc.md`)
6. **Budget per block, in silicon cycles.** A block is 666,667 cycles at 1 GHz. Taken branches cost ~7, CALL+RTS ~14, an L2 miss ~58. The stock engine never misses a block by itself, so code you add must stop on a per-block deadline. On the Syntakt the ColdFire is already at ~89 % at rest. Voices are not tracks. (A25, A34, A35, D12)
7. **Test ladder and logging:** failing test with a stock control first, emulator before every flash, one named image with SHA-256, stop after two failed flashes. (G1-G8; `common/agent-workflow.md`)
8. **Control-side tools must write safely:** back up, allowlist OS builds, change only needed bytes, read back and compare. (F1-F6; `common/sysex-and-midi.md`)
9. **Memory maps differ per device and per core version** - use `common/memory-maps.md` as a checklist, not as gospel. (D11)
10. **Analog Heat +FX is barely charted:** one private research line (the owner's) has a first OS 1.02 profile: unsigned ELE3, MCF5441x, audio on the ColdFire with no DSP, FPGA bitstream, MAIN-only changes ran on a unit. Nothing public, nothing for MKI/MKII. (A27, `devices/analog-heat.md`)

## All files in this folder

- [`common/agent-workflow.md`](common/agent-workflow.md) - Agent workflow for firmware mods (distilled from the digitone-2-modding-skill)
- [`common/dt2-dn2-limits-and-audio-chain.md`](common/dt2-dn2-limits-and-audio-chain.md) - Digitakt II / Digitone II - firmware limits, DSP calling convention and the audio chain (DT2 1.17, DN2 1.12)
- [`common/ecosystem-lessons.md`](common/ecosystem-lessons.md) - Ecosystem lessons - how the 2026 custom-firmware wave is built, verified and what goes wrong
- [`common/firmware-container.md`](common/firmware-container.md) - Firmware container (.syx) - facts shared by the devices
- [`common/flash-procedure.md`](common/flash-procedure.md) - Flash procedure and link pitfalls (Digitone II, as practised by dn2mk2 and dnfw)
- [`common/memory-maps.md`](common/memory-maps.md) - Memory maps and mod areas per device (from elekloader's `docs/DEVICES.md`, v0.9.0 era)
- [`common/os-update-protocol.md`](common/os-update-protocol.md) - How Digitakt II and Digitone II take an OS update from the running OS (DT2 1.17, DN2 1.12)
- [`common/overbridge-usb.md`](common/overbridge-usb.md) - Overbridge over USB (what Overwitch's README reveals) - the only deep source on Analog Heat +FX so far
- [`common/recovery.md`](common/recovery.md) - Recovery and flashing
- [`common/sysex-and-midi.md`](common/sysex-and-midi.md) - SysEx and MIDI control (talking to a unit without flashing it)
- [`common/toolchain-and-emulators.md`](common/toolchain-and-emulators.md) - Toolchains and emulators
- [`devices/analog-heat.md`](devices/analog-heat.md) - Analog Heat (MKI, MKII, +FX)
- [`devices/analog-rytm.md`](devices/analog-rytm.md) - Analog Rytm (MKI, MKII) - OS 1.73 / 1.74
- [`devices/digitakt-2-dsp-optimizing.md`](devices/digitakt-2-dsp-optimizing.md) - Digitakt II (OS 1.17) - writing fast and safe SHARC code: lessons from the PLAITS port
- [`devices/digitakt-2-sharc-measured.md`](devices/digitakt-2-sharc-measured.md) - Digitakt II (OS 1.17) - SHARC facts measured on a real unit
- [`devices/digitakt-2.md`](devices/digitakt-2.md) - Digitakt II
- [`devices/digitakt.md`](devices/digitakt.md) - Digitakt (mk1)
- [`devices/digitone-2-internals.md`](devices/digitone-2-internals.md) - Digitone II - internals collected from the research repos (OS 1.10E / 1.11 / 1.12)
- [`devices/digitone-2-machines-sampler-sharc.md`](devices/digitone-2-machines-sampler-sharc.md) - Digitone II - machine registration, SHARC mod link, sampler/+Drive layout and field incidents
- [`devices/digitone-2-os111-firmware-map.md`](devices/digitone-2-os111-firmware-map.md) - Digitone II OS 1.11 - function and data map (from the digitone-2-modding-skill sources)
- [`devices/digitone-2-os111-reference.md`](devices/digitone-2-os111-reference.md) - Digitone II (OS 1.11) - engineering reference from the digitone-2-modding-skill
- [`devices/digitone-2.md`](devices/digitone-2.md) - Digitone II
- [`devices/digitone.md`](devices/digitone.md) - Digitone (mk1) / Digitone Keys
- [`devices/model-cycles-samples.md`](devices/model-cycles-samples.md) - Model:Cycles and Model:Samples - OS 1.13
- [`devices/octatrack.md`](devices/octatrack.md) - Octatrack (MKI, MKII) - OS 1.40C
- [`devices/syntakt.md`](devices/syntakt.md) - Syntakt

## Status of this folder (2026-10-31, after the "read everything" pass)
Built from README- and docs-level reading of more than 40 repositories, the altstrument and elektronmods directories, two official release-note sets, forum threads and one journalistic audit. The exact depth per source, the pages that were blocked and the ones that need an approval are in [`READING-LEDGER.md`](READING-LEDGER.md); the open reading list is [`MINING.md`](MINING.md).

Coverage per device: Digitakt mk1 **good** (ecosystem + memory map), Digitone mk1 **good**, Digitakt II **good** (static analysis, install/recovery, protocol, SHARC timing and RTOS measured on a unit), Digitone II **good** (the best documented box: container, flash layout, DSP/ColdFire rules, machines, sampler, incidents), Syntakt **medium-good** (platform, memory map, audio path, modding rules, recovery; 1.42 container), Analog Heat +FX **thin** (first OS 1.02 profile from the owner's research, two test builds ran on a unit), Heat MKI/MKII **official facts only**. Phase 2: Octatrack, Model:Cycles/Samples and Analog Rytm have **first profiles**; Analog Four/Keys, Machinedrum and Monomachine are catalogue only.
