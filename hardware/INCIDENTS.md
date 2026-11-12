# Incidents: what went wrong on real units, why, and the rule it taught

A register of failures and tests on real Elektron hardware: stock firmware bugs, mods that hung, crashed or silenced a
unit, places where an emulator or tool disagreed with the unit, and recoveries that were used. Each incident names the
unit and OS, what was seen, the cause **and how the cause was found**, the fix, the evidence level and the rule in
[AGENT-RULES.md](AGENT-RULES.md) that it taught.

How this file relates to the others:
- The **fact** stays in the device page (`devices/…`, `common/…`); it carries `(I<n>)` and links here.
- The **rule** in AGENT-RULES.md names the incidents it comes from. Rule C11: every new incident gets an I-number,
  and if it teaches something general, a rule, or an existing rule gains it as evidence.
- Something not yet seen on a unit is a hypothesis ([HYPOTHESES.md](HYPOTHESES.md)), not an incident.
- Numbers are permanent. A new incident takes the next free number and goes into its group, so numbers within a
  group are not consecutive.

Evidence levels as everywhere: `[hw]` seen on a unit, `[emu]` emulator, `[doc]` a project's own statement. "Cause
found by" says whether the cause was measured on the unit, read statically from the code, shown in an emulator, or is
unknown. Source keys `{…}` resolve in [SOURCES.md](SOURCES.md). The website and `export/aggregat.sqlite` (table
`incidents`) carry the same list.

