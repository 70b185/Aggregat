# Digitakt II (OS 1.17) - writing fast and safe SHARC code: lessons from the PLAITS port

Source: karigardarsson/digitakt-ii-research, All-in-One source (digikit-based), `modules/machines/plaits/OPTIMIZING.md`
and `HARDWARE-TEST.md`, read 2026-10-31. The port brings Mutable Instruments Plaits (MIT) to the Digitakt II as a run-time machine
with 25 models. Every model and each optimisation was flashed step by step on the owner's unit. Key {dt2-plaits}. Results marked
`[hw]` ran on a unit; cycle figures are emulator estimates calibrated against the unit.

## 1. Two hangs on silicon that the emulator ran bit-exactly `[hw]`
- **H-opt1, RINGS as a hand-written SIMD kernel: the DSP hung on the first block, and all audio died.**
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
- **The last 11 instructions of every DO loop are 48-bit, and the loop end is an instruction.** The other code can be compressed. Compression shrank the kernels by 10-30 %, which matters because the instruction cache is the bottleneck (section 3).

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
- **Lazy clear:** skipping a large memory clear at init is exact only if the write-before-read structure is proven per delay line. It removed one model's 70k-cycle spike on the model-change block.

## 5. Practical numbers
- The calibrated estimate of clean tracks (about 87 % or less) for 8 tracks of one model: SQUARE 10; ASYM-TRI and 2FM 9; KICK, NOISE and most DX7 banks 8; RINGS, HIHAT and ADDITIVE 7; most others 6; VA 5.
- The per-voice cost is 3.5-6.8 % of the DSP. Mixed kits add up per voice. `[emu]` calibrated
- **After flashing a build that adds machines, create a new project before testing:** projects saved under an earlier image may not play. A project saved with PLAITS loads on stock 1.17. `[hw]`
