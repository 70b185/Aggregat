# Octatrack (MKI, MKII) - OS 1.40C

Coverage: **first profile** (phase 2). Source: sambanks/octabam docs (`docs/firmware/CHIP.md`, `ARCHITECTURE.md`, `DSP.md`,
`docs/contributing/PLACEMENT.md`, `TRAPS.md`, `docs/guide/BUILDING.md`), read 2026-11-02. octabam marks its facts measured (✅),
inferred (🟡) or retracted (❌); we keep `[hw]` for its hardware rows. Projects: [../../catalog/octatrack.md](../../catalog/octatrack.md).
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
- **Settled: the silence after USB DISK MODE was Modwerk's, not stock's** (finding 72, 2026-11-10): stock pauses the DSP while USB DISK MODE is open; Modwerk's base took that pause for a stalled DSP, and its recovery kept the audio stopped until a power cycle. Fixed in the base; on the owner's MKII (1.40C) PROJ > USB DISK MODE, about 10 s, NO, PLAY now plays. Not tested: the walk on a flashed base, a file copy in that mode, an OS upgrade from the card. A mod that watches for DSP stalls must tell stock's own pauses from a stall (rule C12: it was never reproduced on a stock unit). `[hw]` {modwerk-ot-unit-1110}
- **Field stalls with modules (Modwerk beta, 8-10 Nov):** stalls still come within about a minute of installs or restores, before any module code is placed (finding 71), and on a heavy self-test Part (FILTER and DELAY on every track plus FLANGER and PHASER) 1 run in 21 stalled on the live base, 0 in 5 on the lighter Part; only a power cycle recovered. The base's longest fully masked span measured about 14 µs, far under the roughly 200 µs that stops core 0, so masked ColdFire code is unlikely but not ruled out for the stall itself. One field crash record: vector 3 inside a module's ColdFire code. A unit with 6 modules stayed up 70 hours (longest frame gap 424 µs). `[hw]` {modwerk-ot-beta-1110} {modwerk-ot-unit-1110}

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

