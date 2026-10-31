# Digitakt (mk1)

Coverage: **good**. Everything below targets OS 1.53 unless stated. Projects: [../../devices/digitakt.md](../../devices/digitakt.md)

## Basics
- OS targets in use: **1.53** (nearly all mods), **1.54** (elekloader v0.4.0: "linkable mods and whole builds"). A mod built for 1.53 is refused on a 1.54 stock file. `[doc]` {elekloader-readme} {elekloader-adapting}
- Official minimum OS for Transfer-based update: 1.20. `[doc]` {elektron-support}
- Container unsigned? Not stated for Digitakt; Digitone mk1 is unsigned (trailer = 32 zero bytes). `[?]`
- Recovery: hold FUNC at power-on -> TRIG 4 (OS UPGRADE) -> send the stock `.syx`. `[doc]` {elekloader-readme}

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

## Facts about specific mods (for compatibility)
- Digitakt II is explicitly out of scope for the mk1 mods (e.g. DigiFilter). {digifilter}
- digihealth's FAST AUDIO gives a lower DSP load with the same audio (elekloader v0.2.0 notes; checked alone in digikit's emulator with cold boot). {elekloader-readme}
- Test state varies per build: see the project pages; several are emulator-only.
