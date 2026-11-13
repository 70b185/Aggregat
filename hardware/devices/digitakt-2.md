# Digitakt II

Coverage: **medium**. Projects: [../../catalog/digitakt-2.md](../../catalog/digitakt-2.md)

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
- Startup menu: FUNC at power-on; **SysEx over MIDI DIN only, not USB**. Step by step: [`../common/recovery.md`](../common/recovery.md). `[doc]` {digikit-old}
- Bootstrap = section 2, updater = section 4, DSP program in section 7; patchkit refuses sections 2, 4 and 8 ([`../common/firmware-container.md`](../common/firmware-container.md)). Recovery via the bootstrap menu is stated as **not tested on hardware** by digikit's author. `[doc]` {digikit}
- BOOTSTRAP UPGRADE (irreversible) runs only for a strictly higher bootstrap version; bootstrap version 0x0200 in 1.15C. `[doc]` {digikit-old}
- 1.15C address facts: depacker `0x80000432`, CRC-32 routine `0x80001bd0`, bootstrap upgrade gate `0x80001c72`, content checksum `0x40003ca6`, HMAC-SHA256 trailer check `0x80005e2a` (last two not emulated; container checks: [`../common/firmware-container.md`](../common/firmware-container.md)). `[doc]` {digikit-old}
- Install generated builds via Elektron Transfer; the builders never connect to or flash the instrument. `[doc]` {digitakt-ii-research}
- **The startup-menu recovery has been used on a real DT2** (dt2-machine-lab, 2026-10-06):
  - An experimental build crashed at startup.
  - The owner restored official OS 1.16 through Transfer's recovery mode over **DIN MIDI**, sent from a Novation Launch Control 3's DIN out. Normal boot and audio came back.
  - **A generic "USB2.0-MIDI" cable adapter (VID 1a86, PID 752d) showed no reception at all.** Use a known-good MIDI interface and test it before you need it.

  `[hw]` {dt2-lab-coldfire-fix}

## Hardware test evidence for the mods
- Déjà Vu LFOs (digitakt-ii-research): LFO waveforms DV-F (WAVE 7, free-running random loop) and DV-T (WAVE 8, loop resets on track trigger) on all three LFOs; WAVE 0-6 stay on stock paths. Hardware testing "initial only": normal boot, DV-F/DV-T modulation, DV-T retrigger. Save/reload/power-cycle persistence unverified. `[hw]` {digitakt-ii-research}
- digitakt2-perform: `perform-levels` and the key swap work on a unit, the combination only linted/built. `[hw]`/`[emu]` {digitakt2-perform}
- digi-roll writes patterns over SysEx, gated by a per-device OS-build allowlist; hardware-verified 2026-08-09. `[hw]` {digi-roll}

- **digikit's flash rungs on a real DT2 1.17** (finding 47, 2026-10-18/19): each step was flashed through SETTINGS > SYSTEM > OS UPGRADE with Transfer and logged over USB SysEx. `[hw]` {digikit-f47}
  - Rung A, the runtime in section 3 only, booted with a DIGIKIT menu.
  - Rung B added the DSP link and voice hook (sections 3 and 7) and played stock audio.
  - Rung C, a machine loaded at run time (pluck, 4,484 B uploaded over SysEx), **halted the SHARC at the first trig**. Breadcrumbs narrowed it to the step after the type match.
  - The fix (C3d2) was to route 17 DAG-register stores through an R register, the same-DAG rule. With it, pluck played at ~1,500 dispatches/s with DSP load 41.5 -> 42 %.
