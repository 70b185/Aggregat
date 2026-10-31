# Digitakt (mk1)

Coverage: **good**. Everything below targets OS 1.53 unless stated. Projects: [../../devices/digitakt.md](../../devices/digitakt.md)

## Basics
- OS targets in use: **1.53** (nearly all mods), **1.54** (elekloader v0.4.0: "linkable mods and whole builds"). A mod built for 1.53 is refused on a 1.54 stock file. `[doc]` {elekloader-readme} {elekloader-adapting}
- Official minimum OS for Transfer-based update: 1.20. `[doc]` {elektron-support}
- Container unsigned? Not stated for Digitakt; Digitone mk1 is unsigned (trailer = 32 zero bytes). `[?]`
- Recovery: hold FUNC at power-on -> TRIG 4 (OS UPGRADE) -> send the stock `.syx`. `[doc]` {elekloader-readme}

## Where the audio runs (Digiwerk prior-art survey, 2026-10) {dn2-cfw-prior}
- **The Digitakt mk1 renders all its audio on the ColdFire itself**, in the render interrupt (vector 191). It has no DSP chip. New machines and filters (DigiFilter, digistring, digisophie, digineighbor, digislicer) are ColdFire C built with `m68k-elf-gcc -mcpu=54455`, hooked in the render ISR through elekloader. `[doc]`
- **Measuring load the digihealth way:** read DMA timer 0's counter (`DTCN0`, `0xFC07000C`) at render entry and exit, and add the idle task's time at the RTOS context switch (`0x40000438` on DT mk1). `[doc]`

## Memory and code placement (core 2.x, elekloader)
- Budget shared by all mods (ADAPTING.md, core 2.x era): **128 KB for `.run` + `.bss`**, **2304 bytes of fast SRAM** (`.fast`). Newer cores differ: elekloader kit 0.6.0 gives 4.0 cores a 256 KB Digitakt area, DEVICES.md lists `core_ddr` at `0x47BC0000-0x47C00000` (256 KB) for Digitakt mk1 - see [`../common/memory-maps.md`](../common/memory-maps.md). `[doc]` {elekloader-adapting} {elekloader-devices}
- Main OS ends at `0x4025CA40` (1.53); an appended blob runs there (`__run_start`, `__bss_end`, `__fast_start`, `__fast_len`). `[doc]` {elekloader-adapting}
- FAST AUDIO copies the render block `0x400716c0-0x4007629a` to SRAM; hook sites inside it must be absolute, not PC-relative. `[doc]` {elekloader-adapting}
- Relocations supported: 32-bit absolute, 32/16-bit PC-relative; 16-bit absolute is refused. `[doc]` {elekloader-adapting}
- Core-owned hook sites (1.53): `0x40000538, 0x4000a770, 0x4000a7d6, 0x4000b770, 0x4000b7ba, 0x40058800, 0x40077428, 0x400784c8`; core 2.1 owns about 30 more (listed in `mods/core/mod.json` of elekloader). Never patch them, subscribe to events. `[doc]` {elekloader-adapting}

## Events offered by the core hook bus
`ev_tick(ctrl)` 30 Hz UI task; `ev_draw(bmp, ctrl)` after each frame (y=0 = bottom row); `ev_key`, `ev_enc` (return non-zero to consume); `ev_settings(menu)` adds rows via `core_additem`; `ev_render_in/out` at audio-interrupt level, keep short. Handlers are C functions, arguments on the stack, d0-d1/a0-a1 free, result in d0. `[doc]` {elekloader-adapting}

## SRC machines
- Stock machines at sound byte `+0x7E`: 0 ONESHOT, 1 WERP, 2 REPITCH, 3 SLICE. `[doc]` {elekloader-adapting}
- Custom machine descriptor = six longs: id, name, short name, icon, params, render. `[doc]` {elekloader-adapting}
- IDs 4-127, permanent once kits store them. **Registry** (only what we have seen claimed):

| ID | Machine | Source |
|---|---|---|
| 4 | NEIGHBOR (digineighbor) | {elekloader-adapting} |
| 5 | DIGISLICER | {elekloader-adapting} |
| others | other machine mods (digisophie, DT-FM, digigrain, digidrum, digistring ...) use IDs we have not read | to mine |

## Hardware (teardown reports, not verified)
- One teardown (revision not named by the author) reads: CPU NXP MCF54415 (ColdFire), eMMC KLM461FETE (4 GB per one line, "4Gb" in another), Spansion 128 Mb flash ("FL128", partial name), Nanya NT5U128M8HE RAM (author says 1 GB, but that part number suggests 1 Gbit = 128 MB - likely a unit error), audio codec AK4621EF, a MIDI transceiver and 6N137 opto-isolator; analog and digital sides separated by optocouplers; a debug header (JTAG/UART guessed, not verified). Author speculates the 128 Mb flash holds boot code or all code, with the rest loaded from eMMC - unknown. `[?]` {dt1-teardown}
- A forum photo comparison names the eMMC differently (THGBMDG5D1LBAIT, 4 GB) and the CPU MCF54415CMJ250 - the sources disagree on the eMMC part. `[?]` {elektronauts-dt2-intro}

