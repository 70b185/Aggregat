# Digitakt II (OS 1.17) - writing fast and safe SHARC code: lessons from the PLAITS port

Source: karigardarsson/digitakt-ii-research, All-in-One source (digikit-based), `modules/machines/plaits/OPTIMIZING.md`
and `HARDWARE-TEST.md`, read 2026-10-31. The port brings Mutable Instruments Plaits (MIT) to the Digitakt II as a run-time machine
with 25 models. Every model and each optimisation was flashed step by step on the owner's unit. Key {dt2-plaits}. Results marked
`[hw]` ran on a unit; cycle figures are emulator estimates calibrated against the unit.

## 1. Two hangs on silicon that the emulator ran bit-exactly `[hw]`
- **H-opt1, RINGS as a hand-written SIMD kernel: the DSP hung on the first block, and all audio died.** ([I14](../INCIDENTS.md#i14-dag-registers-stored-through-their-own-dag-hung-the-dsp))
  - Cause, confirmed with a one-variable probe image: **DAG registers stored through their own DAG** (`DM(I7, M7) = M4` and similar, used to save I0/I1/M4/M6/L0/L1/L4). The PRM forbids it for Types 3 and 15. Stock loads such registers through their own DAG thousands of times but **never stores** one.
  - The probe was `probe-samedag-store`, a single `DM(I4, M6) = M4` and no SIMD.
  - Fix: push DAG registers through R0.
- **SIMD-mode loads and stores (the implicit PEy access at +4 bytes) into L2 byte space** have no stock precedent: stock does SIMD data accesses only in L1 normal-word space, and SIMD stores to DDR at most.
  - The manual allows them, but they are unproven on silicon.
  - The shipping kernel does SIMD compute only and moves every load and store in SISD, toggling PEYEN per sample as stock does.
  - Cost: 125,766 -> 31,472 instructions per block versus the C version. The full-SIMD version would have been 27,404.
- **Lesson: an instruction word with a stock precedent is necessary but not sufficient.** How stock combines operands also matters: which registers go through which DAG, and which access mode in which memory region. The encoding gate now refuses same-DAG stores and any data transfer while PEYEN is set.
- **Emulator gaps seen here:**
  - It wraps immediate-offset accesses circularly when L != 0, so own the L register of every I you use that way.
  - It treats never-written L2 as unknown per 32-bit word, which halts code that legitimately reads half of such a word.

## 2. Encoding traps (selas), each caught by a gate before it reached a unit
- `JUMP (PC, label)` assembled to a jump to itself; the kernel spun forever. Write `JUMP label` as selcc does.
- selas does not compress inside a DO loop. Under `.COMPRESS` it can merge or drop a statement after a loop end or a `(DB)` branch. Write delayed-branch code under `.NOCOMPRESS` and cross-check statements against instructions.
- `Rn = Rn + Rm` and `Rn = Rn XOR Rm` compress to 16-bit forms that stock never uses, so write integer adds under `.NOCOMPRESS`. Stock contains no plain XOR at all.
- **A label defined in two sources resolves to one of them in the merged object.** Each kernel's own test passed, but the merged image jumped into the wrong file. Use unique label prefixes per file.
- **Delay slots:** after a delayed branch, the two slots must not hold a branch, a DO, a PC-stack operation, IDLE, or a write of the indirect branch's I/M. After a conditional branch, they should also not hold a flag writer (stock does that, but it is avoided as a precaution).
- **The last 11 instructions of every DO loop are 48-bit, and the loop end is an instruction** ([rule A45](../AGENT-RULES.md)). The other code can be compressed. Compression shrank the kernels by 10-30 %, which matters because the instruction cache is the bottleneck (section 3).

## 3. Where the cycles go on the SHARC+ (calibrated cycle model)
- **Instruction-cache misses are the largest stall class (33 %).** Every model touches 150-300 code lines (10-19 KB) of L2 code per voice block, near or above the 16 KB 2-way cache. The lever is code size (compression, kernels instead of selcc C, fewer calls), not code order.
- **DAG write-to-use stalls are 32 %, almost all in selcc C** (`In = Rm` or `In = DM(..)` followed directly by a use). selcc has no optimiser, so only hand kernels remove them.
- Data-cache misses are 18 % (cold) and only a few % warm: the tables mostly hit. Float forwarding is 14 %, taken branches 4 %.
- **This core has no load-to-use stall, and a cache miss stalls whatever the distance.** Scheduling loads earlier only helps to free registers.
- **Fewer instructions are not fewer cycles.** One kernel cut instructions by 46 %, but the calibrated load fell by only 1.2 points. Code-size changes alone move a measurement by about 1 point (layout noise).
- Stock 1.17 with one trigged track sits at ~48.6 % on the high bound. The calibration on the unit: 8 KICK tracks measured 91.7 %, and the sound turned choppy above ~87 %.

## 4. Optimisation rules the project enforces (worth copying)
1. **Output bit-identical:** never re-record a digest to make an optimisation pass.
2. **Every instruction form has a stock precedent** (the encoding gate). Indirect jumps and calls must be exact stock words.
3. **Restore global state on every exit:** MODE1 (PEYEN, rounding, saturation), MODE2, loop and status stacks, the L/B registers of circular buffers, the circular C stack (L6/L7). Test every exit path.
4. **Measure every change:** the same fuzz seed before and after. Design for the **worst block**, not the mean. Revert changes that do not help.
5. **Profile first.** Per-function and per-loop instruction counts, then stall estimates.
6. Use the platform's free features:
   - multifunction instructions (compute + DM/PM moves);
   - circular buffers via the DAG instead of modulo code;
   - zero-overhead DO loops;
   - filled delay slots;
   - software pipelining of short loops;
   - SIMD pairing only for compute, with data in registers.
- **Current Selache fork (pin 967c1d1e) build rules:** a plain `.SECTION/DM` is laid out in 40-bit words, so digikit assembles DM data as `/DM/BW`; the assembler may set a DO loop's fast-loop F1 bit by itself, so turn that off and write `(F)` where it is meant; `Rn = Fm` is not a plain transfer, use `Rn = PASS Fm`; an undefined name (for example a register SHARC+ lacks) silently becomes an external symbol. The earlier assembler wrote 77 transfers without their width modifiers. `[doc]` {digikit-1116}
- **Lazy clear:** skipping a large memory clear at init is exact only if the write-before-read structure is proven per delay line. It removed one model's 70k-cycle spike on the model-change block.

## 5. Practical numbers
- The calibrated estimate of clean tracks (about 87 % or less) for 8 tracks of one model: SQUARE 10; ASYM-TRI and 2FM 9; KICK, NOISE and most DX7 banks 8; RINGS, HIHAT and ADDITIVE 7; most others 6; VA 5.
- The per-voice cost is 3.5-6.8 % of the DSP. Mixed kits add up per voice. `[emu]` calibrated
- **After flashing a build that adds machines, create a new project before testing:** projects saved under an earlier image may not play. A project saved with PLAITS loads on stock 1.17. `[hw]`

## 6. Measured on silicon: cycles and float rules (digikit findings 101-103, DT2 1.17 and DN2 1.12, 2026-10-31/11-01) {digikit-f103}
A probe module ran 143 items on a real Digitakt II, then the same probe on a real Digitone II. Values, flags and cycles **match between the two units**. 76 value or register items and 39 cycle items differed from the emulator before the emulator was fixed. `[hw]`

**Cycles per instruction on the ADSP-21569** (the emulator counts 1 for almost everything):
| Snippet | Device | Emulator before |
|---|---|---|
| independent ALU, MAC, float multiply | 1.0 | 1.0 |
| **dependent float multiply chain** | **1.5** | 1.0 |
| hardware loop | 1.0 per instruction + **12 cycles start-up** | start-up 1 |
| conditional jump not taken | 1.0 | 1.0 |
| **conditional jump taken / unconditional jump** | **6.75-6.8** | 1.0 |
| delayed jump with two NOPs | 6.5 | 3.0 |
| **CALL + RTS** | **13.9** | 2.0 |
| divide (RECIPS + 2 Newton + multiply) | 15 | 8 |
| RSQRTS + 3 Newton | 31 | 16 |
| L2 loads/stores, sequential or warm | 1.09 | 1.0 |
| L1 and DDR sequential loads | 1.0 | 1.0 |
| **48 loads over 6 lines 16 KiB apart (one cache set)** | **58.4 per load** (~58 cycles per miss) | 1.02 |
| system register read | 2-5; IMASK/IRPTL 27, CMMR_PWR_L1_SD_CTL 28 (the TPERIOD value was withdrawn 2026-11-16: never read; SHL1C_CFG, SHL1C_CFG2 and range-register costs now unverified) | 2 |
- **L2 data is cached by a 16 KiB cache that maps lines 16 KiB apart to the same set.** Buffers spaced at 16 KiB multiples thrash it, so pad or interleave them. Branches and calls are expensive: unroll small loops into hardware loops, avoid calls in per-sample code, and fill delay slots.
- One block measured 666,582 cycles median on DT2 (666,784 on DN2), jittering by ±2.7 % (sd 0.5 %); the emulator does not jitter. With `digikit/remote` and `digikit/debug` loaded, a DN2 showed DSP 57 % average (61 % peak) and ColdFire 26 %.
- Registers read on silicon (DT2 and DN2 alike):
  - IMASK `0x8040801b`, MODE2 `0x42000021`, SHDBG_REVID `0x20`, CMMR_SYSCTL `0x6004`, SHL1C_CFG `0x00010101`, SHL1C_CFG2 `0xf0`;
  - **two non-cacheable ranges: `0x200fa000-0x200fe000` and `0x28240000-0x283a0000`**, with exclusive end addresses. SHL1C_CFG2 `0xf0` enables ranges 2 and 3 with `RRnSEL = 1` (non-cacheable); L2 and DDR outside them are cached ([finding 103, section 4](https://github.com/ElekLabs/digikit/blob/main/docs/findings/103-dsp-facts-on-a-digitakt-ii.md#4-registers-read-on-silicon-d));
  - withdrawn 2026-11-16: the per-device core timer periods reported here were I0/I1 reads. The old assembler encoded the probe's TPERIOD, TCOUNT, MMASK and LIRPTL reads as other registers, so none of them was measured; of the probe's ID words only OSPID differs (DT2 `0x00224601`, DN2 `0x07674700`). {digikit-1116}

**Float and saturation rules the chip follows** (some contradict the PRM):
- A float ALU operation with a NaN input returns `0xFFFFFFFF` with AI set and **AN clear**. Inf - inf also returns `0xFFFFFFFF`. The float multiplier's invalid result (NaN operand, inf x 0) is `0x7FFFFFFF` with MI set and MN clear.
- **The sticky bits (AIS, AVS, AUS, AOS) latch on every float ALU operation**, so a NaN once produced leaves a mark you can read.
- FIX of ±0.5 returns 0 and sets AUS.
- **With MODE1.ALUSAT, fixed add/sub/neg/abs saturate** to `0x7FFFFFFF` / `0x80000000`. The short compute forms (Type 2c), the multifunction ALU halves and the dual add/subtract may still wrap; this is unmeasured.
- Open again (2026-11-16): whether reading an MR word into a register keeps the multiplier flags. The probe's `MRF = R1 * R2 (SSFR)` was assembled without the rounding modifier, so its MV flag proves nothing; the "float multiply with parallel add" item measured only a plain multiply (see CONFLICTS S10). {digikit-1116}
- The RECIPS/RSQRTS seeds come from two 128-entry tables, all measured; the low 15 mantissa bits are zero. Stock's divide helper uses RECIPS plus Newton steps, so the last bit of a division depends on the exact seed.

**Diagnostic reply publication** ([finding 101](https://github.com/ElekLabs/digikit/blob/main/docs/findings/101-module-step-word-on-hardware.md)): the DSP's SPI2 is a slave and its transmit DMA walks two descriptors. Timing of the suspected overlap between DMA and diagnostic writes on silicon remains unmeasured. {digikit-f101}
- On a real DT2 (OS 1.17), digikit's diagnostic word 25 arrived as 0 in 3,995 of 4,000 collected records. The old scheme delivered every second record in the emulator. `[hw]` {digikit-f101}
- **Digikit's own `core/fx` and `core/dsp-voice` diagnostic clears overwrote the previous block's reply word.** Removing those clears restored delivery in the DN2 1.12 emulator; this does not identify stock firmware as the writer or establish silicon DMA timing. `[emu]` {digikit-f101}
- **Keep hook diagnostics in a static word and copy it into the reply at the block tail, after all module calls.** The revised design clears the static word rather than either reply record and passes the emulator regression; finding 101 says it had not yet run on a real DT2. A mark stored in the call that hangs the DSP cannot reach a tail that never runs, so the fault record retains the last completed block's mark. `[emu]` {digikit-f101}

## 7. How a stock DSP interrupt saves registers, and what module code must never write (digikit findings 130, DT2 1.17 and DN2 1.12) {digikit-1116}
- **Three pieces of stock code:** a vector stub, the wrapper `0x1c02a4`-`0x1c066b` (byte-identical on both images, 968 words, return label `0x1c04b7`; it calls the handler through the table at `0x2404b0` with `JUMP (M13, I12) (DB)` at `0x1c04b1`) and a return stub. SEC vector stub DT2 `0x1c0b7b` / DN2 `0x1c0acd`, generic stub `0x1c0b1e` / `0x1c0a70`, return stub `0x1c0be5` / `0x1c0b37`: the DN2 stubs sit `0xae` lower. `[doc]` (both images' bytes, two decoders)
- **What is saved:** the stubs save R4, R8, R12, I6, I7, I12, B6, B7, PX and PCSTK; the wrapper saves the DAG, status, loop-stack and MR/MS registers and zeroes L0-L5 and L8-L15 for the handler. It picks its path by MODE1 bit 16 (RND32) of the interrupted code: with RND32 set it saves only R0-R2, R4 and S0-S15 and relies on the handler to keep the C callee-saved registers; with RND32 clear it saves R1-R15. `[doc]`
- **Never write these in module DSP code, not even with a save and restore:** B7, L6, L7, M5, M6, M7, M13, IMASK, IMASKP, IRPTL, MMASK, TPERIOD, TCOUNT, FLAGS. The stock interrupt code may read them at any instruction, so an interrupt between the save and the restore sees the changed value. The wrapper needs a valid linear stack in I7 (L6 = L7 = 0) and M5 = 0, M6 = 1, M7 = -1, M13 = 0. digikit's `sdk/dsp/REGISTERS.md` generates one contract from this (classes clobber, keep, stack, never_write). `[doc]`
- **Finding 103 was partly withdrawn (2026-11-16):** the old assembler mis-encoded several probe instructions, so the silicon run read MMASK as IMASKP, TPERIOD and TCOUNT as I0 and I1, LIRPTL (which SHARC+ lacks) as IMASK, and the cycle-counter reads of records 118-135 as LCNTR reads; it also dropped SSFR's rounding modifier and turned the dual multiply-plus-add into a plain multiply. The values listed in section 6 that came from these items are void; the non-cacheable ranges, REVID, IMASK, MODE2, the 59 value items and the block cycle counts stand (A41). `[doc]`

## What the stock SHARC kernels look like (digikit finding 72, DT2 1.17 and DN2 1.12, static) {digikit-f72}
Instruction counts come from the listings, with no stalls modelled. Use them as a style reference and a lower bound. `[doc]`
- **Calling convention:** a delayed `CALL` with a frame; arguments in R4, R8, R12, more on the stack; result in R0.
  - Most kernels come as a pair: `reset(record)` and `process(record, in, out, n)`, one 32-sample block per call.
  - The prologue and epilogue cost ~20 instructions, about 0.6 per sample.
- **Every sample loop is a hardware `DO ... UNTIL LCE`.** The loops are software-pipelined (the last stores come after the loop) and have a fast exit for n = 0 or 1.
- **Idioms worth copying:**
  - multiplier + ALU + data move in one instruction;
  - post-modify DAG access with constant M6 = 1 and M5 = 0;
  - RECIPS/RSQRTS seed plus Newton steps, using FAVG to halve;
  - branch-free CLIP/ABS/MIN/MAX;
  - FEXT to wrap an index;
  - SIMD around copy loops;
  - parameter ramps as "accumulator += step per sample";
  - MODE1 saved and restored around RND32 or SIMD.
- **Same code, different address:** the shared kernels are byte-identical on DT2 and DN2 but sit at different addresses (biquad DT2 `0x1ccbd8`, DN2 `0xb81368`). Only the float divide `0x1c06ba` has one address on both. Calling a stock kernel therefore needs a per-device address row.
- **Hidden dependencies of stock kernels:**
  - The envelope reads a rate table at a device-specific absolute address.
  - powf reads three tables and writes error words.
  - Divide and rsqrt flip MODE1 bit 16 and restore it, so don't call them with SIMD or a loop active.
- The DSP sections are byte-identical between DT2 1.16 and 1.17 and between DN2 1.11 and 1.12 (digikit finding 53), so SHARC code and addresses carried over between those OS versions. `[doc]` {digikit-f53}
- **digikit's recommendation:** write your own kernels for the hot path; they can be faster (its estimate: interpolated delay 41 -> 15 instructions per sample, half-band 25 -> 10). Call stock only for the divide.

