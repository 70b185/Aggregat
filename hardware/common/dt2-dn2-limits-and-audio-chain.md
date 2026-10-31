# Digitakt II / Digitone II - firmware limits, DSP calling convention and the audio chain (DT2 1.17, DN2 1.12)

Sources: digikit findings 100 ("Limits for content modules"), 53 ("The shape of the stock machines, effects and parameters"),
57 (capacity), 73 (dnfw coexistence), read 2026-10-31. These are static reads of the images. digikit marks many rows **[V]** (two agents
checked the same image bytes); for us they are `[doc]`, second-hand. Keys {digikit-f100} {digikit-f53} {digikit-f57} {digikit-f73}.
Addresses are for these exact OS versions only (rule C1).

## 1. Machines and parameters (ColdFire)
| Item | DT2 1.17 | DN2 1.12 |
|---|---|---|
| Stock machine types | 7 (bound `moveq 6` at `0x400c89a4`) | 5 (`0x400c25f2`) |
| Type storage | one byte, Sound `+0xa2` | one byte, `+0xde` |
| Per-type tables sized to the stock count (a new type needs a row in **each**) | descriptors `0x4293b960`, MIDI CC/NRPN `0x400dab9e`/`0x400dac80`, UI list `0x40052a2c` | `0x400dc978`, `0x400dca5a`, `0x400dc18e` |
| Parameter table | `0x4020f59c`, 275 rows of `0x3c` B | `0x401f83a4`, 321 rows |
| Row layout | `+4` sound index, `+8/+c/+10` min/max/default, `+28` name, `+30` short name, `+34` formatter pointer | same |
| Knobs per page | 8 + Track Level | 8 + Track Level |
| Pages per machine | 1 (SRC has one descriptor) | set by data, no cap found |
| Machine slots saved and sent to the DSP | 10 (sound index 25-34, shared by all types) | 40 (25-64) |
| P-locks | any saved slot, 80 lanes per pattern | same |
- **The parameter table has 53 absolute references to its base, so rows cannot be appended in place.** Projects (digikit `core/params`, dnfw's hook bus) relocate the table and raise the bounds. On DT2 no stock machine uses knob C. `[doc]`
- There are 55 FX rows (codes `0x69-0x9f`, the same on both devices) and no free FX rows. A new FX code defaults to 0 in a new kit unless the FX index-to-code table is patched (DT2: 71 words at `0x4316e854`). `[doc]`

## 2. Memory
| Item | DT2 1.17 | DN2 1.12 |
|---|---|---|
| ColdFire RAM | 128 MiB, SP `0x48000000` | 128 MiB |
| Firmware heap | 32 MiB buddy heap at `0x44f39c40` | at `0x4464bbf0` |
| **Unreferenced ColdFire RAM** (where mods put code/data) | `0x47e8b000-0x47fe0000`, **1.33 MiB** | `0x4671a000-0x47fe0000`, **24.8 MiB** |
| SHARC L2 | 1 MiB `0x20000000-0x200fffff` | same |
| Stock L2 loaded end | `0x2001ab7c` | `0x2008823c` |
| Free L2 | 914,564 B below `0x200fa000` + 8 KiB at `0x200fe000` | 466,372 B + the same 8 KiB |
| `0x200fa000-0x200fe000` | a cache range set at boot, **keep out** | same |
| Free L1 | block 1 `0x2d7564-0x2ec000` (84 KB), block 2 `0x300000-0x31c000` (112 KiB) | block 1 60 KB, block 2 the same |
| SHARC DDR | 512 MiB configured; stock loaded to `0x8055e890`, fill `0x80a00000-0x82a001c4`, **sample pool 400 MiB from `0x8422b9c8`** (4 KiB pages) | 512 MiB; nothing referenced above `0x80530c00` |
- The free L2 above is a **static** result. The owner measured problems on a real DT2 past `0x200f5a74` (see [`../devices/digitakt-2-sharc-measured.md`](../devices/digitakt-2-sharc-measured.md)), so treat the top of L2 as unsafe in practice. `[?]`
- Cache config `0x414141`: 16 KiB I, DM and PM caches at the block tops. L1 blocks 0 and 3 are full. `[doc]`

## 3. Time and DSP link
- 1 GHz core (20 MHz x 100 / 2), 32-sample blocks at 48 kHz = 1,500 blocks/s = 666,667 cycles/block. This is confirmed on a real DT2 by the owner's idle counter. `[hw]`
- DN2 has 16 voice slots chosen at note-on, not tied to tracks, so it has no fixed stereo pair. DT2 has 32 voices: even = L, odd = R. `[doc]`
- digikit's run-time limits (its own, not the firmware's): 8 modules, 4 FX slots, 512 KiB (DT2) / 320 KiB (DN2) DSP area in 64-byte granules, 64 KiB per module file. The firmware would allow about 900 / 450 KiB. Every limit was filled in the emulator and the next module was refused with a clean error. `[emu]` {digikit-f57}

