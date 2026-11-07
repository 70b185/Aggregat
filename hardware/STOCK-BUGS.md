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
[Model:Cycles](#modelcycles) · [Monomachine](#monomachine) · [Looks like a bug, is not](#looks-like-a-bug-is-not)

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
- **Workaround:** fixed by BATCH_BUGFIXES (`EMPTY_PATTERN_LED_FIX`) under [PTN]; under [BANK] it stays as stock, because scanning 256 patterns' locks on every LED refresh starved the CPU.
- **Test tip:** do not overwrite a "free" pattern slot in a test project without checking for locks.
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
- **Trigger:** erase the last remaining lock of a trigless lock.
- **Cause:** not described in the source.
- **Workaround:** fixed by octatrack-kyoti-fw's ERASE_EMPTY_TRIGLESS_LOCKS (a deliberately empty trigless lock placed with FUNC + TRIG is left alone).
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

## Looks like a bug, is not

These trip tests but are hardware or design, not defects:
- **Memory is not cleared at power-on:** DSP DDR on the Digitone II can hold a NaN that silences a feedback path
  ([I8](INCIDENTS.md#i8-power-on-ddr-holds-garbage-often-a-nan)); the Rytm's mod regions are not cleared either.
  Initialise everything you read.
- **A second application on the port** cuts or mixes SysEx replies
  ([I9](INCIDENTS.md#i9-a-second-application-on-the-port-corrupts-sysex-replies)).
- **A soft reset leaves the Octatrack's USB controller running**
  ([I7](INCIDENTS.md#i7-a-soft-reset-leaves-the-usb-controller-running)).
- **Projects saved by a mod** may stall stock or a newer build if their values no longer fit
  ([I28](INCIDENTS.md#i28-a-select-value-outside-its-count-stalled-the-sequencer)); that is the mod's data, not a stock bug.
