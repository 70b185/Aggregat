# Stock firmware bugs: what Elektron's own OS gets wrong

Bugs in the official OS that mod developers found while testing, collected from the projects' own repositories
(READMEs, changelogs, module notes, test logs) and from our [incident register](INCIDENTS.md). Use it while testing:
a misbehaviour you see with your mod may be stock. **Reproduce it on the unmodified OS with the same steps before you
blame your mod**, and check this list first.

How to read an entry:
- **Device and OS:** where it was seen. Unless an entry says otherwise, nobody has checked other OS versions.
- **Trigger:** the steps that show it, as the source gives them.
- **Workaround:** what a mod (or a user) can do. "Fixed by <project>" means a community mod patches it.
- **Test tip:** how to keep it from spoiling your own test.
- **Found by:** the project and how the cause was found (seen on a unit, read from the code, emulator).
- Evidence levels as everywhere: `[hw]` seen on a unit, `[emu]` emulator only, `[doc]` the project's statement.
  Source keys `{…}` resolve in [SOURCES.md](SOURCES.md).

Numbers (SB1, SB2, …) are permanent. Report a stock bug with the
[stock bug issue form](https://github.com/70b185/Aggregat/issues/new?template=stock-bug.yml), or by a pull request
that adds an entry. Rule C12 in [AGENT-RULES.md](AGENT-RULES.md) says when to check this list and when to add to it.
The website (tab "Stock bugs") and `export/aggregat.sqlite` (table `stock_bugs`) carry the same list.

**Does the newest OS still have them?** Elektron's release notes list **no bug fixes** after the versions most mods
pin: Digitakt II 1.17 (improvements only), Digitone II 1.12 (improvements only), Syntakt 1.42, Analog Heat +FX
1.02 (Overbridge support only) ([DT2](https://www.elektron.se/se/digitakt-ii-os-release-notes),
[DN2](https://elektron.se/release-notes/digitone-ii), [Syntakt](https://www.elektron.se/se/syntakt-os-release-notes),
[Heat +FX](https://www.elektron.se/se/analog-heat-fx-os-release-notes), read 2026-11-07). A bug seen on the pinned
version is therefore probably also in the newest one; that is an inference until someone checks.

Devices: [Digitone II](#digitone-ii) · [Digitone mk1](#digitone-mk1) · [Octatrack](#octatrack) ·
[Analog Rytm](#analog-rytm) · [Model:Cycles](#modelcycles) · [Monomachine](#monomachine) · [Analog Four](#analog-four) · [Syntakt](#syntakt) · [Looks like a bug, is not](#looks-like-a-bug-is-not)

## Digitone II

### SB1. eMMC TRIM fails with TRIM ERROR on a busy card
- **Device and OS:** Digitone II, OS 1.11
- **Area:** storage
- **Symptom:** TRIM ERROR at a sector number; after a restart at another one.
- **Trigger:** many TRIMs in a row while the card is busy (seen while a mod erased its own data).
- **Cause:** the busy wait after CMD38 arms the DAT0 edge interrupt before it tests DAT0, leaving a stale semaphore post; the next TRIM on a busy card returns at once and the call after it gets no answer. The driver has no timeout.
- **Workaround:** read `PRSSTAT` `0xfc0cc024` before every TRIM and verify read, call only when idle; retry (TRIM is idempotent); fixed in dn2mk2 v0.40.
- **Test tip:** a mod that erases or rewrites many blocks must be tested on a card that is busy, not only on an idle one.
- **Found by:** dn2mk2 (error seen on a unit; cause read from stock code)
- **Status:** open in stock
- **Evidence:** `[hw]` {dn2mk2-v040}
- **Incident:** I1

### SB2. Song LOAD trusts a stored row count and halts the unit
- **Device and OS:** Digitone II, OS 1.11
- **Area:** project load
- **Symptom:** a project halts the instrument when opened, on stock and modded builds alike.
- **Trigger:** a song whose stored row count is out of range (one project held 21,503 rows, at most 99 are valid).
- **Cause:** song LOAD `0x400dea6a` reads the count as a signed word at stored `+2891` and copies that many 29-byte rows into 37-byte live rows without a check.
- **Workaround:** fixed by the `songguard` mod (dn2_firmware_explore, also in dn2mk2): a damaged song loads empty; confirmed on hardware. Users: repair the project (row count at record `+0x147`).
- **Test tip:** a project that crashes your build may crash stock too: open it on stock before you debug your mod.
- **Found by:** dn2_firmware_explore (seen on a unit, cause read from stock code)
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[hw]` {dn2-oldproject} {dn2-firmware-explore}
- **Incident:** I2

### SB3. The USB upgrade receiver does not check the 2 MiB limit
- **Device and OS:** Digitone II, OS 1.11
- **Area:** OS update
- **Symptom:** an oversized image stalls at the end of the transfer; nothing is written; a power cycle clears it.
- **Trigger:** a container larger than `0x200000` bytes.
- **Cause:** a 2 MiB receive buffer without a size check.
- **Workaround:** keep the container under 2 MiB; check the size in the build.
- **Test tip:** a build that "hangs while updating" may just be too big.
- **Found by:** dn2mk2 (seen on a unit)
- **Status:** open in stock
- **Evidence:** `[hw]` {dn2mk2-firmware-md}
- **Incident:** I3

### SB4. Auto-commit upload loses its "upload complete" event
- **Device and OS:** Digitone II, OS 1.11
- **Area:** OS update over SysEx
- **Symptom:** the unit sits on "OS UPGRADE / Receiving".
- **Trigger:** the first auto-commit upload after boot, sent before the upgrade view is open.
- **Cause:** the OS posts "upload complete" while the view is not open; the event is lost.
- **Workaround:** upload without auto-commit, then send End(1), which checks the bytes and posts the event itself.
- **Test tip:** a flashing script that hangs once and works the second time may be meeting this.
- **Found by:** complex-ping's Digitone II modding skill (seen on a unit, read from stock code)
- **Status:** open in stock
- **Evidence:** `[hw]` {dn2-skill-scripts}
- **Incident:** I4

### SB5. LFO TRIG MODE ONE and HALF do not run one (half) cycle and hold
- **Device and OS:** Digitone II, OS 1.11
- **Area:** modulation
- **Symptom:** with TRIG MODE ONE or HALF the LFO does not run exactly one cycle (half a cycle) from its start phase and then hold the value it reached; two separate stock bugs, on audio and MIDI tracks.
- **Trigger:** set an LFO's TRIG MODE to ONE or HALF and trigger it.
- **Cause:** not described in the source.
- **Workaround:** fixed by the `lfolength` mod (dn2_firmware_explore; supersedes `lfohold`); confirmed on hardware on an audio track (2026-10-09), MIDI tracks in the emulator.
- **Test tip:** do not judge an LFO mod by ONE/HALF behaviour without comparing stock.
- **Found by:** dn2_firmware_explore (seen on a unit)
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[hw]` {dn2-firmware-explore}

### SB20. Each USB controller reset leaks a timer slot (DT2/DN2, static reading)
- **Device and OS:** Digitakt II OS 1.17, Digitone II OS 1.12
- **Area:** USB, timers
- **Symptom:** none reported on a unit. Each run of the stock controller-reset path (`0x40006ada` -> `0x40007104`) takes one of 16 shared timer slots and does not give it back; the reset also spins on USBCMD.RST with no bound.
- **Trigger:** the firmware's PHY viewport watchdog firing, or a mod calling the reset path.
- **Cause:** read in the image by digikit, not cross-checked.
- **Workaround:** do not call the reset path repeatedly from a mod.
- **Test tip:** count free timer slots before and after forced resets on a unit.
- **Found by:** digikit
- **Status:** open, unconfirmed
- **Evidence:** `[doc]` {digikit-f123-bulk}

### SB31. MIDI-track LFOs freeze after a new project until a note trig plays
- **Device and OS:** Digitone II, OS 1.12
- **Area:** LFOs on MIDI tracks
- **Symptom:** after creating a new project, the LFOs on a MIDI track send nothing until a note trig plays on that track (or its trig key is tapped); lock-only trigs do not start them, so a MIDI track used only for LFO modulation stays frozen.
- **Trigger:** NEW project, MIDI track with an LFO in FRE or TRG mode and no note trigs.
- **Cause:** not described; the fix patches the lane update `0x40137770` and the LFO send loop's destination check `0x4012a340`.
- **Workaround:** tap the track's trig key, or place a note trig; fixed by vitel2's MIDI LFO run mod (which also stops the CCs while the transport is stopped).
- **Found by:** vitel2/digitone2-mods (README)
- **Status:** open in stock; unconfirmed by us (H53)
- **Evidence:** `[doc]` {dn2-mods-vitel2}

### SB43. MACHINE SEL can put the cursor on the wrong row after a SYN/FLTR page change (Digitone II)
- **Device and OS:** Digitone II, OS 1.12
- **Area:** UI, MACHINE SEL
- **Symptom:** with FM DRUM marked, going from the FLTR page back to SYN highlights WAVETONE instead of FM DRUM.
- **Trigger:** LEFT/RIGHT between the SYN and FLTR pages when the marked machine's type number differs from its row number.
- **Cause:** the page change (`0x4005baa8`, `0x4005bab6`) copies the marked type value (`+0x19c` SYN, `+0x1a0` FLTR) into the cursor's row index (`+0x1a4`); rows are not in type order (FM DRUM is type 2, row 1).
- **Workaround:** none needed on stock; a mod that adds machines should not rely on where the cursor lands after a page change. Whether the cursor can land on a divider is not checked.
- **Found by:** digikit (finding 131)
- **Status:** open; emulator observation and static reading, not yet checked by hand on a unit
- **Evidence:** `[emu]` {digikit-1127}

## Digitone mk1

### SB6. The stock restart does not wait for the +Drive or drain the panel link
- **Device and OS:** Digitone mk1 / Keys, OS 1.43 and 1.44
- **Area:** restart
- **Symptom:** a restart triggered by code can cut off a +Drive write or a panel message in flight.
- **Trigger:** calling stock's own restart from a mod while the card or the panel link is busy.
- **Cause:** stock's restart does not wait for the +Drive and does not let the panel link drain with interrupts on.
- **Workaround:** elekloader core-dn1 exports `core_restart`, which does both; use it instead of stock's.
- **Test tip:** a mod that restarts the unit should be tested right after a save and while keys are pressed.
- **Found by:** elekloader (read from stock code)
- **Status:** open in stock; worked around by a core
- **Evidence:** `[doc]` {elekloader-core-dn1}

## Octatrack

### SB7. EP0 data stages of a multiple of 64 bytes stall or freeze
- **Device and OS:** Octatrack MKII, OS 1.40C
- **Area:** USB
- **Symptom:** the request after a 64/128/192/256-byte reply returns 0 bytes; once the unit froze; 128/192-byte OUT stages never complete.
- **Trigger:** a control transfer whose data stage is a multiple of 64 bytes.
- **Cause:** stock leaves zero-length termination on in the EP0 OUT queue head.
- **Workaround:** size replies a byte short, or clear ZLT when priming.
- **Test tip:** test USB replies of exactly 64 and 128 bytes on purpose.
- **Found by:** Modwerk (measured on a unit)
- **Status:** stock behaviour
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Incident:** I5

### SB8. About one EP0 OUT stage in 50-100 goes unanswered
- **Device and OS:** Octatrack MKII, OS 1.40C
- **Area:** USB
- **Symptom:** host requests time out now and then.
- **Trigger:** many EP0 OUT stages in a row.
- **Cause:** the stage completes inside the ISR after stock's poll, or stops part-way.
- **Workaround:** finish a completed stage from a 60 Hz tick, or stall EP0 after 0.5 s so the host resubmits.
- **Test tip:** count timeouts over a thousand requests, not ten.
- **Found by:** Modwerk (measured on a unit)
- **Status:** stock behaviour
- **Evidence:** `[hw]` {modwerk-ot-traps}
- **Incident:** I6

### SB9. A Plays-Free MIDI track stalls after its first step
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** sequencer, MIDI tracks
- **Symptom:** the track stops after its first step on a manual trig.
- **Trigger:** a Plays-Free MIDI track with trig quantize Direct and pattern scale Per Track, triggered manually.
- **Cause:** read from stock code at `0x4009b6f2` (an 18-byte splice fixes it).
- **Workaround:** fixed by octatrack-kyoti-fw's BATCH_BUGFIXES (`MIDI_PLAYS_FREE_FIX`); hardware-confirmed 2026-08-28.
- **Test tip:** a sequencer mod that uses scales Per Track can run into this on stock paths.
- **Found by:** octatrack-kyoti-fw (seen on a unit)
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[hw]` {kyoti-bugfixes}

### SB10. A pattern that holds only parameter locks shows as empty
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** UI
- **Symptom:** the pattern's grid LED stays unlit under [PTN], as for an unused slot.
- **Trigger:** a pattern whose only content is parameter locks (on a MIDI track, or trigless locks on an audio track), with no trig.
- **Cause:** stock's "used" test looks at trigs only.
- **Workaround:** fixed by BATCH_BUGFIXES (`EMPTY_PATTERN_LED_FIX`) under [PTN]; under [BANK] a full scan of 256 patterns' locks on every LED refresh starved the CPU. Since 2026-11-20 (318 B version) [BANK] also lights a bank whose pattern holds a trigless lock with a locked value, by reading only the trigless-lock masks and at most 16 lock rows per pattern; confirmed responsive with [BANK] held on an MKI. Other lock-only content still reads empty under [BANK]. {octatrack-kyoti-fw-1121}
- **Test tip:** do not overwrite a "free" pattern slot in a test project without checking for locks.
- **Also (2026-11-24):** the same "used" test (`0x4009a464`) serves "find next empty pattern", so a lock-only pattern counts as empty and can be overwritten (octabam KITS' PTN + FUNC + RIGHT; the [BANK] caller is `0x4000fd8c`). octabam's BATCH_BUGFIXES content test counts locks, and Modwerk base 0.8 carries the fix at the same site. `[doc]` {octabam-1124} {modwerk-1124}
- **Found by:** octatrack-kyoti-fw
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[doc]` {kyoti-bugfixes}

### SB11. A pattern-triggered Part change carries the old Part's state over
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** sequencer, Parts
- **Symptom:** a track leaving PICKUP for FLEX keeps playing the old Part's pickup loop; the recorder's SRC/RLEN cache goes stale; a pattern switch into a PICKUP track marks the Part edited when nothing changed. Also reported on Elektronauts.
- **Trigger:** a pattern change that changes Part, with a track going from PICKUP to another machine.
- **Cause (read from stock code):** the "select Part" handler `0x400621a6` calls `FUN_400972fc` per track, whose PICKUP-to-other branch does nothing; PICKUP and FLEX share one sample arena, so the stale pointer still looks valid; nothing republishes the recorder cache.
- **Workaround:** fixed by BATCH_BUGFIXES (`PART_CHANGE_CARRYOVER_FIX`): republish the recorder records, set the voice-kill bit, re-seed the slot.
- **Test tip:** a mod that changes Parts (DIRECT JUMP and others) reaches the same stock path and shows the same symptom; compare a stock pattern change.
- **Found by:** octatrack-kyoti-fw
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[doc]` {kyoti-bugfixes}

### SB12. A trigless lock stays lit after its last lock is erased
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** UI, sequencer
- **Symptom:** the step stays lit on the trig row forever, although it is now inert.
- **Trigger:** erase the last remaining lock of a trigless lock (LIVE REC: [NO] + knob), on an audio or a MIDI track.
- **Cause (read from code, 2026-11-20):** the LIVE erase worker (audio `0x40038874`, MIDI twin `0x40038668`) clears the step from the lock bitmap when its row empties, but never the trigless-lock flag at track `+0x10`, which keeps the LED lit. The MIDI clear-trigs path also leaves `+0x10` set where audio clears it. {octatrack-kyoti-fw-1121}
- **Workaround:** fixed by octatrack-kyoti-fw's ERASE_EMPTY_TRIGLESS_LOCKS (a deliberately empty trigless lock placed with FUNC + TRIG is left alone); since 2026-11-20 on MIDI tracks too, confirmed on an MKI (I173).
- **Test tip:** lit steps after a lock edit are not necessarily your mod.
- **Found by:** octatrack-kyoti-fw
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[doc]` {kyoti-bugfixes}

### SB13. LO-FI's AMF ring-mod pitch falls at eleven values instead of rising
- **Device and OS:** Octatrack MKI and MKII, OS 1.40C (LO-FI on FX1 and FX2)
- **Area:** DSP effect
- **Symptom:** turning AMF up lowers the ring-mod pitch at AMF 8, 17, 23, 28, 32, 35, 37, 40, 42, 45 and 48 (worst at 7 to 8, about 63 % lower); monotonic again above 48.
- **Trigger:** LO-FI with AMF in those ranges (also reached by LFOs, scenes and fine values).
- **Cause (read from the DSP code):** the coefficient's extended-precision multiply starts with `mpysu x0,y0,a` (signed x unsigned) on two magnitudes; when the low word's top bit is set the partial product's sign flips. Reported to Elektron, not fixed upstream.
- **Workaround:** `mpyuu` instead (octa-bt-pt's LOFI AMF FIX; also a Modwerk draft module). Saved projects at affected values will sound different with the fix.
- **Test tip:** an effect mod that compares against LO-FI by ear may be comparing against this bug.
- **Found by:** octa-bt-pt (AMF 0-127 x fine 0-127 swept in the DSP emulator with the fix: monotonic)
- **Status:** open in stock; fixed by a mod (not yet run on hardware per the Modwerk draft)
- **Evidence:** `[emu]` {octa-lofi-amf}

### SB14. Probable: SPATIALIZER's ring misaligns when selected mid-play
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** DSP effect
- **Symptom:** a misaligned delay ring when SPATIALIZER is selected while playing with a non-zero held offset; later calls can read across the ring end (wet path only); re-selecting at offset 0 realigns.
- **Trigger:** select SPATIALIZER mid-play.
- **Cause (emulator and model):** the dispatcher splits a frame's FX call at `x:$20c`, and SPATIALIZER's init zeroes its ring write offset between the two calls, misaligning the ring by 32 - 2 x offset.
- **Workaround:** none yet; the source plans a hardware test on stock.
- **Test tip:** odd SPATIALIZER artefacts after switching effects live may be stock.
- **Found by:** octatrack-kyoti-fw (emulator; "probable stock bug")
- **Status:** unconfirmed
- **Evidence:** `[emu]` {kyoti-ot303}

### SB17. The AUDIO EDITOR key opens the sample the track had before
- **Device and OS:** Octatrack MKII, OS 1.40C
- **Area:** UI, audio editor
- **Symptom:** after a track copy/paste or a Part reload, the [AUDIO EDITOR] key shows the old sample's name, waveform and slices.
- **Trigger:** change a track's sample by copy/paste or Part reload, then press [AUDIO EDITOR] without reselecting the track.
- **Cause:** stock reuses the sample the track had when it was last selected.
- **Workaround:** reselect the track first; fixed by OCTAMAX 2f.
- **Test tip:** when a mod changes a track's sample, reselect the track before you judge the editor.
- **Same gap, second path:** with the audio editor open, a pattern change to a pattern on another Part (in the same bank, or a bank pick with BANK AUTO PTN 1) or a Part change leaves the editor on the previous Part's sample while the trigs already play the new one, until it is closed and reopened. Track select publishes the slot to the editor (`0x40083c64`); the pattern-change and Part-change handlers (`0x40062120`, `0x400621a6`) do not. OCTAMAX 2i publishes there too.
- **Found by:** OCTAMAX (seen on a unit; fixes confirmed on an MKII 2026-11-07 (2f) and 2026-11-11 (2i))
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[hw]` {octamax-notes} {octamax-2i}

### SB22. One Part byte outside its stock range drops the whole bank at power-on
- **Device and OS:** Octatrack MKII, OS 1.40C
- **Area:** battery RAM restore, Parts
- **Symptom:** after a restart all eight tracks of the bank read STATIC with no trigs and default FX; the next restart restores the bank with the byte reset to 0.
- **Trigger:** a byte in a Part record outside the range stock's Part check accepts (a mod's packed value of 0x80 or more).
- **Cause:** the boot's battery restore runs stock's Part check and drops the bank when it repairs a byte.
- **Workaround:** store only values stock accepts in stock records (rule A60).
- **Test tip:** after any mod that stores bytes in Parts, save, restart twice and check the bank.
- **Found by:** Modwerk (VECTOR, I95)
- **Status:** stock behaviour
- **Later (2026-11-27):** the fix stock's check makes stays only in the battery copy; a RELOAD of a save that still holds the value brings the empty bank back at every start ([I234](INCIDENTS.md#i234-a-project-came-up-empty-at-every-start-after-a-save-modwerk-octatrack)). {modwerk-1127}
- **Evidence:** `[hw]` (restart with no module) / `[emu]` (stock check called directly) {modwerk-vector}

### SB26. Probable: TRACK COPY / PASTE leaves the LFO designer behind
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** UI, Parts
- **Symptom (expected):** a pasted track whose LFO WAVE is the designer plays the destination track's designer shape, not the copied one; seen only when pasting to another track or into a pattern on another Part.
- **Trigger:** GRID REC copy of a track with a designer LFO, paste onto another track.
- **Cause:** TRACK COPY `0x40029754` copies the record plus six Part blocks into clipboard `+0x91f..+0x9a1`; the designer (`+0x1702+16t`, slope `+0x1782+2t`) is not among them (read from stock code).
- **Workaround:** none yet; KYOTI names a fix (TRACK_PASTE_DESIGNER_FIX, about 60-100 bytes) if it is confirmed.
- **Test tip:** stock test H31 in [HYPOTHESES.md](HYPOTHESES.md).
- **Found by:** octatrack-kyoti-fw ("candidate stock bug", read from the code, not yet seen on a unit)
- **Status:** unconfirmed
- **Evidence:** `[doc]` {kyoti-clyps-scope}

### SB29. WAV files saved by the Octatrack carry a RIFF size 8 bytes too large
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** card, sample save
- **Symptom:** bytes 4-7 of a saved `.wav` hold the whole file size instead of file size minus 8. Most decoders ignore it because they trust the `data` chunk size; strict tools may warn or read past the end.
- **Trigger:** any stock sample save (seen with a recorder buffer saved through the stock routine).
- **Cause:** the header writer stores the file length, not length - 8 (read from the code; measured under the port: 176,444 B file, 176,444 in the field).
- **Workaround:** tools that read Octatrack WAVs should trust the `data` chunk size.
- **Test tip:** H50.
- **Found by:** octabam (docs/firmware/SAMPLE_SAVE.md)
- **Status:** confirmed in emulator, not checked on a unit-saved file
- **Evidence:** `[emu]` {octabam-1118}

### SB30. FX1 SETUP knob F on EQUALIZER changes a hidden Part byte
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** UI, Parts
- **Symptom (expected):** turning knob F on FX1's SETUP page with EQUALIZER loaded changes a Part byte while no screen shows a parameter there.
- **Trigger:** EQUALIZER in FX1, SETUP page, turn F.
- **Cause:** none of the page-2 editors tests an enable bit for the slot.
- **Workaround:** leave knob F alone on that page.
- **Found by:** octabam (docs/firmware/PARAM_PAGES.md, under the port 2026-11-05)
- **Status:** unconfirmed on a unit; audible effect unknown
- **Evidence:** `[emu]` {octabam-1118}

### SB32. A timestretched voice retriggered within about 300 samples stays silent
- **Device and OS:** Octatrack MKI, OS 1.40C
- **Area:** timestretch, slices
- **Symptom:** a voice with TSTR AUTO, NORM or BEAT that is retriggered within its first ~300 samples stalls silent (200 and 250 samples failed, 308 held); slices made by stock's CREATE SLICE GRID show it too.
- **Trigger:** very short slices or fast retriggers with timestretch on.
- **Cause:** timestretch needs about 300 samples of run-up (octabam's reading).
- **Workaround:** keep slices and retrigger gaps above ~300 samples, or turn timestretch off for them; octabam's LAZY CHOP guards against it.
- **Found by:** octabam (LAZY CHOP)
- **Status:** stock behaviour (a limit more than a bug)
- **Evidence:** `[hw]` (one MKI) {octabam-1119}

### SB33. Deleting an arrangement row above a JUMP that targets it turns the JUMP into a HALT
- **Device and OS:** Octatrack MKI, OS 1.40C
- **Area:** arranger
- **Symptom:** FUNC + UP (delete) on row D, with a JUMP on row D+1 that targets D, moves the JUMP into D, where it points at itself and plays as a HALT; no message.
- **Trigger:** delete the row a JUMP below targets.
- **Cause:** the delete routine `0x4009b168` shifts rows without fixing jump targets (matches the image reading).
- **Workaround:** check JUMP targets after deleting rows.
- **Found by:** Modwerk (Arr Rows research; reported to the Modwerk owner)
- **Status:** stock behaviour, reproduced on the developer's MKI with no module
- **Evidence:** `[hw]` {modwerk-ot-1119}

### SB34. Inserting on a HALT row leaves an endless LOOP below it
- **Device and OS:** Octatrack MKI, OS 1.40C
- **Area:** arranger
- **Symptom:** FUNC + DOWN (insert) on a HALT row keeps the HALT and leaves a `LOOP: n/∞` below it.
- **Trigger:** insert on a HALT row.
- **Cause:** not described.
- **Workaround:** check the rows after an insert near a HALT.
- **Found by:** Modwerk (Arr Rows research)
- **Status:** stock behaviour
- **Evidence:** `[hw]` / `[emu]` {modwerk-ot-1119}

### SB37. SAVE TO NEW reports FILE NOT FOUND for a project with no `.strd` files (Octatrack)
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** card, projects
- **Symptom:** SAVE TO NEW shows FILE NOT FOUND, yet the new project folder is written.
- **Trigger:** SAVE TO NEW on a project that has never been saved as a state (no `.strd` files).
- **Cause:** not read; stock first saves the open project, then copies only `.work` files to the new folder.
- **Workaround:** none needed; the new folder is complete. octabam's COPY PROJECT adds the sidecar files to SAVE TO NEW.
- **Test tip:** check the new folder on the card before you trust or distrust the message.
- **Found by:** octabam (COPY PROJECT module)
- **Status:** open in stock
- **Evidence:** `[emu]` (stock code run in octabam's emulator) {octabam-1124}

### SB38. Adding a row at END OF ARR. has no 256-row limit and writes past the arrangement (Octatrack)
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** arranger, projects
- **Symptom:** a 257th row added at the end is written past the 5,652-byte working arrangement, over the next arrangement's name, row count and first row; the next save writes that into the other arrangement's file.
- **Trigger:** keep adding rows at END OF ARR. past 256. Inserting in the middle stops at 255 with ROW LIMIT REACHED.
- **Cause:** the insert routine `0x4009e4c8` checks the count (`cmpil #255`, message at `0x4009e5c6`) only on the middle-insert path; the append path at `0x4009e50c` has no check.
- **Workaround:** stay below 256 rows; octabam's ARR ROW CAP adds the missing check. A saved 256-row arrangement probably loads as 255 rows `[?]`.
- **Test tip:** keep a backup of the project before you build very long arrangements.
- **Found by:** octabam (ARR ROW CAP)
- **Status:** open in stock
- **Evidence:** `[emu]` (stock fails 3 of the module gate's 7 checks under the emulator port) {octabam-1125}

### SB39. After a LOAD the arranger can stay "running" with nothing playing, and refuses every arrangement (Octatrack)
- **Device and OS:** Octatrack MKI, OS 1.40C
- **Area:** arranger, projects
- **Symptom:** after loading another project, picking an arrangement does nothing.
- **Trigger:** LOAD of another project (LOAD also switches arranger mode off and saves first).
- **Cause:** the arranger run state at `0x800066a0` can stay set with nothing playing, so the select routine `0x400a03a0` refuses every choice; stock's reset `0x4009ae48` clears it.
- **Workaround:** Modwerk's Songbook calls the reset after a load.
- **Test tip:** a mod that switches arrangements after a load should check this state first.
- **Found by:** Modwerk (Songbook research)
- **Status:** open in stock
- **Evidence:** `[hw]` {modwerk-1125}

### SB40. The stock DELAY reads 16 bytes past its own table (Octatrack)
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** effects
- **Symptom:** none reported; a latent out-of-bounds read.
- **Trigger:** the DELAY effect's table lookup.
- **Cause:** the read reaches 16 bytes past the table at `0x400d24d0`.
- **Workaround:** a mod that places data right after that table should leave those bytes as they are.
- **Test tip:** none.
- **Found by:** Modwerk (Scale Quantizer upstream notes)
- **Status:** open in stock
- **Evidence:** `[doc]` {modwerk-1125}

### SB42. A sample path longer than the card allows can lock the sample browser until a power cycle (Octatrack)
- **Device and OS:** Octatrack, OS 1.40C
- **Area:** sample browser, card
- **Symptom:** moving the browser cursor near a file whose full path passes 259 characters can leave the footer reading LOADING... for good and the folder line garbled; the browser then refuses to open on any slot, in any project, until a power cycle.
- **Trigger:** a sample whose path from the card root (`/` + set name + `/AUDIO/` + folders + file name) is 260 characters or more.
- **Cause:** the browser builds each path into 260-byte buffers with an unbounded `strcat` and `sprintf`; a longer path runs over the LOADING... flag (`0x460e49f4`) and the current folder (`0x460e4c00`).
- **Workaround:** keep set, folder and file names short enough that every path stays within 259 characters; octabam's BROWSE PATH GUARD bounds the copies so such a file shows ERR.
- **Test tip:** a project's `PATH=` (it starts `../AUDIO/`) can be at most 260 minus the set name's length.
- **Found by:** octabam (BROWSE PATH GUARD, #1258)
- **Status:** open in stock
- **Evidence:** `[emu]` (stock fails 14 of the module gate's 36 checks under the emulator port) {octabam-1126}

### SB44. A retriggered track recorder leaves its old bank reading "recording" (Octatrack)
- **Device and OS:** Octatrack MKII, OS 1.40C
- **Area:** track recorders
- **Symptom:** after a recording is retriggered while it records and then stopped, the bank it left still reads 2 (recording) until that track records again or the unit restarts.
- **Trigger:** TRACK + REC twice on a recording track, then STOP.
- **Cause:** each track has two recorder state rows (`0x80004f1e + 84*(track + 8*bank)`); a retrigger moves the recording to the other bank, and STOP clears only the bank selected by bit t of `0x80004f18`.
- **Workaround:** read only the selected bank's row (rule A102).
- **Found by:** Modwerk ([I233](INCIDENTS.md#i233-a-retriggered-recorder-left-a-stale-state-and-syncs-were-refused-until-a-power-cycle-modwerk-octatrack))
- **Status:** stock behaviour, harmless on stock
- **Evidence:** `[hw]` {modwerk-1127}

### SB46. The power-up check of the current Part fixes only one of its two copies (Octatrack)
- **Device and OS:** Octatrack MKI/MKII, OS 1.40C
- **Area:** power-up restore, Parts
- **Symptom:** none seen; latent. With a damaged Part byte, the CS1 copy is clamped to 3 but the SRAM copy keeps the bad value.
- **Trigger:** a battery-RAM Part byte above 3 at power-up.
- **Cause:** stock keeps the current Part in SRAM `0x80000003` and in CS1 `0x100b14cf`. The restore copies CS1 to SRAM first (`0x4001fb4c`), then the clamp at `0x4000fda8` (called from `0x40025770` at `0x4001fb78`) fixes CS1 only; 94 stock readers use the SRAM copy.
- **Workaround:** a mod that reads the Part from SRAM should clamp it to 0-3 itself.
- **Found by:** Modwerk (read from stock while moving its Part read to SRAM)
- **Status:** open in stock
- **Evidence:** `[doc]` {modwerk-1128}

## Analog Rytm

### SB18. Edits to hidden FX words overwrite the delay's saved TIME (latent)
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** kit storage, FX
- **Symptom:** after an edit of live FX words 38-41 and a power cycle, the delay TIME comes back wrong (2 instead of 23 in the test).
- **Trigger:** a parameter setter writes FX words 38-41. The stock UI never edits them, so only mods reach this.
- **Cause:** the FX edit save maps words 38-41 to stored slot 0, which holds the delay's TIME.
- **Workaround:** keep mod values for those words in your own storage (Modwerk's base redirects them to its kit storage).
- **Test tip:** after any mod that touches FX words, save, power-cycle and check the delay TIME.
- **Found by:** Modwerk (rytm-emu, from the code)
- **Status:** stock behaviour
- **Evidence:** `[emu]` {modwerk-rytm-machines}

### SB19. A non-sample file on the +Drive hangs LOAD TO PROJECT and later stalls the OS upgrade
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** +Drive, SAMPLES browser, OS upgrade
- **Symptom:** loading a file that is not a sample (a raw `.elemod` in this case) into the project hangs the unit; a project that holds such a file then stalls the next OS upgrade at PREPARING until CREATE NEW.
- **Trigger:** any file on the +Drive's sample filesystem is listed by SAMPLES, in every folder; LOAD TO PROJECT reads its first 16 bytes as the sample header without a check.
- **Cause:** per elekloader, LOAD TO PROJECT trusts the 16-byte header at the start of the file.
- **Workaround:** a tool that stores other files on the +Drive starts each with 16 zero bytes, which stock loads as an empty sample (elekloader's Drive Loader does this).
- **Test tip:** keep test files off the +Drive, or give them the zero header; if an OS upgrade stalls at PREPARING after +Drive experiments, try CREATE NEW before blaming the image.
- **Found by:** elekloader (Drive Loader development)
- **Status:** stock behaviour
- **Evidence:** `[doc]` {elekloader-drive}

### SB21. The Rytm MKI's in-OS upgrade decodes into a 2 MiB buffer without a bound check
- **Device and OS:** Analog Rytm MKI, OS 1.74
- **Area:** OS update
- **Symptom:** not seen; an image that decodes past 2 MiB would overrun the buffer.
- **Trigger:** an update image larger than the fixed decode buffer.
- **Cause:** a fixed buffer with no size check (elekloader's profile, static reading). Modwerk's MKI research names the buffer `0x40366570` (2 MiB; reported, still to be checked on a 1.74 image, H36) and notes that the startup menu's MIDI DIN recovery survives an overrun. {modwerk-1117}
- **Workaround:** keep an image at or below `0x1F0000` bytes (elekloader's limit).
- **Test tip:** check the size in the build, as for SB3 on the Digitone II.
- **Found by:** elekloader
- **Status:** open in stock
- **Evidence:** `[doc]` {elekloader-ar1}

### SB25. FX-track lock indexes 38-41 read past their table and share rows with 18-21
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** parameter locks on the FX track
- **Symptom:** the FX track's sound-index-to-row-type table has 38 entries (`0x401c5b4c`), but indexes 38..41 are looked up anyway; they read on into the next table (`0x401c5be4[0..3]`) and get row types 9..12, the same rows as indexes 18..21.
- **Trigger:** a lock on one of the FX track's parameters 38-41.
- **Cause:** the selector (`0x400075c8`/`0x40007602`) picks the table by "track == 12" alone and does not check the index against the FX table's length.
- **Workaround:** a mod that writes FX-track locks should treat 38-41 and 18-21 as one row each.
- **Found by:** trig-seedr (firmware notes for OS 1.74)
- **Status:** open; seen in the emulator only.
- **Evidence:** `[emu]` {trig-seedr-1116}

### SB27. The UI queue overwrites unread messages when more than 1024 wait
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** UI task, message queue
- **Symptom:** under heavy load the panel lags and key, pad pressure and other UI messages are lost.
- **Trigger:** more than 1024 messages waiting in the UI queue (seen with 13 mods and BD ANALOG voices playing, plus pad pressure at 200-290 messages a second during a held pad).
- **Cause:** the queue is a ring of 1024 pointers; its send updates the write index and count with interrupts masked but never checks for a full ring (read in the OS 1.74 disassembly).
- **Workaround:** keep audio-block load low enough that the UI task keeps up; a mod that posts to the queue keeps its own bounded pool and counts only its own waiting events.
- **Test tip:** read the queue's read index and count (Modwerk's test counters) while holding a pad with RTRG under load.
- **Found by:** Modwerk (Live Rec Retrig Fix 0.2.2 testing; overflow counted on a unit, I131)
- **Status:** stock behaviour
- **Evidence:** `[hw]` (overflow counted on a unit) / `[doc]` (no full check, from the disassembly) {modwerk-rytm-1116}

### SB28. Data transfer progress wraps for files over 4,294,967 bytes
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** Data router (USB transfers of files, as Transfer uses)
- **Symptom:** the per-mille progress of a read goes wrong past 4,294,967 bytes.
- **Trigger:** a read of a file larger than 4,294,967 bytes.
- **Cause:** the progress (`0x4008c9d6..0x4008c9e8`) wraps there; 4,294,967 is 2^32 / 1,000, so a 32-bit multiply by 1,000 is the likely cause `[?]` (the source gives only the range and the limit).
- **Workaround:** a client counts the bytes it gets; elekloader's tools do.
- **Test tip:** download a sample over 4.3 MB with Transfer and watch the progress bar.
- **Found by:** elekloader (drive-loader-ar2 STAGE.md)
- **Status:** open
- **Evidence:** `[doc]` {elekloader-drive-1118}

### SB36. Pad pressure goes to the wrong note in CHROMATIC mode and is dropped during RTRG rolls (Rytm MKII)
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** pads, aftertouch, MIDI out
- **Symptom:** in CHROMATIC mode a held pad's poly pressure goes out 24 semitones above the note it played (note on 36, pressure for 60, note off 36), so a synth that follows the note sees no aftertouch. During a retrig roll held with RTRG and VEL.CUR set, the RETRIG menu takes the pressure and throws it away: no AFTERTOUCH movement and no MIDI poly pressure (ALWAYS ON pads with VEL.CUR set keep it).
- **Trigger:** hold a pad in CHROMATIC mode and press it harder; or hold RTRG with VEL.CUR set and squeeze a pad.
- **Cause:** not read; the module README describes the behaviour only.
- **Workaround:** Modwerk's Pad Pressure Fix module (0.2.0-experimental) sends pressure on the played note and routes roll pressure to aftertouch and MIDI out; its fixes are moving into the Modwerk Rytm base.
- **Test tip:** watch MIDI out for the poly pressure note number while you hold a CHROMATIC pad.
- **Found by:** Modwerk (Pad Pressure Fix module)
- **Status:** open in stock
- **Evidence:** `[doc]` (module README; the module's fix is reported on its author's unit) {modwerk-1123}

### SB45. A pattern save silently drops p-locks past 71 lock rows (Analog Rytm MKII)
- **Device and OS:** Analog Rytm MKII, OS 1.74
- **Area:** sequencer, p-locks, project save
- **Symptom:** a lock that makes a pattern need more than 71 lock rows plays, but is gone after the next save and load, with no warning.
- **Trigger:** fill a pattern's lock rows (a lock index with fine resolution costs two rows), add one more lock, save the project, load it again.
- **Cause:** the full pattern rebuild (`0x40009216`, used by SAVE PROJECT) writes at most 71 lock rows (check at `0x400092a2`); it walks lock index 0-41 outer and track 0-12 inner and skips a two-row index whole when it would pass 71, so the send-FX words 38-41 are dropped first.
- **Workaround:** a mod that adds locks should count rows the way the save does and refuse with stock's LOCK MEM FULL! message (Rytm firmware 0.5.2 does this through `0x400acbd2`). UNDO and RELOAD TRACK can still push a pattern past 71 rows.
- **Found by:** Sidecar | Expander (design notes 0025 and 0029)
- **Status:** open in stock; trig-seedr saw a lock past 71 rows survive SAVE PATTERN and RELOAD (O52)
- **Evidence:** `[emu]` {sidecar-mods-1128}

## Model:Cycles

### SB15. A random exception while browsing (filesystem block cache)
- **Device and OS:** Model:Cycles, OS 1.13
- **Area:** storage, UI
- **Symptom:** a random exception while browsing.
- **Trigger:** browsing (the source gives no exact steps).
- **Cause:** the filesystem block cache, per Model-TG.
- **Workaround:** fixed by Model-TG ("a long-standing stock bug"), and in builds that include it (Modded-Cycles lists it).
- **Test tip:** an exception while browsing on a modded build is not necessarily the mod.
- **Found by:** Model-TG
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[doc]` {model-tg-internals}

### SB41. A pad sample assigned to a lock from the +Drive takes a second LOCKS slot (Model:Samples)
- **Device and OS:** Model:Samples, OS 1.13
- **Area:** samples, sample locks
- **Symptom:** the sample is loaded into the LOCKS folder again and uses one of its 20 slots, though it is already on a pad.
- **Trigger:** assign a sample that is already on a pad to a sample lock by picking it from the +Drive (picking it from the LOCKS folder does not duplicate it).
- **Cause:** not read.
- **Workaround:** pick the sample from the LOCKS folder; Yan Hugman's LOCKS duplicate fix mod prevents the duplicate.
- **Test tip:** count the LOCKS slots before and after the assignment.
- **Found by:** ms-mods-yanhugman (LOCKS duplicate fix)
- **Status:** open in stock; fixed by a mod
- **Evidence:** `[doc]` {ms-mods-1125}

## Monomachine

### SB16. Eleven sequencer and UI bugs fixed by ems-monomachine-firmware
- **Device and OS:** Monomachine, OS 1.32B
- **Area:** sequencer, UI, POLY mode
- **Symptom:** as listed in the project's changelog: clearing a track in EDIT KIT sets GND>SIN's TUNE to -64 instead of 0; leaving the snapshot manager through the KIT shortcut can make later COPY/PASTE/CLEAR act on snapshots; switching POLY mode on or off during playback can mute tracks when MULTI ENV > SUS is 0; MULTI ENV changes do not persist while POLY mode is active; notes in POLY mode get stuck after various actions (changing track, pattern); CLEAR > UNDO SONG ROW does not work; CLEAR SONG ROW does not clear per-track transpose data; PASTE > UNDO TRANSPOSE does not work; muting a track that another track triggers and unmuting it later leaves the trigs that fell into the muted time muted; muting such a track does not mute its active ARP sequence; the playhead is not shown for the first step triggered by SPP.
- **Trigger:** see each item.
- **Cause:** not described in the source.
- **Workaround:** fixed in ems-monomachine-firmware (beta).
- **Test tip:** POLY-mode and mute behaviour on a modded Monomachine should be compared with stock 1.32B.
- **Found by:** ems-monomachine-firmware
- **Status:** open in stock; fixed by a custom firmware
- **Evidence:** `[doc]` {ems-fw}

## Analog Four

### SB23. The MKII can hang on its own restart after writing a new OS
- **Device and OS:** Analog Four MKII, OS 1.56 (the running OS does the update)
- **Area:** OS update, restart
- **Symptom:** the unit sits on SUCCESS! REBOOTING, stays on USB, and every MIDI call to it blocks until it leaves USB.
- **Trigger:** a flash that stock 1.56 runs; seen twice in about 30 flashes.
- **Cause:** the restart masks every interrupt and then waits for a serial queue that only those interrupts drain (elkflash's reading). elekloader's reading: 1.56 masks interrupts at `0x4007db24` and then waits in `0x40002766` while bytes are pending behind the panel link's DMA (`0x4133cfc0`) or in the UART queue (`0x4133cfd0`), which only those interrupts drain; core-a4mk2 (0.4+) masks only once nothing is pending, not yet checked on the A4. {elekloader-core-a4}
- **Workaround:** power-cycle by hand; the new OS is already written. Do not reflash, and do not take a screenshot over MIDI.
- **Test tip:** watch the USB node: units leave USB 16-32 s after the commit; one still there after 45 s has stalled.
- **Found by:** elkflash
- **Also (2026-11-22):** the Analog Rytm MKII on OS 1.74 shows the same race in analog-emu: without elekloader core-ar2's restart routine 5 of 15 upgrades hung, with it 0 of 15, and 0 of 30 with the panel link paced as on a unit, so on a unit it is likely rare. `[emu]` {elekloader-1122}
- **Status:** open
- **Evidence:** `[hw]` {elkflash-stall} (I103)

### SB24. Live recording records nothing after a sample arrives by SDS
- **Device and OS:** Machinedrum, OS 1.63
- **Area:** sample receive, live recording
- **Symptom:** after any sample is received over SDS, live recording records no TRIG key and no knob lock until the machine restarts.
- **Trigger:** one SDS sample transfer, then live recording.
- **Cause:** the RECEIVING SAMPLE screen takes the main screen's objects out of a linked list and puts them back without restoring the list head (head cell at RAM `0x28092c`; unlink `0x213450`, append `0x2134ac`), found by bisecting RAM in the emulator.
- **Workaround:** restart the machine after sending samples, before live recording.
- **Found by:** mdmm (B-133)
- **Status:** open; seen on the unmodified OS in the emulator, a real unit "very likely" the same but not tried.
- **Evidence:** `[emu]` {mdmm-091}

## Syntakt

### SB35. A Data API card write takes its length from the host and is bounded only by the card's end
- **Device and OS:** Syntakt, OS 1.42 (the same eMMC write and erase code is in Digitakt II 1.17 and Digitone II 1.11/1.12; whether their Data API sizes a write the same way is not read)
- **Area:** storage, MidiRpc Data API
- **Symptom:** none with Elektron Transfer, which sends the slot size. A host that declares a larger size writes upward from the slot through the next slots, the project pool, the COKi state copies (`0x7a000`) and the working project (`0x7e000`) up to the card's end.
- **Trigger:** a Data API write (samples, projects, sounds) whose import header declares more bytes than the slot holds (the u32 at +`0x19`, copied without a compare in `0x4010b4de`).
- **Cause:** the start comes from the path, the size from the host; the block write `0x4010f7f8` checks only the card capacity, and the block erase `0x4010f52a` checks nothing (a count of 0 makes the end sector `sector - 1`).
- **Workaround:** a host client must bound the size to the slot; digikit's card guard hooks both entries and refuses a request outside the stock area `[0, 0x180000)` (emulator-tested).
- **Test tip:** back up the +Drive card before you test any tool that writes samples or sounds into the stock slots.
- **Found by:** digikit (read from the code; not reproduced on a unit)
- **Status:** open in stock
- **Evidence:** `[doc]` {digikit-1121}

## Looks like a bug, is not

These trip tests but are hardware or design, not defects:
- **Monomachine 1.32B: MIDI Stop is a pause**, and LOAD SONG is silently ignored until the panel's STOP is pressed ([machinedrum-monomachine.md](devices/machinedrum-monomachine.md)).
- **Memory is not cleared at power-on:** DSP DDR on the Digitone II can hold a NaN that silences a feedback path
  ([I8](INCIDENTS.md#i8-power-on-ddr-holds-garbage-often-a-nan)); the Rytm's mod regions are not cleared either.
  Initialise everything you read.
- **A second application on the port** cuts or mixes SysEx replies
  ([I9](INCIDENTS.md#i9-a-second-application-on-the-port-corrupts-sysex-replies)).
- **A soft reset leaves the Octatrack's USB controller running**
  ([I7](INCIDENTS.md#i7-a-soft-reset-leaves-the-usb-controller-running)).
- **Analog Rytm MKII 1.74: a muted track still plays incoming MIDI notes**, and the machine list loads each machine as you scroll with no undo; both are design ([analog-rytm.md](devices/analog-rytm.md#modwerk-rytm-modules-and-stock-behaviour-os-174-2026-11-10-modwerk-rytm-modtests)).
- **Octatrack PART RELOAD restores the whole Part** from its SAVE PART copy, so every track on it reverts, and it needs a SAVE PART first (KYOTI's per-track reload works around this).
- **Projects saved by a mod** may stall stock or a newer build if their values no longer fit
  ([I28](INCIDENTS.md#i28-a-select-value-outside-its-count-stalled-the-sequencer)); that is the mod's data, not a stock bug.
