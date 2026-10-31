# Digitakt (mk1)

Coverage: **good**. Everything below targets OS 1.53 unless stated. Projects: [../../devices/digitakt.md](../../devices/digitakt.md)

## Basics
- OS targets in use: **1.53** (nearly all mods), **1.54** (elekloader v0.4.0: "linkable mods and whole builds"). A mod built for 1.53 is refused on a 1.54 stock file. `[doc]` {elekloader-readme} {elekloader-adapting}
- Official minimum OS for Transfer-based update: 1.20. `[doc]` {elektron-support}
- Container unsigned? Not stated for Digitakt; Digitone mk1 is unsigned (trailer = 32 zero bytes). `[?]`
- Recovery: hold FUNC at power-on -> TRIG 4 (OS UPGRADE) -> send the stock `.syx`. `[doc]` {elekloader-readme}

## Memory and code placement (core 2.x, elekloader)
- Budget shared by all mods: **128 KB for `.run` + `.bss`**, **2304 bytes of fast SRAM** (`.fast`). `[doc]` {elekloader-adapting}
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

## Facts about specific mods (for compatibility)
- Digitakt II is explicitly out of scope for the mk1 mods (e.g. DigiFilter). {digifilter}
- digihealth's FAST AUDIO gives a lower DSP load with the same audio (elekloader v0.2.0 notes; checked alone in digikit's emulator with cold boot). {elekloader-readme}
- Test state varies per build: see the project pages; several are emulator-only.
