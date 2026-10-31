# Digitakt II

Coverage: **medium**. Projects: [../../devices/digitakt-2.md](../../devices/digitakt-2.md)

## Hardware (as reported by digikit's author)
- Control CPU: Freescale ColdFire **MCF54415**, big-endian, runs UI, sequencer, files, MIDI. `[doc]` {digikit-old}
- Audio DSP: Analog Devices **ADSP-21569 SHARC+** running FreeRTOS, shipped as ADI loader records. `[doc]` {digikit-old}
- Display 128x64. Storage: eSDHC controller + eMMC. `[doc]` {digikit-old}
- A forum user notes the Digitone II PCB looks near identical (same P/N PCBA0109B, 32 GB eMMC). `[?]` {elektronauts-dn2-pcb}

## OS versions in use
| OS | Used by | Note |
|---|---|---|
| 1.11 | earlier digikit decoder could read it | |
| 1.16 | current digikit runs it as its default file | |
| 1.17 | current digikit **target** | |
| (1.17 or 1.16) | dn2mk2 uses the user's Digitakt II file only as a source of sample-reading tables for the Digitone II | not a Digitakt II mod |
| 1.15C | earlier digikit README (**only build stated as tested then**), lalzart's research; kept for old analysis in the current digikit | other builds "will likely fail to boot" in the emulator |
| 1.16 | digitakt-ii-research builder, dt2-machine-lab | no longer listed on elektron.se; author suggests asking Elektron support |
| 1.17 | digitakt-ii-research builder (recommended), digitakt2-perform, DigiSplash-II | 1.18+ would need addresses found again |

`[doc]` {digikit-old} {digitakt-ii-research} {digitakt2-perform}

## Bootstrap/recovery facts
- Startup menu: FUNC at power-on; **SysEx over MIDI DIN only, not USB**. `[doc]` {digikit-old}
- Bootstrap = section 2, updater = section 4; DSP program = ADI boot stream in section 7; patchkit refuses to change sections 2, 4 and 8. Recovery via the bootstrap menu is stated as **not tested on hardware** by digikit's author. `[doc]` {digikit}
- BOOTSTRAP UPGRADE (irreversible) runs only for a strictly higher bootstrap version; bootstrap version 0x0200 in 1.15C. `[doc]` {digikit-old}
- 1.15C address facts: depacker `0x80000432`, CRC-32 routine `0x80001bd0`, bootstrap upgrade gate `0x80001c72`, content checksum `0x40003ca6`, HMAC-SHA256 trailer check `0x80005e2a` (last two not emulated). `[doc]` {digikit-old}
- Install generated builds via Elektron Transfer; the builders never connect to or flash the instrument. `[doc]` {digitakt-ii-research}

## Hardware test evidence for the mods
- Déjà Vu LFOs (digitakt-ii-research): LFO waveforms DV-F (WAVE 7, free-running random loop) and DV-T (WAVE 8, loop resets on track trigger) on all three LFOs; WAVE 0-6 stay on stock paths. Hardware testing "initial only": normal boot, DV-F/DV-T modulation, DV-T retrigger. Save/reload/power-cycle persistence unverified. `[hw]` {digitakt-ii-research}
- digitakt2-perform: `perform-levels` and the key swap work on a unit, the combination only linted/built. `[hw]`/`[emu]` {digitakt2-perform}
- digi-roll writes patterns over SysEx, gated by a per-device OS-build allowlist; hardware-verified 2026-08-09. `[hw]` {digi-roll}

- **digikit's flash rungs on a real DT2 1.17** (finding 47, 2026-10-18/19): each step was flashed through SETTINGS > SYSTEM > OS UPGRADE with Transfer and logged over USB SysEx. `[hw]` {digikit-f47}
  - Rung A, the runtime in section 3 only, booted with a DIGIKIT menu.
  - Rung B added the DSP link and voice hook (sections 3 and 7) and played stock audio.
  - Rung C, a machine loaded at run time (pluck, 4,484 B uploaded over SysEx), **halted the SHARC at the first trig**. Breadcrumbs narrowed it to the step after the type match.
  - The fix (C3d2) was to route 17 DAG-register stores through an R register, the same-DAG rule. With it, pluck played at ~1,500 dispatches/s with DSP load 41.5 -> 42 %.
