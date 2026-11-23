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

### I103. Stock Analog Four MKII 1.56 hung on its own restart after writing a new OS
- **Unit:** Analog Four MKII, stock OS 1.56 running the update (elkflash test runs), reported 2026-11-13
- **Seen:** the unit stayed on SUCCESS! REBOOTING and on USB, and every MIDI call to it blocked; twice in about 30 flashes.
- **Cause (read from the stock code by elkflash's author):** the restart masks every interrupt and then waits for a serial queue that only those interrupts drain.
- **Fix:** power-cycle by hand; the new OS is already written and boots. elkflash 0.7 detects the stall from the USB node (exit code 5) and elkbench refuses further commands to that unit until a watched power cycle.
- **Status:** stock bug, open (SB23).
- **Evidence:** `[hw]` {elkflash-stall}
- **Rule:** A23
- **Fact:** [devices/analog-four-keys.md](devices/analog-four-keys.md)

### I114. Stock MidiRpc requests were lost while the boot intro still ran
- **Unit:** none (digikit's emulator, Digitakt II OS 1.17), found 2026-11-16
- **Seen:** a storage device test failed with "no reply to MidiRpc 11" right after a module install had restarted the device.
- **Cause (shown in the emulator):** digikit's runtime answered at once after the restart, but the firmware was still on its boot intro, which drops stock MidiRpc requests. A boot race, not storage code.
- **Fix:** after `restart()` the host's first stock RPC waits for the stock service with a read-only probe (up to about 30 s); a write is never resent. digikit's debug log now has event 47 FW_READY, written with the block counter on the first UI-loop pass after boot; hosts wait on it before they send stock MidiRpc requests (2026-11-18, {digikit-1118}).
- **Status:** fixed in digikit's host (branch `fix/rpc-after-install`); not checked on a unit (stock test H27).
- **Evidence:** `[emu]` {digikit-1117}
- **Rule:** C12
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#card-concurrency-upload-phases-and-hot-reload-facts-digikit-findings-133-135-dt2-117-and-dn2-112-2026-11-1617-digikit-f133-digikit-f134-digikit-f135-digikit-1117)

### I131. An overloaded Rytm overwrote its own UI messages and lost live-recorded hits
- **Unit:** Analog Rytm MKII, OS 1.74, the author's unit with a Modwerk development base and 13 modules (BD ANALOG playing), image LQ05, 2026-11-16
- **Seen:** during RTRG + pad holds of 10-30 s in live recording the unit became very laggy and hits were lost. Test counters: stock's UI queue held 1,931 messages, past its 1024 slots; the module itself dropped none of its 63 hits and freed all its slots once the sequencer stopped.
- **Cause (read in the OS 1.74 disassembly):** stock's UI queue send has no full check, so past 1024 waiting messages it overwrites unread ones (pad pressure, keys, a mod's events). The load (BD ANALOG voices, stock pad pressure at 200-290 messages a second) was past what the UI task can serve.
- **Fix:** none in stock. Live Rec Retrig Fix 0.2.2 frees its slots only after the UI task has taken its message, and drops only its own events past 126 waiting; with lighter load (LQ04, BD ANALOG alone) 145 hits, 0 dropped.
- **Status:** stock behaviour, open (SB27).
- **Evidence:** `[hw]` {modwerk-rytm-1116}
- **Rule:** A50
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#modwerk-findings-mkii-and-mki-os-174-2026-11-1617-modwerk-rytm-1116-modwerk-1117)

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
- **Status:** open; the spring stays shelved. The EEEM test build (with the MRB morphing reverb in its place) ran 15 minutes on the unit without a fault (2026-11-17) {dn2-cfw-1122}.
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
- **Status:** open; documented as a usage rule. A similar case on 2026-11-14: after FLEX tracks played through FM Synth 0.1.2's wrapper in a 16-module set, a rollback was refused as needs-recovery although no track named a module machine; a power cycle was needed again {modwerk-1114}.
- **Evidence:** `[hw]` {modwerk-syntiz}
- **Rule:** A54
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-and-octabam-findings-2026-11-12)

