# Flash procedure and link pitfalls (Digitone II, as practised by dn2mk2 and dnfw)

Synthesised from the dn2mk2 `docs/SAFETY.md` and dnfw `docs/flashing.md` (second-hand, see SOURCES). The device buttons are the same
family-wide (FUNC at power-on, TRIG 4), but the numbers (timings, sections) are Digitone II facts. Re-check before applying to another device.

## Two routes onto the unit
| Route | How | What it writes | Notes |
|---|---|---|---|
| Normal update | Drag the `.syx` onto the **running** unit with Elektron Transfer over USB | the running MAIN OS | dnfw's test images were accepted this way and booted |
| Recovery | FUNC at power-on -> TRIG 4 (OS UPGRADE) -> Transfer SysEx window / legacy OS upgrade over **5-pin DIN MIDI to MIDI IN** (USB MIDI does not work) | goes through the bootstrap (section 2 of the last OS flashed), so it works when MAIN OS is broken | the only route that does |
`[doc]` {dn2-flashing} {dn2mk2-safety}

## Numbers
- MIDI DIN runs at 31,250 baud, about 3,125 bytes/s; a 2,209,184-byte image needs at least ~12 minutes (derived, not timed). Do not interrupt. `[doc]` {dn2-flashing}
- Nothing is written until reception completes. The receiver has **no error recovery**: a bad sequence number or checksum freezes the progress bar with no message and no retransmit. Checksums and sequence counters are content-independent, so the receiver cannot tell a modified image from stock. `[doc]` {dn2-flashing} {dn2mk2-safety}

## The "stalls at ~80 %" problem
- Reported 2026-09-11: Transfer showed 100 % sent while the device bar froze near 80 %; stock 1.10E stalled over the same route, so the link was at fault, not the image. Root cause in that case: a Focusrite Scarlett 4i4's MIDI went idle mid-transfer and dropped packets; the stall point varied (30/70/80 %). `[hw]` {dn2-flashing}
- Fixes: prove the link with the **stock** firmware first; use a dedicated class-compliant USB-MIDI cable for long recovery transfers; disable Windows USB selective suspend and device power management; retry. `[hw]` {dn2-flashing} {dn2mk2-safety}
- Proven on hardware: stock 1.10E via recovery (2026-09-08), stock 1.11 via recovery over a fixed link (2026-09-11); modified images via the normal update path. dnfw records **no modified image completing the recovery route** - recovery has been proven with stock only. `[hw]` {dn2-flashing}

## Rehearsal before the first modified flash
1. Back up everything with Elektron Transfer (and the +Drive).
2. If the unit is on 1.10 (any sub-version), update to stock 1.11 first and do it alone: the 1.10 -> 1.11 upgrade rewrites the bootstrap (1.10E rebuilt it and moved its load address; 1.11 changed it again), so later builds can carry 1.11's bootstrap byte for byte. `[doc]` {dn2mk2-safety}
3. Prove recovery on stock: DIN cable from the computer's MIDI OUT to the unit's MIDI IN, FUNC at power-on, TRIG 4, send the stock file for the exact version (~12 min). Note the interface - it becomes your recovery cable.
4. Confirm the unit boots stock and plays normally. Flash nothing modified until step 3 has worked once. `[doc]` {dn2mk2-safety}

## Every flash
1. Build; run the project's gate so the exact file is cleared (dn2mk2: `scripts/ship_gate.py` prints `CLEARED TO FLASH` and records the file's SHA-256; `dnfw preflight stock.syx build.syx` must print `PASS`). Verify the hash on the machine you flash from (`certutil -hashfile FILE SHA256` on Windows).
2. Back up the +Drive.
3. Flash via USB Transfer on the running unit. Keep the DIN cable within reach with nothing sending on it.
4. Play at low volume (no headphones, monitors down). Engines in dn2mk2 sanitise output (NaN/inf to 0, hard clamp).
5. Run the regression check (~10 minutes): boots without an EXCEPTION screen; each stock track type (FM Tone, FM Drum, WaveTone, Swarmer, MIDI) plays as before; chorus/delay/reverb sends and master overdrive/compressor work; pattern change, song mode, parameter lock, LFO on a stock machine; SAVE PROJECT, power-cycle, reload with all data back; Overbridge/USB audio if used; then the feature's own test.
6. If anything is wrong, recover to stock and report what you saw.
`[doc]` {dn2mk2-safety}

## Practices from dnfw
- Back up with the `.dnx` backup before flashing; run `dnfw inspect` on the exact file you will send (build and patch only refuse output that does not verify).
- Keep the unmodified `.syx` in a firmware folder and never overwrite it with build output.
- **Change one thing per flash.**
- Do not patch the key material.
- Do not start a flash on a crashing host (a previous workstation's `0x9F` crashes were tied to an NVIDIA driver).
- The log records what was sent, not what is resident: write a row when stock goes back on.
`[doc]` {dn2-flashing}

## Risks and mitigations (dn2mk2 table)
| Risk | Mitigation |
|---|---|
| DSP code runs in the emulator but fails on silicon (DSP silence until power cycle) | `scripts/gate_hwrules.py` (complex-ping's `hwrules.py`, MIT) checks DSP code for violations stock lacks |
| Bootstrap (section 2) damaged: permanent brick without a hardware programmer | refuse builds where sections 2, 4, 5 or 8 differ from stock by any byte; mods change only sections 3 (MAIN OS) and 7 (DSP) |
| Power lost during flash (as bad as a bootstrap brick) | stable power; do not touch the unit during "UPGRADING... DO NOT TURN OFF" |
| Build crashes MAIN OS or will not boot | recovery via bootstrap; every build boots in the emulator first (`scripts/emu_boot_check.py`) |
| DSP stops, unit silent | recoverable by reflash; run the SHARC emulator first; use only instruction encodings found in stock |
| Stock machines/FX/sequencer change by accident | check that all 16 track buffers are bit-identical to stock; assert ColdFire edits against stock bytes |
| Project/sound data damaged | back up the +Drive; no direct +Drive writes; test in a scratch project |
`[doc]` {dn2mk2-safety}
