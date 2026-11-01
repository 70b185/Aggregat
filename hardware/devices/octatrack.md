# Octatrack (MKI, MKII) - OS 1.40C

Coverage: **first profile** (phase 2). Source: sambanks/octabam docs (`docs/firmware/CHIP.md`, `ARCHITECTURE.md`, `DSP.md`,
`docs/contributing/PLACEMENT.md`, `TRAPS.md`, `docs/guide/BUILDING.md`), read 2026-11-02. octabam marks its facts measured (✅),
inferred (🟡) or retracted (❌); we keep `[hw]` for its hardware rows. Projects: [../../devices/octatrack.md](../../devices/octatrack.md).
Key {octabam}. **A different platform from the DT2/DN2:** the ColdFire is an MCF5445x, the DSP is a two-core Freescale DSP56721, not a SHARC.

## Silicon
- CPU: **ColdFire MCF5445x** (board photos read MCF54454VR266 or MCF5445AVR266), 32-bit big-endian. The firmware stores **264 MHz**; internal bus 132 MHz (UARTs, PIT, DSPI), FlexBus 66 MHz, 24 MHz crystal. 128 MB SDRAM at `0x40000000`; NOR flash on CS0, 8 MB decode. `[hw]`
- Audio DSP: **Freescale Symphony DSP56721**, two DSP5636x cores **in one chip**, 200 MHz each, with no external memory.
  - Each core has its own P memory. A **64 K-word shared window** at `$030000` is reachable by both cores; P, X and Y alias there.
  - **Tracks 1-4 run on core 1 and tracks 5-8 on core 0** ("inverted from old assumptions"). Each track's FX1 and FX2 run on its own core. `[hw]`
- Storage: CompactFlash (FAT16/32) through an ATA stack (PIO task-file registers at `0x90000000`).
- The kernel is a **proprietary preemptive microkernel** (banner "ElektronOctatrack DPS-1"), not FreeRTOS.

## Cycle budget (measured with a burn probe on units)
- **4,532 cycles per sample per core** at 44.1 kHz (199.9 MHz measured). The older 4,160 / 183 MHz is retracted.
- About **3,120 cycles/sample are usable for DSP work**; stock takes ~1,410.
- Planning number: ~500 cycles on top of the current reverb with 4 FX1 FILTERs, ~900 with 2. One FX1 FILTER costs 192 cycles/sample. `[hw]`
- Stock FX2 costs per sample (one MKII, 1.40C), dearest first: DJ EQ ~340, LO-FI ~310, SPRING ~300, CHORUS ~295, FILTER ~285, DARK ~255, PLATE ~250, PHASER ~240, EQUALIZER ~190, FLANGER ~145, COMB ~125, COMPRESSOR ~100, SPATIALIZER ~80, DELAY ~0. `[hw]`
- **Words are not cycles:** `move x0,a` 2 cycles, a one-word displaced `move x:(r7+$15),a` ~4, a two-word displaced ~6. Static word counts are a floor; only a burn sweep measures the ceiling. `[hw]`
- **ColdFire access costs** (one unit, 132 MHz, inside the frame interrupt, stock cache settings): register/SRAM/cache hit ~2.9 ns, uncached SDRAM store 36 ns, load 69 ns, cache miss ~80 ns, `cpushl` 46-80 ns. **SRAM is 12-28x cheaper than SDRAM**, and caching a transmit buffer does not help. `[hw]`
- USB costs: one recording buffer is about 6 points of the ColdFire's frame share, USB streaming about 12. Six buffers plus streaming drop frames. `[hw]`

## FX slots
- Every track runs `FX1 -> FX2 -> gain`. FX1 has 3,072 words of Y, FX2 16,384, which is why reverbs and delay are FX2-only.
- **Both menus share one DSP dispatch table indexed by the raw id.** A module on a stock effect's id replaces that effect in both slots, and removing an effect from a menu frees no space. The reclaimable pool is FX1's ten effects, 3,384 words. `[doc]`