- **A second SHARC stop on a real DT2: `fx/freqshift` on the send route froze the unit at boot; the emulator showed nothing** (findings 77, 91). Two causes were found. `[hw]` {digikit-f91} ([I15](../INCIDENTS.md#i15-a-frequency-shifter-froze-the-unit-at-boot))
  - A selas defect left the end of a nested hardware loop compressed (VISA). The last 11 instructions of every hardware loop must be 48-bit ISA, so wrap nested loops in `.NOCOMPRESS` ([rule A45](../AGENT-RULES.md)).
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
- **A persistent flashed cave** `0x403117c4-0x40312000` (2,108 B) ends exactly at the reset clear and survives boot. `0x4031be59-0x4031ff60` is inside the clear and **cannot hold flashed code**. The priority-6 task entry `0x40133646` is a candidate one-shot startup hook, after the heap is initialised. `[emu]` Deja Vu, the All-in-One, dt2-machine-lab and 70b185's private project all use it; who holds which bytes: [memory-maps.md](../common/memory-maps.md); one freeze report: [CONFLICTS O18](../CONFLICTS.md).
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
SysEx/MIDI facts, NRPN groups and the safe-write ceremony are in [`../common/sysex-and-midi.md`](../common/sysex-and-midi.md). elekloader supports Digitakt II 1.17 as experimental (core checked in digikit; a key-swap mod works on a unit; README 3016dca, 2026-11-08). {elekloader-main}

## Architecture map from static analysis and simulation (lalzart, OS 1.15C) {lalzart-dt2-arch}
lalzart's public research grades each claim. Everything below is **static or simulator** work; the author explicitly claims nothing about hardware behaviour, safety or recovery. `[doc]`
- **SHARC part:** ADSP-21569. Section 7 holds ADSP-2156x loader/application records (104 records mapped). FreeRTOS, an Audio task and a recurring block loop are traced. The hand-off from the boot kernel to that startup is not.
- **The ColdFire <-> SHARC frame is the same shape as on the Digitone II:**
  - A full-duplex `0xabc`-byte DSPI2 frame carries a `0x802`-byte state payload: 16 records of `0x60` bytes, track n to SHARC unit n.
  - ColdFire eDMA29 sends and eDMA28 receives; the SHARC uses SPI2 with completed-image double buffering.
  - The send is driven from a level-5 interrupt that a level-6 eDMA-completion path forces in software.
  - Link settings: SPI mode 1, 16-bit MSB-first, one `0x55e`-word window.
  - The meaning of the SHARC-to-ColdFire return content is open. Compare the DN2's frame and reply words in [digitone-2-internals.md](digitone-2-internals.md). This is a second, independent reading of the shared design (research map T19).
- **Project samples reach the SHARC over a different path:** ColdFire Rapid-GPIO byte/strobe/ready endpoint -> SHARC link port 0 (LP0_RX, DMA30). Samples are described by five-word resource descriptors with 4 KiB pages. This agrees with digikit finding 15 ([digitakt-2-sharc-measured.md](digitakt-2-sharc-measured.md)). The physical bridge between the two endpoints is not identified.
- **Audio output:** two 64-word banks are selected, then sent by a two-bank circular DMA descriptor (DMA10) to SPORT4 half A. Codec and pin are not identified.
- **Update path:**
  - MAIN validates checksum, minimum version and the cryptographic trailer before it erases and programs the staged ELE3 slot at flash `0x80000`, then requests a reset.
  - Which updater copy runs after reset, and whether recovery is independent of it, is marked opaque.
- **Offline modifications proven in the simulator only:** a byte-exact selector reroute, and a 3-byte change that turns an output-bank negation into pass-through. Re-encoding a modified section and running it on hardware are explicitly unproven.

## What happens on a ColdFire fault (digikit finding 37, DT2 1.16/1.17 and DN2 1.11/1.12, static, checked by a second agent) {digikit-f37} `[doc]`
- The main OS's default exception handler prints `EXCEPTION ...` with the vector, format, PC and twelve stack words, then executes **`halt` with interrupts masked**. It never returns.
- The core watchdog is not used anywhere in the main OS, so **a fault hangs the whole device until the power is cycled**. Messages like the DT2's `V04 M0 P40311A64` (dt2-machine-lab) are this handler's output.
- digikit's runtime counts bad boots: the counter is raised at boot start and cleared only after 30 s of stable running.

`[doc]`

## The stock intro and boot screens (digikit finding 117, DT2 1.17 and DN2 1.11/1.12) {digikit-f117}
digikit marks most of this as verified against the image bytes by a second agent; the timing figures come from its emulator. Addresses are for DT2 1.17 unless named. `[doc]`
- **The intro is its own task, priority 7**, created once by the installer before the main-OS task (DT2 `0x400d1448`, DN2 1.12 `0x400d3920`) and woken by a PIT3 tick. A higher number is more urgent here, so the intro preempts the main-OS task (priority 6). **A frame callback that never returns starves the main OS until power-off.**
- **Five scene tables** at `0x402a1b64`, `0x402a1b74`, `0x402a1b84`, `0x402a1b94`, `0x402a1ba4`. Each boot picks one with an LCG; the first is picked about 99.9 % of the time and has 175 frames. An entry is `{callback, frame count}`, ended by a 0.
- **One pointer drives it:** the current entry is at DT2 `0x43153a00`, DN2 1.12 `0x42c4cacc`, DN2 1.11 `0x42c4bacc`. Only the setup function (DT2 `0x400d1832`, DN2 1.12 `0x400d3d0a`) and the tick function (DT2 `0x400d18f0`, DN2 1.12 `0x400d3dc8`) touch it. Each frame calls `callback(index, count, bitmap)`; count 0 ends the intro the normal way: the pointer is cleared, PIT3 stops and semaphore `0x43149550` releases the main-OS task.
- **Swapping the intro:** a hook before the setup function's argument load (`move.l (0x24,SP),D0; movea.l D0,A0`, DT2 `0x400d183a`, DN2 1.12 `0x400d3d12`, DN2 1.11 `0x400d3bae`, the same 6 bytes on all three) can point it at an own table. In digikit's emulator the UI was then reached after 115 audio blocks instead of 5,973 (DT2) and 6,180 (DN2). Stock's frame clear is `0x40113700` (DN2 1.12 `0x40115074`, DN2 1.11 `0x40114d94`), called as `(bitmap, 0, 1)`. `[emu]`
- **Frame rate unresolved:** digikit's timer model gives 30 Hz (175 frames = 5.8 s); its earlier emulator notes derived 15 Hz. Open conflict [O20](../CONFLICTS.md). Module code first runs at about frame 53-57 of the intro (emulator); almost all of that delay is stock setup.
- **Faults during the intro reach stock's halting handler** (see the section above): digikit installs its own crash handler only from the UI loop.
- **Frame layout on the panel** (measured on one DT2 1.17): with y = 0 at the top, the intro bitmap holds pixel (x, y) at byte `8*x + (63-y)/8`, bit `7 - (63-y)%8`, flipped vertically only. digikit's emulator shows these frames the other way up. `[hw]` ([I53](../INCIDENTS.md#i53-boot-screen-frames-were-upright-in-the-emulator-and-flipped-on-the-panel))
- **Safe mode is digikit's, not stock's:** REC (key `0x13`, state byte 2 bit 2; key state array at DT2 `0x44dc8644`, DN2 `0x445a2e30`) held from power-on skips all modules. On one DT2 1.17 it worked, and a custom boot screen started about 1.8 s after the stock intro. `[hw]` ([I54](../INCIDENTS.md#i54-safe-mode-by-rec-at-power-on-tested-on-a-digitakt-ii))
- With the black intro patch set, the bootstrap's logo, "B" and the OS version stay until the main OS first writes the display, then about 1-2 s of black, then the boot screen. `[hw]`

## Memory map for samples and voices (dt2-machine-lab, OS 1.16, static plus emulator) {dt2-lab-flex-mem}
These figures are from the source and emulator runs, not from a unit. `[emu]`
- **ColdFire heap:** a 32 MiB buddy allocator at `0x44f39c40-0x46f39c40` (16-byte minimum, power-of-two blocks), parameters at `0x402b406c`.
- **Allocating from the stock heap at startup** (digitakt-ii-research, OS 1.16, emulator, byte-verified sites) {dt2-research-heap}:
  - `malloc` is at `0x4011e674` (size at `4(A7)`, pointer in D0, mutex at `0x44e08654`, lazy init on first call).
  - `free` is at `0x4011e87a`. It traps with `illegal` on a pointer outside the heap or not 16-byte aligned, the same rule as the Digitakt mk1's operator delete.
  - The OS clears `0x40312000-0x47e28470` at reset, so static data placed there does not survive boot.
  - A startup hook at `0x40133646` (`link.w` + `movem`) made exactly one 8 KiB allocation that stayed untouched for 20 M instructions. This is the cleanest way to own memory without a cave.
- **Sample pool:**
  - Logical range `0x400-0x19000400`, 400 MiB, allocations rounded to 8 KiB.
  - The ColdFire's allocation records decide admission; no SHARC malloc is involved.
  - In the SHARC's view the pool is a window at DSP byte address `0x8422b9c8 + (offset - 0x400)`, ending at `0x9d22b9c8`. Capicola reserves the top 8 MiB.
- **Recorder:** the main OS fetches recorder data in chunks of at most `0x800` bytes over **DSPI1** from a service whose physical owner (ColdFire, SHARC DDR or a third part) is not established. Staging buffers are at `0x4fe79340` / `0x4fe7a340`.
- **SHARC side:**
  - Sample-slot table at `0x257810 + slot*0x14`: 1,025 entries, slot `0x400` is the preview.
  - Voices at `0x2412cc + lane*0x1d8`, 32 lanes: `+0` PCM pointer, `+0x188` length, `+0x1b8` active.
  - Link-port 0 receive staging at `0x268220` (descriptor) and `0x268240` (a tag plus 4 KiB of payload).
- Once published to the SHARC, PCM keeps playing after the ColdFire source is freed, as long as the stock allocation stays owned. Saving, however, needs the source, and no read-back path from sample memory was found.

## Three Digitakt II mod routes side by side (T21, 2026-11-02)
- digikit's patchkit (used by digitakt-ii-research's All-in-One and dt2-machine-lab), elekloader's core-dt2 (used by digitakt2-perform) and the hand-placed builds share the flash cave `0x403117c4-0x40312000`. elekloader's RAM `0x47f00000-0x47f40000` lies inside digikit's `cf.expansion` `0x47e8b000-0x47fe0000`. Full table of ranges and hook sites: [memory-maps.md](../common/memory-maps.md). `[doc]`
- A decoded section 7 over 1 MiB crashed a unit (dt2-machine-lab, OS 1.16): [firmware-container.md](../common/firmware-container.md), rule A46. `[hw]` {dt2-lab-capicola} ([I16](../INCIDENTS.md#i16-a-decoded-section-7-over-1-mib-crashed-the-unit))

## SHARC measured on a real unit
Which of these hold on the Digitone II, and which DN2 findings hold here: [`../common/dt2-dn2-sharc-crosscheck.md`](../common/dt2-dn2-sharc-crosscheck.md).
Clock (1.000 GHz, 666,667 cycles/block), FreeRTOS task map, free reply words, missed-block behaviour, the STRETCH contract, memory limits and selcc traps: [`digitakt-2-sharc-measured.md`](digitakt-2-sharc-measured.md). `[hw]` {own-dt2-notes}

## Sound parameters, overdrive and run-time machines (digikit, DT2 1.17 / DN2 1.12, 2026-11-10) {digikit-f119}
- **Reading a track's Sound parameter words** needs no fixed address: get the project singleton, its ProjectSettings at project + `0x30` (static analysis only), the selected track from `view_track` (clamped 0-15), then `native_track_sound(active kit, track)` = kit + `0x6c` + `0x3c0` x track; vtable slot `0x28` of that Sound object returns the record pointer `*(sound + 0x10)` (0 when none is bound), and word i is a big-endian s16 at record + `0x14` + 2i. Anchors: settings `0x40041d18` (DT2 1.17) / `0x4003e40e` (DN2 1.12); `native_track_sound` `0x40035cca` / `0x40030e66`. The array holds 71 words on the DT2 and 101 on the DN2. `[doc]`
- On the DN2 a track's Sound record can sit at an odd address (kit stride `0x48b`), so read it byte by byte. A parameter code maps to its array index through the descriptor table (rows of `0x3c` bytes, index as s32 at row + 4, -1 = no word); the same index means another parameter on another machine. P-locks, sound lock, LFO and MIDI CC writes go through other paths, and a latched parameter of a run-time machine changed no word in the array (where it is stored is open). `[doc]`/`[emu]`
- **Track overdrive (stock):** the curve clamps to +-1 and applies y*(2-|y|) three times; the blend is x + mix*(y-x) with stock ramps for drive and mix. OVR Routing is parameter `0x103` (Sound mirror index 68; 0 = pre, `0x100` = post). The per-track stage is called twice per track from the voice chain. `[doc]` {digikit-overdrive}
- **Run-time machines:** on the DT2 they can use knob slots B C E F G H; a parameter on the seventh slot replaces LEV, whose level is then fixed at 100. The run-time module stage is limited to 64 KB; a TB-303 port costs about 8,000 SHARC instructions per 32-sample block. `[doc]` {digikit-tb303}
- **ColdFire jump targets must be even:** a jsr/jmp to an odd address faults with an address error on the unit while the emulator runs on; a byte-aligned mod section froze a DT2 at boot (I61). `[hw]` {elekloader-oddjump}
- **Modwerk's DT2 base:** a combined image booted on a DT2 (OS 1.17, 2026-11-08) and restored saved module kit data after a project reload. Its audio scheduler (grid callbacks and phrase replacement at the stock audio submission call `0x400d82f8`) is a proposal checked only in digikit fixtures. `[hw]` / `[emu]` {modwerk-dt2-base}

## +Drive file writes from mod code (digikit finding 120, DT2 1.17) {digikit-f120}
- **The firmware's own file calls** can write samples: open (`0x40158902`, mode "w"), write (`0x4015866a`), reserve, hash (`0x4015b3aa`), close (`0x401588c0`), info, delete (`0x40157078`), mkdir and rename (`0x40156f6c`, which keeps the inode, size and stored hash). Each takes the recursive filesystem mutex itself and blocks, so call them from a task, never an interrupt. The sampler's recorder `0x40153c70` is a complete stock caller. `[doc]` (static)
- **Open does not truncate:** an existing file opens at position 0 with its old size and data; stock deletes first. Whole 32 KiB pages at multiples of `0x8000` are written straight from the buffer, the rest goes through the page cache. `[doc]`
- **The 16-byte trailer:** files carry 16 zero bytes after the data, and the stored hash covers them; the C calls do not add them (the recorder and stock's MidiRpc close do), so a writer adds them before the hash. File info reports size minus 16. `[emu]` (card read back on the emulator) Elekloader's Rytm loader meets the same 16 bytes as a header at the start of each file on the Analog Rytm MKII ([analog-rytm.md](analog-rytm.md)).
- **Power cut:** a cut mid-write leaves a visible file with a partial size and no hash; the mount was not seen to repair it. Delete refuses an open file (open-file bitmap at `0x46f4ded0`). Only `/factory` is RAM-backed; user files always go to the card, and a failed card write is not reported. `[doc]`
- On a unit (2026-11-11) digikit's bulk uploads through these calls left only complete files after a pulled cable, and the stock sample browser did not list the staging folder `/.dkstage`. `[hw]` {digikit-usbfast}

## Project and kit storage (digikit finding 121, DT2 1.17) {digikit-f121}
- **In RAM:** the project object is at `0x41776c9c`; 128 patterns from `0x41776cb8` (stride `0x1db8c`), 128 kits from `0x426532b8` (stride `0x5574`). Serializer `0x400df66c` (flag bits pick the parts), loader `0x400df95a`. `[doc]`
- **Bytes the serializer never writes:** pattern record `0x15acc-0x15c00`, kit record `0x573e-0x5800`, file header `0x1c-0x200`. Pattern RAM `+0x1cef0..0x1db60` is not saved but is in use: pokes there hung the UI. `[doc]` (the hang `[hw]`)

## UI surfaces for mods (digikit finding 122, DT2 1.17) {digikit-f122}
- **Pointer returns:** the firmware returns pointers in d0, while GCC's m68k ABI reads them from a0; a C prototype returning a pointer froze the UI. Declare such routines as returning a 32-bit integer. `[hw]`
- **Sites:** encoder filter `0x40111cda`; per-frame value block `0x80005b50`; modulator call site `0x4002e90c`; LED frame `0x4003117c`, LED setter `0x400308e0`; NameView wrapper `0x40117c70`. `[doc]`
- **LED colour byte:** on a unit `0x31` looked deep blue and `0x41` yellow (one observer, by eye); this disagrees with digikit's own finding 19 (CONFLICTS O25). `[hw]` `[?]`

## USB mode take-over and fast close (digikit findings 123-125, DT2 1.17 and DN2 1.12) {digikit-f123} {digikit-f124} {digikit-f125}
- **USB mode switch:** `FUN_40006c16` has the same address and bytes on DT2 1.17 and DN2 1.12. It takes no lock and cuts a MIDI reply in flight; USB restarts after a 30-tick counter (about 1 s in the emulator; counter DT2 `0x40965a38`, DN2 `0x4058f280`). The stored USB CONFIG byte (0 MIDI, 1 Overbridge, 2 AUDIO/MIDI; DT2 `0x4099d5c4`, DN2 `0x405ce898`) is written only by the menu actions (DT2 `0x4010331a`/`30`/`48`, DN2 `0x40104dc2`/`d8`/`f0`), never by the switch, so a reboot returns to the stored mode; an Overbridge disconnect (`FUN_400f2ce0`) is the only path that re-applies it by itself. DT2 connection-state word `0x40965a40`. `[doc]`
- **Take-over on units (2026-11-11):** digikit's Fast USB switched both units from USB AUDIO/MIDI to USB MIDI in RAM for an upload over its bulk interface and back (SysEx TAKEOVER `0x1e`, RELEASE `0x1f`); the stored mode byte stayed unchanged and USB audio was heard working afterwards. Longer loops later lost a unit from USB (I80, next section). `[hw]`
- **+Drive internals:** close hash `0x4015b1e8` under the filesystem mutex `0x46f4deb0` (recursive lock `0x400015a0`, unlock `0x400016d2`); inode get/put/write `0x4015b92a`/`0x4015b846`/`0x4015b868`; extent lookup `0x4015813c`; hash-table rebuild `0x4015b0ee` (about 300 ms per file on a unit); event post `0x4015a6aa`. Data page 0 is card sector `0x5ee180` (page p at base + p x `0x40`), the first hash page sector `0x5ee980`. Every file write reaches the card before the call returns. The eSDHC read/write is clamped to 64 KiB (DT2 `0x4012e3c4`, DN2 `0x4012ca8a`). `[doc]`
- **Measured ceilings (8 MiB, 2026-11-11):** DT2 +Drive file write 2.6 MB/s with 64 KiB calls, 7.8 MB/s with 256 KiB, 10.3 MB/s with 1 MiB; the firmware's close-hash re-read 4.2 MB/s; store writes DT2 about 7.2 MB/s, DN2 6.3 MB/s; raw card reads 15.3 MB/s on both; CPU hash 16-18.7 MB/s. A whole 8 MB upload: DT2 2.99-6.15 s (varies a lot between runs), DN2 1.75 s. Per file about 0.18-0.19 s fixed cost. `[hw]`
- **Fast close:** digikit hashes from a card read-back and then runs the firmware's own close steps, byte-identical to the stock close, falling back to the firmware close if the read-back fails. After such uploads the stock browser listed the files, a sample loaded and played, and a project that referenced an uploaded sample reloaded and played it. Creating the staging folder `/.dkstage` cost about 420 ms and removing a file from it about 150 ms, so it now stays for the session. `[hw]`
- **SHARC cycle counter:** each image has exactly one EMUCLK reader, the block handler (DT2 `0x1c74cd`, DN2 `0x1c9d6b`), which keeps a low-word delta for reporting only; nothing branches on it. `[doc]`
- **eMMC EXT_CSD copy in RAM:** DT2 1.17 `0x4fe69100`, DN2 1.12 `0x4e6f9100`; bytes are reversed within each 32-bit word because the eSDHC runs little-endian. `[doc]`

## USB take-over failures and card speed (digikit, 2026-11-13) {digikit-f123-hw} {digikit-f126}
- **The USB mode take-over is not reliable on a unit:** switching a Digitakt II from USB AUDIO/MIDI to USB MIDI in RAM and back lost the unit from USB in cycle 5 of a 20-cycle loop, and in cycle 11 after digikit added a 2 s restart hold and parked the PHY's line during the stop. The host saw no disconnect, the unit no longer answered, a cable replug did not help and only a power cycle did; both failures came on TAKEOVER, never on RELEASE. digikit now keeps the take-over off by default; with USB CONFIG set to USB MIDI in the menu its fast transfer ran fully reliably (I80, rule A55). `[hw]`
- **External ULPI PHY:** the USB controller drives an external ULPI PHY (PORTSC.PTS = ULPI, set at init `0x40006d1c`-`0x40006d2c`). The stock firmware writes no PHY register: its only ULPI_VIEWPORT (`0xFC0B0170`) use is a read of PHY register 0 every 300 calls of a periodic function (`0x40006af8`), which resets the controller (not the PHY) when the read never finishes. It never sets PORTSC.PHCD. The VBUS interrupt (`0x40005e14`, OTGSC.BSVIS) starts or stops the controller; the restart `0x40006bc6` starts it only while OTGSC.BSV is set. Same code on DN2 1.12. `[doc]`
- **eMMC:** both units carry an eMMC 5.1 of 23.05 GiB with identical EXT_CSD: enhanced reliable write supported but not forced, 1 MiB cache off, background operations off, optimal write size 32 KiB. Card clock 37.71 MHz (75.43 MHz divided by 2) on a 4-bit bus in high-speed timing; the eSDHC has no 8-bit mode. `[hw]` (read on the units)
- **Stock card driver:** data moves by eDMA channel 59 to the eSDHC data port, 16 bytes per request; every write uses CMD23 with the reliable-write bit. The block write and read split every transfer into 64 KiB commands: `cmpi.l #0x10000,D2` at offset 0x14 (entry) and 0x22 (chunk loop) of each function, same bytes on both images: DT2 1.17 read `0x4012e1b6` (sites `0x4012e1ca`, `0x4012e1d8`), write `0x4012e39c` (sites `0x4012e3b0`, `0x4012e3be`); DN2 1.12 read `0x4012c87a` (`0x4012c88e`, `0x4012c89c`), write `0x4012ca60` (`0x4012ca74`, `0x4012ca82`). The 64 KiB bounce buffer for unaligned buffers is the likely reason; the eDMA's 15-bit count allows at most 1023 blocks (511 KiB) a command, which digikit's sdhc-large uses (1022) for 16-byte aligned buffers it registers. `[doc]`
- **Raw card rates (DN2, 8 MiB, median of 3):** write 11.4 / 13.3 / 15.3 MB/s and read 13.8 / 15.6 / 16.1 MB/s with 32 KiB / 64 KiB / 511 KiB commands; reliable write and the card cache change nothing within 2 %. A copy in RAM runs at 18 MB/s, USB alone at 20.9 MB/s (13.5 MB/s while the CPU copies). An upload that reads every file back is capped at about 7.2-7.8 MB/s by the card. `[hw]`
- **Cost per file:** on the DN2 store the cost of an upload grows by about 0.46 ms for each file already stored (the store table is rewritten and read back at every commit), on top of about 95 ms; on the DT2 +Drive about 195 ms a file, with no growth across folders. For sample packs of hundreds of files this matters more than the transfer rate. `[hw]`
- **+Drive ids at or above `0x1000000` never reach the card (DT2 1.17):** the inode write-back `0x4015b868` and page write-back `0x40155c34` call the block write only for inode ids and page numbers below `0x1000000`; higher ones are copied into RAM tables (inodes at `0x47d73ed0 + n*0x80`, pages at `0x46f63ed0 + n*0x8000`, n counted from `0x1000000`). `[doc]` {digikit-f120}

## MIDI notes from whiplash (DT2, OS 1.17 manual, 2026-11) {whiplash-ref}
- **NRPN numbers disagree** between the OS 1.17 manual and midi.guide's data for track mute and level, pattern mute, master overdrive, filter env depth, filter base/width and portamento; all CCs agree (CONFLICTS O24). `[doc]`
- **CC 80 (amp HOLD) at 127** switches HOLD to NOTE; it is not the longest hold. A sound ends on note-off only with AMP MODE = ADSR or HOLD = NOTE. Note 60 plays a sample at its own pitch only with TUNE 64 and the preset OCTAVE unchanged. No CC or NRPN selects the machine type. `[doc]`
- **CC 19 selects the sample slot** from the project pool; it switched slots audibly on a unit (2026-11-11). MIDI Start also starts the unit's own sequencer, so the selected pattern's trigs play on top of an external part. `[hw]`
- **USB audio:** class-compliant audio exists only in USB AUDIO/MIDI mode, with one stereo USB OUT pair; track outputs over USB carry no effects; INT TO MAIN = AUTO mutes the internal outs while USB audio streams. `[doc]`

## Gaps
Memory map beyond the numbers above, DSP memory, machine API, parameter-table layout: not collected yet (see `../MINING.md`).
