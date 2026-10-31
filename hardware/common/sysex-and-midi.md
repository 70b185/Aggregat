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

## The live Transfer protocol, MidiRpc (Digitakt II 1.16/1.17; digikit `docs/MIDI-SYSEX-RPC.md`) {digikit-rpc}
This is what Elektron Transfer and Elektroid speak to a running Digitakt II or Digitone II over USB MIDI. No menu setting or handshake is needed. Close Transfer and Overbridge first if they hold the port.

**Frame.** `F0 00 20 3C 10 00 <8-in-7 packed body> F7`.
- Unpacked request body: `seq_hi seq_lo 00 00 type payload...`. **The two bytes after seq must be `00 00`.** A non-zero byte there and the unit never replies.
- Unpacked reply: `counter16 seq16 (type|0x80) payload...`. The first pair is a device-side counter, not the seq; the echoed seq is the second pair.
- The whole body is 8-in-7 packed, one collector per 7 bytes. Short bodies (Ping, `ReadDir /`) look unpacked, which misled early tools. Longer payloads must be packed or the unit answers "Invalid path".
- All integers are big-endian, strings are NUL-terminated (< 256 bytes), and no checksum is used.
- Status: hardware round-trip `[hw]` for Ping, SoftwareVersion ("1.16"), DeviceUID, StorageSpace and ReadDir; the rest `[emu]`.

**The 44 commands the unit advertises** (the Ping reply lists them, then the name "Digitakt II"):
| Group | Types |
|---|---|
| Info/control | Ping `01`, SoftwareVersion `02`, DeviceUID `03`, **Screenshot `04`**, StorageSpace `05`, TempoRead `06`, TempoWrite `07`, Query `09` (feature keys such as `sample_file.interleaved_stereo_support`) |
| +Drive files (by path) | ReadDir `10`, CreateDir `11` (mkdir -p), DeleteDir `12` (empty only), EnumerateFiles `13`, ListRam `17`, ClearRam `18`, Assign `19`, DeleteFile `20`, RenameFile `21`, GetFileInfo `22`/`23`/`28`, MemoryCompaction `29`, read Open/Close/Read `30`/`31`/`32` (+V2 `36`), write Open/Close/Write `40`/`41`/`42` (+V2 `46`) |
| Data objects (projects, soundbanks, kits) | DataList `53`, Read Open/Partial/Close `54`-`56`, Write Open/Partial/Close `57`-`59`, Move `5a`, Copy `5b`, Clear `5c`, Swap `5d`, Rename `5e` |
| OS upgrade | Start `50`, Write `51`, End `52` (see [`os-update-protocol.md`](os-update-protocol.md)) |
Not advertised and dead: all `FsRaw*` (unsandboxed paths) and DataSetTags `5f`. `[doc]`

**Facts you need when writing a client** `[emu]` unless marked:
- **Screenshot `0x04`** returns a 9-byte header (`01`, width 128, height 64, length 1024) plus the 1,024-byte OLED buffer (byte `(7 - y/8) + 8x`, bit `y mod 8`). It works the same on DN2 1.12. This is a no-mod way to see the screen remotely.
- **Writing a sample:**
  1. `CreateDir` the folder.
  2. `OpenFileForWrite 0x40`: `u32` (any value), then the path **with a leading slash**. A bare name creates a *folder*.
  3. `WriteFileV1 0x42`: handle, length, sequential offset, data.
  4. **`CloseFileWriter 0x41` takes the handle AND the byte count.** With the handle alone it fails.
- The firmware appends a 16-byte trailer and stores `content_hash(data ++ 16 zero bytes) | 1`, so a host can verify the upload. An idle writer is closed after 20 s, leaving a half file.
- Chunks of 2-16 KiB work in the emulator (limit ~100 KiB). Device tools keep 2,048 bytes until real USB timing is known.
- The device does no WAV conversion: send the native file (0x40-byte header, 48 kHz big-endian int16, see [`overbridge-usb.md`](overbridge-usb.md)).
- **StorageSpace** (drive 1 = +Drive) returns status, `u64` free and `u64` total.
- **ReadFileV1** layout is still unsettled (it returned no data in the emulator).
- **No wire-controlled memory read or write exists over MidiRpc.** Eight surfaces were audited (Data partial R/W, path resolvers, FsRaw, the backup streams, the route table, the full type factory). Live RAM is not reachable this way; the OS-upgrade path writes flash only. `[doc]`
- `F0 7E ...` always goes to the Sample Dump Standard handler. A Universal Device Inquiry gets `F0 7E 00 7C 00 F7` (WAIT), not an identity. `[hw]`
- **The factory debug console is on UART8, not MIDI:** `#HELLO`, `#READ`/`#WRITE` (an 11-name parameter table, not memory), `#DUMP_AUDIO`, `#ENTER_TEST_MODE`, `#MRAM_DUMP` (a fixed 13.8 MiB factory/calibration blob, magic "COKi"), `#MMCDUMP` (raw eMMC sectors). It is not known to be reachable from outside. **Agents: leave it alone.** `[doc]`

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

## Elektroid (dagargo) - a general sample/SysEx client
- Supported (README list): Analog Four MKI/MKII/Keys, **Analog Heat MKI/MKII/+FX**, Analog Rytm MKI/MKII, Digitakt I/II, Digitone I/II/Keys, Model:Cycles/Samples, Monomachine MKII, Syntakt, plus non-Elektron gear (Arturia, Casio CZ-101, Eventide, KORG, MFB, Moog, Novation, MIDI SDS samplers). No per-device capability table; `elektroid-cli info <device>` shows the compatible filesystems. `[doc]` {elektroid-readme}
- Connectors: `system` (local computer, for format conversion), `elektron`, `cz`, `sds`, `efactor_preset`. Elektron filesystem families: raw/sample (`raw`, `preset-raw`, `sample`), data (`data`, `project`, `preset`, `preset-takt-ii`, `sound`), memory (`ram`, `track`). The Digitakt II "Preset" filesystem is implemented as `preset-takt-ii`. `raw` and `data` are for testing only and not compatible with Transfer formats. A firmware `upgrade` command exists in the CLI (which devices is not stated). Device definitions come from `~/.config/elektroid/elektron/devices.json` if present. Elektron samples cannot be swapped. `[doc]` {elektroid-readme}
- Backends: ALSA MIDI and PulseAudio by default on Linux, RtMidi/RtAudio elsewhere. 2,506 commits, 19 open issues; no version shown on the page (altstrument lists v3.4, 2026-08-22).

## Where the official MIDI tables live (forum reports, not read from the manuals)
- Digitakt (mk1) manual: **Appendix A** lists sound parameters with CC numbers; high-resolution control needs NRPN, which is **four CC messages** (CC 99 = NRPN MSB, CC 98 = NRPN LSB, CC 6 = data MSB, CC 38 = data LSB), the MSB/LSB per parameter come from the manual; "Receive CC/NRPN" must be enabled under SETTINGS > MIDI CONFIG > PORT CONFIG. Digitone (mk1): Appendix B (MIDI implementation), ratio offsets are in a table B.3, CC 70-77 drive the MIDI track's CC value parameters. A forum user reports that the Digitakt II manual lists no CC values for the Euclidean sequencer parameters and that some Euclidean NRPNs misbehaved before OS 1.10 ("Some NRPN parameters regarding the Euclidean sequencer didn't work as intended" is in the 1.10 notes). The Octatrack is said to be the only Elektron device that answers a CC request. Manuals are updated with every OS - always use the one for the OS in hand. `[?]` {elektronauts-dt2-sample-slot} {elektronauts-heat-midi} {elektron-dt2-notes}

