# Digitakt II and Digitone II SHARC: which findings hold on both (task T19, 2026-11-02)

Both units carry the same ADSP-21569 SHARC+ at 1 GHz, and 1,038 of the DT2's 1,228 DSP functions (85 %) have a twin in the DN2 image; what differs is the audio engine itself ([`../devices/digitone-2-internals.md`](../devices/digitone-2-internals.md)). This page goes through the SHARC findings of both device pages and sorts them by where they have been shown. It compares what the projects published; it adds no new measurement.

**Rule of thumb.** Facts about the **silicon** carry over: digikit ran the same 143-item probe on a real DT2 (OS 1.17) and a real DN2 (OS 1.12), and every value, every cycle cost and every core register matched; only three registers that the firmware sets differed. Facts about the **firmware** (memory map, reply records, DDR use, how the engine spends its time) do not carry over until someone checks them on the other unit. `[hw]` {digikit-f103} {digikit-f102}

## 1. Shown on both units `[hw]`
- **Clock and block:** 1 GHz, 32 samples per block, 666,667 cycles nominal. Measured median per block: DT2 666,582, DN2 666,784 (digikit); DN2 666,706 (elekloader's idle-task meter); the owner's idle counter on a DT2 agrees. {digikit-f103} {elekloader-sharc-dn2} {own-dt2-notes}
- **Core behaviour:** 59 value items (saturation with MODE1.ALUSAT, the short and multifunction compute forms, float rounding) and all cycle snippets equal, including the L2 conflict loads (2,769 vs 2,803 cycles for 4,096 loads); the 6,694 RECIPS/RSQRTS seed results are equal. So the cycle budget of rule A35 and the float rules in [`../devices/digitakt-2-dsp-optimizing.md`](../devices/digitakt-2-dsp-optimizing.md) section 6 hold on both. {digikit-f103} {digikit-f102}
- **Core registers set by the boot code:** IMASK, MODE2, SHDBG_REVID, cache configuration (`SHL1C_CFG`) read the same on both. The traps armed (illegal opcode, L1 parity) are therefore the same. {digikit-f103}
- **Never store a DAG register through its own DAG (rule A33):** hung a DT2 (Plaits port, digikit's "rung C"); the DN2 skill names the same pattern "the root cause of silent units" on its unit. {dt2-plaits} {dn2-skill-sharc}
- **Hardware loop ends in 48-bit ISA (rule A45):** a DT2 froze at boot from a compressed loop end; stock DN2 1.11 obeys the rule in all 286 loops and the DN2 skill enforces it. {digikit-f91} {dn2-skill-scripts}
- **Decoded section 7 under 1 MiB (rule A46):** the same 828-byte staging routine on DT2 1.16/1.17 and DN2 1.11/1.12; the overrun crashed a DT2. {digikit-f06} {dt2-lab-capicola}
- **NaN or Inf in stock FX feedback silences everything until reboot:** on a DT2 from an LFO at large depth on TUNE (digikit) and in the owner's builds; on a DN2 from never-written DDR, which powers on as garbage such as `0xFFFFFFFF` (the DN2 skill). Same failure, two triggers: guard every value you feed into a feedback path, and fill new DDR in emulator tests with `0xFFFFFFFF`. {digikit-f51} {own-dt2-notes} {dn2-skill-firmware}
- **Shared stock DSP code, by the bytes:** the DT2's six wavetable render stages are in the DN2 image too. Three are byte-identical; in the other three every differing byte is a PC-relative call offset (same target) or one table-pointer literal. All call the same reciprocal helper at sw `0x1c06ba` in both images (RECIPS plus Newton steps, the helper behind A35's divide cost). A fix or measurement on one of these stages carries over. `[doc]` {digikit-f11}
- **The unused frame tail carries DSP code on both** (+23 instructions per block on DT2, +26 on DN2). `[doc]` {digikit-findings}

## 2. Silicon-level, seen on one unit, expected on the other
The core is the same (section 1), so these should hold on the other unit too. Nobody has shown them there yet.
- **SIMD loads and stores into L2 byte space hang the DSP** (DT2, Plaits port; rule A33's second half). No DN2 report either way. {dt2-plaits}
- **Instruction-cache misses are the largest stall class** (33 % on the DT2 Plaits models), and L2 data lines 16 KiB apart thrash the 16 KiB cache. digikit's DN2 cycle snippets match, so plan DN2 kernels the same way. {dt2-plaits} {digikit-f103}
- **ILOPI catches encodings the toolchain accepts** (negative shift immediates, a 48-bit form of selas): seen on DN2 units. The DT2's IMASK is the same, and 70b185's DT2 rules already forbid the same encodings. {dn2-dspstop} {own-dt2-notes}
- **L1 block 2 holds the PM data cache, so it is not free even though the image leaves it empty** (DN2). The cache configuration register is the same on the DT2. {dn2-dspstop} {digikit-f103}
- **The IIR0 and FIR0 accelerators compute in a different order from the hardware reference** (IIR0 output from stored word 5, FIR0 sums added in pairs, INIDX/OUTIDX written the other way round in ACM). Read on a DN2; neither stock engine uses them. {dn2-accel}
- **DM and PM data caches are not coherent on DDR** (a DN2 finding, applied as a rule on the DT2 without a DT2 test). `[doc]` {own-dt2-notes}

## 3. Firmware-level, one device only: check before relying on it
- **Reply record:** on the DT2 the SHARC writes two copies (`0x266220`, `0x267220`, picked by a selector), words 1-6 are rewritten by firmware and words 670-676 arrive untouched. On the DN2, reply word 2 is free on 1.12 (elekloader). These allocation results have not been checked on the other device; the record addresses differ with the image. {own-dt2-notes} {elekloader-sharc-dn2}
- **Diagnostic reply publication:** digikit's DT2 probe received 0 in 3,995 of 4,000 diagnostic word-25 records. `[hw]` Its own `core/fx` and `core/dsp-voice` clears overwrote the previous block's reply word; removing those clears restored delivery in the DN2 1.12 emulator. The replacement keeps a static word and publishes at block tail. `[emu]` Finding 101 leaves silicon DMA timing unmeasured and says the new design had not yet run on a real DT2; it does not attribute the clears to stock firmware. {digikit-f101}
- **Free L2:** DT2 problems start past `0x200f5a74` on a unit, although the static map shows free space up to `0x200fa000`. DN2: usable `0x20088400-0x200b0000` per the DN2 skill, and one block in L2 stopped a unit from starting. The two stock images load different amounts into L2 (`0x2001ab7c` vs `0x2008823c`), so each device needs its own limit. {own-dt2-notes} {dn2-skill-firmware}
- **Code in L2 "dead" stock FX spots stopped a DN2 at random moments** (Digiwerk SC01); no DT2 test of the same idea. {dn2-cfw-roadmap}
- **Per-sample stores into a stock DDR output buffer crashed a DT2;** render into L2 and copy once. No DN2 test. {own-dt2-notes}
- **The FreeRTOS layout** (idle task, unused priorities 2-4 and 6) was measured on the DT2. The DN2 image has the same FreeRTOS files, but the addresses must be re-found. {own-dt2-notes} {digikit-sharcmap}

## 4. Different on the two devices
- **DSP DDR:** on the DN2, `0x80531000-0xa0000000` (~507 MB) was never written in a fill-and-scan test on a unit. On the DT2 that range is the **sample pool**: its window runs from `0x8422b9c8` to `0x9d22b9c8`. Do not carry the DN2's "free DDR" over to the DT2. The DT2's SHARC image also zero-fills 32 MiB at `0x80a00000` and a `0x1c4`-byte control block at `0x82a00000` that the DN2 image lacks, and the SHARC functions that use them have no DN2 twin. {dn2-ddr} {dt2-lab-flex-mem} {dn2-drive}
- **How stock spends the block:** the DN2 engine renders every voice every block (~63-65 % flat by dnfw's idle-task method, a held voice adds ~8k cycles; elekloader reads ~80 %, conflict O15). The DT2 engine scales with what plays and governs its own load: with 8 heavy tracks it ran at 99-100 % for whole windows and missed no block. Budgets measured on one device say nothing about the other. {dn2-sharcload} {own-dt2-notes}
- **What an overrun does:** on the DT2 a late block is exactly one missed block, and even 54 provoked misses did not leave lasting damage. dn2mk2 users saw custom-voice overruns on the DN2 cut all audio until a power cycle. These are not the same experiment (sustained overload by added voices vs. single late blocks), so they do not contradict each other. A test that settles it: provoke single late blocks on a DN2 the way the DT2 test did. {own-dt2-notes} {dn2mk2-reports}
- **Reply word 0:** on the DT2 it is a true load figure, about 6.5k cycles below an idle-task measure. On the DN2 the DN2 skill uses it as the DSP load, while dnfw reads the frame handler's own count (~416k cycles) from it. Compare both methods on one DN2 before using word 0 there. {own-dt2-notes} {dn2-skill-emulators} {dn2-sharcload}

## What to do next
- Section 2: one probe image per item on the other unit (a SIMD L2 access on a DN2; a negative-shift instruction on a DT2 behind a guard). digikit's probe module `test/dsp-facts` already runs on both.
- Section 3: the reply-record test (write a word from a hook vs. from the block tail, count arrivals) on a DN2 1.12.
- Section 4: the late-block test on a DN2.

These are listed as task T19's remainder in [RESEARCH-MAP](../../RESEARCH-MAP.md).
