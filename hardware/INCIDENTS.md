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
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

### I16. A decoded section 7 over 1 MiB crashed the unit
- **Unit:** Digitakt II, OS 1.16 (dt2-machine-lab)
- **Seen:** crash; recovered over the startup menu.
- **Cause (read from the loader):** the ColdFire depacks section 7 into a 1 MiB buffer and checks the size only afterwards.
- **Fix:** keep the decoded section 7 under `0xfffff` bytes.
- **Status:** rule.
- **Evidence:** `[hw]` {dt2-lab-capicola}
- **Rule:** A46
- **Fact:** [devices/digitakt-2.md](devices/digitakt-2.md)

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