Groups: [S. Stock firmware bugs and limits](#s-stock-firmware-bugs-and-limits) ·
[M. Mods that failed on a unit](#m-mods-that-failed-on-a-unit) ·
[E. Emulator or toolchain disagreed with the unit](#e-emulator-or-toolchain-disagreed-with-the-unit) ·
[R. Recovery and transfer links](#r-recovery-and-transfer-links)

## S. Stock firmware bugs and limits

### I1. Stock eMMC TRIM fails with TRIM ERROR on a busy card
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.39, erasing mod data), 2026-11-05
- **Seen:** TRIM ERROR at sector 817905, after a restart further on at CB1905.
- **Cause (read statically from stock code, not seen on the bus):** after CMD38 the stock busy wait arms the DAT0 edge interrupt before it tests DAT0; a short TRIM that finishes in between leaves a stale semaphore post, so the next TRIM on a really busy card returns at once and the call after it gets no answer. The driver has no timeout.
- **Fix:** read `PRSSTAT` `0xfc0cc024` before every TRIM and verify read, call only when idle; retry five times; ERASE PAUSED and resume on request (v0.40).
- **Status:** fixed in the mod; the stock race remains.
- **Evidence:** `[hw]` {dn2mk2-v040}
- **Rule:** A47
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I2. Stock song LOAD trusts a stored row count
- **Unit:** Digitone II, OS 1.11
- **Seen:** one project crashed stock and modded builds alike when opened.
- **Cause (read statically and confirmed on the project file):** song LOAD `0x400dea6a` copies `count` stored rows without checking it; the project held 21,503 rows instead of at most 99.
- **Fix:** repair the project (row count at record `+0x147`, storage version 4); mods must keep every count in range.
- **Status:** stock bug, open.
- **Evidence:** `[hw]` {dn2-oldproject}
- **Rule:** E3
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I3. USB upgrade receiver does not check the 2 MiB limit
- **Unit:** Digitone II
- **Seen:** an oversized image stalls at the end; nothing is written; a power cycle clears it.
- **Cause (seen on the unit):** the receive buffer is 2 MiB and the receiver does not check the size.
- **Fix:** keep the container under `0x200000` bytes.
- **Status:** stock limit.
- **Evidence:** `[hw]` {dn2mk2-firmware-md}
- **Rule:** A30, A9
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I4. Auto-commit upload loses its "complete" event on the first upload after boot
- **Unit:** Digitone II, OS 1.11
- **Seen:** the unit sits on "OS UPGRADE / Receiving".
- **Cause (read from stock code, seen on the unit):** with auto-commit the OS posts "upload complete" while the upgrade view is not open yet; the event is lost.
- **Fix:** upload without auto-commit, then send End(1), which checks the bytes and posts the event itself.
- **Status:** stock bug, worked around.
- **Evidence:** `[hw]` {dn2-skill-scripts}
- **Rule:** A21
- **Fact:** [devices/digitone-2-os111-firmware-map.md](devices/digitone-2-os111-firmware-map.md)

### I5. EP0 data stages of a multiple of 64 bytes stall or freeze (stock USB driver)
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk USB base)
- **Seen:** the request after a 64/128/192/256-byte reply returned 0 bytes; once the unit froze. 128/192-byte OUT stages never completed.
- **Cause (measured on the unit):** stock leaves zero-length termination on in the EP0 OUT queue head.
- **Fix:** size replies a byte short, or clear ZLT when priming.
- **Status:** stock behaviour, worked around.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A39
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I6. About one EP0 OUT stage in 50-100 goes unanswered
- **Unit:** Octatrack MKII (Modwerk USB base)
- **Seen:** host requests time out now and then.
- **Cause (measured on the unit):** the stage completes inside the ISR after stock's poll, or stops part-way.
- **Fix:** a 60 Hz tick finishes a completed stage, or stalls EP0 after 0.5 s so the host resubmits.
- **Status:** worked around.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A39
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I7. A soft reset leaves the USB controller running
- **Unit:** Octatrack (RAM boot through Modwerk)
- **Seen:** about one RAM boot in six came back with no USB until a power cycle.
- **Cause (measured on the unit):** the controller and PHY keep their state over a soft reset.
- **Fix:** stop the controller (USBCMD.RS = 0), wait ~50 ms, then reset; 20 of 20 good boots.
- **Status:** worked around.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A40
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I8. Power-on DDR holds garbage (often a NaN)
- **Unit:** Digitone II (SHARC)
- **Seen:** a NaN that reached a feedback state (a send effect) silenced the unit until restart.
- **Cause (seen on the unit):** DSP DDR is not cleared at power-on; the emulator zero-fills it and hides this.
- **Fix:** never read memory you did not write; fill new DDR with `0xFFFFFFFF` in tests.
- **Status:** hardware behaviour.
- **Evidence:** `[hw]` {dn2-skill-firmware}
- **Rule:** G8, G9
- **Fact:** [devices/digitone-2-os111-reference.md](devices/digitone-2-os111-reference.md)

### I9. A second application on the port corrupts SysEx replies
- **Unit:** Digitone II (and others with Overbridge/Transfer)
- **Seen:** with Overbridge holding the port replies were cut at exactly 885 bytes; with Transfer open a preset list showed 35 of 256.
- **Cause (seen on the unit):** two clients share the USB MIDI port.
- **Fix:** close Transfer, Overbridge and DNX before a client run; check reply lengths.
- **Status:** behaviour of the host side.
- **Evidence:** `[hw]`
- **Rule:** F7
- **Fact:** [common/sysex-and-midi.md](common/sysex-and-midi.md)

### I70. A 1024-byte bulk IN transfer wedged the Digitone II's USB controller
- **Unit:** Digitone II, OS 1.12 (digikit core/usb-bulk, a vendor bulk interface added in USB MIDI mode), 2026-11-11; the Digitakt II 1.17 ran the fixed adapter the same day
- **Seen:** echo transfers of 1, 511, 512 and 513 bytes worked; 1,024 and 4,096 bytes got no reply, then every bulk send failed and SysEx stopped answering too. The CPU kept running (keys, audio), no crash record was written, and unplugging USB did not bring it back: only a power cycle did.
- **Cause (bisected on the unit, then read in the controller's reference manual):** the controller has a 64-byte transmit buffer per endpoint. Two back-to-back 512-byte IN packets wedged it the moment the host read them; OUT with two 512-byte packets was fine. Stock does the same thing on purpose: it declares its MIDI IN endpoint as bulk 512 but programs the queue head for 64-byte packets (caps `0x20400000`), as in its audio and Overbridge modes. A first guess (dTD page pointers) was not the cause.
- **Fix:** the bulk IN queue head is programmed for 64-byte packets while the descriptor keeps 512; the host reads short packets until a frame is complete. Echo then matched from 1 byte to 1 MiB at about 2.3 MB/s each way (DN2) and 2.9 MB/s (DT2), and the emulator now faults an IN transfer whose packets after the first exceed 64 bytes.
- **Status:** fixed.
- **Evidence:** `[hw]` {digikit-usbfast}
- **Rule:** A39
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#usb-transfer-speed-on-the-units-digikit-2026-11-11-digikit-usbfast)

## M. Mods that failed on a unit

### I10. Byte-wise reads of uncached DMA buffers stalled the sequencer
- **Unit:** Digitone II, OS 1.12 (Digiwerk UM01, multichannel USB audio), 2026-10-31
- **Seen:** 42 channels arrived on the Mac, but the sequencer lagged until unusable.
- **Cause (read from the start-up code, confirmed by the fixed build on the unit):** the main OS sets CACR `0xa50ce100` / ACR0 `0x4007e020` (`0x40000000-0x47ffffff` cached); the SSI DMA buffers at `0x4e6e7100` are uncached, and UM01 packed their slots with byte-wise reads. A first look at the bootstrap's CACR (cache off) gave a wrong conclusion.
- **Fix:** read each of the 14 SSI slots once as a 32-bit word (UM02): no lag with busy sequences.
- **Status:** fixed (Digiwerk 0.3.0).
- **Evidence:** `[hw]` {dn2-cfw-handoff} {dn2-cfw-usb}
- **Count scope:** HANDOFF reports 84 reads per frame; the corrected USB technical note specifies 42 uncached SSI reads (14 slots times three bytes), with the table reads cached. The summaries above retain the byte-wise-to-word-wise change without treating those counts as equivalent.
- **Rule:** A48
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I11. Uncached state in a chord oscillator slowed the UI and could crash the unit
- **Unit:** Analog Four MK1, OS 1.56
- **Seen:** UI slowed; the unit could crash.
- **Cause (read from ACR0, measured by the fix):** only `0x40000000-0x43ffffff` is cached; mod state beside the effect delay lines (`0x468xxxxx`) was uncached; ~1,000 accesses per block per voice.
- **Fix:** copy state to the stack once per block, work there, write it back.
- **Status:** fixed.
- **Evidence:** `[hw]` {a4mods}
- **Rule:** A48
- **Fact:** [devices/analog-four-keys.md](devices/analog-four-keys.md)

### I12. A sample-machine mod could not create the storage it needed
- **Unit:** Digitone II, OS 1.11 (armio R012), 2026-11-03
- **Seen:** on units that never had it: 0 % free / 0 bytes in Transfer, stalled uploads, "Connection failed".
- **Cause (found by new users; the author's unit had storage prepared during development):** R012 mounts an existing sample filesystem but does not create one; stock FORMAT +DRIVE and the resets do not create it.
- **Fix:** R013 adds SYSTEM > FORMAT SAMPLES; formatting, Transfer capacity (~20 GB) and uploads passed on the unit.
- **Status:** fixed in R013 (R014 candidate).
- **Evidence:** `[hw]` {armio-samples}
- **Rule:** A49
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I13. USB audio repeated old audio after a project change
- **Unit:** Digitone II, OS 1.11 (armio R007-R011)
- **Seen:** USB audio froze or repeated while headphones and UI kept working; rejected publications rose by 16,392 in ~10.9 s.
- **Cause (measured with the build's counters):** the TX selector follows RX completion and is no ownership grant; the build bound its queue head to a destination from an older phase.
- **Fix:** R011 picks the candidate from the current DMA START.
- **Status:** fixed; endurance unmeasured.
- **Evidence:** `[hw]` {armio-usb} {armio-r011}
- **Rule:** C9
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I14. DAG registers stored through their own DAG hung the DSP
- **Unit:** Digitakt II (PLAITS RINGS kernel, digitakt-ii-research All-in-One)
- **Seen:** the DSP hung on the first block; all audio died. The emulator ran it bit-exactly.
- **Cause (one-variable probe image on the unit):** `DM(I7, M7) = M4` and similar; the PRM forbids it and stock never does it.
- **Fix:** move DAG registers through an R register.
- **Status:** fixed; the encoding gate now refuses same-DAG stores.
- **Evidence:** `[hw]` {dt2-plaits}
- **Rule:** A33
- **Fact:** [devices/digitakt-2-dsp-optimizing.md](devices/digitakt-2-dsp-optimizing.md)

### I15. A frequency shifter froze the unit at boot
- **Unit:** Digitakt II (digikit `fx/freqshift`, send route)
- **Seen:** frozen at boot; the emulator showed nothing.
- **Cause (two causes, isolated on the unit):** a selas defect left a nested hardware-loop end compressed; code copied into L2 at run time was not written back from the data cache.
- **Fix:** `.NOCOMPRESS` around nested loops; cache write-back before running copied code. Ran on send and master 2026-10-30.
- **Status:** fixed.
- **Evidence:** `[hw]` {digikit-f91}
- **Rule:** A45, A28, A41
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#sound-parameters-overdrive-and-run-time-machines-digikit-dt2-117--dn2-112-2026-11-10-digikit-f119)

### I16. A decoded section 7 over 1 MiB crashed the unit
- **Unit:** Digitakt II, OS 1.16 (dt2-machine-lab)
- **Seen:** crash; recovered over the startup menu.
- **Cause (read from the loader):** the ColdFire depacks section 7 into a 1 MiB buffer and checks the size only afterwards.
- **Fix:** keep the decoded section 7 under `0xfffff` bytes.
- **Status:** rule.
- **Evidence:** `[hw]` {dt2-lab-capicola}
- **Rule:** A46
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#sound-parameters-overdrive-and-run-time-machines-digikit-dt2-117--dn2-112-2026-11-10-digikit-f119)

### I17. Per-sample stores to the DDR output buffer crashed the unit
- **Unit:** Digitakt II, OS 1.17 (70b185's STRETCH replacement)
- **Seen:** continuous tone, unit crashed; the emulator was bit-identical.
- **Cause (measured on the unit):** per-sample accesses to stock buffers in external DDR (`0x8045b3c0`).
- **Fix:** render into L2 and copy once per block.
- **Status:** fixed.
- **Evidence:** `[hw]` {own-dt2-notes}
- **Rule:** A52
- **Fact:** [devices/digitakt-2-sharc-measured.md](devices/digitakt-2-sharc-measured.md)

### I18. The flash cave reportedly froze a unit at the logo
- **Unit:** Digitakt II, OS 1.17
- **Seen:** one report of a freeze at the logo with code in the cave `0x403117c4-0x40312000`; other projects boot from the same cave on units.
- **Cause:** not settled ([CONFLICTS O18](CONFLICTS.md)).
- **Fix:** check the bytes the other cave users leave; prove the cave on a hard run.
- **Status:** open conflict.
- **Evidence:** `[hw]` (report)
- **Rule:** A43
- **Fact:** [common/memory-maps.md](common/memory-maps.md)

### I19. Patching a "free" zero run crashed the unit
- **Unit:** Digitone II, OS 1.11 (dnfw cave search)
- **Seen:** crash; the emulator watch read zeros there.
- **Cause (found by a run-time watch and static analysis):** the run was an array that the code fills at run time.
- **Fix:** two static checks (equal-stride gaps, referenced operands); only 13 runs (4,207 B) pass both.
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-caves}
- **Rule:** D11, A43
- **Fact:** [common/memory-maps.md](common/memory-maps.md)

### I20. Mod code at a "free" address crashed projects with certain samples
- **Unit:** Syntakt, OS 1.41 (SyntHack up to v0.8.0)
- **Seen:** projects with SP TWINSHOT samples crashed at boot.
- **Cause:** mod code at `0x46000000`, memory stock uses for those samples.
- **Fix:** v0.8.1 unpacks the mod code into a 64 KB block that a hook at the end of heap init (`0x4010358E`) reserves first.
- **Status:** fixed.
- **Evidence:** `[hw]` {synthack-docs}
- **Rule:** D11
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I21. MD and Monomachine tracks went silent after an install
- **Unit:** Digitone II, OS 1.11 (dn2mk2)
- **Seen:** intermittent: tracks silent until cleared.
- **Cause:** unknown (suspected stale voice-slot state or state from an older version's project).
- **Fix:** none yet; test an old project after every install.
- **Status:** open.
- **Evidence:** `[hw]` {dn2mk2-reports}
- **Rule:** C9
- **Fact:** [devices/digitone-2-machines-sampler-sharc.md](devices/digitone-2-machines-sampler-sharc.md)

### I22. A mod broke the normal USB update path
- **Unit:** Digitone II (Overtone 1.0)
- **Seen:** the next OS sent with Transfer stopped at "Receiving" or "PREPARING..." and wrote nothing.
- **Cause:** the mod's build; fixed in 1.0.1.
- **Fix:** the STARTUP menu over DIN (~15 min); a release test that installs the next build over USB.
- **Status:** fixed.
- **Evidence:** `[hw]` {overtone}
- **Rule:** A36, C9
- **Fact:** [common/recovery.md](common/recovery.md)

### I23. Plaits builds failed normal Transfer updates at PREPARING
- **Unit:** Digitakt II (digitakt-ii-research All-in-One, earlier Plaits builds)
- **Seen:** updates stopped at 0 % / PREPARING.
- **Cause:** not stated; the author says not to assume the route is reliable everywhere.
- **Fix:** power cycle and the startup menu.
- **Status:** later builds changed.
- **Evidence:** `[hw]` {dt2-install}
- **Rule:** A20, A36
- **Fact:** [common/recovery.md](common/recovery.md)

### I24. A granular engine froze the UI at low pitch
- **Unit:** Digitakt MKI, OS 1.53 (digigrain)
- **Seen:** UI froze at low pitch.
- **Cause:** fixed-length source grains became long, the pool filled and every voice ran its worst case.
- **Fix:** grain length independent of pitch; overlap capped.
- **Status:** fixed.
- **Evidence:** `[hw]` {digigrain-skills}
- **Rule:** A34, D12
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I25. Clobbering R8 at the FX-bus mixer hook lost all audio
- **Unit:** Digitone II, OS 1.11 (SHARC)
- **Seen:** no audio; the emulator ignored the stray state.
- **Cause:** the mixer takes R4 and R8 as arguments; the hook changed R8.
- **Fix:** preserve every register and flag that code after a hook reads; compare callee registers between stock and the build.
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-skill-sharc}
- **Rule:** G9
- **Fact:** [devices/digitone-2-os111-reference.md](devices/digitone-2-os111-reference.md)

### I26. A boot block of 8n+4 bytes left the unit silent
- **Unit:** Digitone II (SHARC section 7)
- **Seen:** silent from power-on; boots in the emulator.
- **Cause:** the L2 instruction-cache line fill over the block's end faults on ECC.
- **Fix:** whole 32-byte boot blocks (`dspblocks.pad_lines`, `bootblocks.py`).
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-skill-sharc}
- **Rule:** G9
- **Fact:** [devices/digitone-2-os111-reference.md](devices/digitone-2-os111-reference.md)

### I27. An encoding every decoder accepts raised ILOPI on the chip
- **Unit:** Digitone II and Digitakt II (SHARC)
- **Seen:** the unit stopped (illegal opcode).
- **Cause (decoded against stock):** negative shift immediates with zero sign bits in the middle parcel (stock: `023e 7800`); selas's 48-bit `Rn = <sysreg>` put the wrong register (EMUCLK read as LCNTR).
- **Fix:** stock encodings only; compressed forms for system registers; check the disassembly.
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-stall} {dn2-skill-sharc}
- **Rule:** A41, G9
- **Fact:** [devices/digitone-2-machines-sampler-sharc.md](devices/digitone-2-machines-sampler-sharc.md)

### I28. A select value outside its count stalled the sequencer
- **Unit:** Octatrack
- **Seen:** after a build changed an effect's parameter layout, an old project stalled the sequencer on first play.
- **Cause:** stored values no longer fit the new layout.
- **Fix:** stamp old projects' stored values after a layout change.
- **Status:** rule.
- **Evidence:** `[hw]`
- **Rule:** E3, C9
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I29. DSP scratch at `$84` and up hung the unit
- **Unit:** Octatrack (DSP56300)
- **Seen:** hang.
- **Cause:** r7 scratch `$00-$83` is the per-instance block; above it belongs to others.
- **Fix:** stay inside the per-instance block.
- **Status:** rule.
- **Evidence:** `[hw]`
- **Rule:** D11
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I30. Key events posted into stock's queues crashed the unit minutes later
- **Unit:** Octatrack (Modwerk)
- **Seen:** two crashes, minutes after the event.
- **Cause:** events posted straight into stock's internal queues.
- **Fix:** feed the panel parser its own bytes instead.
- **Status:** rule.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I31. Restoring DSP-read state every frame corrupted the audio
- **Unit:** Octatrack
- **Seen:** corrupted audio.
- **Cause:** a mod overwrote data the DSP reads each frame; doing so is safe only for CPU-side bookkeeping.
- **Fix:** restore only CPU-side state.
- **Status:** rule.
- **Evidence:** `[hw]` {octamax}
- **Rule:** A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I32. A DSP frame counter saturated after 50.7 minutes
- **Unit:** Octatrack (DSP56300)
- **Seen:** a frame engine stopped after 50.7 minutes.
- **Cause:** a counter past `$7fffff` saturates in `move a,nN`.
- **Fix:** mask counters to 23 bits.
- **Status:** fixed.
- **Evidence:** `[hw]` {octabam-traps}
- **Rule:** A51
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I33. Module state on a load-meter counter gave a jittery pitch
- **Unit:** Octatrack (Modwerk USB base)
- **Seen:** jittery pitch.
- **Cause:** module state at `X:$2840`, core 1's load-meter counter.
- **Fix:** move the state.
- **Status:** fixed.
- **Evidence:** `[hw]` {octabam-traps}
- **Rule:** D11
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I34. A startup change stalled at the logo after a long power-off
- **Unit:** Octatrack
- **Seen:** passed emulator boots and quick power cycles, stalled at the logo after several minutes off.
- **Cause:** unknown; keeping the activation helper resident fixed it.
- **Fix:** qualify startup changes after a long power-off.
- **Status:** fixed; mechanism unknown.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A40
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I35. USB replies stayed stale for minutes
- **Unit:** Octatrack (Modwerk)
- **Seen:** a value the CPU stores rarely stayed stale in USB replies; values stored every frame looked live.
- **Cause (measured):** DMA reads RAM, not the copyback cache.
- **Fix:** copy a reply through the uncached alias and send it from there.
- **Status:** fixed.
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Rule:** A48, A28
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I48. A menu table in a "free" zero run crashed the unit
- **Unit:** Octatrack
- **Seen:** crash.
- **Cause:** the 15 KB zero run at `0x401087e4` lies in the PROJECT subsystem's RAM (the zero region above `0x400d8000`).
- **Fix:** larger code goes to a loader-copied area (octabam's loader stub at `0x4010fdf0`).
- **Status:** rule.
- **Evidence:** `[hw]`
- **Rule:** D11, A43
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I49. Idle paths of sixteen mods cost two percent of a Rytm block
- **Unit:** Analog Rytm MKII, OS 1.74 (Modwerk library, 16-module set, sequencer stopped), 2026-11-06
- **Seen:** the idle audio block took 72.9 % with the set installed.
- **Cause (measured on the unit, block timed on DTIM0 over USB MIDI):** three modules did work every block with nothing to do: Ping Pong Loop's four voice gates called the mirror routine for every voice in stock's sample prefetch, Sample Playback Rate walked all eight voices, QPERF ran its handler in full.
- **Fix:** early returns when idle (a byte of armed voices, "no track has RATE on"): 70.6-71.1 %.
- **Status:** fixed in the pinned packages; not run alone on a unit.
- **Evidence:** `[hw]` {modwerk-rytm-idle}
- **Rule:** A34
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I50. Mod data written for default settings slowed project load and save
- **Unit:** Syntakt, OS 1.41 (Synfact arp-st), 2026-11-06
- **Seen:** a user saw a project load slowly when switched to from another project, and a slower save; a reboot straight into it loaded normally.
- **Cause (shown in the emulator on the user's export):** the ARP mod sealed a 320-byte carrier for every kit even with default settings, so load checked all 1,664 bindings; the project itself was valid.
- **Fix:** leave the carrier absent while all thirteen rows are defaults: 81 % fewer emulated instructions for a full serialization.
- **Status:** fixed offline; wall-clock times on the unit not measured yet.
- **Evidence:** `[doc]` {synfact-lifecycle}
- **Rule:** E4
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I51. The sample popup did not open after switching Machines
- **Unit:** Digitone II, OS 1.11 (armio; R020 last confirmed installation), 2026-11-06
- **Seen:** after selecting ONESHOT, turning knob D did not open the sample list.
- **Cause (native replay):** the separate sampler SYN view was not selected when the Machine changed within the audio-track class. Generic notifications redrew the old stock view. Earlier tests manually reselected SYN and hid the missing lifecycle transition. No live capture established that every intermittent popup report shares this cause.
- **Fix:** R021 defers reconciliation to the existing UI poll, uses native selection and ownership, and avoids modal/selected-trig transitions; included in R022.
- **Status:** ten native transitions and nine guard cases passed; hardware confirmation pending.
- **Evidence:** `[hw]` owner symptom; `[emu]` matching defect and fix {armio-r022}
- **Rule:** C8
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md#sampler-port-lifecycle-findings-dn2-os-111-2026-11-06)

### I52. New project samples were missing after reboot
- **Unit:** Digitone II, OS 1.11 (armio; report build unconfirmed, exact R020 reproduced), 2026-11-06
- **Seen:** newly loaded samples disappeared from the unsaved working project after a freeze and reboot. Deletion of the +Drive sample files was not established.
- **Cause (native replay):** load notification ran the native incremental settings serializer, but the port updated its sample companion only during whole-project serialization. Both prepared working backup and fresh emulated boot retained an empty identity for the loaded slot. The frozen device's actual backup state was not captured.
- **Fix:** R022 refreshes the working sample companion in that settings worker under the existing project lock, validates owner/UID, and preserves explicit saved checkpoints.
- **Status:** load, unload, fresh-emulator restore, saved-cache isolation and invalid-state guards passed. Physical reboot confirmation is pending; a frozen worker or interrupted write can still lose pending work. The USB freeze is unresolved.
- **Evidence:** `[hw]` owner symptom; `[emu]` reproduced stale snapshot and fix {armio-r022}
- **Rule:** E5
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md#sampler-port-lifecycle-findings-dn2-os-111-2026-11-06)

### I55. A knob's own push-button byte was read as FUNC
- **Unit:** Analog Rytm MKII, OS 1.74 (Modwerk, Improved Machine Browser build MBC2), 2026-11-08
- **Seen:** FUNC + knob turn in the machine list behaved like a plain turn.
- **Cause (found from the tester's unit report, then the code):** the module took byte +20 of the encoder event as FUNC; that byte is set while the knob's own push-button is held.
- **Fix:** build MBC3 reads FUNC from the stock key table.
- **Status:** fixed; MBC3 passed on the unit.
- **Evidence:** `[hw]` {modwerk-rytm-modtests}
- **Rule:** C10
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#modwerk-rytm-modules-and-stock-behaviour-os-174-2026-11-10-modwerk-rytm-modtests)

### I57. A demand-loader soak froze an Octatrack MKII
- **Unit:** Octatrack MKII, OS 1.40C (octabam images OCTABAMS4 and OCTABAMS5, both with STEM REC), 2026-11-08/09
- **Seen:** 8 Nov: the DSP frame count stopped in 3 of 19 effect switches during play; panel and MIDI still answered, a power cycle was needed. 9 Nov: OCTABAMS5 froze once in 118 switches with panel, audio and USB all stopped.
- **Cause (open; found by a scripted program-change soak with the load meter and loader diagnostics polled over USB):** the demand loader's BASE/MODULATION transition is the larger factor (only the loader changed between the two images, and the rate fell from about 1 in 6 to 1 in 118); STEM REC and its 18 MiB reserve are not cleared. Candidate for the total freeze: two waits in the frame interrupt with no time limit (the loader's wait before each host word, and stock's spin until the DSP takes the frame's host command).
- **Fix:** partial (one copy per load). Time limits on the waits and copying a slice per frame are proposed, not made.
- **Status:** open (HYPOTHESES H22).
- **Evidence:** `[hw]` {octabam-failures} {octabam-dl}
- **Rule:** A51, A29 (the soak script appends each reading as it reads it, so a freeze still leaves the record)
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-and-octamax-findings-2026-11-10)

### I58. A wavetable machine clicked on every note
- **Unit:** Octatrack MKII, OS 1.40C (octabam WAVE as a ColdFire machine, builds W1-W5), 2026-11-07
- **Seen:** a click on every note.
- **Cause (heard on the unit, then traced under the port):** the DSP's AMP envelope restarts from zero at every trig START; with any ATK above 0 a sound that keeps playing across trigs drops to silence and fades back in.
- **Fix:** hold the DSP at ATK 0 / HOLD INF / REL INF and shape AMP in the machine, as SYNTH MACHINE does (W5).
- **Status:** fixed from W5. The module README still says "not flashed" (CONFLICTS O22).
- **Evidence:** `[hw]` {octabam-wavecf}
- **Rule:** C4
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-and-octamax-findings-2026-11-10)

### I59. Patch state inside a stock task's buffer silenced tracks
- **Unit:** Octatrack MKII, OS 1.40C (OCTAMAX up to 2g), fixed 2026-11-09
- **Seen:** tracks went silent or sounded wrong, scene A showed nothing selected after a pattern change, once `EXCEPTION VEC:03` at the stock key dispatcher's return. Not reproducible on demand.
- **Cause (read from the code):** patch state at `0x80006a00-0x80007000` lay inside the work buffer of the stock audio-analysis task (`0x80006964-0x80007574`). The crash is not proven to come from this.
- **Fix:** OCTAMAX_2h keeps all patch state in DDR; the build refuses any operand that points into the buffer.
- **Status:** fixed, confirmed on the unit 2026-11-09; the crash cause stays open.
- **Evidence:** `[hw]` {octamax-notes}
- **Rule:** A43 (data scratch as well as code), A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-and-octamax-findings-2026-11-10)

### I60. A long copy with interrupts masked clicked on every reload
- **Unit:** Octatrack MKI (KYOTI V1.7 work build, RELOAD_FROM_PROJECT), 2026-11-09
- **Seen:** a click on every [PTN] + [BANK] + trig reload.
- **Cause (found from the user's report):** a 43 KB pattern copy ran with interrupts masked and held off the audio frame.
- **Fix:** copy with interrupts on and publish only the slices that changed. Also fixed in the same round: reloading the current pattern while another was cued let the cued one land anyway.
- **Status:** fixed, confirmed on the unit.
- **Evidence:** `[hw]` {kyoti-reload}
- **Rule:** A34
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-and-octamax-findings-2026-11-10)

### I62. A safe-boot trial crashed every boot
- **Unit:** Syntakt, OS 1.41 (Synfact core-st 1.7), 2026-11-09
- **Seen:** after the first bank was written and the unit restarted, `EXCEPTION DK0094 V03` (address error) at every startup.
- **Cause (from the exception screen's words, then the code):** the boot's eMMC accessor table had no write function, so marking the bank TRYING called address 0; the record never changed, so every boot retried the same bank. The unit tests had replaced exactly this piece with doubles.
- **Fix:** core 1.7.1 adds the write function, storage fails closed on a table without one, and an end-to-end test through the production loader reproduces the crash.
- **Status:** fixed in code; the physical rollback test is pending, and the recovery steps used are not stated.
- **Evidence:** `[hw]` {synfact-safeboot}
- **Rule:** C8
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-core-and-smz4-banks-os-141-2026-11-10-synfact-core-synfact-safeboot)

### I63. A mod's memory window broke the BASE/WDTH filter
- **Unit:** Syntakt, OS 1.41 (Synfact core up to 1.7.1)
- **Seen:** moving BASE gave artifacts and some tracks went silent.
- **Cause (shown in the emulator):** the stock base-width filter reads Q31 poles from a 508-entry table with a zero tail and indexes up to 1023; Synfact's companion window sat in that tail, so BASE+WDTH of 128 or more read code as poles.
- **Fix:** core 1.7.2 bounds the index to 508.
- **Status:** fixed, confirmed on the unit.
- **Evidence:** `[hw]` {synfact-core}
- **Rule:** A43 (zero bytes in an image can be data stock reads)
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-core-and-smz4-banks-os-141-2026-11-10-synfact-core-synfact-safeboot)

### I64. A chorus running from DDR overloaded the Syntakt's MAIN CPU
- **Unit:** Syntakt, OS 1.41 (Synfact chorus 0.1)
- **Seen:** MAIN at 100 % and the sound broke up.
- **Cause (measured on the unit):** all chorus code ran from DDR; about 5.4 KB of code was fetched per block.
- **Fix:** 0.2 moved the hot code and kernels into MAIN SRAM (0.2 KB fetched per block).
- **Status:** fixed.
- **Evidence:** `[hw]` {synfact-chorus}
- **Rule:** A34
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-core-and-smz4-banks-os-141-2026-11-10-synfact-core-synfact-safeboot)

