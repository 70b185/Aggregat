# SysEx and MIDI control (talking to a unit without flashing it)

Everything here concerns the **control side** - patterns, presets, parameters. It is separate from firmware images (`firmware-container.md`).
Elektron has not published the pattern/sound SysEx formats; all of it is reverse-engineered. Tags as in `../README.md`.

## Official
- Each device's manual contains the MIDI implementation (CC and NRPN tables, "Appendix B" in the Digitakt II manual for OS 1.03 per the MCP project). These are the only vendor-documented parts. `[doc]` {digitakt-midi-mcp}
- Elektron Transfer is the official tool for dumps, backups and OS upgrades; its legacy OS-upgrade mode is the DIN-MIDI path. {elektron-dt2-notes}

## Framing and encoding
- SysEx frame starts `F0 00 20 3C` (Elektron manufacturer ID `00 20 3C`), then device ID and command. `[doc]` {digitakt-midi-mcp} {syxgrid}
- Elektron uses its own **7-bit encoding** of 8-bit data, ported from elk-herd into SYXGRID and digi-roll-studio. Decode before analysing dumps, otherwise nothing makes sense. `[doc]` {syxgrid} {digi-roll-studio}
- Digitone mk1 device ID is `0x0D`; its pattern format differs from Digitone II and SYXGRID rejects it. The DN2 device ID byte is not stated. `[doc]` {syxgrid}
- Two protocol generations: the Digitakt II / Digitone II speak "gen-2"; Analog Four speaks "gen-1" with a different pattern format and a slower wire. `[doc]` {digi-roll-studio}
- Digitone II library contains Digitone mk1 preset files, which use a second container format (refuse foreign formats by magic bytes). `[doc]` {digi-roll-studio}
- Container structure and checksums for older machines are best documented in libanalogrytm (Analog Rytm only; no Analog Heat). `[doc]` {libanalogrytm}

## Reverse-engineered format maps
| Source | Covers | Quality marker |
|---|---|---|
| SYXGRID `sysexmap/` (CC BY 4.0) | Digitone II pattern SysEx, 45 mappings, v1.13.0 | A = hardware-confirmed (23), B = corpus-confirmed (12), C = inherited (9), D = unknown, do not rely (1); anything below A may be wrong |
| digitone-syx-toolkit | Digitone II PATTERN: trig slots, step state tables, tempo/speed/total steps; length `0xFF` = inherit, `0x7F` = explicit INF, `0x00..0x7E` finite | hardware-validated for tracks 1-8, steps 1-128, normal trigs |
| digi-roll / digi-roll-studio | Digitakt II + Digitone II patterns, trig conditions, p-lock lanes, pattern settings; +Drive file API | verified against 34 real dumps and on hardware |
| elk-herd (mzero) | codec and framing, "de-facto public documentation" | moved off GitHub, README rejects AI-generated issues/PRs |

Not decoded yet (per SYXGRID): parameter locks, sound parameters (filter, amp, FX, LFO), synth machine choice. `[doc]`

## Safe writing to a unit (digi-roll-studio's ceremony - copy it)
1. Re-read and back up the whole destination pattern first; abort if the backup fails.
2. The target's OS build must be on an allowlist.
3. The user confirms a dialog listing the changes.
4. Change only the bytes that must change.
5. Read the result back and byte-compare.
Also: keep a local stash of overwritten patterns (50) plus pre-restore snapshots (10). `[hw]` {digi-roll-studio}

## +Drive file API (as found by digi-roll-studio)
Commands `0x57/0x58/0x59` (file write) verified on hardware for a single chunk and kept behind a separate allowlist, writes above 16 KiB refused; `0x5A/0x5B/0x5C` (move/copy/delete) not implemented anywhere in that workspace. `[hw]` {digi-roll-studio}

## Operating notes
- Digitone II must be in SYSEX RECEIVE mode to accept a pattern; it lands in the slot selected on the device; queued patterns land consecutively; raise the gap (ms) if large dumps lose trigs. `[doc]` {syxgrid}
- Web MIDI needs Chromium over HTTPS/localhost; Chrome/Edge 152 break SysEx receive on macOS (sending works). `[doc]` {syxgrid}
- NRPN groups (Digitakt II, MCP project): MSB 1 = track/trig/source/filter/amp, MSB 2 = FX, MSB 3 = trig note/velocity/length. Sample select is NRPN MSB 1 / LSB 3 per one forum user, who found that sample-slot control by NRPN looked broken and that a separate "sample slot" + "bank" CC pair may be the real route. `[?]` {digitakt-midi-mcp} {elektronauts-dt2-sample-slot}
- External sequencing: the Digitakt needed MIDI Start + clock pulses + Stop to play when externally controlled (MCP project note). `[doc]` {digitakt-midi-mcp}
- Sample swapping via CC happens on the **next** trigger, not on a trigger that sends the CC (forum report). `[?]` {elektronauts-dt2-sample-slot}
- Overbridge (USB multitrack audio + parameter control) is proprietary; Overwitch reimplements the audio side on Linux for Overbridge-2 devices incl. Analog Heat. {overwitch}

## Rules for agents
- Never write to a unit's storage with an unverified format: back up via Transfer first, work on throwaway projects, read back and compare.
- Treat every "best-guess" request format as unsafe until you have captured the real traffic with a MIDI monitor.
- Do not use libraries that parse a different device generation (Digitone mk1 vs II, Analog Four gen-1 vs gen-2) - the formats differ.
