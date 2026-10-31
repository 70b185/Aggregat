# Digitone II (OS 1.11) - engineering reference from the digitone-2-modding-skill

Source: complex-ping's agent skill (MIT) and its reference files. **All addresses are for stock OS 1.11 only** - the author says so; Overtone ports the work to 1.12 separately. Everything here is second-hand. `[hw]` = the skill's author reports a real-unit incident or test; `[doc]` = stated without a test result. Overview and other OS versions: [`digitone-2.md`](digitone-2.md).

## Hardware as described
- Main CPU: ColdFire V4e, big-endian - the skill writes "MCF5445x", digikit writes MCF54415. Probably the same family; treat the exact part as `[?]`. It runs UI, sequencer, parameters, p-locks, LFOs and builds the **2688-byte frame** sent to the DSP for every audio block. `[doc]` {dn2-skill-firmware}
- Audio DSP: SHARC+ ADSP-21569 at 1 GHz does all audio (4 SYN machines, filters, amp, pan, chorus/delay/reverb, master). `[doc]` {dn2-skill-firmware}
- Audio I/O: physical inputs are IN L/R only; USB class-compliant mode adds 2 channels host->unit and 2 back. `[doc]` {dn2-skill-firmware}
- One DSP block = 32 samples at 48 kHz = **1,500 blocks/s**, budget about **666,667 cycles per block**; stock idles at roughly 63-65 % load on the unit. `[doc]` {dn2-skill-firmware} {dn2-skill-sharc}