- **A second SHARC stop on a real DT2: `fx/freqshift` on the send route froze the unit at boot; the emulator showed nothing** (findings 77, 91). Two causes were found. `[hw]` {digikit-f91}
  - A selas defect left the end of a nested hardware loop compressed (VISA). The last 11 instructions of every hardware loop must be 48-bit ISA, so wrap nested loops in `.NOCOMPRESS`.
  - Code copied into L2 at run time was not written back from the data cache.
  - After both fixes, freqshift ran on the send and master routes (2026-10-30).
- An LFO at large depth on a run-time machine's TUNE drove Inf/NaN into the send FX and **silenced every track until reboot**, while the DSP kept running. The fix was a parameter clamp plus a per-voice guard in the wrapper; the guarded build ran on a unit with 0 faults. `[hw]` {digikit-f51}

- **PLAITS port (digitakt-ii-research All-in-One):** 25 models flashed step by step on a unit, plus one SIMD kernel that hung the DSP. Lessons: [`digitakt-2-dsp-optimizing.md`](digitakt-2-dsp-optimizing.md). `[hw]` {dt2-plaits}

## ColdFire facts from digitakt-ii-research's research notes (DT2 **1.16**, emulator) {dt2-research}
- **LFO tick** `0x40139342` (caller `0x4002e912`):
  - Parameter rows relative to A3: SPD -6, MULT -4, FADE -2, DEST 0, WAVE +2, SPH +4, MODE +6, DEP +8.
  - WAVE is clamped to 0-6 at `0x401393c6`. WAVE 0-5 dispatch through a 6-entry table at `0x4022231c`; WAVE 6 is RAND.
  - **The table cannot be extended by appending**: the RAND slew data sits right after it.
  - The shared RNG is `(A,B) -> (B, A+B)` at `0x402b62c8/cc`.
  - The phase increment is in D5 (signed); the stored phase is in D2.
  - Raw WAVE 7/8 clamp to 6 and play RAND on stock. This is why Deja Vu needs two paired hooks, not one dispatch hook. `[emu]`
- **Firmware heap:** `malloc` at `0x4011e674` (size at `4(A7)`, pointer in D0, mutex `0x44e08654`), `free` at `0x4011e87a` (it checks bounds and 16-byte alignment with `illegal`). The heap is a 32 MiB buddy heap `0x44f39c40-0x46f39c40` with metadata at `0x402b406c`. It sits inside the reset clear and initialises on first call. An 8 KiB block allocated once stayed untouched for 10 M emulated instructions. `[emu]`
- **A persistent flashed cave** `0x403117c4-0x40312000` (2,108 B) ends exactly at the reset clear and survives boot. `0x4031be59-0x4031ff60` is inside the clear and **cannot hold flashed code**. The priority-6 task entry `0x40133646` is a candidate one-shot startup hook, after the heap is initialised. `[emu]`
- These are 1.16 addresses; resolve them on 1.17 before use (rule C1).

## Ecosystem snapshot, Digitakt II (altstrument 2026-10-31: 3 firmware + 2 tools; elektronmods: SYXGRID, digi-roll-studio, digitakt2-perform, digikit, lalzart's research, Overwitch, firmware-tool)
Listings: {alt-digitakt-ii}. **Digitakt II All-in-One** (digitakt-ii-research; v0.3.0-beta 2026-10-23, AGPL-3.0-or-later on altstrument although the repo README said MIT, OS 1.17, brick-risk flag), **digitakt2-perform** (v1.0, 2026-10-04, OS 1.17, GPL-2.0-or-later, elekloader mods), **dt2-machine-lab** (emulator-only, OS 1.16, SINE test machine plus SHARC ports of Plaits engines VA, 2-op FM, bass drum, waveshaping, additive, granular formant), **DigiSplash-II** (OS 1.17, converts an image/GIF to the OLED format and injects it), **digitakt-ii-firmware-research-public** (OS 1.15C architecture notes, CC0). The directory's own summary: early, OS 1.16/1.17 targeted, nothing yet polished, elekloader's 1.17 support experimental. `[doc]` {alt-digitakt-ii}