## Ecosystem snapshot, Digitakt mk1 (altstrument 2026-10-31: 13 firmware entries + screendump; elektronmods lists 20 Digitakt entries)
Distribution is uniform: every mod is an elekloader mod patching the user's own `Digitakt_OS1.53.syx` (some now 1.54) - none ships firmware. Listings: {alt-digitakt} {em-list}. Facts read from the mod READMEs:
- **digiemu** - emulates the Digitakt mk1 firmware on a ColdFire CPU with a **patched Unicorn (six patches: three fix ColdFire flags and the multiply-accumulate unit, three make it fast enough for live audio)**; clickable panel, screen, keys, LEDs, sequencer, +Drive, live 48 kHz audio; tested on OS 1.53 (SHA-256 `9bdd44bb...29bcc92`), other mk1 releases offered as untested; runs about 2.5x faster than the hardware needs; first boot installs the factory project (~25 s, once per firmware); limits: factory sample library absent, 44.1 kHz pitch unverified, interrupt controller approximated, loading samples restarts the firmware (~15 s); its README still says Digitone mk1 is not supported although the directories list it. A content guard in CI rejects firmware, snapshots, card images and files over 1 MB. GPL-2.0-or-later. `[doc]` {digiemu-readme}
- **digislicer** (1.2 README; 2.5 per altstrument) - hold YES ~1 s on a SLICE track's SRC page to open the editor; slices keyed to the sample content and saved to the +Drive about one second after the editor closes (`/cfw/slices.a`, `/cfw/slices.b`; a `/cfw` folder appears in the sample browser); max 64 slices per sample; GRID gets a step past 64 = AUTO (transient slicing); a kit saved with AUTO plays the 64-slice grid on stock firmware; 1.1 and 1.2 "not yet tried on a unit" (an earlier combined build 1.8J ran on one); cold-boot comparison vs stock showed one 1 ms silent block from hook-bus timing. `[hw]/[emu]` {digislicer-readme}
- **DigiFilter** - patches three sites (widen Filter Type range 7->11, re-point the TYPE label formatter, hook the per-voice filter call; stock types tail-call the stock filter); DSP is **integer-only, no FPU, no libgcc**; BP/BP2 = trapezoidal state-variable filter, COMB/TRASH = two feedback combs; coefficients smoothed per block; per voice per block (digiemu): stock TYPE 1 ~2,400 instructions, BP/BP2 ~2,800, COMB/TRASH ~1,750 (the README claims "at or below stock" - contradicted by its own BP figure); BP can clip at high RESO (no output saturation); response curve cosmetic; needs core 2.1; emulator-tested only in the README (later versions: v1.1b lowers per-voice cost, v1.2 caps Digitakt OB resonance at 75 %). `[emu]` {digifilter-readme}
- **digi1_mods** - POLY: extra notes borrow voices from the track idle longest (excluding muted tracks, same-moment triggers and removed tracks); SETTINGS > POLY pool is per pattern and saved with the project (power-cycle persistence since 2.0d); Digi Matrix 8 routing slots (any track's LFO1/LFO2 to any parameter, depth -64..+64); Digi EQ 4-band master EQ after the compressor, on the master mix so all outputs carry it; utility page scope/spectrum (30 Hz-20 kHz, 128 log columns, 60 dB range)/X-Y/tuner (~12 Hz-3 kHz); builds v3p (unit shows 1.5b), v3q-spectrum (1.5c) not yet tested, **v3r-all (1.5d) confirmed on hardware**; the elekloader build 2.0d is emulation-only; Song mode disabled in stand-alone builds. Uses the unit's version string as a build label. `[hw]/[emu]` {digi1-readme}
- **digisophie** - fixed-point adaptation of Sophie for Schwung; uses the stock AMP, filter, mixer and effects path; SRC knobs A TUNE, B MODEL (FUSE/BOOM/PIPE/SHARD), C BR, D SAMP (unused), E SWEEP, F METAL, G FBK, H COLOR, parameter-lockable; HOLD set to NOTE so TRIG LEN sets release; retrigger chokes the previous voice; one instance runs without FAST AUDIO, **two practical on hardware with FAST AUDIO**, eight-track operation not claimed; build S027 hardware-tested with the digihealth configuration. `[hw]` {digisophie-readme}
- **DigiPools** - adds a POOL machine (DIGIPOOLS, version string `DPLS`) that turns the Chromatic keyboard into a pool player over the project's RAM sample slots 1..127; recorded trigs get a SAMP lock; OS 1.54; repo `freeze157-prog/digipools`, created 2026-10-24. `[doc]` {digipools-page}
- **Tone+FX, DigiSplash, DigiCandy, digihealth** also run on the Digitone mk1 - see [`digitone.md`](digitone.md).

## Facts about specific mods (for compatibility)
- Digitakt II is explicitly out of scope for the mk1 mods (e.g. DigiFilter). {digifilter}
- digihealth's FAST AUDIO gives a lower DSP load with the same audio (elekloader v0.2.0 notes; checked alone in digikit's emulator with cold boot). {elekloader-readme}
- Test state varies per build: see the project pages; several are emulator-only.