### I77. Knob assignments a mod kept in a kit's spare bytes were lost at power-on
- **Unit:** Digitakt (mk1), OS 1.53/1.54 (Modwerk's Digi Perform 0.1.2 and 0.1.3), 2026-11-11
- **Seen:** after SAVE PROJECT and a power cycle the mod's knob assignments were gone; LOAD PROJECT brought them back.
- **Cause (shown in the emulator):** after SAVE PROJECT, a cold boot came back with the sound records' spare bytes cleared, and a stock parameter written straight into the kit was lost too; LOAD PROJECT kept both. So the cold-boot path restores from another copy than the saved project file.
- **Fix:** 0.1.4 (2026-11-13) also writes the data into the working image (`0x406490e8` on 1.54, `0x406480e8` on 1.53), which the unit saves at power-off; the author confirmed on a unit (OS 1.53) that assignments survive a power cycle.
- **Status:** fixed.
- **Evidence:** `[hw]` {modwerk-digiperform}
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

### I80. A USB mode take-over left a Digitakt II off the bus until a power cycle
- **Unit:** Digitakt II, OS 1.17 (digikit's Fast USB, core/usb-bulk take-over from USB AUDIO/MIDI to USB MIDI and back), 2026-11-12 and 2026-11-13; a Mac host
- **Seen:** in a loop of take-overs and releases, cycles 1-4 were clean (the host saw the device leave and come back within about 1.5 s). In cycle 5 the host saw no disconnect after TAKEOVER, the device answered nothing at its USB address, and a cable replug did not bring it back; only a power cycle did. With a fix (below) cycles 1-10 were clean and cycle 11 failed the same way, again on TAKEOVER, never on RELEASE. Separately, after about 15 quick take-overs on a Digitone II the host's MIDI connection went stale while the unit was fine; a replug cured that one.
- **Cause (static reading, none proven):** the stock mode switch stops the controller with no lock; most likely the detach never reached the line (the controller stopped while the external ULPI PHY was suspended or busy), or the PHY was left in a state the stock restart does not undo. The stock firmware writes no PHY register itself.
- **Fix:** digikit holds the restart for 2 s, parks the PHY's line (function control through ULPI_VIEWPORT) while the controller is stopped and spaces switches at least 3.5 s apart. That made the failure rarer, not absent, so the take-over is off by default since 2026-11-13; with USB CONFIG set to USB MIDI (no switch) the fast transfer was fully reliable.
- **Later (2026-11-14):** over longer runs failures also came on release; the line stayed at SE0 and after a controller reset VBUS-valid read 0. The USB clock comes from the ULPI PHY, so a PHY link that dies at the stop freezes the controller's USB side; why the stop kills it is open. Parking the PHY made failures about ten times more frequent (1 in 15 against 1 in 76 to 1 in 200), and neither the stock controller reset nor a stop/hold/restart revives it. digikit deleted the take-over and now adds a bulk OUT endpoint to USB AUDIO/MIDI at boot, with no mode switch (ran on a DT2 and a DN2, 2026-11-13).
- **Status:** avoided (take-over deleted); cause open.
- **Evidence:** `[hw]` (cause `[?]`) {digikit-f123-hw} {digikit-f123-bulk}
- **Rule:** A55
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md#usb-take-over-failures-and-card-speed-digikit-2026-11-13-digikit-f123-hw-digikit-f126)

### I81. Released notes that never ended raised a Digitakt's audio load and made the UI lag
- **Unit:** Digitakt (mk1), OS 1.54 (Digi CMI 0.25, elekloader core 4.3), 2026-11-12
- **Seen:** the mod's own CPU meter read 86 % after boot and 94 % after playing, with every note silent; the UI lagged on every page.
- **Cause (shown in digiemu):** 0.25 gave each new MIDI note a free voice, so released notes piled up on all eight voices, and each kept looping silently for good: the envelope value it read (`fw_amp_env`, in fact the filter envelope, S20) settles near -135 dB, so the voice was never switched off. digiemu counted only about 1 % more render instructions for the pile-up; the extra 8 % on the unit is likely memory and cache traffic of six streaming samples, which the emulator does not model.
- **Fix:** 0.26 ended a released voice below -72 dB of that value, which cut sounding notes and was withdrawn (I89); 0.30 switches a voice off by the real amp envelope (below -90 dB for 64 blocks). Not yet re-checked on the unit.
- **Status:** fixed in the emulator; unit re-test open.
- **Evidence:** `[hw]` (load and lag) / `[emu]` (cause) {digicmi-026} {digicmi-037}
- **Rule:** A34, A59
- **Fact:** [devices/digitakt.md](devices/digitakt.md#digi-cmi-on-the-unit-os-154-2026-11-12-digicmi-026)

### I82. A frame interrupt entering about 150 µs late stopped an Octatrack's DSP frame exchange
- **Unit:** Octatrack MKII, OS 1.40C (octabam builds and an octabam control image, a computer recording the USB audio), 2026-11-12
- **Seen:** at the first START after boot, or at a program change, the sequencer held step 1 and the DSP stopped taking frames while panel and USB still answered; a power cycle cleared it. With a USB capture open, 5 of 8 first STARTs stalled (4 or 20 channels alike) and 1 in 27 program changes; without a capture, 0 of 13 first STARTs and 0 of 64 program changes.
- **Cause (measured timing, DSP side inferred):** at START and at a program change one frame interrupt runs 475-585 µs (a frame is 362.8 µs), so the next one enters late. A log of entry times showed: 128-149 µs late, the unit catches up; 155-223 µs late, it skips one frame and runs on; both stalls entered 149 and 155 µs late. A USB capture adds 25-30 µs to the START frame and moved it onto that boundary; adding 60 µs to every frame interrupt without a capture moved it past and caused no stall. Inferred: the ColdFire's transfer chain is still sending when the DSP starts its next frame.
- **Fix:** octabam's FRAME GUARD holds an entry 110-190 µs late until it is 190 µs late, so the DSP skips one frame cleanly; with it 32 first STARTs and 192 program changes ran without a stall at 20 channels. A first version mis-reduced the lateness after a skip and still stalled in a long program-change soak; corrected 2026-11-13. Not measured: what the skipped frame does to sounding audio; an MKI.
- **Status:** guarded; on a test image with extra load, 7 of 16 STARTs froze the whole unit 8.2 s later (not seen on shipping images, open).
- **Evidence:** `[hw]` (timing) / `[?]` (DSP-side mechanism) {octabam-frameguard}
- **Rule:** A56
- **Fact:** [devices/octatrack.md](devices/octatrack.md#frame-interrupt-timing-and-midi-scenes-octabam-2026-11-13-octabam-frameguard)

### I83. Reading the CF card from a mod's UI tick froze an Octatrack
- **Unit:** Octatrack MKII, OS 1.40C with the Modwerk base and the AERIA module (v31), 2026-11-11
- **Seen:** starting a video screensaver that streamed a file from the card stopped the audio frames (the base logged a stall); the unit dropped off USB and needed a power cycle.
- **Cause (from the log, the author's own diagnosis):** the player read the card from AERIA's UI tick; stock does its card work in its own card task.
- **Fix:** v32 switched the player off (plan: read in the card task, or preload the file into RAM); starting the screensaver no longer stalls.
- **Status:** worked around.
- **Evidence:** `[hw]` (freeze) / `[?]` (mechanism) {aeria-log}
- **Rule:** A57
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I85. A delay effect left the next effect in its DSP slot silent
- **Unit:** Octatrack MKII, AERIA OS builds of 2026-11-13
- **Seen:** loading TAPE or BBD on core 1 into a slot that had just held PT2399 silenced the output for good while the DSP still answered; step tests had checked only that the DSP answered.
- **Cause (not found):** moving PT2399 to another block of core 1's X memory (`X:$2000`) stopped it.
- **Fix:** a build that survived 12 rounds of the trigger and 30 random swaps; PT2399 shares memory with BBD, HAIL and AURORA, so those pairs are refused; BBD removed in v0.9.3.
- **Status:** worked around; cause `[?]`.
- **Evidence:** `[hw]` {aeria-log} {aeria-changelog}
- **Rule:** A58
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I86. An own engine filled the output half that was about to play: late samples on the analog outputs only
- **Unit:** Octatrack MKII, AERIA OS, 2026-11-12
- **Seen:** a rasp on the analog outputs: at 35 % DSP load 3 samples in every 16 left main, cue and phones 32 samples late. USB recordings were clean because they are tapped earlier. Found with white noise through a loopback cable.
- **Cause (found on the unit):** the engine wrote into the half of its output DMA buffer that was about to play.
- **Fix:** the engine fills the other half; noise through the loop then arrived with one delay at all 16 positions.
- **Status:** fixed.
- **Evidence:** `[hw]` {aeria-log}
- **Rule:** A58
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I87. FLEX played the track's buffer on every trig, ignoring BUF locks
- **Unit:** Digitone II, OS 1.11, dn2mk2 v0.52 (a tester's unit), reported 2026-11-12/13
- **Seen:** a trig with BUF locked to another buffer played the track's BUF; FLEX REC's PAGE moved the screen's page while the green page LED stayed where stock had it (photos).
- **Cause (from the reports, then reproduced in the gate):** the BUF lock never reached the voice; the page LEDs were never claimed because FLEX REC turns its own page without passing PAGE to stock.
- **Fix:** v0.53: a locked step's voice gets the locked buffer, and FLEX REC lights page LEDs 42-49 in stock's scheme; new gate steps fail on the build before.
- **Status:** fixed in v0.53, gated in the emulator; unit confirmation asked of testers.
- **Evidence:** `[hw]` (user report) / `[emu]` (gate) {dn2mk2-v053}
- **Rule:** A19
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I88. Turned knobs did not reach the sample being previewed
- **Unit:** Model:Cycles, OS 1.13, model27 with SAMPLE (Cycles One-Shot 0.16), 2026-11-12/13
- **Seen:** with the PRESET browser open, each new preview note played the sound as it was when the cursor arrived.
- **Cause (read in OS 1.13):** the OS copies the browser's sound into its own preview buffer (two take turns), and preview notes read that copy, not the sound the mod handed out.
- **Fix:** One-Shot 0.17 writes the track's knobs (not the key) into the buffer that holds the copy on each tick.
- **Status:** fixed; flashed on the unit 2026-11-13.
- **Evidence:** `[hw]` {model27-sample017}
- **Rule:** A64
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md)

### I89. A voice switch-off keyed to the filter envelope cut sounding notes on a Digitakt
- **Unit:** Digitakt (mk1), OS 1.54 (Digi CMI 0.26, elekloader core 4.3), 2026-11-12
- **Seen:** with a long release, a key held for a while and then released stopped dead, with SUS and with HOLD.
- **Cause (measured in digiemu, then found by disassembly):** 0.26 ended a released voice when the core export `fw_amp_env` fell below -72 dB, but that value is the filter envelope; it fell to -135 dB while the output stayed constant (S20).
- **Fix:** 0.28 removed the switch-off; 0.30 switches a voice off only after the real amp envelope (`0x4199ed64 + 8v`) stays below -90 dB for 64 blocks.
- **Status:** fixed in the emulator; unit re-test open.
- **Evidence:** `[hw]` (dead stops) / `[emu]` (cause and fix) {digicmi-037}
- **Rule:** A59
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I90. A Digitakt froze when a mod's engine was switched while notes sounded
- **Unit:** Digitakt (mk1), OS 1.54 (Digi CMI 0.30), 2026-11-13
- **Seen:** the unit froze when ENG was switched (sample to time synth or back) with notes sounding.
- **Cause (not confirmed; not reproduced in digiemu, which does not run in real time):** likely audio overload; the meter already reads 85-94 % and the time synth cost about 1,160 instructions per voice per block.
- **Fix:** 0.31 cut the time synth's cost by about a third.
- **Status:** open; not re-tested on the unit.
- **Evidence:** `[hw]` (freeze) / `[?]` (cause) {digicmi-037}
- **Rule:** A34, A44
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I91. A per-sample division made a Digitakt's UI crawl
- **Unit:** Digitakt (mk1), OS 1.54 (Digi CMI 0.31), 2026-11-13
- **Seen:** with RETRO on the UI slowed right down while playing, in both engines.
- **Cause (from the code):** a remainder (`rems.l`, about 20-35 cycles) on every output sample of every voice; digiemu's instruction profile counted each as one instruction.
- **Fix:** 0.32 truncates once per held value and skips voices that are off (divisions from about 48 to 16 per voice per block).
- **Status:** fixed in the emulator; unit re-test open.
- **Evidence:** `[hw]` (lag) / `[emu]` (fix) {digicmi-037}
- **Rule:** A34
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I92. A release path passed every emulator test but stopped notes dead in the mode the user played
- **Unit:** Digitakt (mk1), OS 1.54 (Digi CMI 0.34), 2026-11-13
- **Seen:** with SUS, a held MIDI note stopped dead on release.
- **Cause (reproduced in digiemu once tested in ping-pong):** the voice's end flag (voice + `0x29`) stays set in ping-pong, so on release the gain stage ramped to 0 while the playhead ran on; earlier tests used FWD.L and checked only the playhead.
- **Fix:** 0.36 clears the flag when the voice leaves the loop.
- **Status:** fixed in the emulator; unit re-test open.
- **Evidence:** `[hw]` (seen) / `[emu]` (cause) {digicmi-037}
- **Rule:** A59, A31
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I93. A recorder mod's startup reservation blocked project load and save on a Digitakt II
- **Unit:** Digitakt II, OS 1.16 (dt2-machine-lab combined Sketch + Capicola + ARP build), reported 2026-11-04
- **Seen:** right after power-on, before any recording, project load and save failed.
- **Cause (reproduced on the guard instructions in the emulator):** the buffer setup at startup set the reservation ownership flag even with no audio, and both project entry guards refuse while it is set.
- **Fix:** a candidate that leaves the buffer keys out of the pool during save, rebuilds empty reservations after load, and lets stock's recovery save to slot 128 through.
- **Status:** fixed in a coupled emulator run; not on a unit.
- **Evidence:** `[hw]` (user report) / `[emu]` (cause and fix) {dt2-lab-sketch}
- **Rule:** C9
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I94. An OS 1.17 rebuild of a recorder mod hid its buffers in a project saved with its OS 1.16 version
- **Unit:** Digitakt II, OS 1.17 (dt2-machine-lab Sketch trial R1), 2026-11-12
- **Seen:** SONG opened SKETCH, but the buffer entries were unavailable in a project used before with the OS 1.16 Sketch; a new project worked.
- **Cause (from the source; the project file was not inspected):** the 1.16 version can leave identity markers in sample rows H124-H127; R1 needs them empty and hides the buffers when the reservation fails.
- **Fix:** none yet; use a new project.
- **Status:** open.
- **Evidence:** `[hw]` (user report) / `[?]` (cause) {dt2-lab-sketch}
- **Rule:** C9, E3
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I95. One byte a mod stored made stock drop a whole Octatrack bank at restart
- **Unit:** Octatrack MKII, OS 1.40C, Modwerk VECTOR 0.2.5-0.3.1, the owner's unit, 2026-11-13 (after a user report)
- **Seen:** after saving and a restart all eight tracks read STATIC with no trigs and default FX; a second restart brought the bank back with the byte reset to 00.
- **Cause (reproduced in ot_emu with stock's check, then on the unit):** VECTOR packed SPAN into a byte's top bits, so SPAN 8-12 stored 0x80 or more; stock's Part check counts that as bad, and at boot the battery restore runs before the base has its modules back, so VECTOR's wrapper around the check did not apply (SB22).
- **Fix:** 0.3.2 moves SPAN's top bit to a free bit of the next byte and rewrites old bytes; the bank stayed intact on restart.
- **Status:** fixed; a power cycle on the flashed base not tested.
- **Evidence:** `[hw]` {modwerk-vector}
- **Rule:** A60, E3
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I96. Every effect pick was refused with NO ROOM after a restart
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk base, 20 modules), three starts, 2026-11-12
- **Seen:** Tape Echo on T4 FX2 was refused although it needs no delay buffer; removing and re-adding Air Chorus on T5 cleared it.
- **Cause (from the code, not read on the unit):** a restore makes all modules live in one pass and the board binds Sidechain's key-bus slot on a later tick, so Air Chorus's buffer took the block before the key bus was counted and every later pick failed.
- **Fix:** the base counts live controllers that no slot holds yet; host-tested only.
- **Status:** fixed in source; not run on a unit.
- **Evidence:** `[hw]` (seen) / `[doc]` (cause) {modwerk-ot-noroom}
- **Rule:** G8
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I97. Four software drum voices overran an Analog Rytm's audio block
- **Unit:** Analog Rytm MKII, OS 1.74 (Modwerk BD ANALOG rig builds), 2026-11-05..11
- **Seen:** 909 voices hit together every 125 ms: four gave sample jumps locked to one place in the block, six lost hits and 6 dB of level; once the USB audio stream then delivered only zeros until a replug.
- **Cause (measured on the unit):** the stock block already takes about two thirds of its time, and the unit costs about three times the emulator's instruction count (EMAC latency, cache refills).
- **Fix:** voices hand-scheduled in assembly; BD ANALOG offered on three tracks only.
- **Status:** limited by design.
- **Evidence:** `[hw]` {modwerk-rytm-analogbd}
- **Rule:** A34
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I99. The first note after a RAM load was near silent on a Rytm
- **Unit:** Analog Rytm MKII, OS 1.74 (Modwerk development base, with and without Improved AMP), 2026-11-11
- **Seen:** about -62 dBFS instead of -12.4 dBFS in 7 of 12 boots with the module and 3 of 11 without; the amp envelope ran on time but the sample did not sound.
- **Cause (unknown):** a boot from flash was not tried.
- **Fix:** waiting 3 s before the first note (0 of 7).
- **Status:** open.
- **Evidence:** `[hw]` {modwerk-rytm-amp}
- **Rule:** A40
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I101. SRC labels read ERR with Digi Perform beside CC Names
- **Unit:** Digitakt (mk1), OS 1.53/1.54 (Digi Perform 0.1.3 and the author's 5.0e build), 2026-11-13
- **Seen:** SRC labels read ERR.
- **Cause (from the code):** CC Names' hook at `0x40030daa` reads d2; Digi Perform called that site as plain C with d2 unset.
- **Fix:** 0.1.4 sets d2 and a4 as stock's caller does; checked in the emulator.
- **Status:** fixed.
- **Evidence:** `[hw]` {modwerk-digiperform}
- **Rule:** A62
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I104. A development core put its module binder in boot storage that startup wipes
- **Unit:** Syntakt, OS 1.41 (Synfact development core "1.8.1", withdrawn; not the released core 1.8.1), 2026-11-12
- **Seen:** after loading the core and bank and restarting, startup stopped with exception V04 at `0x40347BC2` (return address `0x46006410`).
- **Cause (read from the code, then reproduced in the emulator):** to free room in the resident reserve, the module binder had been moved into the storage appended after the MAIN image. Startup clears and reuses that storage once the resident copy is done, so the call from the machine loader jumped into wiped memory. The opcode audit and host tests passed because neither modelled the clearing, and the test fixtures filled the event lists directly instead of calling the binder.
- **Fix:** core 1.8.1.1 puts the binder and dispatcher back in resident memory; the builder now refuses startup entries that are not resident, and a new emulator test clears the appended storage and reproduces the exception at the same address as a negative control. 1.8.1.1 boots and plays on the unit. A failed bank may stay marked TRYING, so send it again and check the versions in System Info.
- **Status:** fixed.
- **Evidence:** `[hw]` {synfact-main-opt}
- **Rule:** A42, C8
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I105. Module picks accepted while stopped stalled the DSP once the unit played
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk development base, 29 modules, the owner's unit), 2026-11-13
- **Seen:** Euclid, Mini Verb, LOFI2 and Tape Echo were accepted while the unit was stopped at about 70 % CPU; playing then reached 95-97 %, and after about 12 s the DSP frames stopped (stall record after a 473 µs frame interrupt).
- **Cause (measured on the unit):** the busy-unit guard judged the stopped load, which is 15-25 points below the playing load, and did not count the picked machine's own cost.
- **Fix:** the guard now adds the machine's price and judges a stopped unit by its last playing load ("WAS BUSY PLAYING").
- **Status:** fixed.
- **Evidence:** `[hw]` {modwerk-1114}
- **Rule:** A65
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I107. An Octatrack left USB during a USB Audio recording on a module trial
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk development base with Amiga 0.2.0, the owner's unit), 2026-11-13
- **Seen:** 231 s into a timed RAM trial with a USB Audio recording running, the unit dropped off USB and did not come back; no crash or stall record was written. Amiga 0.1.0 once did the same while recording.
- **Cause:** unknown (the module, the recording or the development base); six recordings on 2026-11-14 ended normally.
- **Fix:** none yet.
- **Status:** open.
- **Evidence:** `[hw]` {modwerk-1114}
- **Rule:** C11
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I108. A demand load during play stalled an Octatrack's DSP until the copy moved to the frame's end
- **Unit:** Octatrack MKII, OS 1.40C (octabam, 11 test images with FRAME GUARD and a 20-channel USB capture), 2026-11-12..15
- **Seen:** a program change to a demand effect that was not loaded (SPECTRUM, SIDECHAIN_COMPRESSOR) stopped the audio in about two runs of three; panel and USB still answered, and a power cycle cleared it.
- **Cause (partly found on the unit):** DSP core B reached P:`$268` in its first track and stopped, and core A waited at P:`$a3` for good. Frame overrun, the copy alone, its destination, the stack and a stale X word were ruled out; the mechanism is unknown (the emulator port runs one core and cannot show it).
- **Fix:** the loader's copy (DLCOPY) moved from the frame head (P:`0x76`) to the frame end (P:`0x342`); 12 of 12 runs with 251 loads were clean on 2026-11-15.
- **Status:** fixed for this case; one stall without loader activity (a 564 µs program-change frame, the next entry 205 µs late) and one whole-unit freeze stay open. May explain part of I57.
- **Evidence:** `[hw]` {octabam-1115}
- **Rule:** A66, A56
- **Fact:** [devices/octatrack.md](devices/octatrack.md#findings-2026-11-1415-kyoti-reload-octabam-dlcopy-modwerk-kyoti-reload-clyps-octabam-1115-modwerk-1115)

### I109. A module restarted an Octatrack with an illegal instruction its cache still held
- **Unit:** Octatrack MKII, OS 1.40C (Modwerk development twin with an earlier build of Amiga 0.3.0 and a base change under test), 2026-11-14
- **Seen:** about 90 s into a RAM trial the unit restarted; crash record 12 shows an illegal instruction at the first instruction of the module's sample-list function.
- **Cause (open):** the code was present in the cache but read as zeros through the uncached alias. The same package on a twin without the base change ran clean, so the base change is suspected.
- **Fix:** none yet; Amiga 0.3.0's later RAM trial rolled back clean.
- **Status:** open.
- **Evidence:** `[hw]` {modwerk-1115}
- **Rule:** C11
- **Fact:** [devices/octatrack.md](devices/octatrack.md#findings-2026-11-1415-kyoti-reload-octabam-dlcopy-modwerk-kyoti-reload-clyps-octabam-1115-modwerk-1115)

### I110. A remote-commanded REMIX SWITCH boot stopped on the boot screen
- **Unit:** Octatrack MKII, OS 1.40C (octabam image N1 with REMOTE), 2026-11-15
- **Seen:** REMOTE's command 3 booted a `.RMX` file through REMIX SWITCH's YES path; the unit reset, showed the boot screen and did not come back on USB within 150 s. A power cycle recovered it.
- **Cause (unknown):** it was the first boot after flashing, after a project load, panel PLAY, MIDI START, two program changes, STOP and commands 1, 2 and 4. The next nine commanded boots all came back in 7-8 s, two of them after the same sequence.
- **Fix:** none; seen once.
- **Later (2026-11-20):** seen twice more on an MKII. On 2026-11-18 command 3 for `OCTABAM 05.RMX` from image N1 left the boot screen with no USB at 30 s and needed a power cycle, while the same file picked from BRAIN > REMIXES on the panel booted; later commanded boots between BUILD 05 images came back 4 of 4. On 2026-11-19 command 3 sent while BUILD 05's DSP frame count was stopped (I170) did not come back in 150 s; two earlier boots from a stalled DSP (after loader phases, I169) did. `[hw]` {octabam-1120}
- **Later (2026-11-22):** commanded boots sent while the DSP was stalled mostly froze or fell back to the flashed image, which neither the boot screen nor the ring fingerprint shows (only the running image's name does); 39 commanded boots from units whose DSP was counting all came back. `[hw]` {octabam-1122}
- **Status:** open.
- **Evidence:** `[hw]` {octabam-1116}
- **Rule:** A2, A40
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-remote-and-more-stock-sites-os-140c-2026-11-1416-octabam-1116)

### I111. A mod's own SysEx report cut a stock pattern dump on an Analog Rytm
- **Unit:** Analog Rytm MKII, OS 1.73 and 1.74 (Sidecar's Rytm firmware before 0.5.0), reported in the 0.5.0 notes, 2026-11-13..16
- **Seen:** FILL ended with NO ANSWER and SONG fetches needed retries; in an emulator test 2 of 8 multi-part 0x54 pattern dumps were cut by the mod's fx-in report.
- **Cause (shown in the emulator):** a stock multi-part dump releases the MIDI lock between its parts while its SysEx state at `0x413db244` stays set; the mod's try-send took the lock in such a gap and put its own message inside the dump.
- **Fix:** 0.5.0 sends only while `0x413db244` is zero, checked before the try-lock and again while holding the lock, with the wait bounded at 2 s.
- **Status:** fixed in 0.5.0 (emulator).
- **Evidence:** `[emu]` (cut and fix) / `[doc]` (symptom) {sidecar-mods-1116}
- **Rule:** F8
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#sidecar-050-and-rytm-firmware-050-mkii-os-174-2026-11-16-sidecar-0516-sidecar-mods-1116)

### I113. A previewed sample played to its end however short the key press (Model:Cycles)
- **Unit:** Model:Cycles, OS 1.13 (model27 with SAMPLE, Cycles One-Shot 0.17), found 2026-11-15
- **Seen:** with the sequencer stopped and GATE on, a sample previewed from the browser by a TRIG key or the pad played whole, however short the press.
- **Cause (shown in the emulator, envelope run block by block):** the mod sent the note-off at once; the OS chained it with the note into one batch, and the amp envelope ignores an end that comes in the trig's own block, so with GATE on the note stayed in hold. The project's notes had claimed the preview no longer held, without a check.
- **Fix:** One-Shot 0.18 / model27 0.66 records the note and raises the voice's end flag (+0x3c) in the first block without a trig, and hooks both releases (pad `0x4001d0fc`, TRIG keys `0x40019c84`); flashed from the live page 2026-11-15: taps stay short, held keys sound until let go.
- **Status:** fixed.
- **Evidence:** `[hw]` {model27-chips}
- **Rule:** A67, A31
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md#pads-preview-notes-and-the-shared-sine-model27-notes-60-and-66-main-os-113-2026-11-12-model27-preview)

### I115. ARP pages stayed blank or lost their keys after permanent mute (Syntakt)
- **Unit:** Syntakt, OS 1.41 (Synfact arp-st 1.9.1 to 1.10.3 on core 1.8.1, the owner's unit), 2026-11-15/16
- **Seen:** after FUNC + BANK mute and TRIG navigation the ARP pages were empty (1.9.1, 1.9.2), or the screen drew without the blue step keys until FUNC/TRK/BANK was pressed (1.10.2), or normal opening was blank (1.10.3); with 1.10.4 the sequence mute -> ARP -> first TRIG -> close mute -> ARP still left screen and keys absent.
- **Cause (reproduced in Unicorn with the native routines):** several, each hidden by a test double: the opening guard did not know MainScreen's six normal child views; a view pushed by the mod is composed and ticked synchronously before the push returns, so the mod's tick closed its own new view; and stock's deferred view cleanup (`0x40100ea4`) clears its pending flag after the visibility call, losing a close raised by a tick during that call, so a closed view stayed in the list and blocked ARP.
- **Fix:** ARP 1.10.4 selects its page before the push; core 1.8.2 clears the flag before the visibility call (same 18-byte window). Tests now run the native push, compose, tick and cleanup instead of stubs.
- **Status:** fixed in the emulator; the owner's panel confirmation is outstanding.
- **Evidence:** `[hw]` (symptoms) / `[emu]` (causes) {synfact-1117}
- **Rule:** C8
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-findings-sequencer-kit-slots-views-mixer-os-141-2026-11-1416-synfact-1117)

### I116. A step-order mod missed two readers of its state (Syntakt)
- **Unit:** Syntakt, OS 1.41 (Synfact playhead-st builds 2 and 9, the owner's unit), 2026-11-15/16
- **Seen:** build 2 played the steps backwards, but the trig LEDs' playhead still ran forwards; build 9's per-track modes came back after a project save and power cycle, but not after a power cycle without a save.
- **Cause (found on the unit, then in the code):** the trig LEDs read the step through their own accessor `0x4008b734`, not the patched sequencer sites; and a power cycle without a save restores kits from their mirror slots, which are only re-encoded when `KitActive::kitChanged` (`0x40172250`) runs after a native kit edit.
- **Fix:** build 3 patches the accessor as a fifth site; build 10 calls `kitChanged` for the playing kit after each mode change (checked in Unicorn, not yet on the unit).
- **Status:** LEDs fixed on the unit; mirrors fixed in the emulator only.
- **Evidence:** `[hw]` {synfact-1117}
- **Rule:** E5, A31
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-findings-sequencer-kit-slots-views-mixer-os-141-2026-11-1416-synfact-1117)

### I118. Card-loaded mods copied stock bytes the flashed build had already patched (Digitone mk1, Octatrack)
- **Unit:** none (digiemu, Digitone mk1 OS 1.44; ot_emu, Octatrack OS 1.40C), TELOS poc and 0.1, 2026-11-14/15
- **Seen:** on the Digitone, Tone+FX and Mutiny loaded from the store crashed the emulated unit; on the Octatrack, stock parts of the shop's DIRECT JUMP, QUANTIZER and the USB IO mods would have been wrong.
- **Cause (found in the emulators):** a loader that fills a mod's replayed stock instructions from the running OS reads the flashed core's or companions' patches instead; the OS also changes some image data before the load point (1,238 bytes on the Digitone from `0x4018fefc`; Octatrack data in `0x400b9000..0x400e2324`).
- **Fix:** the build descriptor carries a stock shadow of every range the flashed build writes (ABI 1.2), and the core keeps a copy of the OS image made before the OS runs.
- **Status:** fixed in the emulators; the Digitone poc loaded each mod kind on a unit on 2026-11-15 (OS 1.44).
- **Evidence:** `[emu]` (crash) / `[hw]` (later loads) {telos-ot-1117}
- **Rule:** A69
- **Fact:** [devices/octatrack.md](devices/octatrack.md#telos-and-dspload-ot-boot-order-card-mount-run-time-dsp-code-os-140c-2026-11-1416-telos-ot-1117-elekloader-1117)

### I119. A DIRECT JUMP jump popped with SILENCE TRACKS on; the emulator's inferred fix did not help
- **Unit:** Octatrack MKI, OS 1.40C (DIRECT JUMP V7.2 standalone `140C_KDJC6`, then KYOTI with Clyps), 2026-11-14..15
- **Seen:** with CONTROL > SEQUENCER > SILENCE TRACKS on, a jump to a pattern on another Part (OT DEMO A05 -> A03) popped while a sample rang; stock's CHAIN AFTER 2 change did not. V7.2.1 (queue T8's master restart in the switch frame), whose cause was inferred in an emulator that streams no samples, left the pop unchanged on the unit and was reverted.
- **Cause (render with real audio in octabam's ot_emu):** at a switch the engine hard-kills each silenced voice (`0x40006820`), with no declicked release. Stock's change lands on step 0, where most tracks trigger and restart in the same frame; the jump lands mid-pattern, so a ringing track with no trig there is simply cut.
- **Fix:** V7.2.2 calls stock's note-off `0x40008f84(t)` for every track the switch will silence, about a tick before it (the DSP's own fade). The author: "the pattern change pop seems to be fixed" (2026-11-15).
- **Status:** fixed; stock probably pops the same way in the rarer case (H32).
- **Evidence:** `[hw]` (pop, fix) / `[emu]` (mechanism) {kyoti-1117}
- **Rule:** C4, A58
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I121. Hiding a window by unlinking it let stock build SETUP inside it
- **Unit:** Octatrack MKI, OS 1.40C (KYOTI with Clyps, build CL35), 2026-11-15
- **Seen:** peeking at a parameter page from Clyps drew a SETUP page 1 px off with stray pixels; [FUNC] + page locked SETUP and a second hold toggled it back.
- **Cause (read from the code):** Clyps hid its window by unlinking it; the window manager `0x4005829c` finds a free slot by the linked bit (`+32` bit 5), so a SETUP window opened during the peek was built into Clyps' own slot. A plain press of the current page also reached stock, which toggles SETUP. The UI gate missed it: its screen shots were stock's page layer only, never the composed screen.
- **Fix:** CL36 hides the window by its visible bit (`+32` bit 0) and brings it to the front (`0x400117b4`) on return; CL37/CL38 also hide the SETUP window's edges and re-push Clyps' key layers after a peek. The gate now compares the screen as composed (`0x40013abc` into `[0x400b9710]`). Passed on the unit in KYOTI V1.8C (2026-11-15).
- **Status:** fixed.
- **Evidence:** `[hw]` {kyoti-1117}
- **Rule:** A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I122. Redirecting one stock painter drew half track tabs and a stray mark
- **Unit:** Octatrack MKI, OS 1.40C (Clyps CLYPT, CLYPW), 2026-10-31
- **Seen:** for a multi-track group the main screen's tab followed the group only in its upper half; the next build showed a stray `!` beside the machine glyph.
- **Cause (write watch in the emulator):** three routines paint each tab, each with its own active-track test (`0x4004bd48` lower half, `0x4003fed8` upper half, `0x40044804` status mark); the first probe had listed the other writers too, but only one was redirected. Renders that called a painter alone did not show the mark.
- **Fix:** all three tests redirected (CLYPX, all good on the unit the same day); renders now call the whole per-pass routine `0x40052200`.
- **Status:** fixed.
- **Evidence:** `[hw]` {kyoti-clyps-scope}
- **Rule:** A31
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I123. A byte read of a long flag hid the MIDI tracks
- **Unit:** Octatrack MKI, OS 1.40C (Clyps CLYP6), 2026-10-25
- **Seen:** on the MIDI side Clyps showed and loaded the audio tracks.
- **Cause (read from the code):** the "MIDI tracks shown" flag `0x80000012` is a long; a byte read returns its high byte, always 0. The emulator gate passed because its fixture project loaded with the audio tracks shown. RELOAD_FROM_PROJECT's `rl3_arm_n` has the same byte read (reported, status not stated).
- **Fix:** read as a long (CLYP7); a gate scenario on a project that loads with the MIDI tracks shown.
- **Status:** fixed in Clyps; open in RELOAD_FROM_PROJECT as far as the source says.
- **Evidence:** `[hw]` {kyoti-clyps-scope}
- **Rule:** D13
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I124. A flashed image carried another build's OS VERSION name
- **Unit:** Octatrack MKI, OS 1.40C (DIRECT JUMP V7.2.2), 2026-11-15
- **Seen:** the unit flashed with the file reported as `140C_KDJC9` read `140C_KDJ7`.
- **Cause (found in the build scripts):** a later composite build re-ran the base builder without a name and rewrote the same output file; the code (mainos) was the intended one, the name and the reported syx hashes were not. The card `.bin` is ELUP-obfuscated, so the name cannot be read there.
- **Fix:** build the composite without rebuilding the base, and check the "OS VERSION will read" line and the syx hash against a fresh named build before reporting.
- **Status:** fixed in the procedure; three earlier reported hashes were relabelled.
- **Evidence:** `[hw]` {kyoti-1117}
- **Rule:** A6
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I125. A bit-exact sub oscillator sounded as buzz and crackle on the unit (model27 MAXSAW, Model:Cycles)
- **Unit:** Model:Cycles, OS 1.13 (model27 MAXSAW 0.1, the first Sub), 2026-11-16
- **Seen:** with Sub on, often no weight below the note, but artefacts in the mids and highs, crackle and a short noise.
- **Cause (measured on the unit, recordings against the host core):** the device did what the design said: Sub shifted the centre's naive sawtooth two octaves down, which brings as many overtones as fundamental (its reset every 15 ms a buzz), and the pitch-tracked high-pass moved down with it and let 4-8 dB more aliasing through. Recordings matched the host core within 0.6 dB in third-octave bands, so every proof (interpreter, Unicorn bit-exact) had passed.
- **Fix:** a listening page of seven sub variants; the maintainer chose an extra naive sawtooth two octaves down through a 2-pole low-pass at the note, added after the high-pass (MAXSAW 0.2); on the unit "sub klingt jetzt gut" (the sub sounds good now). Released in 0.69, flashed from the page with every card.
- **Status:** fixed.
- **Evidence:** `[hw]` {model27-maxsaw}
- **Rule:** A58
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md#maxsaw-punch-and-the-output-stage-model27-notes84-modelcycles-os-113-2026-11-16-model27-maxsaw)

### I127. YES changed a track at once with RECORD off (trig-seedr 0.5.0, Analog Rytm MKII)
- **Unit:** Analog Rytm MKII, OS 1.74 (trig-seedr 0.5.0/0.5.1 under elekloader core-ar2 0.13), first hardware pass 2026-11-16
- **Seen:** every feature worked, but YES on a track wrote real trigs at once, with RECORD off, unlike every other trig edit on the Rytm; leaving the track or pattern kept an unapplied take.
- **Cause (by design):** the mod must write stored trigs to be heard (stock's Euclidean mode plays a separate pattern and never touches stored trigs), and 0.5.0 treated leaving as keeping.
- **Fix:** 0.5.1 "generate and apply": YES writes only with grid recording on (flag byte `0x417e320c`), FUNC + YES is the only way a take stays, and changing track or pattern, closing or turning RECORD off restores the original (NOT APPLIED). 0.6.0 played on the unit: works. 0.7.0 adds a pending-take dot and makes YES after a revert bring the same take back.
- **Status:** fixed; 0.7.1 passed on a unit 2026-11-17 {trig-seedr-1118}.
- **Evidence:** `[hw]` {trig-seedr-1117}
- **Rule:** C11 (a usability fault, no safety rule)
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#trig-seedr-05-07-grid-recording-lock-lanes-redraw-cost-and-first-unit-passes-mkii-os-174-2026-11-16-trig-seedr-1117)

### I129. An Octatrack restore left out the same module at nearly every start
- **Unit:** Octatrack (model not stated), Modwerk base `f6422fa6`, a saved set of 12 modules (Mini Verb, Tape Echo, TapeHead, E-Verb, BBD Delay, LOFI2, Scale Quantizer, FM Synth, Play Modes, POLY8, Deja Vu, SC Ringmod), field diagnostics 2026-11-12..16
- **Seen:** at six of seven starts the power-on restore loaded 11 modules and refused SC Ringmod for module memory; at the seventh it refused Tape Echo (no free handle). A sync from the site then added the missing module and all 12 ran.
- **Cause (unknown):** a set the unit accepts at a sync does not always fit again at the restore; not reproduced.
- **Fix:** none yet; Modwerk plans to restore that set in the emulator.
- **Later (2026-11-20):** Modwerk found the same shape on another unit on base 0.7.8 (11 modules; SC Ringmod restored at two starts, refused for "module memory" at the next two, and a one-package sync refused the same way). There the cause was a DSP claim meeting a delay buffer: SC Ringmod 0.2.1 claims the key bus, and the base counts a module effect's whole FX2 block as a delay buffer; the refusals began when Air Chorus sat on T5 FX2. The module pool was far from full (161,344 of 786,432 bytes), so the refusal was right but its name was wrong. This unit's records do not line up with that, so I129 stays unconfirmed; the other candidate is the dropped effect line of I154. Base 0.7.10 is to give the case its own refusal code. `[hw]` (field log) / `[emu]` {modwerk-1120}
- **Later (2026-11-21):** base 0.7.10 refuses that case as `RUNTIME_BUFFER` (12), its message names the FX2 slot to move (T1, T5 or T7), it counts reviewed buffer extents so E-Verb, Mini Verb, BBD Delay and Vibrato there no longer cause it (Air Chorus still does), and a refused restore logs which check refused and how much module memory was in use, so the next such field record can tell the causes apart. `[doc]` {modwerk-1121}
- **Status:** open.
- **Evidence:** `[hw]` (field records) {modwerk-ot-beta-1116}
- **Rule:** C11
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-2026-11-1617-modwerk-1117-modwerk-ot-kits-modwerk-ot-midiscenes-modwerk-ot-beta-1116)

### I130. A timed module trial could not roll back while the module's window was open
- **Unit:** Octatrack MKII, OS 1.40C, development twin of Modwerk base 0.7.5 (`7db3251b`), Tuner 0.1.0-experimental USB package, 2026-11-16
- **Seen:** with Tuner's window left open, the trial's automatic Undo at 45 s was refused; the host gave up after 3 s of retries (`needs-recovery`), the module stayed live and the window kept drawing.
- **Cause (by design, from the base's refusal code):** base 0.7.5 refuses to remove, replace or undo a module while stock's window manager or input layer still names its memory (`RUNTIME_UI_OPEN`); the timed trial's rollback had no path for it.
- **Fix:** after NO closed the window, `device -- recover` rolled the trial back; a second trial with the window closed rolled back at once. The site's handling of a trial that ends with a window open is not yet tested.
- **Later (2026-11-20):** a Micro Timing 0.1.1-experimental trial on a RAM-booted development twin (OS 1.40C, 2026-11-19, about 180 s, no crash, stall or skipped track) ended with its automatic rollback refused (`needs-recovery`); the cause is not stated. The unit came back on the flashed base `c889442d` with the same 24 kept modules and no trace of the trial. On 2026-11-18 (flashed base `931a91bd`) removing the module was refused (loader refusal 11, `RUNTIME_UI_OPEN`) while TRACK TRIG EDIT's key layer was up, even after leaving the list for the grid; after a power cycle with the menus closed it went. `[hw]` {modwerk-1120}
- **Later (2026-11-21):** the Micro Timing case had a second cause: with a module's page open when the trial ended, the base counted the module's own change to the stock page as a use, so Undo stayed refused even after the page was closed and only a power cycle helped (USB unplug did not). Base 0.7.10 judges the page as it will read once the module is out; with the page still open Undo waits, and after closing it `device -- recover` finishes without a restart (MKII, MICRO T highlighted in TRACK TRIG EDIT, 2026-11-19). `[hw]` {modwerk-1121}
- **Status:** worked around; open for the site's sync dialog.
- **Evidence:** `[hw]` {modwerk-1117}
- **Rule:** A54, A2
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-2026-11-1617-modwerk-1117-modwerk-ot-kits-modwerk-ot-midiscenes-modwerk-ot-beta-1116)

### I132. A rate mod silenced the Rytm's sample preview
- **Unit:** Analog Rytm MKII, OS 1.74, Improved SMPL 0.5.0-experimental (Modwerk), reported as issue #1591, fixed 2026-11-16
- **Seen:** FUNC + YES in a sample list played nothing.
- **Cause (shown in rytm-emu):** stock's preview routine `0x400a0dac` puts the sample in slot 129 with TUN and FIN at rest (`0x4000`); the mod read FIN at rest as RATE 0 and scaled the step to 0.
- **Fix:** 0.5.1 plays any voice whose sample slot is 128 or above at 1x, forward. The author's unit (SU02, from RAM): previews at RATE 0, +63, -64 and with an LFO on RATE all at normal speed.
- **Status:** fixed in 0.5.1.
- **Evidence:** `[emu]` (cause) / `[hw]` (fix) {modwerk-rytm-1116}
- **Rule:** C11
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#modwerk-findings-mkii-and-mki-os-174-2026-11-1617-modwerk-rytm-1116-modwerk-1117)

### I133. FLEX's MUTE SRC left tracks muted until a power cycle (dn2mk2)
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.55/v0.56), tester report 2026-11-15
- **Seen:** with MUTE ON the SRC track was muted as soon as a take existed, even while recording; some tracks could not be unmuted (stock unmute did not bring them back) until a power cycle.
- **Cause (found in the coupled emulator):** the mute followed the existence of a take, not whether the FLEX track was playing. DSP play positions could not tell when a FLEX note ends, because a FLEX voice's take keeps looping silently after its release.
- **Fix:** v0.57 mutes the SRC only while a FLEX voice has its note on (frame trigger words 34/36, bit per voice) and its LEVEL is above 0, with a 300-frame (about 0.2 s) hold; stopping or muting the FLEX track or MUTE OFF gives the SRC back. Gated in the coupled emulator (`mute`, `flexplay`).
- **Status:** fixed in v0.57 (emulator); no unit result yet. Remaining: a long gap between FLEX notes un-mutes the source.
- **Evidence:** `[hw]` (symptom, tester) / `[emu]` (fix) {dn2mk2-v057}
- **Rule:** A8
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#rift-v04-organ-and-dn2mk2-v057-flexmute-os-111-2026-11-16-dn2-rift-v04-dn2mk2-v057)

### I134. A held-key view stayed on after the key was released (Digitakt LED colours)
- **Unit:** Digitakt MKI, OS 1.54 (ledcolors 0.4), fixed 2026-11-16
- **Seen:** holding TRK shows every track's colour on the trigs; that view could stay on after TRK was let go, usually after TRK + a trig or a long hold.
- **Cause (the author's statement):** the mod missed TRK's release (it did not read the release the way the firmware does).
- **Fix:** 0.5 reads TRK's release as the firmware does, and as a safety net ends the view 2 s after the last TRK key, colour change or track change. 0.5 tested on a unit by the author.
- **Status:** fixed in 0.5.
- **Evidence:** `[hw]` (fix tested; where the fault was seen is not stated) {ledcolors-1117}
- **Rule:** C11
- **Fact:** [devices/digitakt.md](devices/digitakt.md#led-colours-mod-on-the-unit-os-154-2026-11-16-ledcolors-1117)

### I135. FASCIA with BEND up and DAMP near 0 decays unevenly and drops voices (RIFT)
- **Unit:** Digitone II, OS 1.11 (RIFT v0.3/v0.4), owner's report 2026-11-15
- **Seen:** some hits sustain, others decay short, and now and then a voice cuts out.
- **Cause (suspected by the project):** BEND's glide can feed a long-ringing body.
- **Fix:** none yet; workaround BEND 10 or less, or raise DAMP. A fix is planned.
- **Status:** open.
- **Evidence:** `[?]` (owner's report; the notes do not say unit or emulator, likely a unit) {dn2-rift-v04}
- **Rule:** C11
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md#rift-v04-organ-and-dn2mk2-v057-flexmute-os-111-2026-11-16-dn2-rift-v04-dn2mk2-v057)

### I136. One held key with the sequencer stopped played a run of different notes (DigiArp MIDI, Digitone mk1)
- **Unit:** Digitone mk1, OS 1.44 (DigiArp MIDI DA27 beta), the author's known issue; investigated by morriess 2026-11-14
- **Seen:** sometimes one held key, sequencer stopped, plays a repeating run of different notes on a MIDI track.
- **Cause (unknown):** ruled out: hook arguments, interleaved DIN bytes (the send routine masks interrupts), release with a different note, ARP page vs engine bytes, the engine maths. Suspects: sequencer notes left after STOP; a release path (release-all `0x4003bc0e`) that bypasses the note-off hook; the worker sharing RTOS priority 1 with a stock task, making timing cases likelier on a unit than in the emulator.
- **Fix:** none known; a proposed guard clears the track's engine notes while stopped with no keys held.
- **Status:** open (morriess removed its notes from the repo on 2026-11-16; DigiArp now lives in the elekloader Mod Shop).
- **Evidence:** `[hw]` (author's known issue) / `[doc]` (analysis) {drummode-1117}
- **Rule:** C11
- **Fact:** [devices/digitone.md](devices/digitone.md#drum-mode-and-digiarp-notes-leds-record-modes-pages-os-144-2026-11-1416-drummode-1117)

### I137. A per-track colour hid the stock quick-mute colours (Digitakt LED colours)
- **Unit:** Digitakt MKI, OS 1.54 (ledcolors 0.6), user report, fixed 2026-11-17
- **Seen:** while holding TRK + FUNC (quick mute) the keys showed the track colours instead of stock's green (playing) and red (muted).
- **Cause:** the mod's track colour replaces the theme's red everywhere, including the quick-mute view.
- **Fix:** 0.7 shows the stock mute colours while TRK + FUNC is held; track colours return when FUNC is released.
- **Status:** fixed in 0.7 (0.9 tested on a unit by the author).
- **Evidence:** `[hw]` {led-colors-1118}
- **Rule:** C11
- **Fact:** [devices/digitakt.md](devices/digitakt.md)

### I138. A new keyboard scale crashed the unit in a chord MODE (dn2mk2 v0.58)
- **Unit:** Digitone II, OS 1.11 (dn2mk2 v0.58 SCALES), tester report, 2026-11-17
- **Seen:** with PR12 or PM12 selected, a chord MODE crashed the unit: EXCEPTION at P `40034BA6`.
- **Cause (the project's analysis):** a division by an empty chord list; the chord MODEs use a sixth per-scale table, built in RAM at run time, which v0.58 did not extend when it added two scales to the five stock tables.
- **Fix:** v0.58 pulled from the patcher the same day; v0.57 is the latest again and the code is reverted on main. A fix (chord lists extended, plus a chord-MODE gate test still to write) is on a branch.
- **Status:** open (withdrawn)
- **Evidence:** `[hw]` {dn2mk2-v058}
- **Rule:** A8, A16, A72
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I139. A neutral filter setting still coloured the mix through the analog FX block (Syntakt Performance Mods)
- **Unit:** Syntakt, OS 1.41/1.42 (Performance Mods TEST36b), the author's unit, 2026-11-16
- **Seen:** with the PERFORM filter at THRU the mix sounded harder and crackly.
- **Cause:** THRU left the whole mix routed through the analog FX block.
- **Fix:** TEST37c makes THRU a full bypass (filter off, stock routing kept, no CPU at THRU).
- **Status:** fixed in TEST37c (tried on the author's unit; "much better"); heavy sets not proven.
- **Evidence:** `[hw]` {stpm-1118}
- **Rule:** A73
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I140. A 70 % CPU budget greyed out every heavier machine on old projects (Modded Cycles Techno Edition)
- **Unit:** Model:Cycles, OS 1.13 (Modded Cycles Techno Edition up to v1.4), user report, fixed 2026-11-17
- **Seen:** on a project made before flashing, every heavier machine in the list was greyed out even with nothing playing.
- **Cause:** the project keeps the six stock machines, which with the rest of the OS already count about 74 % against the CPU Lim default of 70 %.
- **Fix:** v1.4.1 sets the default to 80 % (a user who had chosen 80 % now reads 70 % and must step it on). New projects start with EMPTY on all six tracks.
- **Status:** fixed in v1.4.1.
- **Evidence:** `[hw]` (user report) {mcte-1118}
- **Rule:** A65 (judge a load budget by the playing load, and know the baseline before setting a limit)
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md)

### I141. Drum Mode's lane strip disappeared on page switches (Digitone mk1)
- **Unit:** Digitone mk1, OS 1.44 (Drum Mode 0.8), 2026-11-17
- **Seen:** the lane strip in the screen corner sometimes vanished while browsing pages (e.g. LFO, then SYN1); not reproduced in digiemu, where the strip was there after every switch. Whether it returns by itself is not stated.
- **Cause:** unknown; suspected stock repainting the whole page after the mod drew, while the mod redraws only on a change.
- **Fix:** proposed: redraw whenever the shown page changes.
- **Later (2026-11-20):** probable cause found on the unit on pattern H02: after a pattern pick with BANK or PTN one of the firmware's permanent views stays on top of the main view stack. It draws nothing, but the mod asked for the top view and drew only while the parameter page was on top, so the DRUM pages were empty and the strip was gone. Drum Mode 0.8.3 walks the view stack past that view; the page-switch case is still to be checked on a unit. The lesson is then not "redraw on a page change" but "find your page in the view stack; do not assume it is the top view" (A79 again: H02, not A01). `[hw]` (symptom on H02) / `[emu]` (cause) {drum-mode-1120}
- **Later (2026-11-22):** in the unit test of 0.10 the lane strip no longer disappeared while switching pages. `[hw]` {drum-mode-1123}
- **Status:** fixed (0.8.3; the page-switch case passed on the unit with 0.10)
- **Evidence:** `[hw]` {drum-mode-1118}
- **Rule:** C11 (a candidate general rule, if a second case appears: "a mod that draws over a stock page must redraw when the page changes, not only when its own content changes")
- **Fact:** [devices/digitone.md](devices/digitone.md)

### I144. An added machine clicked at trigs through the stock VCA (model27 TERRA, Model:Cycles)
- **Unit:** Model:Cycles, OS 1.13, model27 TERRA 0.1b with the CPU page (command-line build), 2026-11-17
- **Seen:** small clicks now and then at trigs. The same clicks were known from earlier added machines (SWARM).
- **Cause:** the stock VCA (`0x400a9430`) cuts the level in a trig's block and jumps at the attack. TONE's chain does that to TERRA's output, which runs on through the trig without a reset.
- **Fix:** TERRA 0.2 clears voice `+0x34` and `+0x38` only for the VCA call and restores them before PUNCH; the VCA ramps from its last level each block. Unicorn retrig check at DECAY 127/60/30: gain never dips toward zero, largest step a frame 0.0014/0.0064/0.0190.
- **Status:** fixed in TERRA 0.2 (release 0.72); heard on the unit: "no more clicks". SWARM's version of the fix is on a branch, not tried on a unit.
- **Evidence:** `[hw]` {model27-1118}
- **Rule:** A75
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md)

### I145. Many stock samples overwrote Synfact's resident core and crashed it at boot (Synfact)
- **Unit:** Syntakt, OS 1.42 (and the same layout on 1.41), Synfact core 2.0.0 and older, the owner's unit, 2026-11-17
- **Seen:** with all 64 stock sample slots holding 5 s samples, the core crashed; earlier user reports of exceptions at `0x460001d0` and `0x460001d6` lie in the window that gets overwritten (that link is not proven).
- **Cause:** at boot stock concatenates all 64 stock samples into one blob in MAIN DDR from `0x4584f2c5`; past 84 s of audio in all it runs over the 64 KiB resident core at `0x46000000`. The core's guards checked each slot on disk and parsed the blob only after stock had built it. Reproduced in Unicorn for both OS versions (first overlapping write in stock's memcpy while copying slot 17).
- **Fix:** core 2.0.1 no longer calls the stock builder; it streams each sender page from eMMC with 5 KiB of scratch, and draws waveforms on demand.
- **Status:** fixed in 2.0.1 (prototype booted with the same 64 samples on the owner's unit; the final 2.0.1 not stated on hardware)
- **Evidence:** `[hw]` (crash and prototype boot, owner's report) / `[emu]` (cause) {synfact-1118}
- **Rule:** A34, D11 (a repeat of I20 at the same address)
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I146. PATTERN MUTE stored its layer in the one-shot trig mask (octabam)
- **Unit:** Octatrack MKI, OS 1.40C, octabam 0.4 with PATTERN MUTE, reported 2026-11-16 (octabam#1143)
- **Seen:** a one-shot trig on step 1 of an audio track muted that track in the PATTERN layer, one on step 2 muted the matching MIDI track, and a PATTERN-layer unmute deleted the one-shot. The double-FUNC layer switch also flipped in ordinary use when FUNC+track or FUNC+trig was pressed twice within 300 ms.
- **Cause:** the module used bits 0-1 of byte 40 of each audio track record, which is the low byte of the one-shot trig mask (steps 1-8). The check that called the byte unused ran on a project with no one-shots on steps 1-2. The switch counted any two FUNC presses, chords included.
- **Fix:** PATTERN-layer mutes moved to a side file `pmute.work` (STORE client 11, 512 B, CRC-32) plus a 48-byte battery copy at `0x100fbdc0`; projects saved under 0.4 load no PATTERN mutes and keep their one-shots; a pattern copy no longer carries PATTERN mutes. The switch now drops a pending FUNC press once the panel row states show another key. The gate now seeds one-shots on steps 1-2.
- **Status:** fixed on main 2026-11-17 (emulator gate, 16 checks); the fix not yet flashed
- **Evidence:** `[hw]` (MKI over REMOTE) / `[emu]` {octabam-pmute-1118}
- **Rule:** A43, A77
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I147. Kit data overlapped the project archive: a module setting came back off after a power cycle (Modwerk)
- **Unit:** Digitakt II, OS 1.17, Modwerk base `e88273ed` with Chord Arp, Euclidean Scale and Track Names, 2026-11-17
- **Seen:** after Save Project and a power cycle Euclidean Scale kept its settings but Chord Arp's ARP came back OFF.
- **Cause:** core 1.1's kit data (191 B) ran into the last 48 B of the kit record that the base's project archive uses; saving a kit-data module zeroed the archive.
- **Fix:** base `8650bb8a` ends core's kit data before the archive (`KIT_ROOM` 146, one byte of the package); a check refuses an overlap.
- **Status:** fixed in 8650bb8a (KR17 passed on the same unit)
- **Evidence:** `[hw]` {modwerk-1118}
- **Rule:** A78
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I150. Powering off on a mod page broke the stock Euclidean page at the next boot (Euclidean Scale)
- **Unit:** Digitakt II, OS 1.17, Modwerk base with Euclidean Scale build P117, 2026-11-08
- **Seen:** after powering off on the SCF/RNN page, the next boot showed the stock Euclidean page without its page indicators; FUNC + AMP did nothing until the tester changed page and came back.
- **Cause:** at startup the stock Euclidean view's track-editor cache is unset; the module read the track from that cache.
- **Fix:** read the track through the stock Euclidean view's own accessor (S117); confirmed on the unit.
- **Status:** fixed in S117
- **Evidence:** `[hw]` {modwerk-1118}
- **Rule:** A40
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I151. A Rytm MKII mod read a 32-bit kit index as 16 bits and played the old sound (MIDI Engine)
- **Unit:** Analog Rytm MKII, OS 1.74, MIDI Engine build ME08 (flashed), early November 2026
- **Seen:** on a project whose current kit was not kit 1, a track switched to the MIDI machine kept playing its previous sound from pads and sequencer, and its AMP page showed stock values.
- **Cause:** the current kit's index is a 32-bit word; the build read its top half, which is 0, so it always used kit 1.
- **Fix:** read the whole word (ME09); reproduced and cleared in rytm-emu with kit 2 current.
- **Status:** fixed in ME09
- **Evidence:** `[hw]` {modwerk-rytm-1118}
- **Rule:** A51
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I154. A project load dropped installed effects from the next start's list (Modwerk Octatrack base up to 0.7.8)
- **Unit:** Octatrack (MKII units in the shared diagnostics), OS 1.40C, Modwerk bases up to 0.7.8, reported 2026-11-18
- **Seen:** at the next start Tape Echo, BBD Delay and Euclid were refused with NO ROOM FOR IT; the shared diagnostics of four units show it.
- **Cause:** a project load replaced the base's effect map; a module that stayed on its handle was left unnamed, so the save dropped its line. Found from the diagnostics and reproduced in a host test.
- **Fix:** base 0.7.9 names every module that stays on its handle and gives legacy projects the catalogue's handle.
- **Status:** fixed in 0.7.9, not yet tried on a unit; may explain I129
- **Evidence:** `[hw]` (diagnostics) / `[doc]` {modwerk-ot-1119}
- **Rule:** C9
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I155. Arr Rows drew its selection wrong and pasted as an insert (Modwerk draft, Octatrack MKI)
- **Unit:** Octatrack MKI, OS 1.40C, Arr Rows 0.1.0-experimental draft, 2026-11-17
- **Seen:** selection marks were drawn on the wrong rows; paste acted as an insert; once, MIDI to external synths stopped during a many-row copy while playing.
- **Cause:** the module read `0x460d16e8` as the first row shown (stock's is `0x460d1c64`), and judged CUE from its own key count, which a missed release left stuck. Found on the unit, diagnosed in the emulator. The MIDI stop is unexplained. An earlier build had marked the bank bit `0x100b14ce` instead of the arrangement bit `0x100b14d1`; the emulator caught that, the host test could not.
- **Fix:** the stock row variable, and CUE state read from stock.
- **Status:** two fixed; the MIDI stop open
- **Evidence:** `[hw]` {modwerk-ot-1119}
- **Rule:** A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I157. FM+ knobs moved the wrong parameters (dn2mk2 v0.59)
- **Unit:** Digitone II, OS 1.11, dn2mk2 v0.59 FMPLUS, testers' units, 2026-11-18
- **Seen:** on FM+ STAT, PAR and DYN the knobs moved other parameters and some read "unused"; the sound engine itself was fine.
- **Cause:** the page lookup skipped over BOUNCE's machine number, so STAT got PAR's page, PAR got DYN's and DYN read past the table. Found from the testers' reports; the 57-step gate had no check for which knob reaches which parameter.
- **Fix:** v0.60 finds each Monomachine machine's page by an explicit test; a new gate step `mnmpages` checks that each type's page record is its own.
- **Status:** fixed in v0.60 (gated; unit report pending)
- **Evidence:** `[hw]` {dn2mk2-v061}
- **Rule:** A8
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I158. A mis-encoded DSP multiply put garbage on the Octatrack's headphones (AERIA OS)
- **Unit:** Octatrack MKII, AERIA OS builds of 2026-11-13..15
- **Seen:** the headphones carried garbage: far too loud, never negative, the same level whatever the volume; main was fine. Earlier (2026-11-13) the owner heard "stereo, then right only, then left only, then cut out".
- **Cause (found by the author, read from the listing):** a multiply in the DSP engine had its operands in an order the assembler silently encodes as the signed-by-unsigned `mpysu`, so the sample was read as unsigned.
- **Fix:** operands reordered (builds of 2026-11-15, tested and flashed on the unit); the build script now refuses a DSP listing with an `mpysu`-encoded multiply or with unassembled lines.
- **Status:** fixed
- **Evidence:** `[hw]` {aeria-1120}
- **Rule:** A41
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I159. Headphones silent after flashing, though every RAM-boot bench test passed (AERIA OS)
- **Unit:** Octatrack MKII, AERIA OS releases of 2026-11-15/16, flashed; reported 2026-11-17
- **Seen:** no sound from the headphone output after flashing; main worked. The bench tests (RAM boot, 2026-11-15) had passed.
- **Cause (likely, read from code; not confirmed on the unit):** at a cold start core 0 started the ESAI and lined its output rings up with the converter before core 1 set the shared PLL; the PLL lock then stalled it, and the eight output words could sit shifted in the converter's slots (a shift of two puts main on the main jacks and unused words on the headphones). A RAM boot runs with the PLL already locked, so no bench test could see it. Also found: AERIA's MKII headphone left and right were swapped against stock.
- **Fix:** v0.9.5-beta (2026-11-19): the engine waits for a host flag raised 20 ms after core 1 and the PLL are set; the MKII phones order follows stock (right in word 4). Simulator-tested only; the simulator does not model the cold-start clock. The owner's check: cold power-on, sound on main and headphones; if still silent, listen on CUE (main there means the slots are still shifted).
- **Status:** open (fix not yet run on the unit)
- **Evidence:** `[hw]` (silence) / `[?]` (cause) {aeria-1120}
- **Rule:** A40
- **Fact:** [devices/octatrack.md](devices/octatrack.md#aeria-os-repair-facts-mkii-v095-beta-2026-11-19-aeria-1120)

### I160. A chord set just before a live note slid in from the old chord (model27 Chord Joy, Model:Cycles)
- **Unit:** Model:Cycles, OS 1.13, model27 release 0.76 full build, 2026-11-19
- **Seen:** some Chord Joy chords sounded broken: the note started on the chord held before and slid to the new one, worst on TRIG 6-8; also with keys played one after another. SHAPE turned by hand between trigs played cleanly.
- **Cause (read in OS 1.13):** the set reaches the voice target at once, but the audio side smooths every target per block, and CHORD reads the smoothed word. The OS snaps the smoothing state only when a note brings another sound, not for a live note on the track's own sound. A second bug found while reading: a degree pressed while another was held released the wrong root.
- **Fix:** after each SHAPE set, Chord Joy also writes the smoothing state of that parameter before the note's event; the sounding root is tracked. The fixed build passed on the unit the same day.
- **Status:** fixed (confirmed on the unit 2026-11-19)
- **Evidence:** `[hw]` {model27-1120}
- **Rule:** A80
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md#chord-joy-the-keyboard-slot-parameter-writes-and-smoothing-model27-notes87-modelcycles-os-113-2026-11-19-model27-1120)

### I161. Held chord notes were cut when a melody played over them (RIFT v0.10 and earlier, Digitone II)
- **Unit:** Digitone II, OS 1.11, RIFT v0.10 or earlier, user report on Discord, 2026-11-19
- **Seen:** on a busy FASCIA or SILT track a held chord lost notes when a melody played over it, or when one of its notes was struck again (voice mode REUSE).
- **Cause (read from code, shown in the emulator):** the frame guard renders voices in ORDER and leaves out, then steals, those that no longer fit. ORDER was newest first (inherited from dn2mk2 v0.29), so new and re-struck notes took the DSP time ahead of held ones.
- **Fix:** v0.11 marks a voice released at its note-off until its next note and orders all released voices after all held ones; an emulator test holds two notes under a melody with the clock squeezed to about three voices.
- **Status:** fix gated in the emulators 2026-11-19, no unit result yet; the REUSE case did not reproduce at the emulator's CPU level. More held notes than the DSP can run still lose the oldest.
- **Evidence:** `[?]` (user report; a unit is implied but not stated) / `[emu]` (fix) {dn2-rift-1120}
- **Rule:** A44
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I162. A drone kept sounding on a muted track (Modded Cycles Techno Edition ATMOS, before v1.9)
- **Unit:** Model:Cycles, OS 1.13, Techno Edition v1.8 or earlier, user report, 2026-11-19
- **Seen:** ATMOS with GATE on kept droning after its track was muted, even across a pattern change.
- **Cause (from the project's notes):** the Cycles' mute only holds back the sequencer's trigs; the GATE drone plays without a trig.
- **Fix:** v1.9 ends the drone on mute (FUNC + track or latched mute) and fades its reverb tail in about a second; unmute starts it again.
- **Status:** fixed in v1.9 (emulation only, not yet played on a unit)
- **Evidence:** `[?]` (user report; unit not stated) {mcte-1120}
- **Rule:** A81
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md)

### I163. An Octatrack froze while playing after the walk PROJ, DOWN, YES, YES (Modwerk base 0.7.9)
- **Unit:** Octatrack (model not stated), Modwerk base 0.7.9 (`c889442d`), eight modules (E-Verb, BBD Delay, LOFI2, Recorder Loop, DirectJmp Kyoti, Deja Vu, Temp Save, Repitch), field diagnostics 2026-11-18/19
- **Seen:** froze until a restart while playing at 58 % CPU; the last keys were PROJ, DOWN, YES, YES (four times), the last followed by PLAY. Earlier the same night it froze while stopped after the same walk. All eight modules came back at the next start.
- **Cause:** unknown. Freezes while stopped after this walk were read earlier as OS upgrades or USB DISK MODE seen by the freeze watch, but this one was playing and kept its base.
- **Fix:** none yet. Modwerk's test: on 0.7.9 with that set, play, repeat the walk and read the log.
- **Status:** open
- **Evidence:** `[hw]` (field record) {modwerk-1120}
- **Rule:** A29
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I164. A 303 voice lost its last step, popped and played a blip at Part and pattern changes (KYOTI BLACKPYRAMIDS_303)
- **Unit:** Octatrack MKI, OS 1.40C, octabam test images OCTABAM40-43 with KYOTI's blackpyramids-303 module, 2026-11-19
- **Seen:** OCTABAM40: a quiet pop at a cued Part switch into a Part whose 303 track had no trig on step 1, and the outgoing pattern's last-step note never sounded. OCTABAM41: a note tied to the end of a pattern was cut at a change to a pattern starting with ties. OCTABAM42: the first note after a load or into another Part was a blip or cut short.
- **Cause (shown in ot_emu after each report):** the voice asked the UI Part, which stock moves about 7 ticks before the switch, so the outgoing track changed a step early; a note's gate was worked out a step ahead from its own pattern only; and GATE was read from the live SETUP byte, which stock re-stages only at the track's trig (0 after a load).
- **Fix:** read stock's per-track Part pair, re-time a tied note from the next pattern's first steps, and read GATE from the scheduled pattern's Part. OCTABAM43 passed all checks; the same code is in KYOTI V1.8BC FINAL (2026-11-19). All three bugs were in the earlier FINAL too.
- **Status:** fixed (confirmed on the unit in the octabam form, not in V1.8BC itself)
- **Evidence:** `[hw]` {kyoti-1120}
- **Rule:** A82, A79
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18bc-a-dsp-voice-per-core-part-changes-paste-paths-os-140c-2026-111719-kyoti-1120)

### I165. A FLEX SRC page pasted onto a 303 track left a 303 with FLEX's numbers (KYOTI V1.8BC)
- **Unit:** Octatrack MKI, OS 1.40C, KYOTI V1.8BC first test image, 2026-11-18
- **Seen:** a FLEX track's SRC page pasted onto a 303 track left it a 303 with VOL 0 and the other FLEX values.
- **Cause (read from code):** the 303 machine is stored as FLEX in the machine bytes plus a signature in NEIGHBOR's bytes; a page paste writes one machine's twelve bytes and the machine byte, never the signature.
- **Fix:** hooks at the page copy core, the page paste and the page UNDO set the machine before stock writes. The rebuilt image behaved as intended on the unit, 2026-11-19.
- **Status:** fixed
- **Evidence:** `[hw]` {kyoti-1120}
- **Rule:** A77
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18bc-a-dsp-voice-per-core-part-changes-paste-paths-os-140c-2026-111719-kyoti-1120)

### I166. The sequencer stayed on step 1 after a 303 track was pasted into another Part's pattern (KYOTI V1.8BC, seen once)
- **Unit:** Octatrack MKI, OS 1.40C, KYOTI V1.8BC test image, 2026-11-18/19
- **Seen:** while setting up a test by TRACK COPY of a 303 track and TRACK PASTE onto T2 or T5 of a pattern on another Part, PLAY left step 1 lit and the sequencer did not advance.
- **Cause:** unknown; the author could not repeat it, and an ot_emu replay of the steps ran normally in every variant.
- **Fix:** none; if it comes back, record the steps and build a diagnostic image.
- **Status:** open (seen once)
- **Evidence:** `[hw]` {kyoti-1120}
- **Rule:** A29
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I167. Holding a step again deleted its trig (octabam LOCK EDIT)
- **Unit:** Octatrack MKI, OS 1.40C, a contributor's LOCK EDIT build, 2026-11-17
- **Seen:** with the audio editor opened by [TRIG] + [BANK], holding the same step again and releasing it removed the step's trig while the editor stayed open.
- **Cause (shown in the port's probe):** LOCK EDIT's hold hook kept the lock popup closed but returned before stock's hold handler cleared the key's hold bit; the release toggles the trig while that bit is set.
- **Fix:** the hook clears the bit itself and still keeps the popup closed; a gate holds again for 400 ms and checks that the step survives.
- **Status:** fixed (port gate; a unit re-run is not stated)
- **Evidence:** `[hw]` (symptom) / `[emu]` (cause) {octabam-1120}
- **Rule:** A50
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-sequencer-and-editor-modules-mkii-tooling-os-140c-2026-111720-octabam-1120)

### I168. Per-track trig modes were saved but gone after a power cycle (TRACK TRIG MODE)
- **Unit:** Octatrack MKI, OS 1.40C, test images ACCLOOP14 and ACCLOOP16 (Hteah's TRACK TRIG MODE), 2026-10-27/28
- **Seen:** ACCLOOP14: the modes survived SAVE but were gone after a power cycle. ACCLOOP16: leaving QUICK MUTE with FUNC + UP/DOWN wrote the mode it passed over onto the track (T1's SLICES became CHROMATIC).
- **Cause (read from code, shown in the emulator):** a power-up restores the project from battery RAM and never parses `project.work`, and the mode table was in DRAM. The QUICK MUTE exit treated the passing mode as a pick.
- **Fix:** the table moved to 8 bytes of battery RAM; a step out of TRACKS, QUICK MUTE or DELAY CONTROL never overwrites a track's mode. ACCLOOP15 passed switching, save, reload and a power cycle on the MKI.
- **Status:** fixed
- **Evidence:** `[hw]` {octabam-1120}
- **Rule:** A40
- **Fact:** [devices/octatrack.md](devices/octatrack.md#octabam-sequencer-and-editor-modules-mkii-tooling-os-140c-2026-111720-octabam-1120)

### I169. A project reload after a demand-loader phase left the DSP frame count stopped (octabam BUILD 05)
- **Unit:** Octatrack MKII, OS 1.40C, `octabam` and `octabam-verbs` BUILD 05 (`5b991c85`), 2026-11-18/19
- **Seen:** a project reload over USB (DISK MODE, copy, then the reload command) right after a scripted demand-loader phase left the DSP's frame count fixed, still so after 90 s and after 20 minutes; the ColdFire frame interrupt ran on and USB answered. Seen three times; never after a reload straight after boot, nor after the FX phases.
- **Cause:** unknown.
- **Fix:** none; workaround: boot the image again (REMOTE command 3) after each loader phase, which restarted the count without a power cycle.
- **Status:** open
- **Evidence:** `[hw]` {octabam-1120}
- **Rule:** A51 (related: I57, H22)
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I170. DARK REV picked on all eight tracks while MODULATION was loaded stopped the DSP (octabam BUILD 05)
- **Unit:** Octatrack MKII, OS 1.40C, `octabam` BUILD 05 (`5b991c85`), seeded fuzz soak (seed 3401), 2026-11-19/20
- **Seen:** the DSP frame count stopped 1,612 s into the run, at a START after a program change; panel, USB and the ColdFire frame interrupt went on. A commanded boot did not bring it back (boot screen, I110); a power cycle did. A 573 s replay stalled 2 of 2 times at the same START; with the last program change set to MODULATION, PLATE or SPRING REV instead of DARK REV it did not (one run each). Three diagnostic builds still stalled; in all, 6 of 9 runs stalled. ot_emu did not stall.
- **Cause (narrowed, not found):** it needs MODULATION loaded by the demand loader and live on FX2 when DARK REV, whose buffer reaches the demand effect's code, is picked on every track and START follows. An earlier overwrite of the frame guard's cells is not the cause.
- **Fix:** none
- **Later (2026-11-22):** narrowed on an MKII: with MODULATION loaded, 5 of 7 runs stalled with DARK REV on 8 tracks, 1 of 6 on 4 tracks, 0 of 2 on 1 track; with SPECTRUM loaded instead, 0 in 25 cycles; a stock-effects image without the demand loader, 0 in 60 STARTs. Two of the diagnostic builds were invalid because their window stubs sat inside DARK REV's buffer ([I188](#i188-window-stubs-placed-inside-dark-revs-buffer-stopped-the-dsp-octabam-test-images)). The ColdFire frame interrupt stops with the DSP (it does not go on, as written above). `[hw]` {octabam-1122}
- **Later (2026-11-23):** MODULATION counts as loaded while a track uses it and for 10 s after the last one stops. Suspected, not confirmed: DARK REV's inits (about 800 instructions each, four on core B) fall in the START frames beside the loaded block; the guard's cells and resume path are ruled out. v0.5 ships with the stall as a known fault. octabam-verbs (no stock DARK REV) and octabam-bus (no demand loader) cannot meet it this way, but neither was run against it. Open: whether CHARACTER, SHATTER or SIDECHAIN_COMPRESSOR do the same. `[hw]` / `[?]` {octabam-1123}
- **Status:** open
- **Evidence:** `[hw]` {octabam-1120}
- **Rule:** A56, A51 (related: I57, I110)
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I171. A third LFO page showed ERR labels when the bank held only modules (Synfact core 2.1.1, Syntakt)
- **Unit:** Syntakt, OS 1.42, Synfact core 2.1.1 with a bank of LFO3 only (one module, no machine), 2026-11-19
- **Seen:** the third LFO page appeared, but its parameters showed ERR labels, no ranges and no editor data.
- **Cause (read from code, reproduced in a host test):** the machine binder returned early for a bank with no machines and never set the registry active. The LFO3 page hooks still ran, but every provider lookup was skipped while the registry was inactive, so LFO3's ids fell through to stock's fallbacks. Every earlier test had at least one machine in the bank.
- **Fix:** core 2.1.2 drops the early return; an empty registry gets valid storage before it becomes active. A host regression and a Unicorn test with two module-only banks cover it, with the old core as a negative control.
- **Status:** fixed in 2.1.2 (the owner ran the old and the new core with the LFO3-only bank and confirmed the fix on the unit, 2026-11-19)
- **Evidence:** `[hw]` {synfact-1120}
- **Rule:** A83
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I172. A 303 chosen on a FLEX track was silent until switched away and back (KYOTI V1.8BC RC1)
- **Unit:** Octatrack MKI, OS 1.40C, KYOTI V1.8BC release candidate RC1 (`KY18BC RC1`), 2026-11-20
- **Seen:** a BLKPYRAMD (the 303 voice) chosen from the machine chooser often made no sound; switching to NEIGHBOR or THRU and back once or twice woke it.
- **Cause (shown in the emulator):** the 303 is stored as FLEX, so FLEX to BLKPYRAMD is FLEX to FLEX for stock, and stock's machine commit re-stages a track's live machine bytes only for PICKUP; otherwise they follow at the track's next trig after a real machine change, or at a Part apply. The voice played FLEX's live values (VOL = FLEX's TSTR byte: OFF gives silence). The project's checks seeded the bytes before PLAY, so none caught it. The same was in V1.8BC FINAL.
- **Fix:** after a machine commit on the current Part, call stock's seed when the stored machine is FLEX and set the track's Part pair to `0xff`, but not while the track still carries the old Part's note. `KY18BC RC2` passed every item on the unit, 2026-11-20.
- **Status:** fixed in RC2 (not yet promoted; waits for RC3)
- **Evidence:** `[hw]` {octatrack-kyoti-fw-1121}
- **Rule:** A85
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-release-candidates-spare-part-bytes-machine-switches-live-erase-on-midi-os-140c-2026-111920-octatrack-kyoti-fw-1121)

### I173. A fix for erased trigless locks covered audio tracks only (KYOTI ERASE_EMPTY_TRIGLESS_LOCKS)
- **Unit:** Octatrack MKI, OS 1.40C, KYOTI V1.8C and V1.8BC RC1, 2026-11-20
- **Seen:** on a MIDI track, erasing the last lock of a trigless lock left the step lit, as on stock (SB12); audio tracks were fixed.
- **Cause (read from code):** the LIVE erase calls a separate MIDI twin of the audio worker; the fix had only hooked the audio one. The emulator showed the bug on the FINAL and RC1 images once a MIDI case was added.
- **Fix:** one shared rule behind two hooks, one per worker (240 B). `KY18BC RC2` passed every MIDI and audio item on the unit, 2026-11-20; promoted the same day.
- **Status:** fixed
- **Evidence:** `[hw]` {octatrack-kyoti-fw-1121}
- **Rule:** A84
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-release-candidates-spare-part-bytes-machine-switches-live-erase-on-midi-os-140c-2026-111920-octatrack-kyoti-fw-1121)

### I174. A track that stopped being a 303 played a burst of its FLEX sample (KYOTI V1.8BC RC2)
- **Unit:** Octatrack MKI, OS 1.40C, `KY18BC RC2`, sequencer running, 2026-11-20
- **Seen:** switching a track with samples between BLKPYRAMD and FLEX, STATIC or NEIGHBOR played a bit of the FLEX or STATIC sample at the switch, often a very short fast loop.
- **Cause (shown in the emulator):** the 303 rides on a hidden stock FLEX voice. After the switch the frame's renderer for the track stays the 303's until the track's next trig, and it handed the hidden voice to stock's sample renderer, which played it for about 300 ms. Present since V1.8BC FINAL.
- **Fix:** while a track that was a 303 waits for its trig (also when it yields at a cued Part switch), render stock's idle record instead. RC3 carries it.
- **Status:** fixed in the emulator; RC3 not yet flashed
- **Evidence:** `[hw]` symptom, `[emu]` fix {octatrack-kyoti-fw-1121}
- **Rule:** A85
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-release-candidates-spare-part-bytes-machine-switches-live-erase-on-midi-os-140c-2026-111920-octatrack-kyoti-fw-1121)

### I175. QUAN read 5/4 instead of 1/1 on entering VARI; VARISPEED and the 303 shared spare bytes (KYOTI VARISPEED)
- **Unit:** Octatrack MKI, OS 1.40C, `KY18C VRG1` test image, 2026-11-19
- **Seen:** setting TSTR to VARI showed QUAN `5/4` instead of `1/1`, also on a track that seemed fresh.
- **Cause (emulator):** which meaning a parked byte had (PTCH or QUAN) lived only in RAM and was forgotten at every Part apply, so the next poll read the PTCH park as QUAN (PTCH +12 = `5/4`), and that value was then saved with the Part. Present in every FINAL VARISPEED, VARISPEED_EMUS and KYOTI. A follow-up probe found that VARISPEED parked PTCH in NEIGHBOR's spare bytes, which BLACKPYRAMIDS_303 also used: PTCH was lost or changed, a track that had been a 303 entered VARI at `5/4`, and a real 303's signature could break. A flag in bit 7 was also zeroed by stock's Part validator on every load.
- **Fix:** VRG3 keeps VARISPEED's state in four Part bytes nobody else uses, each below 128, with the meaning in the bytes; older projects are migrated at first sight, and VARISPEED never touches a 303 track. Confirmed on the unit in RC1 (VARI entry, QUAN across a save, a project from the old build, a 303 beside VARI), 2026-11-20; promoted.
- **Status:** fixed
- **Evidence:** `[hw]` {octatrack-kyoti-fw-1121}
- **Rule:** A77, A60
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-release-candidates-spare-part-bytes-machine-switches-live-erase-on-midi-os-140c-2026-111920-octatrack-kyoti-fw-1121)

### I176. A USB Audio Undo froze the panel and left the Octatrack off USB (Modwerk 0.7.11 candidates)
- **Unit:** Octatrack MKII, OS 1.40C, owner's unit, RAM-booted Modwerk 0.7.11 release candidates with USB Audio 0.3.0-experimental as a package, macOS host, 2026-11-20
- **Seen:** (1) on candidate `a2ae64eb`, Undo of a 16-channel POST LEVEL trial was acknowledged, then the unit left USB and its panel froze; the log kept a freeze (UI tick stopped at least 5 s while the frame interrupt ran, CPU 38 %), and the Mac's port reset failed to enable the port. (2) On the rebuilt `e0cbd717`, seven trials passed; the eighth (Track 8/Master) acknowledged its set and the unit vanished from USB before the host read the new descriptors, while the panel still answered keys. Both times a cold start with USB unplugged brought back the flashed base and all ten kept modules, checksum for checksum.
- **Cause:** (1) after a descriptor change only the UI tick could switch the USB controller back on (host test); (2) not proven: the base started its host deadline when it set the controller's run bit and never checked that the controller attached.
- **Fix:** a one-second fallback in the frame interrupt re-enables the controller; later the base checks attach, suspend and reset after three seconds and offers the descriptors once more if VBUS is valid and the port stayed disconnected. Release base 0.7.12 then passed eight trials (2 to 20 channels, Track 8/Master twice), Keep, a power cycle and a restore from the card.
- **Status:** fixed in 0.7.12 (the retry itself did not fire on the unit; it runs in a controller model only)
- **Evidence:** `[hw]` {modwerk-1121}
- **Rule:** A88, A55
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-bases-0710-0712-unused-module-cost-usb-audio-as-a-module-os-140c-2026-111921-modwerk-1121)

### I177. A paired browser tab rolled back USB Audio trials at the reconnect (Modwerk)
- **Unit:** Octatrack MKII, OS 1.40C, development base with the USB function slot, macOS host with a Modwerk page open in a browser, 2026-11-20
- **Seen:** four-channel USB Audio trials driven by a native test tool rolled back during the reconnect that follows the descriptor change, two of three times; once the unit came back with the audio configuration live but its module row gone.
- **Cause (by elimination):** the macOS USB log showed the browser opening the vendor interface about 200 ms before the test tool; the site's link undoes an unfinished trial when a paired page reconnects. The log does not show an Undo command from the browser.
- **Fix:** with the browser closed, Main + Cue passed three times in a row and all six layouts recorded; Modwerk's guide says to close paired tabs before a native USB Audio trial, and the site now leaves another session's USB Audio trial running when the unit reconnects.
- **Status:** worked around
- **Evidence:** `[hw]` {modwerk-1121}
- **Rule:** A88
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-bases-0710-0712-unused-module-cost-usb-audio-as-a-module-os-140c-2026-111921-modwerk-1121)

### I178. Analog BD stayed silent after a rolled-back trial until a power cycle (Modwerk base 0.7.9)
- **Unit:** Octatrack (field report #1736), Modwerk base 0.7.9; reproduced on an MKII with a development copy of the beta base, 2026-11-19
- **Seen:** a trial that took out Analog BD (or Sidechain, or Output Matrix) to make room for another module was rolled back; Analog BD was listed again and could be picked but made no sound until a power cycle.
- **Cause:** the base released the module's DSP engine for good while the trial was still open.
- **Fix:** base 0.7.10 keeps the module ready to come back until the trial is kept or rolled back, while still giving its DSP room to the trial. Release candidate on an MKII: the kick measured -19.3 dBFS on T4 before and after a 60 s trial that removed Analog BD and added Vibrato.
- **Status:** fixed in 0.7.10
- **Evidence:** `[hw]` {modwerk-1121}
- **Rule:** A54
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-bases-0710-0712-unused-module-cost-usb-audio-as-a-module-os-140c-2026-111921-modwerk-1121)

### I179. A VECTOR trial's Undo left the loader in recovery until a power cycle (Modwerk 0.7.11 development image)
- **Unit:** Octatrack MKII, OS 1.40C, 0.7.11 development image `fac15232`, VECTOR 0.3.2 alone in a 30 s stopped whole-set trial, 2026-11-20
- **Seen:** the rollback left the loader in recovery; a fresh connection and `recover` failed too. After the owner's power cycle the flashed 0.7.9 base and its ten modules were intact.
- **Cause (partly found):** before removing a departing track machine the loader checked its stock menu definitions as they read with the machine still patched in, so it saw the machine as still in use. The log did not name the reference that blocked.
- **Fix:** the loader now judges a departing machine's menu entries as they will read after its stock handlers return, and still checks cached callbacks and every Part live. Five later VECTOR trials (stopped and after playback, three builds, the release candidate included) rolled back normally.
- **Status:** fixed in the 0.7.11 release
- **Evidence:** `[hw]` {modwerk-1121}
- **Rule:** A54
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-bases-0710-0712-unused-module-cost-usb-audio-as-a-module-os-140c-2026-111921-modwerk-1121)

### I180. A project load after a card restore stalled the DSP (Modwerk 0.7.9 development base)
- **Unit:** Octatrack MKII, OS 1.40C, 0.7.9 Tracks Post development base `c6345a32`, six modules (Tape Echo, Euclid, LOFI2, Sidechain Compressor, POLY8, Slow LFO) restored from the card, 2026-11-19
- **Seen:** the first load from one project to another (stock SPRING REV on T1 FX2 and SPATIALIZER on T5 FX1 in both) stalled the DSP twice before PLAY. The same load passed once without modules and four times with the same modules sent over USB.
- **Cause (narrowed):** the base's DSP manager began changing which effects the DSP held while the bank and Parts were still loading: at the stall core 0 had bound SPATIALIZER and the manager waited for core 1's SPRING REV bind, with the incoming effect map not yet published. Why the frame edge went missing is open.
- **Fix:** a gate that continues open requests but starts no new plan until the whole effect map is loaded (base 0.7.11). On 0.7.11 two restoring boots loaded with no extra DSP packet or commit; shipped 0.7.10 did not stall in two tries either but made the same residency changes the stall trace had shown.
- **Status:** fixed in 0.7.11; the stall itself did not reproduce on 0.7.10
- **Evidence:** `[hw]` {modwerk-1121}
- **Rule:** A89, A56
- **Fact:** [devices/octatrack.md](devices/octatrack.md#modwerk-findings-bases-0710-0712-unused-module-cost-usb-audio-as-a-module-os-140c-2026-111921-modwerk-1121)

### I181. The digikit MODULES page froze a Syntakt: it used the Digitakt II key ids
- **Unit:** Syntakt, OS 1.42, digikit `device` image, 2026-11-20
- **Seen:** DIGIKIT > MODULES showed an empty list ("NO STORE") and afterwards no key worked, not even NO; the unit needed a power cycle.
- **Cause (reproduced in the emulator, also on a blank card):** the list page replaces the stock key handler and compared key ids with the Digitakt II values (YES 10, NO 12, RIGHT 15). An empty list passes only NO to the stock handler. On the Syntakt the firmware key index 12 is YES and NO is 13 (decoder table `0x401d7a48`), so NO was swallowed with every other key.
- **Fix:** key ids and flag bits per device in the device file (Syntakt YES 12, NO 13, RIGHT 17, LEVEL push 48); an empty list now swallows only YES and RIGHT and passes every other key to the stock handler; the build refuses a device file without the key table. A test compares the ids with the stock decoder table.
- **Status:** fixed; the fix ran in the emulator, a flash of the fixed build is not reported as the cause check
- **Evidence:** `[hw]` (symptom) / `[emu]` (cause) {digikit-1121}
- **Rule:** A86
- **Fact:** [devices/syntakt.md](devices/syntakt.md#digikit-on-a-syntakt-unit-section-7-packed-bootstrap-stage-key-ids-card-capacity-write-guard-os-142-2026-111921-digikit-1121)

### I182. The first digikit store on a Syntakt lay beyond the unit's card
- **Unit:** Syntakt, OS 1.42, first digikit `device` build, 2026-11-19/20
- **Seen:** the runtime reported `CARD_TOO_SMALL` and had no store; nothing was written (the check refuses every write before a sector is touched).
- **Cause:** the store reused the Digitone II range (sectors `0x800000-0x2e1a000`, made for the 32 GB part the emulators model), but the unit's eMMC is the 1.82 GiB part (`0x3a4000` sectors, the smallest the firmware's part table lists; the table is not enforced at boot).
- **Fix:** a fixed 512 MiB store at `0x200000-0x300000`, above every stock sector (below `0x180000`) and below the smallest listed capacity, checked at boot against the driver's capacity getter; INFO and HEALTH show the capacity. On the unit the new store took uploads, listing and removal, and a content module ran from it.
- **Status:** fixed (confirmed on the unit)
- **Evidence:** `[hw]` {digikit-1121}
- **Rule:** A87
- **Fact:** [devices/syntakt.md](devices/syntakt.md#digikit-on-a-syntakt-unit-section-7-packed-bootstrap-stage-key-ids-card-capacity-write-guard-os-142-2026-111921-digikit-1121)

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

### I84. Uninitialised shared-window memory crashed DSP core 1 on a cold boot; the emulator starts it at zero
- **Unit:** Octatrack MKII, AERIA OS bring-up builds, 2026-11-11
- **Seen:** after a cold boot core 1 sent one report and crashed; a crashed core 1 then blocked a DSP reload over USB until a power cycle.
- **Cause (found on the unit):** core 1's slot table in the shared window held random values at power-on; the emulator zeroes that memory.
- **Fix:** core 1 clears its table before it starts.
- **Status:** fixed.
- **Evidence:** `[hw]` {aeria-log}
- **Rule:** C10
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I98. MIDI hits on a software voice were silent on a Rytm; the emulator could not show it
- **Unit:** Analog Rytm MKII, OS 1.74 (BD ANALOG development builds), 2026-11-05
- **Seen:** 39 of 40 MIDI hits were silent.
- **Cause (found on the unit, then from stock's code):** a MIDI trig sets the voice timer to a start tick of 0-15 or later, but the base took a hit only when it read 0; rytm-emu does not trigger track 1 from pads or MIDI, so only sequencer trigs had been tested.
- **Fix:** the voice waits for the scheduled tick, as stock BD CLASSIC does (`0x40110a06`).
- **Status:** fixed.
- **Evidence:** `[hw]` / `[emu]` {modwerk-rytm-analogbd}
- **Rule:** C10
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I106. A UI pointer the emulator filled stayed 0 on a Digitakt II
- **Unit:** Digitakt II, OS 1.17 (Modwerk's Track Names, first build, the author's unit), 2026-11-13
- **Seen:** the module loaded but never recognised the Internal Mixer, so no track names were drawn; in digikit's emulator it worked.
- **Cause (shown on the unit):** the module found the mixer through the view controller's page-set pointer at `+0x9c`, which was non-zero in the emulator and 0 on the unit.
- **Fix:** 0.1.3 recognises the mixer from the frame the OS has just drawn; about 2 h on the unit with core 1.0.
- **Status:** fixed.
- **Evidence:** `[hw]` {modwerk-dt2-tracknames}
- **Rule:** C10
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I112. The compiler merged two stores and broke a step move (trig-seedr, emulator)
- **Unit:** none (analog-emu), trig-seedr 0.4.0 for Analog Rytm MKII OS 1.74, 2026-11-15
- **Seen:** a moved step lost its note and velocity and corrupted the step before it.
- **Cause (found in the emulator and the compiler output):** Homebrew m68k-elf-gcc 16.2 at -O2 miscompiled a struct copy followed by stores to its fields; with store merging one 4-byte store landed 6 bytes early.
- **Fix:** from 0.4.1 every ColdFire build (the mod, core-ar2, the device checks) uses `-fno-store-merging`. 0.4.0 had passed every emulator check, so the same fault may sit in code the checks do not reach.
- **Status:** fixed in 0.4.1; not run on a unit.
- **Evidence:** `[emu]` {trig-seedr-1116}
- **Rule:** A41
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#step-records-locks-and-the-stock-write-routines-trig-seedr-mkii-os-174-analog-emu-only-2026-11-14-trig-seedr-notes)

### I117. Two ColdFire instruction forms where GCC and ot_emu disagree (Octatrack, emulator)
- **Unit:** none (octabam's ot_emu), TELOS 0.1 for Octatrack OS 1.40C, 2026-11-14
- **Seen:** the boot linker misbehaved in the emulator until two code patterns were removed.
- **Cause (found in the emulator and the compiler output):** for `move.b (a0)+,(0,a0,a1)` GCC assumes the destination uses the old a0 and ot_emu the new one; for a byte push to `-(sp)` GCC assumes SP moves by 1 and ot_emu by 2.
- **Fix:** `dl_memcpy` kept out of line and `-fno-ipa-sra`, so neither form is in the build.
- **Status:** avoided; which reading the ColdFire takes is not checked on a unit (H29).
- **Evidence:** `[emu]` {telos-ot-1117}
- **Rule:** A42
- **Fact:** [devices/octatrack.md](devices/octatrack.md#telos-and-dspload-ot-boot-order-card-mount-run-time-dsp-code-os-140c-2026-11-1416-telos-ot-1117-elekloader-1117)

### I120. A landing on the boundary tick was exact in the emulator and sometimes a step off on the unit
- **Unit:** Octatrack MKI, OS 1.40C (KYOTI with Clyps, CL25), 2026-11-12
- **Seen:** with DIRECT JUMP on, a loaded sequence now and then came in one step off and fell into phase at the next step.
- **Cause (from the report and the code; the emulator's exact clock never shows it):** CL25 landed on the boundary tick and purged the old boundary event only if its fire time was at or after the sample clock; on the unit that clock runs in audio frames, so the comparison flipped by a frame and the old step stayed. Tick-level oracles in the emulator had passed.
- **Fix:** CL26 lands a tick before the boundary (ahead 2) and purges a full tick ahead (measured margin: one tick in every purge); RELOAD_FROM_PROJECT and DIRECT JUMP V7.1 took the same rule. CL29 "timing correct" on the unit.
- **Status:** fixed.
- **Evidence:** `[hw]` {kyoti-1117}
- **Rule:** A70
- **Fact:** [devices/octatrack.md](devices/octatrack.md#kyoti-v18-clyps-and-direct-jump-v73-os-140c-2026-11-1316-kyoti-1117-kyoti-clyps-scope)

### I126. Two lock lanes on one parameter lost one lane's locks (trig-seedr, emulator)
- **Unit:** none (analog-emu), trig-seedr 0.5 for Analog Rytm MKII OS 1.74, found 2026-11-16 by the host fuzzer and the emulator sample
- **Seen:** a recipe with lane 1 at 100 % on the sample slot and lane 2 left on the sample slot too: the emulated Rytm stored lane 2's value (the original locks) and lane 1's new locks were lost, with no error; the host reference showed a lock on every trig.
- **Cause (shown in the emulator):** the Rytm keeps one lock per parameter and step; the second write replaced the first.
- **Fix:** 0.6.0 refuses such a recipe (SETTING OUT OF RANGE, nothing written) and LOCK's PARM skips the other lane's parameter; host test `test_found_lanes`.
- **Status:** fixed before any unit ran it.
- **Evidence:** `[emu]` {trig-seedr-1117}
- **Rule:** A71
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#trig-seedr-05-07-grid-recording-lock-lanes-redraw-cost-and-first-unit-passes-mkii-os-174-2026-11-16-trig-seedr-1117)

### I128. Idle CPU cost overstated five times: an instruction budget read as one second (trig-seedr, analog-emu)
- **Unit:** none (analog-emu), trig-seedr 0.4-0.5 for Analog Rytm MKII OS 1.74, found 2026-11-16 (status M2.3)
- **Seen:** the screen's idle cost was reported as 7.8 % and 9 % of the CPU and planned around.
- **Cause (found in the emulator's options):** `dtboot --instr 1000M` at the default `--ips 200M` runs 5 emulated seconds; the count was divided by one second.
- **Fix:** measured again per emulated second: 1.9 %, then 0.25 % after redrawing only on change; F10's status file carries a correction.
- **Status:** corrected.
- **Evidence:** `[emu]` {trig-seedr-1117}
- **Rule:** C10
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#trig-seedr-05-07-grid-recording-lock-lanes-redraw-cost-and-first-unit-passes-mkii-os-174-2026-11-16-trig-seedr-1117)

### I142. A function without a return value passed the emulator by chance (trig-seedr 0.7.0)
- **Unit:** Analog Rytm MKII OS 1.74 in analog-emu, trig-seedr 0.7.0, found 2026-11-17
- **Seen:** no failure seen; a code review for the manual found that `take()` is declared `int` but falls off its end on success, and YOLO tests its result. A successful roll could be treated as failed and the old recipe put back, depending on a leftover register value. Every emulator test passed.
- **Cause:** undefined return value in C (m68k-elf-gcc gives no error by default); the register happened to hold a non-zero value in the emulator runs.
- **Fix:** `return 1;` added; the mod builds with `-Werror=return-type`.
- **Status:** fixed in 0.7.1 (0.7.1 passed on a unit, 2026-11-17).
- **Evidence:** `[emu]` {trig-seedr-1118}
- **Rule:** A74
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I143. Gearmulator's DSP56300 JIT misexecuted `cmpm` and X/Y half writes (gearmulator-md-mm)
- **Unit:** Machinedrum / Monomachine emulator (gearmulator-md-mm before mdmm-v0.1.0-alpha.15; the same JIT is upstream Gearmulator's), 2026-11-10 to 2026-11-17
- **Seen:** two wrong results inside one JIT block: after `cmpm a,b` or `cmpm b,a` the source accumulator held its magnitude, so later instructions in the block read |S1|; and after a write to x0/x1 (or y0/y1) followed by a read of the whole 48-bit x (or y) in the same block, the halves were never stored back, so the next block read a stale x.
- **Cause:** JIT code generation bugs (the interpreter was right; the `cmpm` fix came from upstream dsp56300).
- **Fix:** dsp56300 submodule moved to the fixed release branch; an interpreter-versus-JIT test for X/Y half writes was added.
- **Status:** fixed in mdmm-v0.1.0-alpha.15.
- **Evidence:** `[emu]` {gearmulator-1118}
- **Rule:** C4 (re-run emulator checks made on an older pin, e.g. machinedrum-kit pins a gearmulator-md-mm commit, and test DSP code under the interpreter too)
- **Fact:** [devices/machinedrum-monomachine.md](devices/machinedrum-monomachine.md)

### I153. Live-recorded beats went into pattern A01: every emulator test had run on A01 (Drum Mode 0.8/0.8.1)
- **Unit:** Digitone MKI, OS 1.44, Drum Mode 0.8 and 0.8.1 on elekloader, 2026-11-17/18
- **Seen:** the pads, notes, pages and mutes worked, but beats recorded live on a Drum Mode track never played back; in the emulator they did.
- **Cause:** the project holds one set of track edit objects per pattern (128 sets `0x38c` apart); 0.8 always wrote through A01's set, 0.8.1 through A01's or A02's, so on H02 the beats went into A01. Found with three debug builds that printed the playback path's view on the unit's screen, then by hooking the stock trig setter in digiemu on the same pattern.
- **Fix:** 0.8.2 uses the active pattern's own set (checked by its data pointer, all 128 searched otherwise); a test now records on H02.
- **Status:** fixed in 0.8.2 (confirmed on the unit 2026-11-18)
- **Evidence:** `[hw]` {drum-mode-1119}
- **Rule:** A79
- **Fact:** [devices/digitone.md](devices/digitone.md)

### I183. A full digikit image hung a Syntakt at the logo: the bootstrap's unpack overran its stream
- **Unit:** Syntakt, OS 1.42, digikit full `device` set (runtime, menu, HEALTH, input, section 7 packer), 2026-11-19
- **Seen:** after the flash the unit restarted and stayed at the Elektron logo on every power cycle. The smaller `device-peer` image (the section 7 packer only) booted. Every emulator boot of the same image had passed.
- **Cause (read from the bootstrap, reproduced by running its own depacker on the emulator core):** the Syntakt bootstrap stages packed MAIN at `0x40200000`, not at the `0x40400000` of the Digitakt II and Digitone II, and unpacks it in place with no bound. The full image's stream had an in-place margin of -42,486 bytes at that stage (stock +96,356), so the output overwrote unread stream bytes and the decoder ran away before MAIN started. The emulator installs MAIN directly and never runs that unpack; the device file had copied the Digitakt II stage value; the margin was checked only for the repacked section 7.
- **Fix:** the stage is per-device data read from section 2; patchkit writes the stream's last tokens as literals until the margin is at least 8 KiB and refuses an image below that in `verify`, `preflight` and `flash`, printing the margin. The repaired full image boots on the unit. Finding 159 (2026-11-23, static) adds that the 8 KiB floor is a safety default, not measured, and that the stored MAIN cannot go below unpacked MAIN - 2,096,128 B + floor whatever the packer does {digikit-1123}.
- **Status:** fixed (confirmed on the unit). How the hung unit was brought back is not stated; digikit's documented path is the startup menu (FUNC at power-on, TRIG 4, stock file over DIN).
- **Evidence:** `[hw]` {digikit-1121} {digikit-1123}
- **Rule:** A14
- **Fact:** [devices/syntakt.md](devices/syntakt.md#digikit-on-a-syntakt-unit-section-7-packed-bootstrap-stage-key-ids-card-capacity-write-guard-os-142-2026-111921-digikit-1121)

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

### I100. A Windows PC could not open the Octatrack's vendor interface
- **Unit:** Octatrack MKII with the Modwerk base and a Windows 11 PC, 2026-11-12/13, after member reports
- **Seen:** with `DeviceInterfaceGUIDs` missing from the interface's registry key the USB bridge could not open the unit; a replug did not help.
- **Cause (found on the PC):** Windows writes that value only at an interface's first setup; why it was missing on members' PCs is unknown.
- **Fix:** the base reports `bcdDevice` 0x0101, which made Windows write the value again.
- **Status:** fixed by hand on one PC; not confirmed on an affected member's PC.
- **Evidence:** `[hw]` {modwerk-win-usb}
- **Rule:** A63
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I102. A repacked stock image ran on an Analog Rytm MKI, and stock came back over USB and DIN
- **Unit:** Analog Rytm MKI, OS 1.74 (elekloader's new ELE2 writer), reported 2026-11-13
- **Seen:** stock 1.74 rebuilt by the writer (version field EL01) was flashed with Transfer, booted and played; the stock file then restored the unit over USB and, from the startup menu, over DIN.
- **Cause (planned test):** a null repack before any mod, the first check of a new file writer.
- **Fix:** none needed.
- **Status:** passed.
- **Evidence:** `[hw]` {elekloader-ar1}
- **Rule:** A2, A6
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I148. OS UPGRADE from the card installed an older base .bin (Modwerk)
- **Unit:** Octatrack (MKI/MKII not stated), OS 1.40C, Modwerk base install from the CF card, reported up to 2026-11-17
- **Seen:** with an older Modwerk base `.bin` still on the card, OS UPGRADE installed that one; the unit came back on the base it ran before and the guide waited with no hint.
- **Cause:** stock's choice between several `.bin` files at the card's top level; the rule is unknown.
- **Fix:** the guide says to remove every other `.bin` and to rerun if the old base comes back.
- **Status:** workaround documented; stock behaviour open
- **Evidence:** `[hw]` (user reports) {modwerk-1118}
- **Rule:** A6
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I149. A trial rollback timed out halfway and left the unit in recovery (Modwerk)
- **Unit:** Octatrack MKII, OS 1.40C, Modwerk base, 24-module timed trial, about 2026-11-17
- **Seen:** the rollback stopped at the tool's 3 s limit with 16 of 24 modules undone; the unit waited in recovery until `device recover`.
- **Cause:** the base undoes a set one module at a time; 24 modules need more than 3 s.
- **Fix:** the tool waits up to 20 s.
- **Status:** fixed (tooling)
- **Evidence:** `[hw]` {modwerk-1118}
- **Rule:** A54
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I152. A Transfer install stalled at "Waiting for SysEx" on a Rytm MKII
- **Unit:** Analog Rytm MKII, OS 1.74 (running MIDI Engine ME17), installing MER1 with Transfer DROP, 2026-11-17
- **Seen:** the first DROP stalled at the startup screen's "Waiting for SysEx"; after a power cycle ME17 still booted; a second DROP installed MER1.
- **Cause:** unknown.
- **Fix:** power cycle and send again.
- **Status:** open (once)
- **Evidence:** `[hw]` {modwerk-rytm-1118}
- **Rule:** A23
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I156. The first USB OS send to a Model:Samples stalls at 0-1 % (Modded-Cycles protocol flashers)
- **Unit:** Model:Samples, OS update over USB with model27's flasher and other flashers of the same protocol, a tester's report, 2026-11-18
- **Seen:** the first send stalls at 0-1 % with every such flasher; the second send always works.
- **Cause:** unknown; the guess is that the first reply after the MIDI ports are reopened is lost (macOS/Chrome), or that the unit answers slowly on its first start.
- **Fix:** model27 0.73 waits 2 s, reopens the ports, identifies the unit again and resends the whole file once (nothing is written before the user confirms on the unit).
- **Status:** open; the retry passed a simulated-machine test only
- **Evidence:** `[hw]` symptom, `[doc]` fix {model27-1119}
- **Rule:** A11
- **Fact:** [devices/model-cycles-samples.md](devices/model-cycles-samples.md)

### I184. A memory canary held with all 64 sample slots loaded, then trig-seedr passed its first checks (Syntakt)
- **Unit:** Syntakt, OS 1.42, trig-seedr 0.7.1-labelled build (same code as 0.8.0) on a minimal elekloader hook-bus core, one unit, 2026-11-19
- **Seen:** in order: the STARTUP menu (FUNC at power-on) with TRIG 4 = OS UPGRADE was checked on stock; the stock file round-tripped by elektron-firmware-tool (`-r`, byte-identical) flashed and booted as stock; a canary build kept a pattern over `0x478b0000-0x47bf0000` intact (OK and a growing pass count) through a session with all 64 sample slots loaded, project load and save and a power cycle; then trig-seedr passed its 15 first checks, including an applied and a pending take kept across a power off.
- **Cause (planned test):** the project's staged first-flash plan: way back first, a null repack, a memory canary, then the mod.
- **Fix:** none needed.
- **Status:** passed on one unit; other units not yet.
- **Evidence:** `[hw]` {trig-seedr-1121}
- **Rule:** A11, A43
- **Fact:** [devices/syntakt.md](devices/syntakt.md)

### I185. A FLEX take level built in by ear was 12 dB too loud (dn2mk2 v0.63-v0.64)
- **Unit:** Digitone II, OS 1.11, dn2mk2 v0.63 (and v0.64), a tester's unit, measured about 2026-11-20
- **Seen:** a FLEX take of a single track played about 12 dB louder than its source at GAIN 0; with every level at 127, recorded through a DAW over USB, a take matched its source at GAIN -12.
- **Cause (from the project's notes):** v0.63 built +24 dB into such takes because GAIN +24 had matched a take to its source by ear on the owner's unit; that number had been judged on another firmware, not on the mod build that shipped it.
- **Fix:** v0.65 builds in +12 dB (`TRK_HW_DB` 12); users who set FLEX tracks to GAIN -12 are told to set them back to 0. RIFT v0.13-v0.14 ported the +24 and still ship it.
- **Status:** fixed in dn2mk2 v0.65 (gated in the emulator; the tester's measurement is the hardware evidence). Open in RIFT. MAIN and IN takes got their own +12 dB in v0.66, which the owner thinks may still be short; not yet measured.
- **Later (2026-11-22):** disputed. dn2mk2 v0.68 goes back to +24 dB for track takes and also builds +24 dB into MAIN and IN takes, after the owner measured on v0.67 (pattern volume 100, compressor off) that +12 needed 12 dB more. That contradicts the tester's measurement (all levels 127, recorded through a DAW over USB); RIFT v0.13-v0.17 ship +24 dB for track takes, the same as dn2mk2 again, and +12 dB for MAIN and IN. See [O48](CONFLICTS.md). `[hw]` (both measurements) {dn2mk2-1122} {dn2-rift-1122}
- **Evidence:** `[hw]` (tester's measurement) {dn2mk2-1121}
- **Rule:** G8
- **Fact:** [devices/digitone-2-internals.md](devices/digitone-2-internals.md)

### I186. A user machine that loaded samples between hits reset a Sidecar Pi 5 (WAVESURFER 1.0.0)
- **Unit:** Analog Rytm MKII with the Sidecar expander on a Raspberry Pi 5, Sidecar firmware 0.5.1, community machine WAVESURFER 1.0.0 (a user's setup), reported by 2026-11-21
- **Seen:** frequent resets of the Sidecar, with USB drops, when an LFO moved WAVESURFER's sample, bank, first-row or bank-size knobs; long or large samples (over about 12 MB or 60 s) went with USB drops and resets too.
- **Cause (from the package's README):** in 1.0.0 every knob change asked the Sidecar for the selected sample, so a modulated knob made it load several samples a second from the SD card; long, heavy card reads are the common factor. The Sidecar side of the reset is not explained.
- **Fix:** WAVESURFER 1.0.1 asks for a sample only when a trig comes in (or for the one playing); the README asks for samples under 12 MB and 60 s.
- **Status:** fixed in the package (1.0.1); the Sidecar's own behaviour under heavy card reads is open.
- **Evidence:** `[hw]` (user report in the package README) {sidecar-machines-1122}
- **Rule:** A90
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md)

### I187. Panel froze after a Grain trial, and a later RAM boot hung (Modwerk, Octatrack MKII)
- **Unit:** Octatrack MKII, OS 1.40C, Modwerk base 0.7.11 development twin, a Grain draft (two voices) on track 5, no CF card, MIDI and 20-channel USB capture, 2026-11-21
- **Seen:** after 61 s of play and STOP the audio frames kept running but the UI tick stayed stuck for at least 27 s; the machine chooser never confirmed Flex, and the USB rollback and RAM restart could not finish. A power cycle restored the production base. Separately, a RAM boot back to the shipping base after the Grain timing runs (no module live) hung on the startup animation with no controls and no USB, and the log kept no crash or stall record; a power cycle with the card booted the flashed base.
- **Cause:** open. The trace shows no faulting UI address; a redundant per-track source rewrite on the next UI tick was removed as a suspect, but the emulator did not reproduce the freeze. A stock-Flex control run did not freeze.
- **Fix:** none yet.
- **Status:** open
- **Evidence:** `[hw]` {modwerk-1122}
- **Rule:** A29
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I188. Window stubs placed inside DARK REV's buffer stopped the DSP (octabam test images)
- **Unit:** Octatrack MKII, OS 1.40C, octabam diagnostic images (P1, D4), 2026-11-21/22
- **Seen:** image P1 booted with the DSP frame count at 0 for 90 s, twice; D4 stalled 6.6 s into its run with no DARK REV picked.
- **Cause (found from the build map):** SIDECHAIN_COMPRESSOR's hook stubs had grown past `0x33fff` into the FX2 slot at `0x34000`, which DARK REV fills up to slot + `0x3da2`. The window believed free, `0x33da3..0x37eff`, is really two gaps: `0x33da3..0x33fff` and `0x37da3..0x37eff`. The results of those diagnostic builds for I170 were discarded.
- **Fix:** octabam's build refuses a window record inside the extent of a guarded reverb's slot.
- **Status:** fixed (build gate)
- **Evidence:** `[hw]` {octabam-1122}
- **Rule:** D11
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I189. v0.5 release check: 3 of 32 program changes were not applied (octabam)
- **Unit:** Octatrack MKII, OS 1.40C, octabam v0.5 images `octabam`, `octabam-verbs` and `octabam-bus` built from `main` at `382a478b` plus the release commit, booted by REMIX SWITCH from the flashed image (none flashed), 2026-11-22
- **Seen:** the 32-program-change soak left 3 of 32 changes unapplied on `octabam`, 0 on `octabam-bus`, and 0 on `octabam-verbs`, which still logged 32 bad DSP records (one per transition, when the dearest layouts loaded). The meter, transport, USB and DSP-watch checks passed on all three. The long mixed soak did not complete on any image.
- **Cause:** not given. v0.4 had applied 32 of 32 in the same soak (2026-11-08).
- **Fix:** none. v0.5 was tagged with this result, with the DARK REV stall (I170) as a known fault, and with module changes made after the tested commit that never ran on a unit.
- **Status:** open
- **Evidence:** `[hw]` {octabam-1123}
- **Rule:** A51 (related: A18, I170)
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I190. A SMEAR note silenced the whole Digitone II until a reboot (RIFT v0.16/v0.17)
- **Unit:** Digitone II, OS 1.11, RIFT v0.16 and v0.17 (gated in the emulators), the owner's and a tester's units, 2026-11-22
- **Seen:** a SMEAR note gave a short burst, then the whole output went silent, every other machine with it, until a power cycle; projects were unharmed. PLATEAU (v0.17) also did nothing while other tracks played. Separately, the first start after a flash could leave ORGAN silent until one more power cycle.
- **Cause (author's analysis):** SMEAR's vocoder (VOC) jobs cost 200,000-260,000 cycles a block on a cost model of the unit (instructions plus memory waits, fitted to the idle frame's measured 416k of 667k cycles), which runs the DSP past its frame. The frame guard expected each voice to cost what its last block cost, and VOC's light blocks kept that figure low, so a heavy block was let through. PLATEAU was dropped for the rest of a note whenever the guard was short of time.
- **Fix:** v0.18 (2026-11-22) turns VOC off, makes the guard expect a voice's peak cost, adds an output guard that replaces any block that is not finite or runs away with silence and restarts that voice, and skips PLATEAU only for a block with no room. The release gate now prices every machine's worst block on the unit's cost model (`rcost`) and checks non-finite blocks (`sanitize`). The fix itself is gated in the emulators only.
- **Status:** fixed in v0.18 (not yet confirmed on a unit)
- **Evidence:** `[hw]` (owner and tester) {dn2-rift-1123}
- **Rule:** A35
- **Fact:** [devices/digitone-2.md](devices/digitone-2.md)

### I191. The UI stopped during playback with six modules installed (Modwerk base 0.7.13)
- **Unit:** Octatrack (model not stated), OS 1.40C, released Modwerk base 0.7.13, six modules including Tape Echo and E-Verb, a tester's field diagnostics, 2026-11-22
- **Seen:** the UI tick stopped during playback while the audio frame interrupt kept running long enough to record the freeze; the CPU meter read about 78 %. The incident and its installed set belong to the same boot. At the next start all six modules were restored. An earlier boot on base 0.7.12 with only Tape Echo and E-Verb installed showed the same symptom.
- **Cause:** unknown. The record gives the set and the transport state but not the last action or where the UI stopped making progress; the overlap in installed modules does not show that either effect is responsible.
- **Fix:** none yet; Modwerk needs the action and the point where the UI stopped in the next record.
- **Status:** open
- **Evidence:** `[hw]` (field record) {modwerk-1123}
- **Rule:** A29 (a field record with the set and transport state alone did not find the cause; compare I163, I187)
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I192. A small USB staging transfer went unconfirmed, and a USB Audio trial rolled back at the reconnect (Modwerk, Windows)
- **Unit:** Octatrack (model not stated), OS 1.40C, Modwerk bases 0.7.12 and 0.7.13, a tester's unit on a Windows host with the Modwerk site open in a browser, reported 2026-11-22
- **Seen:** (1) a USB staging transfer went unconfirmed on both bases; on 0.7.13 the offer held only two removal headers, small enough for one chunk. All three failed attempts recorded one more primed USB receive than completed receives, and zero bus resets. (2) Other attempts with the same removals reached the trial, disconnected during the USB Audio configuration change and came back with the previous active set. Removing MIDI Scenes alone was then kept.
- **Cause:** (1) open; the released diagnostics do not say which command failed. (2) not proven on the unit: in Modwerk's host link test the first claim of the returning interface fails, and the installer then entered its ordinary busy state, ended the page's wait and released its lock on the open trial.
- **Fix:** (2) the installer retries the claim under the trial's existing lock and deadline (host tests cover Keep once the interface is free and expiry while it stays busy); diagnostic summaries now name USB Audio, and an opted-in report shows a failed claim during the trial. (1) none yet; the next record needs the upload command and the remaining receive length.
- **Status:** open (1); fix not yet tried on a physical Windows reconnect (2)
- **Evidence:** `[hw]` (tester's records) / `[emu]` (host link test) {modwerk-1123}
- **Rule:** A88
- **Fact:** [devices/octatrack.md](devices/octatrack.md)

### I193. Drum Mode kept the trig keys from the stock SCALE menu and covered the PTN/BANK LEDs (Digitone mk1)
- **Unit:** Digitone mk1, OS 1.44, Drum Mode 0.10 on elekloader core-dn1 5.3, the author's unit, 2026-11-22
- **Seen:** in the SCALE menu (FUNC + PAGE) the trig keys played pads instead of setting the number of steps; only PAGE and the knob worked. While PTN or BANK was held the trig keys showed the pads, not the stock's pattern and bank LEDs. The emulator test sets had passed.
- **Cause (from the project's notes):** Drum Mode handed the trig keys back to the stock only while PTN or BANK was held, the pattern/bank select was open or a chain's key was held; the SCALE menu was not on that list, and its LED painting ignored all of these states. The emulator tests did not cover either case.
- **Fix:** 0.10.1 leaves the trig key LEDs to the stock in those states; 0.10.2 leaves the trig keys and their LEDs to the stock while the SCALE menu is open. `test_stock_keys.py` grew from 25 to 33 checks.
- **Status:** fixed in the emulator; waits for the unit (0.10.4)
- **Evidence:** `[hw]` {drum-mode-1123}
- **Rule:** A59 (test in the mode the user plays: a mod that takes stock keys must list every stock mode and menu that uses them and test each)
- **Fact:** [devices/digitone.md](devices/digitone.md)

### I194. A MIDI track showed "Drum Mode off" and then could not be used (Drum Mode 0.10)
- **Unit:** Digitone mk1, OS 1.44, Drum Mode 0.10 on elekloader core-dn1 5.3, the author's unit, 2026-11-22
- **Seen:** on some MIDI tracks the screen showed Drum Mode turned off, and the track could not be used after that.
- **Cause:** unknown. Which tracks, what was pressed before and what "unusable" means (no sound, dead keys, stuck UI) are still to be recorded. The author thinks it may be linked to the UI hang with the Mod Menu open seen once in digiemu (digitone.md, 2026-11-17 section).
- **Fix:** none yet.
- **Status:** open
- **Evidence:** `[hw]` (author's report) {drum-mode-1123}
- **Rule:** C11 (record the steps on the unit; nothing more is known yet)
- **Fact:** [devices/digitone.md](devices/digitone.md)

### I195. Stock Rytm samples played under Sidecar machines (Rytm firmware 0.4.4/0.5.0)
- **Unit:** Analog Rytm MKII with Sidecar, Rytm firmware 0.4.4 (a user's unit; reported before 2026-11-22)
- **Seen:** the Rytm's own samples sounded under PLAITS and SOPHIE.
- **Cause (read from the code and shown in the emulator):** page 2 of every Sidecar machine is the sound's sample words 17-24, and the stock sample player renders them for every voice. The mod zeroed the voice's sample gain (`0x80007000 + 8 x voice`), which scales buffer B only. The layer's output S (`0x800067f8 + 128 x voice`) is written by `sample_render` after the machine renders, so the machine cannot clear it.
- **Fix:** Rytm firmware 0.5.1.1: a detour at the mixer call zeroes S of voices under a Sidecar machine, and the stock sample player skips its resampler and filter for those voices (also some Rytm CPU back). A stock track's sample-only trig on a shared voice still plays. The mirror case (a stock-latched engine and a sample-only trig from the Sidecar track) still plays the Rytm sample.
- **Status:** fixed in 0.5.1.1 (emulator; no unit run stated).
- **Evidence:** `[hw]` (user report) / `[emu]` (cause and fix) {sidecar-mods-1123}
- **Rule:** A85 (a mod machine that stock sees as another machine must handle stock's layer for it); also A59 (check against the audio output, not a gain word)
- **Fact:** [devices/analog-rytm.md](devices/analog-rytm.md#sidecar-0511-and-rytm-firmware-0511-mkii-os-174-2026-11-22-sidecar-1123-sidecar-mods-1123)

### I196. A compressor's GR meter raised MAIN CPU through screen repaints (Synfact comp-st 0.2.0, Syntakt)
- **Unit:** Syntakt, OS 1.42, Synfact core 2.4.0 with comp-st 0.2.0 (the owner's unit), 2026-11-20/21
- **Seen:** MAIN's CPU reading rose a lot while the COMP page was open.
- **Cause (counted in the emulator):** not the DSP. Every meter change asked for a repaint, and each repaint recomposes every visible view of the double-buffered screen (about 30,000 instructions for the COMP page). With drums the meter asked on 24-26 of the 30 UI ticks a second.
- **Fix:** comp-st 0.3: the meter repaints at most every third tick (10 Hz) and ignores 1-pixel moves except to zero; 8-10 repaints a second with drums, none with a steady signal.
- **Status:** fixed in 0.3 / 1.0.0 (emulator count); the CPU drop is not measured on the unit.
- **Evidence:** `[hw]` (symptom) / `[emu]` (cause and fix) {synfact-1123}
- **Rule:** A65 (judge the budget by the playing load, the module\'s own UI cost included; rate-limit redraw requests)
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-screen-redraw-cost-stereo-inside-the-audio-chain-edma-self-link-os-142-core-250-2026-11-2122-synfact-1123)

### I197. An eDMA block without a self-link moved only its first 16 bytes (Synfact stereo tracks, Syntakt)
- **Unit:** Syntakt (the owner's unit), Synfact stereo engine development build, 2026-11 (before samplers-st 1.6)
- **Seen:** a block sent by AUDIO eDMA channel 46 to the shared window never arrived whole: only the first 16 bytes (sequence, mask, shifts) reached it, never the tag; the profile written by the CPU did arrive. Synfact went back to copying word by word (about 6 % of the block against 5.1 % with DMA).
- **Cause (as the docs state it; how it was found is not said, the fix copies stock's channel 47 TCD):** the TCD set CITER 35 without the channel link; a software start runs one minor loop of 16 bytes. Stock's channel 47 links the channel to itself.
- **Fix:** samplers-st 1.6 sets CITER/BITER `0xdc23` (ELINK to channel 46, 35 loops of 16 bytes).
- **Status:** fixed in 1.6 (emulated TCD check); not stated on a unit.
- **Evidence:** `[hw]` (16-byte failure) / `[emu]` (fix) {synfact-1123}
- **Rule:** D13 (trap register: a software-started ColdFire eDMA channel runs one minor loop unless it is linked to itself)
- **Fact:** [devices/syntakt.md](devices/syntakt.md#synfact-screen-redraw-cost-stereo-inside-the-audio-chain-edma-self-link-os-142-core-250-2026-11-2122-synfact-1123)