## From the official manual (OS 1.17; first part only - appendix B not reachable)
16 tracks (audio or MIDI), **16 stereo voices**, 128 patterns (8 x 16) with one kit each, up to 128 steps, 16 songs of up to 99 rows, up to 128 projects, 1,024 kits and 2,048 presets on the +Drive, **up to 1,016 sample slots and 400 MB of sample memory per project** (about 72 min mono / 36 min stereo), a +Drive sample bank of up to 20 GB, 66 s maximum sampling time; send FX chorus, delay, reverb; master compressor and overdrive. MIDI tracks: chords of up to 4 notes per trig, pitch bend, aftertouch, 16 assignable CCs; notes 0-15 trigger tracks, 16-84 play chromatically (keyboard channel must equal the MIDI Auto Channel), program change selects patterns. Screen dims after 5 min idle and turns off after 60 min. The manual's appendix numbering is duplicated (B.8/B.9 appear twice; A.3.5 twice). Startup menu entries as on the Digitone II. `[doc]` {dt2-manual}

## Official support page (read 2026-10-31)
OS **1.17** dated 2026-10-01 ("adds some Outbox 8-related features"); English manual for OS 1.17 (file `Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf`); Japanese manual only for OS 1.02; Elektron Transfer **1.10.3** (2026-03-04) - note that the Analog Heat MKII page listed Transfer 1.10.4 (2026-06-23), so the pages are not in sync. Factory-reset FAQ in [`../common/recovery.md`](../common/recovery.md). The page does not cover MIDI or SysEx. `[doc]` {elektron-dt2-support}

