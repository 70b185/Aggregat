# Digitakt II (OS 1.17) - SHARC facts measured on a real unit

**Findings by 70b185 (owner of this repo)**, from their own private Digitakt II DSP project (a replacement for the STRETCH machine's SHARC code), notes up to
2026-10-29. Key: {own-dt2-notes}. **Not public, not listed in INDEX.** Many figures are measured on a real Digitakt II with a
read-only USB probe or with telemetry sent as audio, so they carry `[hw]` here. Everything else is static reading or emulator `[emu]`.
Addresses are DT2 OS 1.17. The section 7 (SHARC) image is byte-identical to 1.16, so digikit's 1.16 SHARC addresses apply.
Code addresses marked "sw" are short-word SHARC addresses. DM data addresses are byte addresses, 4 units per 32-bit word.

## 1. Timing - the numbers that matter
- **The core runs at 1.000 GHz** (DSP clock against the host's wall clock: 1000.1 MHz median). A block is 32 samples at 48 kHz = **666,667 cycles, 1,500 blocks/s**. Earlier "~650k / ~975 MHz" figures were a unit error (counted in units of 1,024). Guards built on 650k are about 2.5 % too strict. `[hw]` {own-dt2-notes}
- **Stock load with nothing playing: about 43-49 %** (word 0 ~280-320k cycles, idle-task measure 48.6-49 %). `[hw]`
- **On the Digitakt II, reply word 0 is a true load figure.** It tracks an idle-task measure second by second, about **6.5k cycles/block below it** (interrupts, RPC, timers outside the frame handler). This differs from the Digitone II, where dn2_firmware_explore found word 0 misreading. Add ~6.5k for the whole DSP. `[hw]`
- Device cycles are about **2x the emulator's instruction count** for this project's own code, which reads samples from DDR. The emulator models no memory stalls. Stock render code is reported at ~9 cycles/instruction on the DN2. A hard stop that the emulator showed overshooting by ~25k overshot by ~75k on the unit. `[hw]`
- Free budget with one plain stock track: about 330k cycles per block (calibration burn builds). `[hw]`

## 2. FreeRTOS on the DT2 SHARC (static, confirmed by a task-switch hook on the unit)
| Priority | Task | TCB | Behaviour (nothing playing) |
|---|---|---|---|
| 0 | IDLE | `0x2698d8` | 1,500 switch-ins/s; ~51 % of the DSP |
| 1 | RPC | `0x2cc550` | runs only when the ColdFire asks; **sample loading wakes it** (7.9 %, 472 switch-ins/s) |
| 5 | Audio | `0x2cb548` | woken once per block; ~48.6 % |
| - | Tmr Svc | - | waits on its queue (TmrQ) |
- Priorities **2-4 and 6 are unused**, probably with configMAX_PRIORITIES = 7. A task at priority 2-4 runs only after Audio finishes its block and is preempted by the next one, so it **cannot make Audio miss a block**. Only work inside Audio, or at priority 6, can. `[hw]`
- Kernel globals: `pxReadyTasksLists` `0x2ca2e8` (20 bytes each), `pxCurrentTCB` `0x2ca3e0`, `uxCurrentNumberOfTasks` `0x2ca3e8`, `uxTopReadyPriority` `0x2ca3f0` (bit mask, `31 - leftz`), `xSchedulerRunning` `0x2ca3f4`, `uxSchedulerSuspended` `0x2ca414`. The TCB is 88 bytes and statically allocated (`xTaskCreateStatic` sw `0xb86014`). Stack overflow check method 2 (`0xa5a5a5a5`). **No run-time stats are compiled in.** `[doc]`
- `prvIdleTask` is at sw `0xb863ca` with no idle hook; its back edge is at sw `0xb863df`. `vTaskSwitchContext` sw `0xb85af7` stores `pxCurrentTCB` at sw `0xb85b6b`. Both are workable hook points for an idle counter or a task map, at ~250 device cycles per switch (~0.1 %). L2 code loads at byte `0x20000000` (sw `0xb80000`). "Audio" and "RPC" are created from internal-memory code (sw `0x1c3f6a`, `0x1c7775`). `[hw]` (hooks ran on the unit)

## 3. Missed blocks, overload and "bitcrush until reboot" (what the runs showed)
- **A late block is always a whole missed block.** Audio is locked to the block interrupt. If one block's work runs past the next interrupt, that interrupt is lost and Audio runs one block later: an exactly one-block dropout, never drift. `[hw]`
- **The stock engine governs its own per-block load.** With 8 heavy stock tracks the Audio task ran at 99-100 % for whole 4 s windows and **missed no block**. Misses happen only when extra code inside the Audio task adds work the stock governor doesn't know about. **So a custom engine must stop on a per-block deadline measured from the block start, with margin, not on an average budget.** `[hw]`
- **Provoked missed blocks (54 in one boot, three back to back) did NOT cause the sticky bitcrush.** Neither did stock overload, nor sample loading at low load. The sticky "everything bitcrushed until reboot" appeared only with several custom-engine tracks at extreme settings. An emulator write audit showed no stray stores, so the cause is still open. Proven causes of a sticky whole-mix bitcrush from earlier builds: a render call much longer than a block with interrupts off; NaN/Inf reaching stock FX feedback; a value routed through a "free" stock parameter slot; overrunning the L2 area. `[hw]`
- Reading load by sampling word 0 (~17 reads/s = ~1 % of blocks) misses single late blocks. Count late blocks on the DSP side instead (task-switch gaps > 1.25 blocks). `[hw]`

## 4. The ColdFire <-> SHARC reply record
- The SHARC writes two copies, at DM `0x266220` and `0x267220`. A selector at `0x261ca4` picks the copy being written (`0x266220 + (sel << 12)`), so write both. The ColdFire copies it every frame to **`0x8000488C` (2,748 bytes, at most 687 words)**. The 16-bit halves arrive swapped. `[hw]`
- **Word k is at `0x266220 + 4k`**, not `+ k`. Two test builds wrote to the wrong place because of this; copy addresses from the compiler's disassembly. `[hw]`
- Which words are free (DT2 1.17, measured): **670-676 arrive untouched**. heavylight's engine uses 672-676. **Words 1-6 are rewritten by the firmware** after the block, so writes there never arrive. Word 5 is the firmware's while a track plays (unlike the DN2). **677-686 are the firmware's.** From word 7 on there is a per-track table: 21 words per track at `0x8000488C + 0x1C + 84*track`. `[hw]`

## 5. STRETCH machine contract (measured in the emulator, used on the unit)
- Render `FUN_1c5576 -> FUN_1c5615`, only caller `FUN_1c642a` (selector 2). Replace the body. **Do not patch the call at `0x1c6af1`.** The stock renderer costs ~1,720 instructions per 32-sample call. `[emu]`
- Call: R4 = voice record (`0x2412cc + v*0x1d8`, 32 records), R8 = output (32 floats, 48 kHz, int16/32768 scale), R12 = 32. Voices are rendered in ascending order 0..31, so a new block starts when v <= last v. Record words: w00 sample pointer (int16 mono, L = voice 2t, R = 2t+1), w62/63 length, w64/65 loop start, w68/69 end (Q31), w6a/6b step (Q31, 96 kHz units), w6c/6d phase, bytes 0x1b8 active / 0x1b9 stop / 0x1bb reverse / 0x1bc loop, w72 = a (tempo fit, float) and w73 = b (pitch ratio). A trigger is visible as w70 == w71 == 0. +4 is a 96 kHz work buffer and +0x104 is decimator state, **not scratch**. Tempo is a float BPM at DM `0x252d50`. `[emu]`
- Stock STRETCH: fixed 2,048-sample grains, 128-sample crossfade, linear interpolation. `a = BPM*(end-start)/(96000*120*2^bars)`, grid speed `clamp(a, 0.125, 4) + P - b`. `[emu]`
- Knob frame working copy: short at `0x2558dc + 0xde + 0x60*track` (the hidden CFADE slot, 0..0x7f00). **Routing a value through this "free" slot also feeds a stock per-voice flag that acts on the delay feedback** (`FUN_1c24e9`, slot struct `0x2506ec + v*0xdc + 0x10`). That leaked into the delay and once caused a sticky bitcrush. Check every reused slot with a memory-write diff of the stock chain. `[hw]`
- The SHARC upload in MAIN OS checks only `length <= 1 MiB` (no fixed size). Insert new boot blocks before FINAL. `[doc]`

## 5b. How a sample reaches a SHARC voice (digikit finding 15, DT2 1.16, emulator) {digikit-f15}
- **Samples go to the DSP over link port 0** (LP0_CTL `0x30FFE000`; SEC sources 81/82/168), not over the frame link. LP1 is unused.
  - One transfer is 0x401 words: a tag and 1,024 payload words.
  - Tag `0xFFFFFFFF` means a slot header: slot, startL, startR, rate, len. Stereo means startL != startR.
  - A tag below `0x19200` is a page number into the 400 MiB DDR sample pool at `0x8422B9C8`.
  - This is the RPC-task work the owner saw while samples load.
- **Slot table:** 0x14-byte records at DM `0x257810 + slot*0x14` (start L/R relative to the pool, length, ...), at most 0x401 slots.
- Track t owns voices 2t and 2t+1, with no dynamic allocation (unlike the DN2). The frame's trig mask is at payload `0x22` (bit t = track t). `[emu]`

## 6. Memory rules learned the hard way
- **L2:** the static analysis says `0x2001ab7c..0x20100000` minus `0x200fa000..0x200fe000` is free, but going past **`0x200f5a74`** gave clicks and leaks into the delay on the unit. Keep your data at or below that. `[hw]`
- **External DDR:** the stock output buffer (`0x8045b3c0`) and the sample data are in DDR. Per-sample stores to the DDR output buffer crashed the unit (continuous tone), although the emulator was bit-identical. **Render into L2 and copy once per block.** Read int16 samples two at a time. `[hw]`
- DM and PM data caches are not coherent on DDR (DN2 finding). Don't write through one bus and read through the other. `[doc]`
- Keep long calls short with interrupts off: a watchdog of **at most ~1M cycles per call**. Burns of ~1.27M with interrupts off left no lasting harm; longer calls knocked the audio stream out of step for good. `[hw]`
- Save MODE1 on entry and restore it on exit. A changed MODE1 alters the whole stock DSP until reboot. `[doc]`
- Never let NaN/Inf/huge values leave the machine: per-sample guard `!(|x| < 1e6)` -> 0 and restart the voice, clip to ±2. `[hw]`

## 7. selcc/selas (selache) traps, each seen on the unit or in the emulator
- `double` is 32-bit float. A read position in float loses resolution from ~22 s into a sample, which sounds like sample-rate reduction. **Use Q32.32 fixed point for positions.** `[hw]`
- No integer `/` or `%` where the operand can be 0 (`___umod32` runs LCNTR = 32 - leftz(x); 0 means a hang).
- No loops with early exit (`break`/`return`): they become DO loops left by a jump.
- `int more = a < b; while (more)` compiled into an endless loop. Write a counted `for` with an `if` body.
- Large initialised `static const float` tables arrive as garbage, so compute them at run time. Complex float expressions passed as arguments lost terms. `static int a = 1, b;` lost `b`. Keep compound conditions simple. Pass at most 3 arguments (stack arguments are passed wrongly) or a struct pointer.
- selas: multifunction (MUL+ALU) and dual-load forms are encoded wrongly; `Ia = MODIFY(Ib, ..)` becomes `Ib = ..`; system registers (MODE1, LCNTR, EMUCLK) moved in 48-bit form are wrong, so use compressed code. Negative shift immediates are wrong (`023e 0000` vs stock `023e 7800`: ILOPI on the unit). Shift by a register.
- selcc treats R3, R5-R7 as scratch where the ADI ABI preserves them: save them at the bridge.
- A selcc peephole bug (frame-reload forwarding clobbering the reload register) was patched locally. The patch also added a `SELCC_SAFE=1` switch that skips the post-allocation peepholes. If code misbehaves only when optimised, try that.
- DAG registers moved via the same DAG's addressing hang the unit; move them through R registers. Same rule as the DN2 skill.

## 8. Measuring on the unit without a debugger
- **Read-only USB SysEx probe in MAIN OS** (heavylight's dt2-keyframer, derived from irpina/digihealth via dn2_firmware_explore): `F0 00 20 3C 7D 00 <pack7> F7`. Commands: HELLO 1 (returns word 0) and PEEK 3 (address, up to 256 bytes). There is no write command. It hooks the SysEx router at `0x40120006` (router `0x4011ffda`, header `0x4021e5d2`, send `0x40121d2a`, USB port 2), and the router itself drops device id 0x7D. It fits in 532 bytes of a free 896-byte run in MAIN OS 1.17 (`0x402e4f64`, `0x402e609c`) and coexists with Deja Vu V5.1, Musical V4 and Zoom V11. It also went into an elekloader-built image. It is built with plain binutils (`m68k-linux-gnu-as -mcpu=5475`). **Overbridge suspected of conflicting:** keep the probe build separate. `[hw]`
- **Telemetry as audio:** a DSP track outputs one constant level per block (frame of 47 blocks with sync levels), recorded via an Overbridge track output. Overbridge applies a DC-blocking highpass (one pole, a = 0.9981 at 48 kHz) that the decoder must undo. About 50 % of frames decode. `[hw]`
- Load display build: show peak cycles per call on the playhead. This is the only figure that includes real DDR stalls without a probe.
- Recovery used throughout: FUNC at power-on, TRIG 4, stock `.syx` over DIN. Bootstrap 0x0201 is the same on 1.16 and 1.17, so the 1.16 <-> 1.17 update is reversible. `[hw]`