## OS format, update and recovery
- Elektron ships the same OS as `.bin` and `.syx` (the MKI and MKII files are byte-identical for 1.40C).
  - `.bin` = ELUP header + seed + XOR-feedback-obfuscated `[len] + ELEK(aPLib(MAIN OS))` + checksum.
  - `.syx` = SysEx-packed ELEK container.
  - The MAIN OS is 1,112,560 B. **No cryptographic signature in any layer.** `[doc]`
- **Validation on update** returns: -1 IO, -2 not a valid OS, -3 length (more than 1 MB + 12 B), -4 checksum, -5 MK1 not allowed (version code below "0156"), **-6 cannot downgrade (below "0178")**. octabam images keep code 0178. `[doc]`
- **The card path:** OS UPGRADE lists `/*.BIN` on the CF, validates, programs NOR from `0x4000` and verifies it word by word. Stock then shows "PLEASE REBOOT!" and never resets the unit itself.
- **Recovery:** hold **FUNC** at power-on, **TRIG 3 = MIDI UPGRADE** (not TRIG 4 as on the small boxes), send the stock `.syx` over DIN MIDI. `TRIG 2` (EMPTY RESET) clears battery-backed RAM and settings, not the card.
  - Pace about 7,460 messages at DIN rate. Filter MIDI clock on that port and merge nothing else into it: a MIDI-hub preset caused a CHECKSUM ERROR.
  - If the unit loses sync, send again slower (60-300 ms between messages).
  - The unit may update its bootstrap after the flash. `[hw]`
- After flashing a build that changes an effect's parameter layout, old projects need their stored values stamped. A select value outside its count stalls the sequencer on first play. `[hw]`

## Memory and code placement
- **The free ROM is small:** zero runs in `0x400c0000-0x400d8000` total ~8.4 KB, shared by every mod.
  - **The zero region above `0x400d8000` is the PROJECT subsystem's RAM.** A menu table placed in a 15 KB zero run at `0x401087e4` crashed a unit.
  - Larger code goes to a loader-copied area: octabam's loader is a stub at `0x4010fdf0`, right after the OS image, reached from the boot site. `[hw]`
- DSP code that does not fit a core's P memory (ends `P:0x1fff`) runs from the shared window `P:0x30000-0x3ffff`. This was proven on a unit (PEXT probe, 2026-10-25). `[hw]`
- **DSP scratch:** r7 scratch `$00-$83` is the per-instance block, and **`$84+` hangs the unit**. Stock effects scratch `X:0x20-0xff`, and the hardware dispatcher passes the audio block at X:0. `[hw]`

## DSP56300 assembler and emulator traps (from octabam's trap register; each cost real work)
- `dsp_asm` **silently mis-encodes**: `tfr a,b` as `rnd b`, and any `mpy` operand order it does not know as `mpysu`. `lua (rN+d),rM` takes d in -64..63 and silently wraps larger values. Labels resolve **by prefix**, so a new label may not have an existing label as its prefix.
- DSP56300 semantics:
  - A logical op on an accumulator leaves the extension byte stale, so the next store saturates to full scale.
  - `move a,b` limits; `tfr a,b` moves all 56 bits.
  - A Tcc pair sharing one compare breaks with any arithmetic in between.
  - `asr #n,a,a` shifts into a0, and Z is set only when all 56 bits are zero.
  - Reading a0 exposes the fractional left shift that a1 hides.
- **No `rep` in an effect's init or proc** (it cannot be interrupted, and the host-command handlers need to run). No dense X work in a DMA's 8K block.
- **Instruction-form rule, as on the SHARC:** a DSP form ships only if a stock payload runs it or a hardware probe approved it.
- **Stock Unicorn halves every ColdFire fractional-mode multiply and adds where `msac` subtracts** (the firmware runs EMAC with MACSR = 0x20), and its MAC-with-load decode has three defects. MACSR S/U is bit 6, and in fractional mode it selects 16-bit rounding. These are the same EMAC pitfalls as on the Syntakt and DN2 (rule G-series, `common/toolchain-and-emulators.md`). `[hw]`
- The emulator (`ot_emu`) charges one step per instruction, with no cache or memory timing. A change can be cycle-identical in the port and several percent worse on the unit.

## Gaps
NOR layout beyond the OS window, the trig dispatch source, the MKI vs MKII hardware differences beyond the CPU marking.
