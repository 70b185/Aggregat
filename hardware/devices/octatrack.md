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
- **How stock writes NOR** (1.40C, Modwerk's reading, `[doc]` {modwerk-ot-traps}):
  - OS UPGRADE reads the whole card file into RAM, then erases and programs NOR from there (sector erase `0x40020628`, 256-byte page program `0x400206f4`, the 37 sector starts listed at `0x400a95c0`).
  - The layout is 8 KB boot sectors from `0x4000`, then 64 KB sectors up to `0x1f0000`.
  - Both routines poll the chip themselves and mask interrupts only around the command bytes, so a mod can call them from a task without breaking the frame interrupt.
  - The bootloader below `0x4000` is never written. It depacks NOR from `0x4012` **without checking anything**, so an image that doesn't boot is recoverable over DIN MIDI only. The startup menu's MIDI UPGRADE checks the received file, not NOR. `[hw]` (testers' units)
- **Don't verify a running image against its own RAM:** once running, stock rewrites bytes inside its bootloader copy (`0x400e201e-0x400e2108`) and reuses the RAM after the image. Compare against digests taken before stock started. `[hw]` {modwerk-ot-traps}
- After flashing a build that changes an effect's parameter layout, old projects need their stored values stamped. A select value outside its count stalls the sequencer on first play. `[hw]` ([I28](../INCIDENTS.md#i28-a-select-value-outside-its-count-stalled-the-sequencer))

## Memory and code placement
- **The free ROM is small:** zero runs in `0x400c0000-0x400d8000` total ~8.4 KB, shared by every mod.
  - **The zero region above `0x400d8000` is the PROJECT subsystem's RAM.** A menu table placed in a 15 KB zero run at `0x401087e4` crashed a unit. ([I48](../INCIDENTS.md#i48-a-menu-table-in-a-free-zero-run-crashed-the-unit))
  - Larger code goes to a loader-copied area: octabam's loader is a stub at `0x4010fdf0`, right after the OS image, reached from the boot site. `[hw]`
- DSP code that does not fit a core's P memory (ends `P:0x1fff`) runs from the shared window `P:0x30000-0x3ffff`. This was proven on a unit (PEXT probe, 2026-10-25). `[hw]`
- **DSP scratch:** r7 scratch `$00-$83` is the per-instance block, and **`$84+` hangs the unit**. Stock effects scratch `X:0x20-0xff`, and the hardware dispatcher passes the audio block at X:0. `[hw]` ([I29](../INCIDENTS.md#i29-dsp-scratch-at-84-and-up-hung-the-unit))

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

## USB device side (both octabam and Modwerk, measured on units) {octabam-traps} {modwerk-ot-traps}
- **No EP0 reply or OUT data stage may be a whole multiple of 64 bytes.** A reply of 64/128/192/256 bytes left a stale zero-length packet, and the next request returned 0 bytes (once, the unit froze). Stock leaves zero-length termination on in the EP0 OUT queue head, so a 128- or 192-byte OUT stage never completed. Send one byte less, or clear ZLT when priming. `[hw]` Rule A39. ([I5](../INCIDENTS.md#i5-ep0-data-stages-of-a-multiple-of-64-bytes-stall-or-freeze-stock-usb-driver))
- **About one EP0 OUT stage in 50-100 goes unanswered** on a MKII: completed inside the ISR after stock's poll, or stopped part-way. Modwerk runs a 60 Hz tick that finishes a completed stage, or stalls EP0 after 0.5 s so the host resubmits. `[hw]` ([I6](../INCIDENTS.md#i6-about-one-ep0-out-stage-in-50-100-goes-unanswered))
- **DMA reads RAM, not the copyback cache.** A value the CPU stores rarely stayed stale for minutes in USB replies, while values stored every frame looked live. Copy a reply through the uncached alias and send it from there. `[hw]` (Same idea as A28 on the SHARC.) ([I35](../INCIDENTS.md#i35-usb-replies-stayed-stale-for-minutes))
- **A soft reset leaves the USB controller and PHY as they were:** one RAM boot in about six came back with no USB until a power cycle. Stop the controller (USBCMD.RS = 0) and wait ~50 ms before resetting; that gave 20 of 20 good boots. `[hw]` {modwerk-ot-traps} ([I7](../INCIDENTS.md#i7-a-soft-reset-leaves-the-usb-controller-running))
- **Never post key events into stock's queues directly** (two crashes minutes later). Feed the panel parser its own bytes instead. `[hw]` {modwerk-ot-traps} ([I30](../INCIDENTS.md#i30-key-events-posted-into-stocks-queues-crashed-the-unit-minutes-later))

## ColdFire load (Modwerk's meter on a MKII, Oct 2026) {modwerk-ot-traps}
- The Modwerk base with nothing installed shows ~42-47 % CPU. That is mostly stock's own tasks; there is no clean stock baseline yet. `[hw]`
- An FM synth module costs ~8 points just by being installed, plus ~5 while a track plays it. Small effects cost 0.5 points or less on the ColdFire, but their DSP cost lands on their core (BBD on T6: core T5-8 went from ~44 % to 54 %). `[hw]`
- **Uncached module code is expensive:** Analog BD on one track cost ~20 points.
  - 93 % of each call was a write lease whose owner check read the module header through the uncached alias (~0.6 µs a read).
  - With one lease per frame it dropped to ~10 points.
  - Lesson: take locks only where a call writes, at most once a frame, and keep uncached reads out of hot paths. `[hw]`
- UI-task edits can cost milliseconds: a 64-step MIDI rewrite took 3.9 ms per knob turn, mostly stock's lock-index rebuild. Updating only the own track's bits brought it to 0.5 ms. Audio frames stayed ~406-417 µs apart throughout, because it all ran on the UI task. `[hw]`
- **The DSP peak meter shows the busiest single frame** of a 1,024-frame window. A self-test or sync leaves it at ~99.7 % while the mean is flat and the audio fine. Judge overload by the longest frame of a real load, not the peak. `[hw]`
- **Frame budget from the field (Modwerk beta, 2026-11-08):** audio frames are 363 µs apart (16 samples), and the DSPs starve once a gap passes about 515 µs. A unit left stopped and connected for about 23 hours with 6 modules showed 42 % CPU and a longest gap of 423 µs, with no freeze. `[hw]` {modwerk-ot-beta}
- **Open: stalls after PROJECT > SYSTEM walks** (Modwerk finding 72, several units, nothing installed or no base change): the DSPs report stopped after key walks that likely open USB DISK MODE or OS UPGRADE and back out. The first full stall record puts the stall 15-17 s into the boot, not at the walk 109 s in. So either stock resets the base's counters when it enters that mode, or the walk did not cause the stall. Not yet reproduced on a unit with a stock OS, so not a stock bug (rule C12). `[hw]` {modwerk-ot-beta}

## More DSP and boot traps (measured on units) {octabam-traps} {modwerk-ot-traps}
- **An effect's `init` must preserve r1:** the FX1 dispatcher keeps the effect id there and calls `proc` through it. An init that moved r1 jumped to the reset vector and killed the core at project load. octabam's build refuses an init that writes r1/n1/m1. `[hw]`
- **A persistent slot that `init` does not clear holds the previous effect's leftovers.** The emulator boots with zeroed RAM and cannot show it. `[hw]`
- **Resident window code must sit in `0x33da3..0x37eff`:** payload B's boot loop clears `Y:0x37f00..0x3ffff`, and DARK REV writes up to `0x33da2`. `[emu]` (both cores faulted at boot in the port)
- **A DSP frame counter past `$7fffff` saturates in `move a,nN`**, which stopped a frame engine after 50.7 minutes. Mask counters to 23 bits. `[hw]` ([I32](../INCIDENTS.md#i32-a-dsp-frame-counter-saturated-after-507-minutes))
- **Core 1's load-meter counter** is at `X:$2840` on Modwerk USB bases; module state there gave a jittery pitch. `[hw]` ([I33](../INCIDENTS.md#i33-module-state-on-a-load-meter-counter-gave-a-jittery-pitch))
- **Cold starts:** an early-startup change passed emulator boots and quick power cycles but stalled at the logo after several minutes powered off. Keeping the activation helper resident in the OS image fixed it; the mechanism is unknown. **Qualify startup changes after a long power-off** (rule A40). `[hw]` ([I34](../INCIDENTS.md#i34-a-startup-change-stalled-at-the-logo-after-a-long-power-off))
- **A write-watch on cached addresses is blind to a clear through the uncached alias.** A "free 8.8 MB" region turned out to be the stock delay rings. Before trusting a null result, ask what the instrument cannot see (rule A31). `[emu]`

## From KYOTI (Zac-Kyoti/octatrack-kyoti-fw, OS 1.40C) {kyoti-fw}
- **A core's crash threshold, found on hardware in KYOTI's own cost model:** stock's heaviest effects plus the sidechain compressor model at ~3,516 cycles per sample. The core crashed somewhere between ~3,760 and ~3,830.
  - With DJ EQ in both slots on T5-T8, one extra REPITCH voice (~240) was clean; adding a second (RPS9 ~77 or RPSP ~240) crashed.
  - KYOTI's bar: a feature must not break any configuration that is clean on stock. So **beside stock's heaviest effects a core has room for about one heavy voice**.
  - Note that these "modelled cycles" are KYOTI's estimate, not octabam's measured 4,532 cycles per sample. Compare figures only within one model. `[hw]`
- **The DSP shared window in work RAM is volatile:** at boot, `0x401086f4` is copied to `0x80000000` (`0x3e88` bytes) and the rest is zero-filled up to `0x80004000`. Nothing of yours survives there across a boot. `[doc]`
- **One image for MKI and MKII:** the OS probes `0x46c8d18c` and shows 15 (MKI) or 16 (MKII) PERSONALIZE items. `[doc]`
- KYOTI keeps a merged, confidence-tagged 1.40C address map (`reference/kb/memory-map.md`) that cross-references octabam. It is a good second reading. `[doc]`

## Debugging on the unit by writing a log to the CF card (OctaMax, MKII, OS 1.40C) {octamax}
- When the emulator cannot run the code you need to see (here, the EMAC-heavy frame builder), log from the unit itself.
  - OctaMax added two detours that call the firmware's own file primitives (open `0x40016864`, write `0x400166b8`, close `0x4001677c`, sprintf `0x40013a08`) and write `/HOTDBG.TXT` to the CF card.
  - Pull the card and read it.
  - It works on hardware, and it showed that values seeded in the emulator had been guessed wrong (a voice type byte of 1, not 4). `[hw]`
- **The DSP never plays on its own:** every frame the ColdFire builds a per-voice packet in shared RAM (double buffer at `0x80000000`, selector `0x800000e0`) and pokes the DSP. A voice that stops being fed goes silent without any "stop". `[doc]`
- Recorder buffers live in a paged RAM pool (base `0x40a955e0`, ~89 MB) that survives a project change; the voices are torn down and rebuilt by the load. `[hw]`
- **Restoring state every frame is safe only for CPU-side bookkeeping.** Overwriting data the DSP reads corrupted the audio. `[hw]` ([I31](../INCIDENTS.md#i31-restoring-dsp-read-state-every-frame-corrupted-the-audio))
- An Octatrack emulator built on QEMU (ColdFire MCF54455) plus dsp56300, octemu by markandrus, targets firmware development including USB MIDI and audio; PassOS uses its 20-channel USB audio work. `[doc]`

## Where code and data may go: KYOTI's cave ledger (OS 1.40C, `reference/kb/caves.md`) {kyoti-caves}
Five projects (octabam, octalab, midisc, octemu, ems-octakit, KYOTI) cut code into the same few kilobytes of the same image. Read KYOTI's ledger before you pick an address.
- **The parameter-page descriptor table is live data, zeros included.** It is 31 entries of `0x192` bytes at `0x400d2e52-0x400d5f00`, and a zero entry means "the default". Never place code or data there unless the entry is proven unreachable. `[hw]`
- **The canary test** (from octalab) before anything ships in a new region:
  1. Fill the range with a pattern, or a 32-bit counter so that partial overwrites show.
  2. Use the unit for a full session: load, record, change patterns, save, power-cycle, load again.
  3. Read the range back and compare.

  octamax lost tables to a heap tail and probe counters to a region restored on every load. See rule A43. `[hw]`
- **Scratch RAM `0x80006a40+` is not safe under live audio:** a magic word at `0x80006a60` was overwritten by the next key press on a real MKI while recording; the emulator, which runs no DSP/audio path, kept it forever. `[hw]`
- **Past the image's ceiling, two routes:**
  - append a runtime after the OS image (octabam's loader stub; proven on an MKI);
  - put a position-independent payload with a relocation table on the **CF card** and load it at run time. octemu does this for USB audio (four UAC2 descriptors, iso servicing and a 36 KB ring against ~408 B of slack).

  `[doc]`

## Gaps
NOR use above the OS image, the trig dispatch source, the MKI vs MKII hardware differences beyond the CPU marking.
