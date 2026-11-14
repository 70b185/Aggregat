# Digitakt (mk1)

Coverage: **good**. Everything below targets OS 1.53 unless stated. Projects: [../../catalog/digitakt.md](../../catalog/digitakt.md)

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

## Render path, injection point and key tables (digigrain's platform skills, OS 1.53, Ghidra plus digiemu) {digigrain-skills}
A compact, agent-oriented map of OS 1.53 exists in digigrain's `.claude/skills/digitakt-firmware-map` (and nine sibling skills: hook bus, DSP, recorder, audio input, testing). **Read it before tracing the engine yourself.** The essentials:
- **Free areas for mods:** DDR `0x47BE0000-0x47C00000`; SRAM `0x8000F700-0x80010000` and `0x80003360-0x80008000`. `[doc]`
- **The cleanest place to add a machine:** each voice's mono block at **`0x80001a18 + 128*v`** (32 x int32, Q31). Anything written there before the per-voice processing step gets the stock filter, amp, pan, level, mute and effects for free, and resampling records it too. Bit reduction acts *inside* the stock voice synth, before that point. `[emu]`
- **Samples:** table at `0x403193a0`, 16 bytes per slot `{PCM ptr, ?, length, ratio Q30}`, valid slots 0..130 (`0x82` is the audition slot); PCM is **s16 mono**. A voice advances its position by 32 x the pitch ratio per block. `[emu]`
- **Parameter descriptors:** `0x401a9d9c + 52*id`. 44 code sites clamp ids >= 164 to 0, so new parameters must fit below 164 or every one of those sites needs a patch. `[doc]`
- **Heap:** `operator new` is `0x400d4180`. **Never free a firmware-owned buffer:** operator delete halts on a non-heap pointer. Never write message `+0x48` (the next link). `[doc]`
- **Bound the worst case, not the average:** an early granular engine froze the UI at low pitch, because fixed-length source grains became long, the pool filled up and every voice ran its worst case. The fix made grain length independent of pitch and capped overlap. `[hw]` ([I24](../INCIDENTS.md#i24-a-granular-engine-froze-the-ui-at-low-pitch))
- **Recorder (static reading, not yet run in an emulator; digigrain's recorder skill):** the record buffer holds 1,584,000 frames (33.0 s at 48 kHz mono) as two planes written together, the top 16 bits at `0x4237DF90 + 2n` and bits 8-15 at `0x421FB410 + n`, so the reassembled sample is 24-bit. The source selector fills a mono capture block at `0x800032c4`; sources 9-16 (TRK1-8) are a straight copy of the voice block `0x80001a18 + 128*(t-1)`, so a machine that writes the voice block can be resampled for free. Sample slot `0x82` is the recorder's preview slot; a sample-table setter at `0x400763b4` fills a slot and, below `0x80`, its 255-entry slice table. `[doc]` {digigrain-skills}
- CPU naming: this map says MCF54418; a teardown reads MCF54415. Both are MCF5441x and run the same code. `[?]`

## Events offered by the core hook bus
`ev_tick(ctrl)` 30 Hz UI task; `ev_draw(bmp, ctrl)` after each frame (y=0 = bottom row); `ev_key`, `ev_enc` (return non-zero to consume); `ev_settings(menu)` adds rows via `core_additem`; `ev_render_in/out` at audio-interrupt level, keep short. Handlers are C functions, arguments on the stack, d0-d1/a0-a1 free, result in d0. `[doc]` {elekloader-adapting}

## SRC machines
- Stock machines at sound byte `+0x7E`: 0 ONESHOT, 1 WERP, 2 REPITCH, 3 SLICE. `[doc]` {elekloader-adapting}
- Custom machine descriptor = six longs: id, name, short name, icon, params, render. `[doc]` {elekloader-adapting}
- IDs 4-127, permanent once kits store them. **Registry** (only what we have seen claimed):

| ID | Machine | Source |
|---|---|---|
| 4 | NEIGHBOR (digineighbor) | {elekloader-adapting} |
| 5 | DIGISLICER, and **reslicer on purpose** (kits saved with digislicer's machine load and play on reslicer) | {elekloader-adapting}, reslicer README |
| 6 | GRANULAR (digigrain) | digigrain `mods/digigrain/CLAUDE.md` |
| 7 | SOPHIE (digisophie; taktone-extended reuses the same id) | digisophie `DSP.md`, taktone `SECONDARY-CPU.md` |
| 9 | DT-FM | DT-FM `src/mod.json`, `DSP.md` |
| 10 | vawt | vawt README |
| 27 | DigiMono (as carried by Vampire Manga OS) | Vampire Manga OS `THREE_FX_AND_MACRO.md` |
| 69 | OB-1 (elektrob-1), the same id on Digitone mk1 | elektrob-1 README, `docs/architecture.md` |
| 77 | SAY IT (sayit) | sayit `machines/digitakt/mod.json` |
| others | digidrum (repo unreachable) and machine mods published after 2026-11-02 | check their `mod.json` |

**Clash watch:** two mods with the same id cannot be in one build, and a kit saved with one plays the other. Before you pick an id, check this table and the `mod.json` files of the mods your users combine. (Collected 2026-11-02; ids are claims from each project, not checked against builds.) `[doc]`

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

## elekloader core 4.1-4.3 and compatibility (2026-11-10) {elekloader-core-dt1}
- Core 4.2 adds a live-note event (live notes before the voice; a handler can take them). Stock NOTE_ON/NOTE_OFF are at `0x400d53dc`/`0x400d575e` on 1.53 and `0x400d5604`/`0x400d5986` on 1.54; digipoly, digislicer and OB-1 hook these routines themselves. Core 4.3 adds a MIDI CC event at `0x400158ec` in the CC router `0x400158d2` (same on 1.53 and 1.54). `[doc]`
- Core 4.1 patches the master-output sites itself, so Digi EQ 1.0c and Tone+FX's Digitakt files (3.2a3, 4.0c), which patch the same places, refuse to link with it; the builder falls back to core 4.0 for them. Tone+FX and Digi EQ also cannot go together: both take the master view's draw, the render site `0x400721e6` and kind-0 pages. `[doc]` {elekloader-cores} {tonefx-dt-port}
- Up to Tone+FX 4.1a its author found no spare per-pattern MIDI block on the DT1 (4.3b then used a saved MIDI-track record, below); the kit spare at kit + `0x530` and the pattern spare bytes are already used by Digi Matrix, Digi Poly and Digi EQ, so Tone+FX up to 4.1a keeps its Digitakt data in RAM, lost on power cycle or project load. `[doc]` {tonefx-pattern-storage}
- **Tone+FX 4.3b keeps its Digitakt settings in MIDI track 8's saved kit record** at kit + `0x8ba` (the track reserved on channel 16, block magic "DGX4"), so the stock serializer saves them and they survive a pattern switch, a project load and a power cycle. Users must leave MIDI track 8 alone; another mod using that record clashes. Not yet tested on a unit. `[doc]` {tonefx-43b}
- **Kit MIDI-track records:** the DT1 kit holds eight MIDI-track records at kit + `0x59a` + t x `0x70`, each `0x6c` bytes; the stock pattern serializer carries only the first 41 words of each to the +Drive, and elekloader rewrites the byte at record +8, so Tone+FX's block starts at record +`0x10` (+`0x10`..+`0x51`). On OS 1.54 save runs `0x4007a300` -> `0x40079d22` and load `0x40079f86` -> `0x40079cc2`. `FW_TEMPO` is at `0x4020db60` on 1.53 and `0x4020df10` on 1.54. `[doc]` {tonefx-records}
- **GLIDE (ClaidArremer) stores PORT and LEG in the MIDI chord-note fields NOT3 and NOT4** of the pattern, which audio tracks never play, so stock saves, locks, copies and clears them like any trig parameter, and old patterns open with both OFF. Another mod using NOT3/NOT4 on audio tracks clashes. 0.4 tested on a Digitakt mk1, OS 1.54. `[hw]` {glide-dt}
- **elekloader Digitakt cores and Tone+FX 4.3b:** core 4.0 lacks the `fw_tempo` export the stutter needs and cores 4.3 and 5.0 claim its master sites (render `0x400721e6`), so the release ships its own core-4.0.1 (S21). On 1.54 the Digitakt file takes `.run` 20,352 and `.bss` 104,300 bytes. `[doc]` {tonefx-43b}

## Modwerk Digi Perform (OS 1.53/1.54, 2026-11-11) {modwerk-digiperform}
- **Cold boot vs LOAD PROJECT:** after SAVE PROJECT, a cold boot came back with the sound records' spare bytes cleared, and a stock parameter written straight into the kit was lost too; LOAD PROJECT kept both. Mod data kept in a kit's spare bytes needs its own path through a power cycle (I77). `[hw]` (power cycle) / `[emu]` (the cause)
- **The working image survives a power cycle:** Digi Perform 0.1.4 copies its data into the working image, the serialized project in RAM that the Digitakt writes to the +Drive at power-off and starts from (`0x406490e8` on OS 1.54, `0x406480e8` on 1.53); the assignments then survived a power cycle on the author's unit (I77). The stock CC send queue is `0x400e0b94` (1.54) / `0x400e096c` (1.53), called from the UI task only. `[hw]` {modwerk-digiperform}
- **Shared hook sites read registers:** CC Names' hook at `0x40030daa` reads the parameter id from d2; Digi Perform called that site as plain C with d2 unset and SRC labels read ERR (I101). `[hw]` {modwerk-digiperform}
- **Patch sites in use:** render after the LFOs `0x40077eb2` (shared with Digi Matrix); TRIG view draw `jsr` `0x400368e0`; SRC-page routines also patched by CC Names and Digi Mono (`0x40030daa`, `0x40032d36`, `0x40032d16`) and by DigiChain/DIGISLICER (`0x4000f534`). Check these before you claim one. `[doc]`
- **Load:** heavy Digi Mono machines with Overbridge streaming run near the audio budget (96 % load shown on a stock page). Digi Perform 0.1.3 takes 26,776 bytes. `[hw]`

## Digi CMI on the unit (OS 1.54, 2026-11-12) {digicmi-026}
- **The stock render already takes about 85 % of the audio interrupt:** Digi CMI's meter (render entry to exit over the block period, timed with PIT0's counter `0xFC080004`, read only; 0.485 µs a tick, about 1,375 ticks a block of 667 µs) read 85 % peak right after boot. In digiemu the render (`0x40077428`-`0x400784c8`) runs about 85,000 instructions a block, 98 % of them stock's; at about 1.6-1.7 cycles an instruction that fits the 85 %. The UI gets what is left, so a few percent more load show as lag everywhere. `[hw]` (meter) / `[emu]` (instruction count)
- **Voices that never switch off cost load:** released voices kept looping silently and took the meter from 86 % to 94 % (I81). Switch a voice off only by the real amp envelope (below), and clear its on flag (voice + `0x28`), not only its end flag. Digi CMI 0.30 switches a voice off after the amp envelope stays below -90 dB for 64 blocks; 0.26's -72 dB rule read the filter envelope and cut sounding notes (I89, S20). `[hw]` (load) / `[emu]` (rule) {digicmi-026} {digicmi-037}
- **Voice internals (digiemu):** voice + `0x00` is the PCM pointer of the sample playing, + `0x10` the gain, + `0x14` the sample length, + `0x28` voice on. AMP kit slots: attack 38, hold 39, decay 40, overdrive 41, delay send 42, reverb send 43, pan 44, volume 45. digiemu does not model the PIT counters. `[emu]`
- **The real amp envelope is at `0x4199ed64 + 8*v` on OS 1.54** (8 bytes a voice: +0 phase, +4 value), updated by the render's amp stage `0x400716c0` from kit slots 38-40 (attack, hold, decay). Phase 2 attack (value rises as negated Q31), 1 hold, 0 decay (|value| / 2^31 is the level, 0 when idle). After a release it matched the output level within about 5 %. On OS 1.53 presumably `0x4199dd64`, unverified. `[emu]` (1.54) / `[?]` (1.53) {digicmi-037}
- **elekloader's `fw_amp_env` export (`0x4199ef54` on 1.54) is the filter envelope, despite its name:** `0x40073304` fills it from kit slots 29-32 and 35; it fell to -135 dB while a held looping note's output stayed constant. Do not use it as a voice's level (S20). `[emu]` {digicmi-037}
- **Velocity is a square law in stock:** both sample players pass the clamped velocity to `0x40074c60`, which returns gain = (vel/127)^2 x (VOL/127). `[emu]` {digicmi-037}
- **Count divisions in per-sample code:** a `rems.l` costs about 20-35 cycles on this ColdFire but one instruction in digiemu's profile; a per-sample remainder in Digi CMI's RETRO made the UI crawl on the unit (I91). `[hw]` (lag) / `[emu]` (fix) {digicmi-037}