### I65. A machine kind past the end of a label table froze Digitone II units
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.44), 2026-11-07/08
- **Seen:** the unit froze on MACHINE SEL > BOUNCE, and at every power-on of a project holding a BOUNCE track.
- **Cause (from a user's freeze report, then traced):** the label lookup picked the Monomachine label table by range; BOUNCE (kind 13) read past its end and walked address `0xEE` as a list. The emulator reads low memory as zeros, which hid it (I66 has the gate side).
- **Fix:** one explicit test per machine kind, a `machines` gate step, and a trap on any non-stock read below `0x40000000` in every emulator step (v0.45). Recovery used: FUNC at power-on, TRIG 2 (EMPTY RESET; the +Drive is kept), then flash v0.45.
- **Status:** fixed; v0.44 withdrawn.
- **Evidence:** `[hw]` {dn2mk2-v045}
- **Rule:** A53
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#dn2mk2-findings-v045-v048-os-111-2026-11-11)

### I69. A mod took stock's USB DISK MODE pause for a DSP stall and kept the audio off
- **Unit:** Octatrack MKI and MKII, OS 1.40C (Modwerk beta base; finding 72, several testers' units), late Oct to 2026-11-10
- **Seen:** after walking PROJECT > SYSTEM into USB DISK MODE (or OS UPGRADE) and backing out, the unit stayed silent until a power cycle; the base's records said the DSPs had stopped.
- **Cause:** stock pauses the DSP while USB DISK MODE is open. The base's stall watch read that pause as a stalled DSP, and its recovery held the audio stopped. It was never reproduced on a stock unit.
- **Fix:** the base tells that pause from a stall (2026-11-10); on the owner's MKII the walk, about 10 s in the mode, NO and PLAY now plays.
- **Status:** fixed on the live base; a flashed base, file copies in the mode and an OS upgrade from the card not yet tested.
- **Evidence:** `[hw]` {modwerk-ot-unit-1110}
- **Rule:** C12
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I68. Spring-reverb builds lost their sound on a Digitone II; no cause found offline
- **Unit:** Digitone II, OS 1.12 (naturarum's Digiwerk / dn2-cfw, spring builds EFES and EEES), 2026-11-04 to 11-08
- **Seen:** EFES locked three times on Digiwerk 0.4 (twice in a short session, once after about 50 minutes; no sound on PLAY, the synths silent), always on USB MULTI/MIDI. EEES, the spring alone, stopped the sound for good one or two minutes after a pattern stop and in OS UPGRADE. A build with a -240 dB floor in the spring was silent from power-on. CFTE without the spring ran an hour and 30 minutes on the same USB mode without a lock.
- **Cause:** not found. An offline search ruled out illegal instructions and accesses, parity, FP exceptions, the stack, Elektron's code, timing in digikit's coupled emulator, and digikit's SHARC+ silicon rules (checked on every build, no hit). The one lead: the spring's output is exactly 0 from 1.4 s into FX kill and 78 s after a stop, as at both unit stops [inferred].
- **Fix:** the spring is shelved; its six builds stay withdrawn. The author stopped blind device tests. The next test build (EEEM, a light morphing reverb in the reverb slot) sends the stock DSP's idle parks to a fault tone whose pitch names the fault (1500 Hz illegal instruction, 3000 Hz parity, 6000 Hz emulation or default handler, 1500 + 6000 Hz abort or stack check; a ~750 Hz buzz or silence is a hang).
- **Status:** open; EEEM not yet on the unit (2026-11-10).
- **Evidence:** `[hw]` {dn2-cfw-sp02} {dn2-cfw-mr03}
- **Rule:** A16
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I71. A DSP load guard dropped a sample voice block after block
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.47, a user's unit), reported 2026-11-10
- **Seen:** with a SID voice and three PERC tracks playing, an ONESHOT kick sounded crunchy at about 85 % DSP load.
- **Cause (from the report and the guard's code):** the frame-time guard left the sample voice out when a block ran short of time, and because a sample voice is retried in every block it came and went block by block instead of stopping.
- **Fix:** planned for v0.49: render the sample voices first, so time runs out on the heavy synth voices, and keep a dropped sample voice stopped until its next note, as PERC voices already are.
- **Status:** fix built in v0.49 (2026-11-11): the guard gives the sample voices their time first and keeps a dropped one stopped until its next note; not verified at the unit's real load.
- **Evidence:** `[hw]` (user report) {dn2mk2-v048} {dn2mk2-v049}
- **Rule:** A44
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#dn2mk2-findings-v045-v048-os-111-2026-11-11)

### I72. A drum machine mod played silent hits after power-up and misread stock's voice start
- **Unit:** Octatrack MKII, OS 1.40C (octabam's DRUMMER by djib, the author's unit, images 44-46), 2026-11-05/06
- **Seen:** the machine, its kit window and AUTO kit worked, but hits stayed silent until the machine was chosen again or the track's audio editor was touched; retrigs did not run.
- **Cause (found under octabam's emulator after the unit test):** the hit level was scaled from a base read only when a restore bit at `0x80001538` was clear, and on the unit that bit can be set at power-up, so the base stayed 0. Separately, the mod's wrapper of the FLEX voice start passed two arguments where stock's routine `0x4000f450(track, slot, flags)` takes three, so stock read a word of the wrapper's stack.
- **Fix:** the base is now the lane's VOL; the wrapper forwards all three arguments, and stock's retrigs run.
- **Status:** fixed; later images (to 78, 2026-11-09) ran on the author's MKII.
- **Evidence:** `[hw]` {octabam-drummer}
- **Rule:** G8, C10
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-findings-2026-11-11)

### I73. An old project stopped all sound on a sample-machine mod
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.48, a user's unit), reported 2026-11-11
- **Seen:** a project saved on an earlier build played a STRETCH track once, briefly; then every track went silent until a reboot. A new project on the same build did not show it.
- **Cause:** unknown. The author's sampler model plays STRETCH, REPITCH and ONESHOT cleanly with odd stored STRT/LEN words (old 127, 120.00, out of range), so the stored data of the old project is the main suspect; not reproduced.
- **Fix:** none yet. The author plans two gate steps: projects saved on earlier builds played in the coupled emulator, and every stored control word driven through the DSP code.
- **Status:** open (2026-11-12).
- **Evidence:** `[hw]` (user report, not reproduced) {dn2mk2-v049}
- **Rule:** C9
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#dn2mk2-v049-flex-os-111-2026-11-11-dn2mk2-v049)

### I74. Filter builds overloaded the DSP and broke USB audio
- **Unit:** Digitone II (armio's dn2-dt2-firmware-research, the owner's unit), unpublished builds R023 and R024, early November 2026
- **Seen:** USB audio was reported broken on the two SEM-filter builds, which overloaded the DSP.
- **Cause (the project's own model, not measured):** the right-hand effects chain was duplicated and ran for every voice. With it gated to sampler voices (R025), the model predicts about 81.7 % of the audio block with 16 voices; it leaves out interrupts, cache, DMA and USB.
- **Fix:** R025 runs the right effects chain only for sampler voices; R027 keeps that.
- **Status:** the owner reports R025's audio working, but USB audio has not been checked since R024; the project tells USB-audio users to stay on R012.
- **Evidence:** `[hw]` (owner report, no timing capture) {armio-r027}
- **Rule:** A16, A37
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I75. Removing a synth module that tracks still used left the loader stuck in recovery
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk beta base with SYNTIZ 0.1.0-experimental, the owner's unit), 2026-11-09 and 2026-11-11
- **Seen:** an Undo of the module install while tracks used SYNTIZ ended in the loader's `needs-recovery` state. The unit stayed in recovery, and the loader's own `recover` was refused even after the tracks were set back to STATIC.
- **Cause:** not traced in the source; the module's README now says to remove it only while no track in the Part uses it.
- **Fix:** a power cycle brought the unit back.
- **Status:** open; documented as a usage rule.
- **Evidence:** `[hw]` {modwerk-syntiz}
- **Rule:** A54
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-and-octabam-findings-2026-11-12)

### I77. Knob assignments a mod kept in a kit's spare bytes were lost at power-on
- **Unit:** Digitakt (mk1), OS 1.53/1.54 (Modwerk's Digi Perform 0.1.2 and 0.1.3), 2026-11-11
- **Seen:** after SAVE PROJECT and a power cycle the mod's knob assignments were gone; LOAD PROJECT brought them back.
- **Cause (shown in the emulator):** after SAVE PROJECT, a cold boot came back with the sound records' spare bytes cleared, and a stock parameter written straight into the kit was lost too; LOAD PROJECT kept both. So the cold-boot path restores from another copy than the saved project file.
- **Fix:** none yet (0.1.3 behaves the same).
- **Status:** open.
- **Evidence:** `[hw]` (power cycle) / `[emu]` (cause) {modwerk-digiperform}
- **Rule:** E5, C9
- **Fact:** [devices/digitakt.md](devices/digitakt.md#modwerk-digi-perform-os-153154-2026-11-11-modwerk-digiperform)

### I78. The first PLAY after power-on started a track's recorder
- **Unit:** Octatrack MKII, OS 1.40C (octabam rig image 41 with djib's FREE LOOP), 2026-11-05
- **Seen:** in MIDI mode, the first PLAY after power-on started T1's recorder while T1 was idle. A double STOP before PLAY prevented it.
- **Cause (inferred, not traced):** a quantized REC start left staged at `0x800018be`/`0x800018de` (the QREC branch of REC_POST `0x40005178`). Whether stock alone does this is unclear.
- **Fix:** FREE LOOP's `stray_guard` stops such a recording; not seen on images 42-43.
- **Status:** guarded, cause open at the source.
- **Evidence:** `[hw]` (cause `[?]`) {octabam-freeloop}
- **Rule:** A40, G8
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-and-octabam-findings-2026-11-12)

### I79. Three FM Synth tracks beside a busy pattern froze an Octatrack
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk development base, the owner's unit), 2026-11-12
- **Seen:** three tracks of FM Synth 0.1.2, a machine rendered on the ColdFire, beside a busy eight-track pattern froze the unit.
- **Cause:** the CPU-rendered machines were not counted against any budget, so nothing stopped the load from passing the frame (measured by the fix, not traced further).
- **Fix:** the base prices each CPU machine, refuses a pick over the limit (CPU FULL) and drops voices at the frame guard; the same set then played on a development build. A busy project may now drop FM Synth notes.
- **Status:** fixed on a development build; the release base was not run on a unit.
- **Evidence:** `[hw]` {modwerk-1112}
- **Rule:** A25, A34
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-and-octabam-findings-2026-11-12)

## E. Emulator or toolchain disagreed with the unit

### I36. The emulator undercounted DSP time by 2x to 12x
- **Unit:** Digitakt II (70b185's project; digimod's Plaits mod)
- **Seen:** device cycles about 2x the emulator's instruction count for code reading DDR; a hard stop the emulator showed overshooting by ~25k overshot by ~75k on the unit; digimod reports 7-12x on hardware for one case.
- **Cause:** the emulators model no memory stalls.
- **Fix:** budget with silicon costs; leave a margin; measure once per project on the unit.
- **Status:** known limit.
- **Evidence:** `[hw]` {own-dt2-notes} {digimod}
- **Rule:** A35, C4, C10
- **Fact:** [devices/digitakt-2-sharc-measured.md](devices/digitakt-2-sharc-measured.md)

### I37. A SHARC emulator shifted every fractional multiply
- **Unit:** Digitone II (complex-ping's emulator)
- **Seen:** found when the emulator was checked against stock routines.
- **Cause:** the emulator shifted every fractional multiply left; the PRM shifts only signed x signed.
- **Fix:** fixed in the emulator; `sharc_checks.py` calls stock routines and compares.
- **Status:** fixed.
- **Evidence:** `[emu]` {dn2-skill-md}
- **Rule:** C10
- **Fact:** [devices/digitone-2-os111-reference.md](devices/digitone-2-os111-reference.md)

### I38. Low-window flash pointers boot in the emulator and hang on the unit
- **Unit:** Machinedrum / Monomachine (Gearmulator board model)
- **Seen:** images boot in the emulator and hang on the unit.
- **Cause:** after the OS remaps CS0, nothing decodes the low window on hardware; the emulator maps flash at `0x0` and `0x10000000`.
- **Fix:** link and point through `0x10000000`; scan images for low pointers.
- **Status:** rule.
- **Evidence:** `[hw]` {mdkit-docs}
- **Rule:** A53
- **Fact:** [devices/machinedrum-monomachine.md](devices/machinedrum-monomachine.md)

### I39. The default compression level corrupted a DN2 image
- **Unit:** Digitone II
- **Seen:** corrupt image.
- **Cause:** section 4's in-place loader has a stock margin of +31,182 bytes; elektron-firmware-tool's `-l 3` gives -39,318. Stock DT2 1.17 also fails the in-place path (margin -31,912).
- **Fix:** check the margin at every loader stage; a dense packer.
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-cfw-handoff}
- **Rule:** A14
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I40. A "no change" rebuild came out 2 bytes short
- **Unit:** Analog Rytm MK1
- **Seen:** the null repack failed.
- **Cause:** elektron-firmware-tool padded ELE2 containers to 2 bytes; stock pads to 4.
- **Fix:** pad to 4; always null-repack the stock file first.
- **Status:** fixed in hugz202's patch.
- **Evidence:** `[hw]` {rytm-mk1-mods}
- **Rule:** A6, A32
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I41. A label defined twice resolved to the wrong file
- **Unit:** Digitakt II (Plaits kernels, caught before a unit)
- **Seen:** each kernel's own test passed; the merged image jumped into the wrong file.
- **Cause:** a label defined in two sources resolves to one of them in the merged object.
- **Fix:** unique label prefixes per file.
- **Status:** rule.
- **Evidence:** `[emu]` {dt2-plaits}
- **Rule:** D4
- **Fact:** [devices/digitakt-2-dsp-optimizing.md](devices/digitakt-2-dsp-optimizing.md)

### I42. Checks reported success about work they never did
- **Unit:** Digitone II (dnfw LFO4 bridge)
- **Seen:** the build passed every check and faulted on the unit.
- **Cause:** snapshot harnesses cleared code no real boot ran; a boot gate printed "Safe to flash" after its coverage section was deleted; an emulator call returned 0 for a present value.
- **Fix:** every check gets a control that must fail.
- **Status:** rule.
- **Evidence:** `[hw]` {dn2-lfo4}
- **Rule:** C8
- **Fact:** [AGENT-RULES.md](AGENT-RULES.md)

### I53. Boot-screen frames were upright in the emulator and flipped on the panel
- **Unit:** Digitakt II, OS 1.17 (digikit, branch image), 2026-11-08
- **Seen:** a boot screen whose bar was at the bottom in the preview and the emulator appeared at the top on the panel; left-to-right fill was unchanged.
- **Cause (shown on the unit, plus a comparison of the stock logo with the bootloader picture: 0 mismatching pixels after a vertical flip):** the emulator decodes the intro bitmap as if the intro flush flipped like the main-UI blit. On the panel, intro rows are stored top-down mirrored. Why the intro path differs (flush routine or panel scan direction) is not established.
- **Fix:** digikit's `.dkbs` frames, safe screen and pixel helper use the panel's layout. The emulator decoder is not fixed yet.
- **Status:** worked around; emulator still wrong for intro frames.
- **Evidence:** `[hw]` {digikit-f117}
- **Rule:** C10, D13
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#the-stock-intro-and-boot-screens-digikit-finding-117-dt2-117-and-dn2-111112-digikit-f117)

### I56. A test plan pressed the wrong key, and the emulator reference did not match the unit
- **Unit:** Analog Rytm MKII, OS 1.74 (Modwerk, Kit A/B runs KBH7 and KBH8), 2026-11-08/09
- **Seen:** two runs tested only the KIT-menu path; another run stopped because the unit's kit list draws markers after kits 02-16 that the emulator's reference image lacks.
- **Cause (caught in review):** rytm2_mods' documentation gives the reload key as NO + PLAY, so the remote-key plan pressed transport PLAY; the OS 1.74 manual says NO + PLAY MODE.
- **Fix:** rerun with NO + PLAY MODE and narrow the screen check to the cursor row.
- **Status:** passed in KBH8 (CONFLICTS S18).
- **Evidence:** `[hw]` {modwerk-rytm-modtests}
- **Rule:** C8, C10
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#modwerk-rytm-modules-and-stock-behaviour-os-174-2026-11-10-modwerk-rytm-modtests)

### I61. Odd jump targets froze a Digitakt II at boot; the emulator kept running
- **Unit:** Digitakt II, OS 1.17 (elekloader core-dt2 2.0), fixed 2026-11-08
- **Seen:** the unit froze at boot.
- **Cause (per the fix's commit message):** byte-aligned code sections put routines at odd addresses; a jsr/jmp to an odd address stops the ColdFire with an address error (vector 3), while the emulator keeps running.
- **Fix:** the linker refuses an odd-target absolute jsr/jmp into mod RAM; each code section starts with a 2-byte alignment.
- **Status:** guarded in the builder.
- **Evidence:** `[hw]` (commit message only) {elekloader-oddjump}
- **Rule:** A42
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#sound-parameters-overdrive-and-run-time-machines-digikit-dt2-117--dn2-112-2026-11-10-digikit-f119)

### I67. Code built into .bss crashed a Digitakt II at boot; the emulator ran the zeros
- **Unit:** Digitakt II, OS 1.17 (gdeo607's Digi2Core, core-dt2 2.4-2.6), fixed in 2.6.1 on 2026-11-09
- **Seen:** right after boot the unit stopped with an illegal-instruction exception.
- **Cause (per the 2.6.1 note):** two new routines were placed in `.bss` instead of the code section, so the unit jumped into zero-filled memory. The emulator executed the zeros as no-ops and booted.
- **Fix:** the routines are code again in 2.6.1. The README says not to flash a 2.4, 2.5 or 2.6 build; Digi2MacroOSC and Digi2ElixirPotionsDRUM still name core 2.4.
- **Status:** fixed in 2.6.1.
- **Evidence:** `[hw]` {digi2core}
- **Rule:** A42, C10
- **Fact:** [AGENT-RULES.md](AGENT-RULES.md)

### I66. A feature that crosses ColdFire and DSP passed the gate and failed on units
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.45/v0.46, BOUNCE), 2026-11-08/09
- **Seen:** on testers' units BOUNCE recorded nothing, or recorded and never played back.
- **Cause:** unknown. The gate never ran the ColdFire and the DSP together. Per the v0.48 notes the recorder trigs fired and takes were made, but the track never played its buffer.
- **Fix:** BOUNCE removed from the menu in v0.47 and its code removed in v0.48 (old projects load, the track silent). v0.48 adds a coupled emulator that runs both processors one audio block at a time (faithful in order and content, not in timing margins) and the first gate step on it; FLEX, the replacement, is to be tested from recording to playback on it.
- **Status:** open (FLEX not built yet, 2026-11-11).
- **Evidence:** `[hw]` {dn2mk2-v046} {dn2mk2-v047} {dn2mk2-v048}
- **Rule:** C4, C2
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#dn2mk2-findings-v045-v048-os-111-2026-11-11)

## R. Recovery and transfer links

### I43. Recovery stalled at ~80 %: the MIDI link, not the image
- **Unit:** Digitone II (dn2_firmware_explore), 2026-09-11
- **Seen:** Transfer showed 100 % sent; the unit's bar froze near 80 % (30/70/80 % on different tries).
- **Cause (shown by sending stock 1.10E over the same route):** a USB MIDI interface went idle mid-transfer and dropped packets.
- **Fix:** a MIDI interface that stays awake for the ~12-15 min transfer.
- **Status:** settled.
- **Evidence:** `[hw]` {dn2-firmware-explore} {dn2-flashing}
- **Rule:** A11, A20
- **Fact:** [common/recovery.md](common/recovery.md)

### I44. Recovery used on a Digitakt II after a crashing build; a cheap cable delivered nothing
- **Unit:** Digitakt II, OS 1.16 (dt2-machine-lab), 2026-10-06
- **Seen:** startup menu over DIN restored 1.16; a generic USB-MIDI cable (VID 1a86, PID 752d) showed no reception, a known-good interface worked.
- **Cause:** the cable.
- **Fix:** rehearse recovery with your exact cable and the stock file.
- **Status:** recovered.
- **Evidence:** `[hw]` {dt2-lab-coldfire-fix}
- **Rule:** A11, A36
- **Fact:** [common/recovery.md](common/recovery.md)

### I45. Recovery used on a Digitone MK1 after a logo hang
- **Unit:** Digitone mk1, OS 1.44 (digitone-arp-mod), 2026-10-08
- **Seen:** a build hung on the logo; stock 1.44 restored over the startup menu and DIN.
- **Cause:** the build.
- **Fix:** startup menu; not EMPTY RESET or FACTORY RESET.
- **Status:** recovered.
- **Evidence:** `[hw]` {dn1-arpmod-e04}
- **Rule:** A2, A36
- **Fact:** [common/recovery.md](common/recovery.md)

### I46. Syntakt startup-menu recovery tested over DIN
- **Unit:** Syntakt, OS 1.42 (Modwerk boot probe), 2026-11-04
- **Seen:** FUNC at power-on, TRIG 4, stock 1.42 from Transfer's legacy SysEx page through a generic USB-to-MIDI cable: the unit booted 1.42. A working unit; a unit that does not boot is untested.
- **Cause:** test.
- **Fix:** —
- **Status:** tested.
- **Evidence:** `[hw]` {modwerk-st-probe}
- **Rule:** A11, A36
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I47. Stock storage resets did not create the sample filesystem
- **Unit:** Digitone II, OS 1.11 (armio)
- **Seen:** per the author, FORMAT +DRIVE, EMPTY RESET and FACTORY RESET do not create the sample filesystem and can erase projects.
- **Cause:** stock has no such filesystem on the DN2.
- **Fix:** the mod's own FORMAT SAMPLES (R013).
- **Status:** see I12.
- **Evidence:** `[doc]` {armio-samples}
- **Rule:** A3, A49
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I54. Safe mode by REC at power-on, tested on a Digitakt II
- **Unit:** Digitakt II, OS 1.17 (digikit, branch image with loadable boot screens), 2026-11-08
- **Seen:** REC held from power-on gave digikit's safe mode (no modules loaded; the DIGIKIT menu showed "safe mode key held"). Without REC, the selected boot screen played about 1.8 s after the stock intro started, and the module setting survived power cycles.
- **Cause:** test. In the emulator, digikit's earlier queue scan missed the key (`safe:0`); reading the stock key state fixed it. On the unit, a key held at power-on does produce a report.
- **Fix:** —
- **Status:** tested on one DT2. Other panel firmware versions and the Digitone II are not measured. A fault during the intro still reaches stock's halting handler; the 30 s boot counter, not REC, catches that (emulator only).
- **Evidence:** `[hw]` {digikit-f117}
- **Rule:** A29
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#the-stock-intro-and-boot-screens-digikit-finding-117-dt2-117-and-dn2-111112-digikit-f117)

### I76. A loader base update over USB said Done but did not stick
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk beta base, the author's unit), 2026-11-09
- **Seen:** the web page's "Update over USB" reported Done, but the new base stalled at +0 s on its first start, and the next boot ran the old base. A second update held. In the same trials the loader's diagnostic log once showed a "hot" record (CPU 98.9 %) with the transport stopped, not explained.
- **Cause:** unknown.
- **Fix:** update again and check the base version after the reboot.
- **Status:** open.
- **Evidence:** `[hw]` {modwerk-syntiz}
- **Rule:** A23
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-and-octabam-findings-2026-11-12)