## 4. SHARC calling convention of the stock code (selcc emits the same)
- Call: `CALL (linked, delayed)` (Type 25a). Prologue `I7 = MODIFY(I7, -N)`, saves to `DM(I6 - n)`. Return `I12 = DM(I6, M7); JUMP (M14, I12) (DB)` with `RFRAME` in the delay slot.
- Arguments R4, R8, R12, then the stack (`DM(I6, M6)`). Result in R0 (F0; R0:R1 for 64-bit). Render kernels return nothing and write through pointers.
- Callee-saved: R3, R5-R7, R9-R11, R13-R15, I0-I3, I5, M1-M3, B3.
- **Constant registers that voice code never writes: M5 = 0, M6 = 1, M7 = -1, M13 = 0, M14 = 1, M15 = -1.** Indirect jumps use DAG2 (`JUMP (M13, I12)` relies on M13 = 0).
- The exception is the float divide `0x1c06ba` (plain CALL, R4/R8 in, F0 out). `[doc]`
- Parameters: the ColdFire smooths them (one-pole) before the frame. The DSP converts s16 to float once per block (scale 1/32512) and ramps per sample by (new - old)/32 inside a block (/64 in DN2 FM operators).
- DT2 sample machines and DN2 FM TONE render 64 samples at 96 kHz and decimate to 32 with a half-band filter.

## 5. The DT2 audio chain per block (planar floats, 32 L then 32 R; voice blocks mono)
| # | Stage | Buffers |
|---|---|---|
| 1 | frame copy to DM `0x2558dc`; unpack `0x1c24e9` x32 | track records `0x2506ec + 0xdc*t` |
| 2 | voice render `0x1c4ecf` (STRETCH: `0x1c5576`) | mono block `0x252df8 + 0x80*v` |
| 3-5 | level, bit reduction, overdrive, SRR, filter, pan | track bus `0x252df8 + 0x100*t` |
| 6 | sends + FX `0x1c18a6`: chorus `0xb82680`, delay `0xb82150`, reverb `0xb80fe0` | FX return `0x254778` |
| 7 | master `0x1c207b`: dynamics, clip, overdrive, gain ramp | -> `0x25f180` |
| 8 | post-master `0x1c14e7`, `0x1c80f2`, `0x1c28b5` (probably USB out) | |
| 9 | Q31 converter `0x1c7734` | -> output ring |
DN2 has the same shape with its own drivers: sends `0x1c1738`, master `0x1c1f1e`, converter `0x1c9fd2`. The FX units, dynamics, overdrive and filters are shared code across the two devices.

**Where an effect can sit** (patch a callee's first instruction rather than a call site in the big orchestrator):
| Site | DT2 / DN2 | Sees | Note |
|---|---|---|---|
| H0 converter call | `0x1c7734` / `0x1c9fd2` | final master | probably **not** in USB audio |
| H1 post-master | `0x1c14e7` / `0x1c244d` | master at `0x25f180` / `0x268438` | before USB out and meters |
| H2 sends driver | `0x1c18a6` / `0x1c1738` | 16 track buses before sends | DN2 has slots, not tracks |
| H3 master entry | `0x1c207b` / `0x1c1f1e` | FX return and input buses | |
| H4 an FX unit | chorus / delay / reverb entries | replaces a stock unit | in/out pointers DT2 `0x252d40`/`0x252d48`, DN2 `0x257e70`/`0x257e78` |
| H5 voice chain | `0x1cdd8b` / `0xb8251b` | one mono voice block | 32 calls per block |
- At H2/H3 SIMD is off and no DO loop is active. The stock FX state lives in DDR: chorus `0x80459388`, delay `0x8005912c` (rings of 524,288 floats, max 8 s), reverb `0x80000018`. FX rings wrap by index arithmetic; FX units never write B or L registers, but the voice renderer does and restores them. Static FX cost: chorus 7.1k, delay 6.0k, reverb 17.2k instructions per block. `[doc]`
- The stock machines share almost no code (each machine is one large function). Only the post-voice chain and a few maths helpers are shared between DT2 and DN2. `[doc]`

## 6. Two mod platforms in one image (dnfw + digikit, DN2 1.11) {digikit-f73}
A static comparison found 361 identical writes, 8 digikit hook sites that a dnfw mod also changes, 10 dnfw RAM chunks inside digikit's expansion region, and both rebuilding the DSP boot stream. Both platforms raise the same parameter and machine-type bounds. **They cannot be combined as they are.** Each mod should declare every range it writes so that tools (`dnfw mods overlap`, `patchkit --plan`) can detect collisions. `[doc]`