## Official OS list (elektron.se release notes, page updated 2026-10-01)
Newest **1.17**, then 1.16, 1.15C, 1.15B, 1.15A, 1.15, 1.10B, 1.10A, 1.10, 1.03A, 1.03, 1.02, 1.01A, 1.01 (1.00 baseline). No dates per version. Feature milestones from the notes: 1.03 added Overbridge 2.13 support; 1.10 added the Comb+ filter machine, configurable routing of distortion and base-width filter, key tracking; 1.15 added the Slice machine; 1.15A added track swap within a pattern and overdub in live recording. 1.15B and 1.15C are described only as support for "updated production processes" - our inference: newer production batches may need those builds, so check which OS a unit actually runs before assuming a mod's stock hash applies. `[doc]` {elektron-dt2-notes}
(Earlier in this repo we noted that 1.16 had vanished from Elektron's download page; the release-notes page still lists it. Which files are downloadable now was not re-checked.)

## Identifying stock files (SHA-256 as published by projects; use to check you hold the right file)
| OS | SHA-256 | Source |
|---|---|---|
| 1.17 | `26c22f6652625ac2cfd47f7ee970d388ed8b6427dae3563c0a6a2f2d334350d5` | {digitakt-ii-research} |
| 1.16 | `278541e466edcd77d6b3e018a91fb90185932d3c7de224dd3e68294dddf3a9ec` | {digitakt-ii-research}, {digikit-forks} |
| 1.15C | `62d588456e47194bd56dfee9568fb9dd4521c4ff1e8b5427eb461355532e8c6c` | {digikit-forks} |
Hashes agree across independent repos where two sources exist (1.16). Always compare against the file you actually downloaded; the hash is how builders recognise a file. `[doc]`

## Deja Vu / zoom builder facts (digitakt-ii-research)
- Releases: v0.1.0-beta (16 Oct, OS 1.16 only), v0.1.1-beta (17 Oct, adds 1.17, "recommended"), v0.2.0-beta (18 Oct, adds the ONESHOT zoom for 1.17 only). All three generated outputs were validated on a physical unit for normal boot and operation. Output files are identified by hash too (1.17 Deja Vu `cd553ef6...67b2e`, 1.17 Deja Vu + zoom `6163640c...febd4`, 1.16 Deja Vu `d9fe67b3...7835`). `[hw]` {digitakt-ii-research}
- Builder checks: SHA-256 of input and output, package identity, six-section decode, HMAC/checksums, Sound-object conversion, stock WAVE 0-6 behaviour. The ColdFire side uses a trampoline and a startup allocation (source in the repo's `coldfire/`). `[doc]` {digitakt-ii-research}
- Open: broad MIDI/sequencer/sync regression and save-reload-power-cycle persistence are unverified. `[doc]` {digitakt-ii-research}

## Hardware claims from forums and teardowns (not verified)
- Forum users who opened the unit: main CPU is the same ColdFire as the Digitakt mk1 (MCF54415CMJ250 reported); **new in the Digitakt II**: the ADSP-21569 SHARC system, a larger eMMC and an additional 512 MB DDR3L; audio codec looks the same, a DAC was added. `[?]` {elektronauts-dt2-intro}
- On the day of the first teardown photos (from Discord, hedged with "supposedly"/"possibly") a poster spotted a ColdFire CPU (NXP MCF54415CMJ250), linked the ADSP-21569 as the SHARC part, and a 2023-dated mainboard; others complained that both are old "legacy" parts. Eventually a separate thread confirmed it as the Digitakt II PCB (not readable by us). `[?]` {elektronauts-dt2-teardown}
- Another poster says the main CPU is a legacy chip first launched Dec 2017 and that the board has many Kingston memory chips. `[?]` {elektronauts-dt2-pcb}
- The Digitone II board has the same part number PCBA0109B as the Digitakt II (32 GB Kingston eMMC), so both likely run the same hardware with different OS images and header boards. `[?]` {elektronauts-dn2-pcb}
- Specs from reviews: 400 MB sample memory, 20 GB internal storage, 16 tracks (synthtopia summary); sample memory pool of dn2mk2 on the Digitone II is also 400 MB. `[doc]` {dn2mk2-firmware-md}

## digitakt-ii-research "All-in-One" v0.3.0 (install guide, 2026-10)
Windows executable (`DT2-All-in-One-Builder.exe`, release zip `DT2-All-in-One-v0.3.0-beta-Windows-r2.zip`), OS 1.17 only, offline, never connects to or flashes a device; the builder must show "Detected OS: Digitakt II 1.17"; input SHA-256 `26c22f66...334350d5` (1.17 stock), generated firmware SHA-256 `426dd1be...d95eec76` - hashes of the older v0.2.0 builder do not apply. Warnings in the guide: the exact release image is **not hardware-tested**, a recurring Plaits trigger click remains, earlier Plaits builds failed normal Transfer updates at 0%/PREPARING, no support or future-OS compatibility is promised, do not redistribute the generated `.syx` (it contains Elektron material). Backups of projects, Sounds and samples and a working DIN recovery connection are required before starting. `[doc]` {dt2-install}
Recovery steps in this repo's `RECOVERY.md` are summarised in [`../common/recovery.md`](../common/recovery.md) (DIN only; Transfer's SYSEX TRANSFER page, "OS upgrade via device startup menu"; recovery not guaranteed; no hardware test reported). `[doc]` {dt2-recovery}
Core support: elekloader lists core-dt2-1.0 as unreleased (build from source) with SETTINGS and PERSONALIZE rows and `.fast` code in SRAM; **no render events** because audio renders on the DSP. `[doc]` {elekloader-cores}

## Control from outside
SysEx/MIDI facts, NRPN groups and the safe-write ceremony are in [`../common/sysex-and-midi.md`](../common/sysex-and-midi.md). elekloader's simonjohansson fork supports Digitakt II 1.17 as experimental (core checked in digikit; a key-swap mod works on a unit). {elekloader-simonjohansson}

## SHARC measured on a real unit
Clock (1.000 GHz, 666,667 cycles/block), FreeRTOS task map, free reply words, missed-block behaviour, the STRETCH contract, memory limits and selcc traps: [`digitakt-2-sharc-measured.md`](digitakt-2-sharc-measured.md). `[hw]` {own-dt2-notes}

## Gaps
Memory map beyond the numbers above, DSP memory, machine API, parameter-table layout: not collected yet (see `../MINING.md`).