## Stock addresses (OS 1.11)
| What | Address / value |
|---|---|
| MAIN OS (section 3) | `0x40000400`, 3,192,192 bytes, GCC C++ with RTTI (dnfw's README gives 3,085,696 bytes for a Digitone II image without naming the version - different builds) |
| SPI frame ColdFire -> DSP | 2688 B from `0x80005e60`, transfer 2748 B; driver call `0x400cf7be(2688, tx, 2748, rx)`; TX DMA list `0x80002510`, 4 B per entry |
| Reply DSP -> ColdFire | 2748 B, lands at `0x800053a4` |
| Voice -> track map | `0x8000dda0[voice]` (also frame +0xa5a) |
| DSP view of FX params | `0x25CE54 + 2*id`, scaled x1/32512 |
| Value setter slot bound check | `0x40037bd0`; getter bound `0x4003717c` |
| Live sound of voice v | `0x800052A8[v]`; live sound of track t = `*(0x800052A0) + 52 + 1163*t` |
| Per-track arp counter / state | `0x4058e918[t]` / `0x405984a8 + 40*t` |
| Exception reporter | `0x4011ea6a` (code that falls into zeroed `.bss` dies here) |
| Audio ISR RTE | `0x40027bbe` |
`[doc]` {dn2-skill-firmware} {dn2-skill-coldfire}

## Container as seen by this skill
`.syx` = SysEx (`F0 00 20 3C 15 00 ...`) with 8-in-7 packing, an 8-byte preamble (length, checksum), then an ELE3 container of aPLib sections: **5** meta, **2** bootstrap (holds signing-key material - never edit), **3** MAIN OS, **4** updater, **7** SHARC, **8** accessory ARM. Integrity: per-packet checksums, a 32-bit content checksum and an HMAC-SHA256 trailer, all recomputed by dnfw. `dnfw inspect OUT.syx` must print 21 `[ok]` lines including "HMAC-SHA256 reproduced". `[doc]` {dn2-skill-firmware} {dn2-skill-setup}

## Free memory
- **ColdFire:** `0x46700000..0x46900000` unused by stock; cfmod links at `0x46800000`, dnfw uses `0x467c8000..0x467fffff`. More RAM above is plausible but must be verified (fill, reboot, read). `[doc]`
- **SHARC L2:** usable `0x20088400..0x200B0000`; stock loads L2 code only up to `0x2008823c`. Not above `0x200B0000` (stock data points to `0x200C0008` and `0x200C1F84`; `0x200FA000..0x200FDFFF` is non-cacheable DMA buffers; L2 is shared with the boot ROM and **one block there stopped a unit from starting**). New boot blocks: code at `0x20090000` (sw `0xBC8000`), data at `0x20098000` onward - hardware-proven. `[hw]` {dn2-skill-firmware} {dn2-skill-sharc}
- **SHARC DDR (512 MB):** stock references go up to `0x8052FBE0`; `0x80800000` and above read back untouched on hardware. Large tables can live in DDR blocks (sw `0x800000` on, byte `0x80A00000` on) but every fetch is slow. The delay's L/R rings are masked to 2^18 samples; their upper halves are free if delay time is capped. `[hw]` {dn2-skill-firmware} {dn2-skill-sharc}
- **Power-on DDR is garbage** (`0xFFFFFFFF`, a NaN, is common). A NaN that reaches a feedback state (send FX, say) silences the unit until restart. The emulator zero-fills DDR and hides this: fill new DDR with `0xFFFFFFFF` in tests. `[hw]` {dn2-skill-firmware}

## ColdFire-to-DSP frame (per voice, big-endian halfwords; the DSP swaps halves of each 32-bit word)
| Offset | Content |
|---|---|
| +0x00 | command (3 = render) |
| +0x02 + 2v | note << 8 |
| +0x22 / +0x26 | note-on mask (bit v); +0x24 / +0x28 note-off |
| +0x34 + 2v | velocity << 8; +0x54 + 2v velocity curve |
| +0x74 + 2v | voice level |
| +0x94 + 2v | machine (0 FM TONE, 1 WAVETONE, 2 FM DRUM, 3 SWARMER, 4 MIDI) |
| +0xd8 | tempo x 120 |
| +0xda + 146v | voice sound record |
| +0x9c8 + 2*id | FX/global params 25..69 (chorus 25-31, delay 32-40, reverb 41-48, ext-in 49-59, master comp 60-67) |
| +0xa58 | master tune x 10 |
| +0xa5a + 2v | voice -> track |
Values are raw (knob << 8 | fine). Details are in the `dn2synth.py` docstring of the skill. `[doc]` {dn2-skill-firmware}
- **Side channels:** the DMA moves 1374 halfwords; the 30 halfwords after the 2688-byte frame (data halves of TX entries 1344..1373) are never rewritten by the stock driver and reach the DSP - write packets there from a hook just before the driver call (header word + checksum, round-robin if larger). Return: reply word 0 = the DSP's cycle count for the block (a load meter), +0x16 = master compressor gain reduction, `+0xa9c..+0xabc` (ColdFire `0x80005e40`, 16 u16) is unused by stock and free as a DSP -> ColdFire channel. `[doc]` {dn2-skill-firmware}
- **Timing:** the DSP renders on the codec clock and does not wait for the ColdFire. A frame that arrives after render started is dropped and the previous frame repeats, including its note-on masks ("the trig lights, no sound"). This is what happens when the ColdFire audio ISR overruns. `[hw]` {dn2-skill-firmware} {dn2-skill-coldfire}
- **Voices are not tracks.** The DSP renders 16 voices; the ColdFire allocates them per note and copies the track's sound into the voice record; unison uses several voices per note. Note path, lock applier, LFO evaluator and per-voice mirror blocks all work per voice - map voice -> track everywhere. The skill calls this the #1 bug source. `[doc]` {dn2-skill-firmware} {dn2-skill-coldfire}

## ColdFire hook rules
- Hooks are `jsr stub` / `jmp stub` over N displaced bytes; the build asserts the displaced bytes match stock. Arguments on the stack, result in d0 (GCC ColdFire convention); d0, d1, a0, a1 are scratch. A hook in the middle of a function must preserve d0, d1, a0, a1 for the code after it; a hook replacing a function's entry must preserve the callee's exit d0, d1, a0, a1 and copy every stack argument. `[doc]` {dn2-skill-coldfire}
- `movem` accepts only `(An)` or `d16(An)`: push with `lea -12(%sp),%sp; movem.l %d1/%a0-%a1,(%sp)`; recount `sp@(n)` after every push. Every symbol a hook references must be an entry or `--gc-sections` drops it. No libc: zero-initialised locals become `memset` calls and the link fails - use static const data or field-by-field stores. Appended asm after `.bss` lands in zeroed memory and the boot dies in the exception reporter. `[doc]` {dn2-skill-coldfire}
- Compiler: m68k GCC `-mcpu=5475 -Os`; build system `dnfw.patch.cbuild` with `cfmod.Mod` as startup loader. cfmod's loader cave: 138 bytes at `0x4028da6e` (copies the appended area to its load address at boot and calls your init); proven asm cave: 170 bytes at `0x4028ea02`; never use the ~64 KB of zeros near `0x402e2000` (the `.data` initializer). `[doc]` {dn2-skill-coldfire}
- **Audio ISR budget `[hw]`:** period ~0.67 ms per block; stock already uses ~64 % during playback; code at `0x46xxxxxx` costs roughly 4x more cycles per instruction than stock (DDR + cache misses) while SRAM at `0x8000xxxx` is cheap. Keep ISR C short, non-blocking, allocation-free; defer per-note work; **count DDR accesses, not instructions**. A laggy UI usually means ISR work is too heavy. `[hw]` {dn2-skill-coldfire}
- **Slot bounds:** every stock value, lock and LFO routine bounds `slot <= 100`; slots 0, 65 and 100 are holes; a sound stores 101 u16 values at `sound + 0x14 + 2*slot`. A new slot means hooking every one of those routines. Your own p-lock record headers need an ID no stock slot uses, and copy/paste/recount/clear routines must skip them. `[doc]` {dn2-skill-coldfire}
- **Pitfalls:** a new parameter record needs a guard record after the last entry (the drawer reads one past); enum formatters print ERR past their table; every per-sound side table needs a reset hook (sound reset and kit creation reuse memory); sound save rewrites LFO DEST words in slots 4, 12 and 20; skipping the stock redraw request can add ~1 s UI latency on hardware (the emulator does not show it); never draw the stock screen and then patch it (panel can receive a frame mid-draw); a new machine type means re-entering every per-type accessor bounded by `type <= 4`. `[doc]` {dn2-skill-coldfire}

## SHARC rules - each one "silenced or crashed a real unit at least once while the emulator passed" (author's statement) `[hw]`
1. **Whole 32-byte boot blocks.** A block of 8n+4 bytes boots in the emulator but leaves the unit silent from power-on (the L2 I-cache line fill over the block's end faults on ECC). Pad with `dspblocks.pad_lines`; check with `bootblocks.py SEC7`.
2. **Stock encodings only.** Some fields are decoded narrower by decoders than the silicon reads. A negative shift immediate (Type 6a, LSHIFT/ASHIFT by -k) needs its sign bits in the middle parcel (stock writes `023e 7800` for all 368 cases); zeros there are accepted by every decoder and emulator but the unit raises ILOPI and stops. Copy load/store encodings from real firmware and check access size (`4bfe 003c` is a BYTE load). Use the skill's bundled decoder, not digikit's VISA decoder or the SLEIGH SHARC Ghidra module (wrong tables per the author), and not the PRM's Type 2a/2b figures.
3. **Follow the PRM loop, DAG and branch rules.** Hardware loops: the last 11 instructions must be 48-bit ISA; a body shorter than 11 must be all ISA; end on a 48-bit instruction; no nested loops in your code. Branch spacing: at least 12 valid 48-bit instructions after every branch in the same block, no two branches within one 48-bit window; usual pattern NOP48, CALL, NOP48; end code with 12 NOP48. Same-DAG: never load a DAG register through the same DAG with post-modify (`M4 = DM(I0,M6)`), never store a DAG register through the same DAG (`DM(k,I6) = I0`) - load a data register first, then `M4 = R15`; save I/M registers via `R2 = In`.
4. **No L2 above `0x200B0000`.** Code caves only in unreferenced stock functions. Not as caves: L1 block tails `0x39C000-0x39FFFF` (caches, cause silence); the 12 NOPs after the SHBTB_CFG write at sw `0x1C12E8` (boot crackle); `0x1c0a6e-0x1c0b2f` (interrupt trampoline); `0x1c113e` (live at boot).
5. **Never read memory you did not write** (power-on DDR is NaN garbage).
6. **Preserve state at hooks.** Keep every register and flag that code after a hook reads; save what you touch in an absolute save area in L2 data. The FX-bus mixer takes R4 and R8 as arguments - **clobbering R8 at its hook lost all audio**. The emulator ignores stray memory accesses, so compare every callee register between stock and your build.
7. **The unit pays for memory, not instructions.** L2 and DDR accesses and DDR code fetches cost several times their instruction count (+7 % instructions once gave +21 % load); a per-voice DDR path can cost ~10x; a loop costs at least the larger of its memory and floating-point operations. Mitigate: skip effects at mix 0 (keep any state later code reads), keep hot state in L1/L2. EMUCLK counts instructions, the unit counts cycles including stalls.
8. Image limits: **2 MiB as received** (`cfmod.flash_check`; stock 1.11 uses ~1.87 MB, ~220 KB left) and **section 7 under 1 MiB**, or the ColdFire DSP loader refuses it and no DSP boots. Don't resize sections in place: ColdFire code goes into the appended area, DSP code into new boot-stream blocks.
Static/runtime checks the skill ships: `hwrules.py SEC7 --baseline STOCK` (reports only new violations), `sim.strict_hw` (raises HWRuleError), `sasm.lint` (branch spacing, prefetch, same-DAG, register whitelist, loop shape), `shapecheck.py`, `encodecheck.py`, `bootblocks.py`. {dn2-skill-sharc}

## Emulator coverage (skill's view)
- **SHARC** (`sim.py`/`simc.py`, ~200 blocks/s with the C core, ~7 on PyPy, ~1 on CPython): logic and arithmetic in the real frame, stock-vs-mod A/B, memory footprint, the PRM rules it encodes. **Cannot** cover timing, caches, stalls, interrupts, DMA, branch predictor, ECC, boot-ROM loading, power-on memory contents; "instruction counts under-predict the unit's load". One-time boot ~4 min (`dn2setup.py --boot`). `[doc]`
- **ColdFire** (digikit + `fastemu.py` + `cfkit.py`, 10-30 M instr/s): main OS in Unicorn with HLEs for flash, SD, panel, screen; boots to the main screen (~1 min first time, cached). Divergences: idle skip fires widget timers far more often (redraws look smoother than the unit's ~1/s); encoders register in bursts (single detents do nothing, use `turn_to` with 11-detent messages); holds need >= 12 M instructions; keys right after encoder bursts may drop; Python hooks do not fire under the fast stepper; panel TX ring is never drained; no DTCN2 timer; plain Unicorn halves fractional EMAC results (use digiemu's patched Unicorn); test from several start offsets - a real bug fails at every offset. `[doc]` {dn2-skill-emulators}
- Measuring on hardware: a screenshot RPC (`dn2rpc.c shot`) lets a mod publish a debug page; DSP load = reply word 0; ColdFire ISR time = DTCN2 stamps at hook entry and before the RTE (`0x40027bbe`). `[doc]` {dn2-skill-emulators}

## Flashing notes from the skill's setup
- Flash with `scripts/rpc_flash.py IMAGE.syx` over USB or Elektron Transfer and confirm on the unit. Keep USB quiet for ~90 s during the flash write. The first upload after boot is lost with auto-commit; kill stale flasher processes before rerunning. Python + mido can hang at exit on CoreMIDI. Avoid flashing or measuring during heavy local jobs (USB MIDI timing). **Raw SysEx over USB to the running OS is ignored** (only the update protocol works). Recovery: FUNC at power-on, TRIG 4, DIN MIDI, ~12-15 min. `[doc]` {dn2-skill-setup}
- Toolchain: `gcc-m68k-linux-gnu` / `binutils-m68k-linux-gnu` with `-mcpu=5475` on Linux/WSL; on macOS build GCC 13 and binutils 2.42 from source; PyPy 3.10+, `cffi`, `mido`, `python-rtmidi`; dnfw from angellinares/dn2_firmware_explore; digikit (the skill clones m-dwyer/digikit and applies `scripts/digikit-local.patch`). The stock-file check: SHA-256 starts `2af43e65` and ends `72e0` (the full value is `dn2paths.STOCK_SHA256`; elsewhere in this repo: `2af43e65e3d8390b41c9f66222620f8cce027d73ed87db00c80b440f628472e0`). `[doc]` {dn2-skill-setup}