## octabam and octamax findings (2026-11-10)
- **AMP envelope:** the DSP's AMP envelope restarts from zero at every trig START, so with any ATK above 0 a sound that plays across trigs drops out and fades back in, a click on every note. A ColdFire machine holds the DSP at ATK 0 / HOLD INF / REL INF and shapes AMP itself, as SYNTH MACHINE does. Measured laws (Tim Hastie): ATK is a linear ramp of 3.85 ms x 2^(ATK/8.53), at least 16 frames; REL is exponential with tau 0.295 ms x 2^(REL/8.53). `[hw]` {octabam-wavecf} (I58)
- **Crossfader:** stock maps the crossfader through one table of 128 Q15 values at `0x400bcd90`; the panel handler `0x40061e40` and the MIDI CC 48 handler `0x400626ba` rebuild the per-track weights at `0x80003c60` from it. Replacing the table changes scene locks, XVOL and the morph alike; MIDI SCENES mixes linearly on its own. `[hw]` {octabam-xfcurve}
- **Demand loading:** the loader copies a whole effect block (MODULATION, 1,561 words, an estimated ~31k of the 72,512 cycles in a frame) inside one DSP frame hook; the DSP-busy meter reads 99.7 % in that window `[hw]`. The frame interrupt has two waits with no time limit (the loader's wait before each host word, and stock's spin at `0x4000ab26` until the DSP takes the frame's `0x8c` host command); if the DSP stops taking host words, the ColdFire can spin forever `[?]` {octabam-dl} (I57, H22).
- **CF write throughput (STEM REC, MKII):** write time per KB grows with the number of files written at once: 54-92 us/KB for one file, 423 us/KB for eleven (212 after writing whole 32 KB clusters only). Samples streamed by Static machines from the same card slow writes further (252 -> 387 us/KB for ten files); eleven 24-bit files need 2.9 MB/s. `[hw]` {octabam-stemrec}
- **Test host:** octabam's hardware tools run on Linux and on WSL2 with usbipd; MIDI, transport and the load meter work there, but USB-audio capture over usbip delivered only about a quarter of the frames. `[hw]` {octabam-hwtest}
- **Key bus (Modwerk):** the key bus moved from Y `$800-$9FF` to Y `$7E00-$7FFF` on each core, the tail of the first internal FX2 slot, which frees Y `$7F0-$9FF` for a DSP machine's voice. An FX2 effect that fills the whole 16,384-word buffer is then refused on T1/T5; Mini Verb, E-Verb (15,870 words) and BBD still fit. A keyed duck lands within one 5 ms window of the kick, on the same core and across cores; in the DSP simulator the cross-core key arrives exactly two blocks late. Four RINGMOD SC plus four BBD while playing: CPU 85.1 %, core peaks 66/74.5 %. `[hw]` (MKI 2026-10-30, MKII 2026-11-10), memory survey `[emu]` {modwerk-ot-keybus}
- **Module cost (Modwerk survey):** module DSP code runs at 1.4-1.7 cycles per instruction against about 1 for stock, and installed but unused modules add frame-interrupt time (23.3 % -> 28.2 % stopped with 26 installed). `[hw]` {modwerk-ot-options}
- **Internal SRAM has no free holes:** `0x80000000-0x80008000` is the program's `.data`/`.bss`, filled at boot from the image tail; `0x80006964-0x80007574` is the work buffer of the stock audio-analysis task, which writes up to 768 words from `0x80006974`. This explains the KYOTI scratch-word loss at `0x80006a60`. OCTAMAX keeps patch state in DDR at `0x40af0000-0x40af0600`, inside a reserve stock never references, cleared by its boot stub. `[hw]` {octamax-notes} (I59; boot-fill extent disputed, CONFLICTS O23)
- **Sequencer state:** current bank/pattern at `0x800065bd/be`, the cued pair at `0x800065bf/c0` ("nothing cued" when both pairs are equal); cueing the playing pattern cancels in stock, and a switch to the same pattern is a restart with no Part reload. Active bank `0x80000002`, active Part `0x80000003` (disputed, O23); whole-Part apply `0x40009094`. `[hw]` {octamax-notes}
- **Step timing (KYOTI):** the sequencer schedules each step one step ahead, so a Part change sent to the engine in the landing tick sounds a step early; a per-track apply must wait one of the track's steps `[hw]`. The whole-Part apply posts a kernel message and belongs on the UI task; a storage job's done-callback runs on the UI task, which ticks at 1/60 s `[emu]`. Copies with interrupts masked click (I60). {kyoti-reload}
- **Sample pool:** paged in 6 KB pages (MEMORY shows 85.5 MB); KYOTI V1.7 takes 11 pages on DRAM units, octabam reserves 10 MiB when any module runs from DRAM, 18 MiB with STEM REC. `[doc]` {kyoti-build}

## octabam findings (2026-11-11)
- **Audio-interrupt budget (CX OSC on a MKII):** with nothing playing the ColdFire idles at 44.7 % with a mean audio interrupt of 125 us (max 212 us); four CX OSC tracks: 21.8 % idle, 272 us; six: about 12 %, 309 us mean but a 376 us maximum past the 363 us frame; seven: 0 % idle and MAIN clipped. The module now refuses a seventh instance. `[hw]` {octabam-cxosc}
- **Stock icon blit** (`0x400128a8`, a 13-row column word with mask `0xfff80000`): bit 31 is the bottom row and bit 19 the top, so a left shift moves the picture down. Five flashes went into one pixel before this was written down. `[hw]` {octabam-traps}
- **FLEX slices (DRUMMER, OS 1.40C):** in slice mode the voice start `0x4000f450(track, slot, flags)` plays slice `min(STRT >> 1, count - 1)`; the slice table is 64 entries of 12 bytes from +312 of the FLEX slot record `0x100b14f0 + 0x448*slot` (octabam's own STORAGE note said 20 bytes; the code multiplies by 12). `[emu]` {octabam-drummer}
- **Adding and moving trigs:** the sequencer builds each step about 912 samples after the step counter changes, one step ahead; a detour right after the builder (`0x400a2d82`) can add a trig on an empty step or rewrite its micro-timing (one unit is 1/24 of a step). Locks staged for an added trig are ignored, and its lock block holds zeros at boot unless the mod fills it (all 32 lane values of the track went to 0 until DRUMMER wrote `0xff` there). `[emu]` {octabam-drummer} DRUMMER ran on the author's MKII from these sites; two bugs found after the first unit test are I72. `[hw]`
- **Scene locks** sit at Part `+0x662 + (scene*8 + track)*32`, one byte per parameter, `0xff` for none. Retrig time RTIM is exponential: half a step at 79, doubling every 12. `[emu]` {octabam-drummer}

## Modwerk and octabam findings (2026-11-12)
- **Boot keys (OS 1.40C):** FUNC held from power-on opens Elektron's startup menu; PROJ held at power-on is ignored by the bootloader and the unit starts normally. Modwerk therefore moved its "skip modules" gesture from FUNC to PROJ on the MKII (the MKI keeps FUNC). `[hw]` {modwerk-ot-base}
- **Scene keys take the encoders:** pressing a scene key writes stock's scene-lock knob handler `0x40053498` into every encoder slot of the table at `0x46c7dede + 20*enc` (writer `0x40031406`, dispatch `0x40031944`), so a page editor's hook sees no turn while a scene is held. `[emu]`, seen by a user {octabam-traps}
- **Stock calls clobber scratch registers:** the CC sender `0x4009eec8` saves only d2-d7/a2-a5; any `jsr` into stock can change d0, d1, a0 and a1. `[emu]`, seen by a user {octabam-traps}
- **Render after stock's trig work:** in SYNTIZ, a render in the same frame after stock's trig handling cost up to 2.25x a first render (33.6 % vs 14.9 % of a frame); stock's own work reached 84 % of a frame at pattern transitions. Modwerk refuses a RAM boot or trial while the sequencer plays. `[hw]` {modwerk-syntiz}
- **An installed module that never plays can cost margin:** on an MKII, FM Synth 0.1.2 installed beside SYNTIZ gave light crackle and one sample track less of headroom; removing it cured both (one A/B, cause unknown). `[hw]` {modwerk-syntiz}
- **Removing a module in use** left the loader stuck in recovery until a power cycle (I75, rule A54); a base update over USB once reported Done and did not stick (I76). `[hw]` {modwerk-syntiz}
- **USB base:** Modwerk's Octatrack base is open to everyone since 2026-11-11; the first install still goes through the CF card, a module set holds at most 20 modules, and USB Audio is off (USB MIDI only) unless the set has the USB Audio module. `[doc]` {modwerk-ot-base}
- **Analog BD 0.1.7 (909 model):** tables and voices in DSP X `$2841-$3200`, next to the core-1 load counter at X:`$2840`; glue plus engines take 1,003 P words per core. On an MKII a voice on T5 (core 2) was refused even alone with every core-2 effect slot off, and the DSP `meter` command did not answer on that base. `[hw]` {modwerk-analogbd}
- **A recorder started on the first PLAY after power-on** (MIDI mode, T1 idle), probably from a quantized REC start left staged at `0x800018be`/`0x800018de` (QREC branch of REC_POST `0x40005178`); a double STOP before PLAY avoided it (I78). `[hw]`, cause `[?]` {octabam-freeloop}
- **The stock DELAY's coefficient table `0x400d1ce0-0x400d2cdf` is not free space:** its upper half is zero in the stock OS and looks unused, but DELAY reads it. Code that card builds placed there dulled DELAY repeats; Modwerk's checks now refuse any package or base site that writes into it. `[doc]` {modwerk-1112}
- **CPU-rendered machines need a budget like DSP effects:** on the owner's MKII, three FM Synth tracks beside a busy eight-track pattern froze the unit (I79). Modwerk's base now prices machines (first estimates: 45 % of the CPU for added machines, 12 % for one that names no price), refuses a pick over the limit (CPU FULL) and drops a voice instead of freezing. Seen on development builds; the release base was not run on a unit. `[hw]` {modwerk-1112}
- **Modwerk dropped its card firmware builder (2026-11-12):** Octatrack modules now reach a unit only through the Modwerk base, over USB or as one set file (`MODWERK0.SET`) on the CF card. `[doc]` {modwerk-1112}
- **FREE LOOP and RELOAD_FROM_PROJECT can share the UI tick:** both detour the UI task's 1/60 s tick `0x40056c28` (the toast countdown's read), which made them a listed conflict. octabam's HOOKS now chains the site (FREE LOOP first, then RELOAD_FROM_PROJECT); the chain passed four cases under Unicorn, not flashed yet. `[emu]` {octabam-hooks}

## Frame-interrupt timing and MIDI scenes (octabam, 2026-11-13) {octabam-frameguard}
- **Frame grid:** the DSP raises the frame interrupt once a frame (362.8 µs) and the ColdFire answers with the next frame; the handler's entry is `0x4000aad0`. At START and at a program change one frame interrupt runs 475-585 µs on every image measured, so the next one enters late. `[hw]`
- **Late-entry window:** measured on an MKII, an entry 128-149 µs late is followed by one back-to-back frame interrupt and the unit runs on; 155-223 µs late, one frame is skipped and it runs on; the two stalls logged entered 149 and 155 µs late, after which the DSP took no more frames (sequencer held at step 1, panel and USB alive, power cycle needed). A USB audio capture adds 25-30 µs to the START frame. octabam's FRAME GUARD waits out entries 110-190 µs late until 190 µs; the DSP-side mechanism is inferred (I82, rule A56). `[hw]`
- **Open:** on a test image with 60 µs added to every frame interrupt and a 20-channel capture (the frame interrupt at 91 % of the ColdFire), 7 of 16 STARTs froze the whole unit 8.2 s later, at the pattern's wrap; not seen on shipping images. `[hw]`
- **Scene lock view (stock):** the audio pages draw scene locks from a view byte `0x460d1694` (1 scene A, 2 scene B), set only by the hold-and-turn paths and the scene press handlers `0x40054c80` (A) and `0x40054c5c` (B), which return at once in MIDI mode; the MIDI key's handler (`0x40055548`-`0x40055676`, tail `jmp 0x4007e998` at `0x40055670`) does not set it. So a scene held while switching from the MIDI to the audio tracks shows no locks on stock; octabam's MIDI SCENES hooks the tail to fix that. `[emu]` {octabam-msc}

## AERIA OS findings (own OS on the MKII, 2026-11-09..13) {aeria-log}
- **Audio codec:** the converter on one MKII board was read as a Cirrus Logic CS42432 (marking read off the board). `[hw]` (one unit)
- **Stock does not set up the codec over SPI;** its only SPI traffic is the real-time clock (stock's code traced, every hardware write logged in octabam's emulator). `[emu]`
- **The analog outputs stayed silent under an own DSP program** that copied every DSP register write stock makes; inputs worked. Bisecting put the switch-on in a ~40 ms slice of stock's start-up where its frame exchange with the DSP begins, and the outputs came alive once the engine used a DMA-driven audio ring restarted by a DMA interrupt, as stock does. `[hw]` What actually un-mutes them is `[?]`: the CHANGELOG names the codec's DAC mute, the log the DMA ring. {aeria-changelog}
- **DSP memory per core:** a probe on core 0 measured 48K words of private Y and 36K words of private X (core 1 assumed the same). `[hw]`
- **Running code from the shared window costs about 2x,** and the two cores slow each other there. Moving AERIA's engine into core 0's private P memory cut its worst case from ~700 to ~370 instructions a sample and a sequencer stress test from 89 % to 50 % of core 0. `[hw]` {aeria-changelog}
- **Shared-window memory is not zeroed at a cold boot,** unlike in the emulator; core 1 ran a garbage effect from an uninitialised slot table and crashed (I84). Clear any table there before use. `[hw]`
- **A crashed core 1 blocks a DSP reload over USB;** only a power cycle clears it. A memory probe that wrote past the end of core 1's private memory did the same. `[hw]`
- **Feeding sample audio to the DSP word by word over the host port starved it** (about 4,000 frames a second instead of 44,100); taking the data by interrupt, later by DMA sorted once a frame, held full rate. `[hw]`

## Modwerk findings (2026-11-12/13) {modwerk-1113} {modwerk-perf}
- **Stall frames:** Modwerk's base keeps the 128 frames (46 ms) before a DSP stall in battery RAM at `0x100ffb30`, next to its crash record `0x100ff800` and stall record `0x100ff900`: for each frame the gap to the one before (363 µs on time) and how long the frame interrupt before it ran. `[doc]` {modwerk-ot-driving}
- **Older Modwerk stalls are ambiguous:** stalls at a high frame-interrupt share (24 Oct, POLY8 + FM Synth + USB recording; 10 Nov, FM Synth beside eight FLEX tracks) kept no entry times, so they cannot be told apart from the late-entry stall (I82). `[hw]` (stalls) / `[?]` (cause)
- **Busy-unit refusal:** the base refuses a module machine or effect pick while the CPU meter stands at 85 % or more over its last four seconds; stock machines and effects are never refused. Since 2026-11-14 the guard also adds the picked machine's own price and judges a stopped unit by its last playing load, after picks accepted while stopped led to a stall (I105). In diagnostics from 32 units, a five-minute window at 85 % or more had a UI-tick gap over 100 ms more often than not; under 65 %, one window in twenty did. `[hw]` (field)
- **Stock CPU meter readings (MKII, OS 1.40C):** about 45 % stopped and 60-75 % playing on a stock unit; a stopped unit spends a second or two near 90 % on a key press or project load, with or without modules. Going from 62-74 % stopped to 87-97 % playing made knob redraws wait 0.1-0.2 s. `[hw]` {modwerk-1114}
- **Two-step base update:** a base too big for an old unit's RAM stage installs through a smaller step base; with the host lost during the send or save the unit finished the write and the next update completed, and two power cuts during a slot write left that slot incomplete while the confirmed base still started. The base stages the next image in 1.5 MiB of RAM (1.25 MiB before 2026-11-13). `[hw]` {modwerk-1114}
- **Unit left USB during a USB Audio recording** with Amiga 0.2.0 on a development base, 231 s into the trial, and did not come back; cause open (I107). `[hw]` {modwerk-1114}
- **Judge panel lag by the CPU meter, not the frame guard's share:** on an MKII, Euclid on one track raised the guard's share by 10 points but the CPU meter by only 2.5. `[hw]`
- **Read battery RAM once a frame:** one read of the current Part index `0x100b14cf` costs about 0.5 µs; modules that read it at every site for every track added about 8 points of frame interrupt while installed on no track (MKII, 2026-11-10). `[hw]` Later bisects (2026-11-14) put only 0.6 of POLY8's 12.2 points in that read: most of the cost of a module installed on no track came from touching module code or data on every stock track's path, most likely cache misses (inferred, no cache counters read). Measured beside 4 FLEX tracks: FM Synth 0.1.2 +19.0 points, POLY8 0.3.1 +12.2, Repitch 0.2.0 +5.3; after the fixes POLY8 0.3.3 +4.9 and FM Synth 0.1.3 +3.2; declaring `RENDER_FLEX` alone cost 6.5 points on 4 tracks. Stock calls the increment builder `0x40004100` on every frame's second render of every track, so an increment subscriber runs once per track per frame. `[hw]` / `[doc]` {modwerk-1114}
- **Windows keeps an interface's first setup:** WinUSB opens the vendor interface (`VID_1935&PID_0002&MI_01`) only while `DeviceInterfaceGUIDs` is under its Device Parameters key; Windows writes it once, and a replug at the same `bcdDevice` did not bring it back. A new device revision (stock 0x0001 -> 0x0101) made Windows write it again (I100). `[hw]` {modwerk-win-usb}
- **RAM-boot restarts and USB:** a twin RAM-booted through a serve session kept running but dropped off USB until a power cycle (2026-11-13); the clean-restart figure rests on 20 boots. `[hw]` {modwerk-ot-driving}
- **Remote keys wait for a whole panel report:** a USB key spliced between a fader report's two bytes left TRIG keys held or lost a FUNC release; the base now queues keys and sends them only when the panel parser expects a report's first byte. `[emu]` / `[hw]` {modwerk-ot-driving}
- **One Part byte outside its stock range drops a whole bank at power-on** (SB22, I95): the battery restore checks Parts before any loader restores its modules. `[hw]` {modwerk-vector}

## Stock OS facts from elekloader's core-ot 0.9-0.40 (OS 1.40C, static reading and emulator probes, 2026-11-13) {elekloader-core-ot-events}
- **Settings record:** stock copies the battery-RAM settings record (`0x100fff00`, 100 bytes) to the live settings at `0x80000070` at boot and in two panel actions. `[doc]`
- **Pattern validator:** stock checks and clamps every pattern at boot's restore (before any mod's data is back) and at every bank load; a mod that keeps values in pattern bytes stock does not know must restore them after the check. `[doc]`
- **LFOs:** 19 waves (TRI to RND, then T1-T8); the LFO step runs in the frame interrupt for each of a track's three LFOs (24 calls a frame); phase `0`-`0x7fffff` over a cycle. The EMAC accumulator is live there, so hooked code must not use it. `[doc]`
- **Playback increment:** each STATIC, FLEX and PICKUP track gets a Q26 increment every frame (`0x04000000` plays at the sample's own speed); elekloader's sites sit beside octabam REPITCH's at `0x40004100`. `[doc]`
- **Interrupts and timers:** the frame interrupt is vector `0x41`; the UI task ticks 60 times a second with 32 timer slots. A stock routine that returns a pointer answers in d0, while GCC expects a0. `[doc]`
- **Card and engine:** the CF card's dispatcher issues 22-byte command records (ATA command byte at +5); the engine task runs stock jobs 0-45 (job 16 is the sample editor's render/commit). `[doc]`
- **Panel:** the LED map is 17 bytes, one bit per LED; stock rewrites its bits at every flush, so a mod sets its LEDs again at each flush. `[doc]`
- **Sequencer timing:** each track's length check and the master pattern's wrap run in the sequencer's tick, a timer interrupt, so code hooked there must stay a few dozen instructions. `[doc]`
- **SEQUENCER menu rows:** octabam's SCALE QUANTIZER v1.0 and elekloader's seqrows-ot patch the same seven places in PROJECT > CONTROL > SEQUENCER and refuse each other. `[doc]`

## Gaps
NOR use above the OS image, the trig dispatch source, the MKI vs MKII hardware differences beyond the CPU marking.
