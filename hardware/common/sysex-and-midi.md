# SysEx and MIDI control (talking to a unit without flashing it)

Everything here concerns the **control side** - patterns, presets, parameters. It is separate from firmware images (`firmware-container.md`).
Elektron has not published the pattern/sound SysEx formats; all of it is reverse-engineered. Tags as in `../README.md`.

## Official
- Each device's manual contains the MIDI implementation (CC and NRPN tables, "Appendix B" in the Digitakt II manual for OS 1.03 per the MCP project). The tables of the current Digitakt II, Digitone II and Analog Heat +FX manuals are transcribed below under "Official CC and NRPN tables". These are the only vendor-documented parts. `[doc]` {digitakt-midi-mcp}
- Elektron Transfer is the official tool for dumps, backups and OS upgrades; its legacy OS-upgrade mode is the DIN-MIDI path. {elektron-dt2-notes}

## Framing and encoding
- SysEx frame starts `F0 00 20 3C` (Elektron manufacturer ID `00 20 3C`), then device ID and command. `[doc]` {digitakt-midi-mcp} {syxgrid}
- Elektron uses its own **7-bit encoding** of 8-bit data, ported from elk-herd into SYXGRID and digi-roll-studio. Decode before analysing dumps, otherwise nothing makes sense. `[doc]` {syxgrid} {digi-roll-studio}
- Digitone mk1 device ID is `0x0D`; its pattern format differs from Digitone II and SYXGRID rejects it. The DN2's is `0x15`. All known device bytes: [firmware-container.md](firmware-container.md#sysex-device-byte-per-device-merged-from-the-projects-that-decode-these-files). `[doc]` {syxgrid}
- Two protocol generations: the Digitakt II / Digitone II speak "gen-2"; Analog Four speaks "gen-1" with a different pattern format and a slower wire. `[doc]` {digi-roll-studio}
- Digitone II library contains Digitone mk1 preset files, which use a second container format (refuse foreign formats by magic bytes). `[doc]` {digi-roll-studio}
- Container structure and checksums for older machines are best documented in libanalogrytm (Analog Rytm only; no Analog Heat); the frame, packing and checksum match the newer devices, the type bytes do not (section "Dump messages and device ids across generations" below). `[doc]` {libanalogrytm}

## Reverse-engineered format maps
| Source | Covers | Quality marker |
|---|---|---|
| SYXGRID `sysexmap/` (CC BY 4.0) | Digitone II pattern SysEx, 45 mappings, v1.13.0 | A = hardware-confirmed (23), B = corpus-confirmed (12), C = inherited (9), D = unknown, do not rely (1); anything below A may be wrong |
| digitone-syx-toolkit | Digitone II PATTERN: trig slots, step state tables, tempo/speed/total steps; length `0xFF` = inherit, `0x7F` = explicit INF, `0x00..0x7E` finite | hardware-validated for tracks 1-8, steps 1-128, normal trigs |
| digi-roll / digi-roll-studio | Digitakt II + Digitone II patterns, trig conditions, p-lock lanes, pattern settings; +Drive file API | verified against 34 real dumps and on hardware |
| elk-herd (mzero) | codec and framing, "de-facto public documentation" | moved off GitHub, README rejects AI-generated issues/PRs |

Not decoded yet (per SYXGRID): parameter locks, sound parameters (filter, amp, FX, LFO), synth machine choice. `[doc]`

## Dump messages and device ids across generations (task T22, 2026-11-02)
Compared: libanalogrytm (Analog Rytm, 2014) against digi-roll's protocol notes (Digitakt, Digitakt II, Digitone II, from elk-herd and captures on units) and syxgrid's Digitone II map. Restated facts, no code copied.

- **One dump frame for every generation compared:** `F0 00 20 3C <device> <dev id> <type> 01 01 <index> <packed payload> <checksum hi lo> <count hi lo> F7`. The Rytm writes the same `01 01` version field ("OS 1.02c" in libanalogrytm), the same index byte and the same trailer. `[doc]` {libanalogrytm-sysex} {digi-roll-protocol}
- **The same 7-bit packing:** groups of one header byte plus up to 7 data bytes; header bit 6 holds the MSB of the first data byte, bit 0 that of the seventh; a short last group keeps its header. syxgrid's DN2 field "control byte 101506, mask `0x40`, payload 101507" is exactly this rule (first byte of a group). `[doc]` {libanalogrytm-sysex} {digi-roll-protocol} {syxgrid-map}
- **The same checksum and count:** checksum = sum of the **packed** payload bytes (header bytes included) mod 2^14, sent as two 7-bit bytes, high first; count = packed length + 5 (checksum, count and `F7`), also mod 2^14. syxgrid recomputed the checksum over raw bytes `[10, 114113)` and matched the DN2's own on every fixture. A DN2 pattern message is 114,118 bytes, so its count field wraps; tools must not use it as a length. `[doc]` {libanalogrytm-sysex} {digi-roll-protocol} {syxgrid-map}
- **Requests:** an empty payload, trailer `00 00 00 05` (checksum 0, count 5) on both generations; the Rytm's request is 15 bytes, `F0 00 20 3C 07 00 <id> 01 01 <nr> 00 00 00 05 F7`. `[doc]` {libanalogrytm-sysex} {digi-roll-protocol}
- **The type bytes differ, so never reuse a type table across devices:**
  - Rytm: dumps `0x52` kit, `0x53` sound, `0x54` pattern, `0x55` song, `0x56` settings, `0x57` global; `0x58-0x5D` the same objects from the unsaved work buffer; requests `0x62-0x6D` the same way.
  - Digitakt / Digitakt II / Digitone II: `0x50` pattern plus kit in one message, `0x51` pattern, `0x52` kit, `0x53` sound, `0x54` project settings; requests `0x60-0x64`, and `0x6F` asks for the whole project.
  - So `0x54` is a Rytm pattern but a DT2/DN2 project-settings message. syxgrid's guess "`0x53` = kit" for the DN2 (graded D, unknown) is a sound dump by digi-roll's table. `[doc]` {libanalogrytm-sysex} {digi-roll-protocol} {syxgrid-map}
- **The index byte on receive:** a DN2 stores a received pattern in the slot armed on the device, not in the index the message carries (syxgrid, on a unit). libanalogrytm does not say what a Rytm does with it. `[hw]` {syxgrid-map}
- **Device byte in dumps:** Rytm (libanalogrytm's era, MKI) `0x07`; Digitakt `0x0A`; Digitakt II `0x14`; Digitone II `0x15`. A DN2 answered only `0x15` in a sweep and ignored `0x0B-0x0E`, `0x14` and `0x16`. The same bytes appear in the OS files ([`firmware-container.md`](firmware-container.md)). `[doc]` {libanalogrytm-sysex} {digi-roll-protocol}

**Three different device ids.** They are easy to mix up, and the same number means different devices in different namespaces:

| Device | SysEx device byte (dumps, OS files) | Product id (RPC `Device` reply; Elektron's FAQ table) | Overbridge USB product id |
|---|---|---|---|
| Analog Heat | - | `0x0A` | `0x0B50` |
| Digitakt | `0x0A` | `0x0C` | `0x0B2C` |
| Digitone | `0x0D` | `0x14` | `0x0B36` |
| Analog Heat MKII | - | `0x16` | `0x0B52` |
| Analog Heat +FX | `0x13` | `0x20` | `0x0B53` |
| Digitakt II | `0x14` | `0x2A` | `0x0B2B` |
| Digitone II | `0x15` | `0x2B` | `0x0B34` |

- `0x14` is the Digitakt II's SysEx byte but the Digitone mk1's product id; `0x0A` is the Digitakt's SysEx byte but the Analog Heat's product id. Name the namespace whenever you write an id down.
- Elektroid reads the product id from byte 5 of the decoded `Device` (Ping) reply and looks it up in its device table; digi-roll captured 42 and 43 from a DT2 and a DN2 the same way. The FAQ table on elektron.se (Heat `000A`, Digitakt `000C`, Digitone `0014`, Heat MKII `0016`, Model:Samples `0019`, Model:Cycles `001B`, Digitone Keys `001C`) matches Elektroid's table entry for entry, so that table lists product ids. `[doc]` {elektroid-devices} {digi-roll-protocol} {elektron-faq}
- Elektroid's further product ids: Analog Four `0x04`, Analog Keys `0x06`, Analog Rytm `0x08`, Analog Four MKII `0x0E`, Analog Rytm MKII `0x10`, Syntakt `0x1E`. Overwitch's Overbridge ids: Analog Four MKII `0x0B47`, Analog Rytm MKII `0x0B48`, Digitone Keys `0x0B35`, Syntakt `0x0B4A`. digikit read the DT2's USB ids from the image: `0x012B` (USB MIDI), `0x102B` (audio/MIDI), `0x0B2B` (Overbridge), so the low byte is shared across modes. `[doc]` {elektroid-devices} {overwitch-devices} {digikit-f42}

- **Identifying a unit on a DIN port (elkbench, 2026-11-14):** the stock OS answers neither the RPC Ping nor a MIDI Identity Request over DIN, so elkbench sends the working-kit dump request on each DIN interface and reads the device byte in the reply; a Digitone's DIN SysEx reply arrives later than over USB, so allow about 8 s. `[doc]` {elkbench-readme}

## Digitone II pattern dump: hardware-confirmed offsets (syxgrid's map v1.13.0, CC BY 4.0, facts restated) {syxgrid-map}
syxgrid grades 45 mappings A (hardware-confirmed) to D (unknown). Only the 23 level-A facts are listed here; read the source for B/C/D and the evidence. `[hw]`
- **Message:** product byte `0x15`, message type `0x50` (pattern). A pattern dump is 114,118 bytes. The body from raw byte 10 to 114113 is 7-bit packed (one control byte per 7 payload bytes); "decoded" offsets below are into the unpacked payload.
- **Slot:** raw byte 9 is the slot the device dumped from (0 = A01 ... 127 = H16), **not a destination**. A received pattern is stored in the slot **armed on the device**, advancing by one per pattern.
- **Step states:** at decoded `4 + 1187*(track-1) + 2*(step-1)`, two bytes per step, 16 tracks x 128 steps.
  - Odd-step trig `03 81`, even-step trig `03 91`. `03 90` / `03 80` (bit 0 clear) is not an occupied step.
  - First byte `0x78` = trigless trig (parameter automation, no note).
- **Trigger records:** at decoded `18996`, 6 bytes each, up to 8,192 records.
  - Fields: track, step, note, velocity (`0xFF` = track default), length index (`0xFF` = inherit), and a signed micro-timing byte (1/384 note, -23..+23).
  - A record is free when its track byte is `0xFF`; nothing terminates the table, so skip and keep scanning.
  - Chords are stored as all primary notes first, then all chord extras.
- **Track type bitmask** at decoded `99348-99349`, big-endian, bit i = track i+1, 1 = MIDI track.
- **Machine per track** at `89160 + 359*(track-1) + 232`: 0 FM TONE, 1 WAVETONE, 2 FM DRUM, 3 SWARMER, 4 MIDI.
- **MIDI channel per track:** the enabled flag is at `95064 + 268*(track-1) + 245`, the channel (0-15) at `... + 82`.
- **Pattern length:** raw payload byte 101507 (control byte 101506, mask `0x40`), 1-128 steps.
- **Playback needs a clock:** `0xF8` at 24 ppqn, `0xFA` start, `0xFC` stop. Program Change 0-127 on the program-change-in channel selects A01-H16.

## The live Transfer protocol, MidiRpc (Digitakt II 1.16/1.17; digikit `docs/MIDI-SYSEX-RPC.md`) {digikit-rpc} `[doc]`
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

## Digitone II specifics and client pitfalls (dnfw `midi-rpc.md`, live on a DN2 1.11) {dn2-midirpc}
- The DN2 answers the same MidiRpc framing: Ping replies with 22 command codes and the name "Digitone II". DNX reports the same set on 1.10E. **The file-API product id is `0x2b`; the dump protocol calls the same unit `0x15`.** `[hw]`
- **The DN2 does not answer the MIDI Universal Device Inquiry** at all. The DT2 answers it with an SDS WAIT. `[hw]`
- **A second application on the port corrupts replies:** with Overbridge holding the port, replies were cut at exactly **885 bytes**, and with Transfer open a preset list showed 35 of 256. Close Transfer, Overbridge and DNX before a client run. `[hw]` ([I9](../INCIDENTS.md#i9-a-second-application-on-the-port-corrupts-sysex-replies))
- Windows client bug, silent: using `MIM_ERROR` (0x3C5) instead of `MIM_LONGDATA` (0x3C4) drops every SysEx reply while short messages still arrive. Validate a client against a known reply first (rule A31). `[hw]`
- Screenshot `0x04` returns the 128x64 frame; polling it gives a live mirror of the screen. `[hw]`
- **The same screen request works on more devices:** Elek View, a browser port of screendump that sends the request in the `F0 00 20 3C 10 00` RPC framing, was tested on a Digitakt II and a Model:Cycles, and its author reports an Analog Heat MKII working too. So the Heat MKII speaks this RPC framing; whether the Heat +FX does is a stock test (HYPOTHESES H18). `[doc]` {elek-view}
- **Project files (`.dt2prj`, `.dn2prj`, also Model:Samples/Cycles) are renamed zip files** holding a compressed project image named after the project, a `manifest.json` and, on sampling devices, a samples folder. Decompress-recompress scripts round-tripped projects that then loaded on DN2, DT2, M:S and M:C (forum post, no log); the compression is LZ4 according to syxgrid's author. `[doc]` {em-dx2-scripts}

## The panel wire protocol (digikit finding 58, DT2 1.17 / DN2 1.12) {digikit-f58} `[doc]`
- The panel MCU sends **2-byte packets on UART8**:
  - key packet: `0x20 | channel`, then the channel's 8-bit button mask;
  - encoder packet: `0x30 | (encoder-1)`, then a signed 8-bit delta;
  - high nibble 7: the factory console.
- Key code = `channel*8 + bit + 1` (codes 1-48, plus a few exceptions per device). There are nine encoders.
- Toward the panel: `B9 idx val` sets an LED to a palette entry, `B5 i r g b` sets a palette entry.
- **Remote control without touching the UART:** the firmware's button decoder `f(channel, new_mask)` (DT2 1.17 `0x4011e318`, DN2 1.12 `0x4011fc8c`) and encoder decoder `f(encoder0, delta)` (`0x4011e598` / `0x4011ff0c`) can be called from a mod.
  - Mask SR to `0x2700` around the call; the decoders do unprotected read-modify-write.
  - Neither checks the channel (safe: buttons 0-6, encoders 0-8). An encoder turn is ignored for 40 ticks after its click key is released. `[emu]`

## Hardware ports and the hidden service console (DT2 1.16 / DN2 1.11) {digikit-f25} {dn2-service}
- **DIN MIDI runs on UART9** (`0xec074000`, 31,250 baud, receive by eDMA channel 36). The front panel talks over **UART8** (`0xec070000`). Panel key codes used by emulators: SETTINGS 8, FUNC 17, YES 10, NO 12, UP 11, DOWN 14, LEFT 13, RIGHT 15. `[emu]`
- **Maintenance mode** (a power-on key combination, or a reboot marker) presents a **USB CDC-ACM serial port, VID `0x1935` PID `0xFFFF`**. It speaks a line protocol: `#COMMAND\n` text lines, `!` + 4-byte big-endian length for binary frames.
  - About 60 factory commands. Read-only examples: `#HELLO` (answers "HOW DO YOU DO?"), `#STATUS` (reports `PLATFORM PCBA0109..`, `PRODUCT 52;5;15;Digitone II`), `#READ_SERIAL` (the "SERI" record at flash `0x3C0000`).
  - **Writing commands change persistent state:** `#WRITE_SERIAL`, `#WRITE_TESTED`, `#WRITE_UI_TESTED`, `#WRITE_AUDIO_TESTED`, `#MMC_RECONFIGURE`, `#WRITE`, `#UPGRADE`, `#FULL_UPGRADE` (unchecked flash path, see `os-update-protocol.md`).
  - **Agents never send these.** `[doc]`

 (digi-roll-studio's ceremony - copy it)
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

## Elektroid (dagargo) - a general sample/SysEx client {elektroid-readme}
- Supported (README list): Analog Four MKI/MKII/Keys, **Analog Heat MKI/MKII/+FX**, Analog Rytm MKI/MKII, Digitakt I/II, Digitone I/II/Keys, Model:Cycles/Samples, Monomachine MKII, Syntakt, plus non-Elektron gear (Arturia, Casio CZ-101, Eventide, KORG, MFB, Moog, Novation, MIDI SDS samplers). No per-device capability table; `elektroid-cli info <device>` shows the compatible filesystems. `[doc]` {elektroid-readme}
- Connectors: `system` (local computer, for format conversion), `elektron`, `cz`, `sds`, `efactor_preset`. Elektron filesystem families: raw/sample (`raw`, `preset-raw`, `sample`), data (`data`, `project`, `preset`, `preset-takt-ii`, `sound`), memory (`ram`, `track`). The Digitakt II "Preset" filesystem is implemented as `preset-takt-ii`. `raw` and `data` are for testing only and not compatible with Transfer formats. A firmware `upgrade` command exists in the CLI (which devices is not stated). Device definitions come from `~/.config/elektroid/elektron/devices.json` if present. Elektron samples cannot be swapped. `[doc]` {elektroid-readme}
- Backends: ALSA MIDI and PulseAudio by default on Linux, RtMidi/RtAudio elsewhere. 2,506 commits, 19 open issues; no version shown on the page (altstrument lists v3.4, 2026-08-22).

## Official CC and NRPN tables (transcribed from the manuals, task T13, 2026-11-11)

Elektron's own numbers, from the MIDI appendix of each current manual. Read as: `CC n` is the controller number (the manual's "CC MSB"), `(LSB m)` the second controller for the fine part of a high-resolution parameter, `NRPN a:b` the NRPN MSB and LSB. An NRPN is sent as four controllers: CC 99 = `a`, CC 98 = `b`, CC 6 = value MSB, CC 38 = value LSB. A parameter with no NRPN (or no CC) has none in the manual.

How this was transcribed, and how far to trust it: the tables were read from the PDFs by a text-extraction tool in two separate passes per manual (all rows once, then a sample of 26 to 40 rows again), and both passes agree. Rows that print fewer than four numbers were assigned to columns by the pattern of the fully printed rows (three numbers: CC, NRPN MSB, NRPN LSB; two: NRPN only; one: CC only). Nobody here has compared the result with the printed page by eye, and nothing was sent to a unit. Check a number against the manual before you ship a tool that depends on it.

Oddities that are in the manuals as extracted (possible misprints; a unit test would settle each):
- Digitakt II: Env. Depth and Env. Delay both print NRPN 1:23; Portamento On/Off and Euclidean Pulse Generator 1 both print NRPN 3:8; Input R Delay Send and Input R Chorus Send both print NRPN 2:35 (the Digitone II manual has 2:37 for the delay send). `[?]` {dt2-manual}
- Digitone II: AMP Decay Time and Sustain Level both print CC 86 (87 is unused in the table, so 87 is the likely value for Sustain Level). LFO 3 has NRPN numbers but no CC. `[?]` {dn2-manual}
- Analog Heat +FX: LFO1 Fade prints NRPN 1:60 where the pattern of its neighbours gives 1:69; COMP Release prints NRPN 2:21, the same as COMP Attack (pattern: 2:22); Expr. B Destination prints NRPN 1:108, the same as AMP Circuit Select. `[?]` {heatfx-manual}
- Digitakt II and Digitone II print the same Send FX and Mixer numbers (delay, reverb, chorus, compressor, external in), apart from the oddity above. On the Digitakt II the DELAY, REVERB, CHORUS and COMPRESSOR pages answer on the channel set as FX CONTROL CH (manual section 14.4.3); the Digitone II manual was not checked for this. `[doc]` {dt2-manual} {dn2-manual}
- High resolution: the Digitakt II manual says the speed and depth of LFO 1-3 are high-resolution parameters with CC LSB values; the Digitone II manual says high-resolution parameters cannot be controlled with CC and need NRPN. `[doc]` {dt2-manual} {dn2-manual}

### Digitakt II, manual for OS 1.17, Appendix B `[doc]` {dt2-manual}

- **Digitakt II B.1 Track:** Mute CC 94, NRPN 1:101; Track level CC 95, NRPN 1:100.
- **Digitakt II B.2 Trig:** Note CC 3, NRPN 3:0; Velocity CC 4, NRPN 3:1; Length CC 5, NRPN 3:2; Filter Trig CC 13; LFO Trig CC 14; Portamento Time CC 9, NRPN 3:7; Portamento On/Off CC 65, NRPN 3:8.
- **Digitakt II B.3 Source:** Tune CC 16, NRPN 1:0; Play Mode CC 17, NRPN 1:1; Sample Bank Select CC 24, NRPN 1:9; Sample Slot Select CC 19, NRPN 1:8; Data entry knob E (machine dependent) CC 20, NRPN 1:4; knob F CC 21, NRPN 1:5; knob G CC 22, NRPN 1:6; Sample Level CC 23, NRPN 1:7.
- **Digitakt II B.4 Filter:** Filter Frequency CC 74, NRPN 1:20; Data entry knob F (machine dependent) CC 75, NRPN 1:21; knob G CC 76, NRPN 1:22; Env. Depth CC 77, NRPN 1:23; Attack Time CC 70, NRPN 1:16; Decay Time CC 71, NRPN 1:17; Sustain Level CC 72, NRPN 1:18; Release Time CC 73, NRPN 1:19; Env. Delay CC 91, NRPN 1:23; Key Tracking CC 92, NRPN 1:69; Base CC 26, NRPN 1:51; Width CC 27, NRPN 1:52; Env. Reset CC 111, NRPN 1:68.
- **Digitakt II B.5 Amp:** Attack Time CC 79, NRPN 1:30; Hold Time CC 80, NRPN 1:31; Decay Time CC 81, NRPN 1:32; Sustain Level CC 82, NRPN 1:33; Release Time CC 83, NRPN 1:34; Env. Reset CC 88, NRPN 1:41; Mode CC 87, NRPN 1:40; Pan CC 90, NRPN 1:38; Volume CC 89, NRPN 1:39.
- **Digitakt II B.6 Euclidean sequencer (NRPN only):** Pulse Generator 1 NRPN 3:8; Pulse Generator 2 NRPN 3:9; Euclidean Mode On/Off NRPN 3:14; Rotation Generator 1 NRPN 3:11; Rotation Generator 2 NRPN 3:12; Track Rotation NRPN 3:13; Boolean Operator NRPN 3:10.
- **Digitakt II B.7 FX:** Bit Reduction CC 54; Overdrive CC 57; Sample Rate Reduction CC 55; SRR Routing CC 56; Delay Send CC 84, NRPN 1:36; Reverb Send CC 85, NRPN 1:37; Chorus Send CC 12, NRPN 1:35.
- **Digitakt II B.8 Mod:** LFO 1 Speed CC 102 (LSB 58), NRPN 1:42; LFO 1 Multiplier CC 103, NRPN 1:43; LFO 1 Fade In/Out CC 104, NRPN 1:44; LFO 1 Destination CC 105, NRPN 1:45; LFO 1 Waveform CC 106, NRPN 1:46; LFO 1 Start Phase CC 107, NRPN 1:47; LFO 1 Trig Mode CC 108, NRPN 1:48; LFO 1 Depth CC 109 (LSB 59), NRPN 1:49; LFO 2 Speed CC 112 (LSB 60), NRPN 1:50; LFO 2 Multiplier CC 113, NRPN 1:51; LFO 2 Fade In/Out CC 114, NRPN 1:52; LFO 2 Destination CC 115, NRPN 1:53; LFO 2 Waveform CC 116, NRPN 1:54; LFO 2 Start Phase CC 117, NRPN 1:55; LFO 2 Trig Mode CC 118, NRPN 1:56; LFO 2 Depth CC 119 (LSB 61), NRPN 1:57; LFO 3 Speed CC 78 (LSB 62), NRPN 1:58; LFO 3 Multiplier CC 52, NRPN 1:59; LFO 3 Fade In/Out CC 53, NRPN 1:60; LFO 3 Destination CC 28, NRPN 1:61; LFO 3 Waveform CC 29, NRPN 1:62; LFO 3 Start Phase CC 30, NRPN 1:70; LFO 3 Trig Mode CC 31, NRPN 1:71; LFO 3 Depth CC 86 (LSB 63), NRPN 1:72.
- **Digitakt II B.9 Send FX, delay:** Delay Time CC 21, NRPN 2:0; Pingpong CC 22, NRPN 2:1; Stereo Width CC 23, NRPN 2:2; Feedback CC 24, NRPN 2:3; Highpass Filter CC 25, NRPN 2:4; Lowpass Filter CC 26, NRPN 2:5; Reverb Send CC 27, NRPN 2:6; Mix Volume CC 28, NRPN 2:7.
- **Digitakt II B.9 Send FX, reverb:** Predelay CC 29, NRPN 2:8; Decay Time CC 30, NRPN 2:9; Shelving Freq CC 31, NRPN 2:10; Shelving Gain CC 89, NRPN 2:11; Highpass Filter CC 90, NRPN 2:12; Lowpass Filter CC 91, NRPN 2:13; Mix Volume CC 92, NRPN 2:15.
- **Digitakt II B.9 Send FX, chorus:** Depth CC 16, NRPN 2:41; Speed CC 9, NRPN 2:42; High Pass Filter CC 70, NRPN 2:43; Width CC 71, NRPN 2:44; Delay Send CC 12, NRPN 2:45; Reverb Send CC 13, NRPN 2:46; Mix Volume CC 14, NRPN 2:47.
- **Digitakt II B.10 Mixer, compressor:** Threshold CC 111, NRPN 2:16; Attack Time CC 112, NRPN 2:17; Release Time CC 113, NRPN 2:18; Makeup Gain CC 114, NRPN 2:19; Pattern Volume CC 119, NRPN 2:24; Ratio CC 115, NRPN 2:20; Sidechain Source CC 116, NRPN 2:21; Sidechain Filter CC 117, NRPN 2:22; Dry/Wet Mix CC 118, NRPN 2:23.
- **Digitakt II B.10 Mixer, external in:** Dual Mono CC 82, NRPN 2:40; Input L Level CC 72, NRPN 2:30; Input L Pan CC 74, NRPN 2:32; Input R Level CC 73, NRPN 2:31; Input R Pan CC 75, NRPN 2:33; Input L Delay Send CC 78, NRPN 2:36; Input R Delay Send CC 79, NRPN 2:35; Input L Reverb Send CC 80, NRPN 2:38; Input R Reverb Send CC 81, NRPN 2:39; Input L Chorus Send CC 76, NRPN 2:34; Input R Chorus Send CC 77, NRPN 2:35; Input L R Level CC 72, NRPN 2:30; Input L R Balance CC 74, NRPN 2:32; Input L R Delay Send CC 78, NRPN 2:36; Input L R Reverb Send CC 80, NRPN 2:38; Input L R Chorus Send CC 76, NRPN 2:34.
- **Digitakt II MIDI tracks, CC VAL:** VAL1 CC 70, NRPN 1:16; VAL2 CC 71, NRPN 1:17; VAL3 CC 72, NRPN 1:18; VAL4 CC 73, NRPN 1:19; VAL5 CC 74, NRPN 1:20; VAL6 CC 75, NRPN 1:21; VAL7 CC 76, NRPN 1:22; VAL8 CC 77, NRPN 1:23; VAL9 NRPN 1:60; VAL10 NRPN 1:61; VAL11 NRPN 1:62; VAL12 NRPN 1:63; VAL13 NRPN 1:64; VAL14 NRPN 1:65; VAL15 NRPN 1:66; VAL16 NRPN 1:67.
- **Digitakt II Misc:** Pattern Mute CC 110, NRPN 1:104; Sample Slot CC 19, NRPN 1:8; Sample Bank CC 24, NRPN 1:9; Master Overdrive CC 17, NRPN 2:37.

### Digitone II, manual for OS 1.12, Appendix C `[doc]` {dn2-manual}

- **Digitone II C.1 Track:** Mute CC 94, NRPN 1:108; Track level CC 95, NRPN 1:110.
- **Digitone II C.2 Trig:** Note CC 3, NRPN 3:0; Velocity CC 4, NRPN 3:1; Length CC 5, NRPN 3:2; Filter Trig CC 13; LFO Trig CC 14; Portamento Time CC 9, NRPN 3:6; Portamento On/Off CC 65, NRPN 3:7.
- **Digitone II C.3 Source, SYN page 1 (data entry knobs A-H, machine dependent):** A CC 40, NRPN 1:73; B CC 41, NRPN 1:74; C CC 42, NRPN 1:75; D CC 43, NRPN 1:76; E CC 44, NRPN 1:77; F CC 45, NRPN 1:78; G CC 46, NRPN 1:79; H CC 47, NRPN 1:80.
- **Digitone II C.3 Source, SYN page 2:** A CC 48, NRPN 1:81; B CC 49, NRPN 1:82; C CC 50, NRPN 1:83; D CC 51, NRPN 1:84; E CC 52, NRPN 1:85; F CC 53, NRPN 1:86; G CC 54, NRPN 1:87; H CC 55, NRPN 1:88.
- **Digitone II C.3 Source, SYN page 3:** A CC 56, NRPN 1:89; B CC 57, NRPN 1:90; C CC 58, NRPN 1:91; D CC 59, NRPN 1:92; E CC 60, NRPN 1:93; F CC 61, NRPN 1:94; G CC 62, NRPN 1:95; H CC 63, NRPN 1:96.
- **Digitone II C.3 Source, SYN page 4:** A CC 70, NRPN 1:97; B CC 71, NRPN 1:98; C CC 72, NRPN 1:99; D CC 73, NRPN 1:100; E CC 74, NRPN 1:101; F CC 75, NRPN 1:102; G CC 76, NRPN 1:103; H CC 77, NRPN 1:104.
- **Digitone II C.4 Filter:** Frequency CC 16, NRPN 1:20; Data entry knob F (machine dependent) CC 17, NRPN 1:21; knob G CC 18, NRPN 1:22; Env. Depth CC 24, NRPN 1:26; Attack Time CC 20, NRPN 1:16; Decay Time CC 21, NRPN 1:17; Sustain Level CC 22, NRPN 1:18; Release Time CC 23, NRPN 1:19; Env. Delay CC 19, NRPN 1:23; Key Tracking CC 26, NRPN 1:69; Base CC 27, NRPN 1:24; Width CC 28, NRPN 1:25; Env. Reset CC 25, NRPN 1:68.
- **Digitone II C.5 Amp:** Attack Time CC 84, NRPN 1:30; Hold Time CC 85, NRPN 1:31; Decay Time CC 86, NRPN 1:32; Sustain Level CC 86, NRPN 1:33; Release Time CC 88, NRPN 1:34; Env. Reset CC 92, NRPN 1:41; Mode CC 91, NRPN 1:40; Pan CC 89, NRPN 1:38; Volume CC 90, NRPN 1:39.
- **Digitone II C.6 Euclidean sequencer (NRPN only):** Pulse Generator 1 NRPN 3:8; Pulse Generator 2 NRPN 3:9; Euclidean Mode On/Off NRPN 3:14; Rotation Generator 1 NRPN 3:11; Rotation Generator 2 NRPN 3:12; Track Rotation NRPN 3:13; Boolean Operator NRPN 3:10.
- **Digitone II C.7 FX:** Bit Reduction CC 78, NRPN 1:5; Overdrive CC 81, NRPN 1:8; Sample Rate Reduction CC 79, NRPN 1:6; SRR Routing CC 80, NRPN 1:7; Overdrive Routing CC 82, NRPN 1:9; Delay Send CC 30, NRPN 1:36; Reverb Send CC 31, NRPN 1:37; Chorus Send CC 29, NRPN 1:35.
- **Digitone II C.8 Mod:** LFO 1 Speed CC 102, NRPN 1:42; LFO 1 Multiplier CC 103, NRPN 1:43; LFO 1 Fade In/Out CC 104, NRPN 1:44; LFO 1 Destination CC 105, NRPN 1:45; LFO 1 Waveform CC 106, NRPN 1:46; LFO 1 Start Phase CC 107, NRPN 1:47; LFO 1 Trig Mode CC 108, NRPN 1:48; LFO 1 Depth CC 109, NRPN 1:49; LFO 2 Speed CC 111, NRPN 1:50; LFO 2 Multiplier CC 112, NRPN 1:51; LFO 2 Fade In/Out CC 113, NRPN 1:52; LFO 2 Destination CC 114, NRPN 1:53; LFO 2 Waveform CC 115, NRPN 1:54; LFO 2 Start Phase CC 116, NRPN 1:55; LFO 2 Trig Mode CC 117, NRPN 1:56; LFO 2 Depth CC 118, NRPN 1:57; LFO 3 Speed NRPN 1:58; LFO 3 Multiplier NRPN 1:59; LFO 3 Fade In/Out NRPN 1:60; LFO 3 Destination NRPN 1:61; LFO 3 Waveform NRPN 1:62; LFO 3 Start Phase NRPN 1:70; LFO 3 Trig Mode NRPN 1:71; LFO 3 Depth NRPN 1:72.
- **Digitone II C.9 Send FX, delay:** Delay Time CC 21, NRPN 2:0; Pingpong CC 22, NRPN 2:1; Stereo Width CC 23, NRPN 2:2; Feedback CC 24, NRPN 2:3; Highpass Filter CC 25, NRPN 2:4; Lowpass Filter CC 26, NRPN 2:5; Reverb Send CC 27, NRPN 2:6; Mix Volume CC 28, NRPN 2:7.
- **Digitone II C.9 Send FX, reverb:** Predelay CC 29, NRPN 2:8; Decay Time CC 30, NRPN 2:9; Shelving Freq CC 31, NRPN 2:10; Shelving Gain CC 89, NRPN 2:11; Highpass Filter CC 90, NRPN 2:12; Lowpass Filter CC 91, NRPN 2:13; Mix Volume CC 92, NRPN 2:15.
- **Digitone II C.9 Send FX, chorus:** Depth CC 16, NRPN 2:41; Speed CC 9, NRPN 2:42; High Pass Filter CC 70, NRPN 2:43; Width CC 71, NRPN 2:44; Delay Send CC 12, NRPN 2:45; Reverb Send CC 13, NRPN 2:46; Mix Volume CC 14, NRPN 2:47.
- **Digitone II C.10 Mixer, compressor:** Threshold CC 111, NRPN 2:16; Attack Time CC 112, NRPN 2:17; Release Time CC 113, NRPN 2:18; Makeup Gain CC 114, NRPN 2:19; Pattern Volume CC 119, NRPN 2:24; Ratio CC 115, NRPN 2:20; Sidechain Source CC 116, NRPN 2:21; Sidechain Filter CC 117, NRPN 2:22; Dry/Wet Mix CC 118, NRPN 2:23.
- **Digitone II C.10 Mixer, external in:** Dual Mono CC 82, NRPN 2:40; Input L Level CC 72, NRPN 2:30; Input L Pan CC 74, NRPN 2:32; Input R Level CC 73, NRPN 2:31; Input R Pan CC 75, NRPN 2:33; Input L Delay Send CC 78, NRPN 2:36; Input R Delay Send CC 79, NRPN 2:37; Input L Reverb Send CC 80, NRPN 2:38; Input R Reverb Send CC 81, NRPN 2:39; Input L Chorus Send CC 76, NRPN 2:34; Input R Chorus Send CC 77, NRPN 2:35; Input L R Level CC 72, NRPN 2:30; Input L R Balance CC 74, NRPN 2:32; Input L R Delay Send CC 78, NRPN 2:36; Input L R Reverb Send CC 80, NRPN 2:38; Input L R Chorus Send CC 76, NRPN 2:34.
- **Digitone II C.11 VAL (MIDI tracks):** VAL1 CC 70, NRPN 1:16; VAL2 CC 71, NRPN 1:17; VAL3 CC 72, NRPN 1:18; VAL4 CC 73, NRPN 1:19; VAL5 CC 74, NRPN 1:20; VAL6 CC 75, NRPN 1:21; VAL7 CC 76, NRPN 1:22; VAL8 CC 77, NRPN 1:23; VAL9 CC 78, NRPN 1:60; VAL10 CC 79, NRPN 1:61; VAL11 CC 80, NRPN 1:62; VAL12 CC 81, NRPN 1:63; VAL13 CC 82, NRPN 1:64; VAL14 CC 83, NRPN 1:65; VAL15 CC 84, NRPN 1:66; VAL16 CC 85, NRPN 1:67.
- **Digitone II C.12 Misc:** Pattern Mute CC 110, NRPN 1:109; Master Overdrive CC 17, NRPN 2:50.

### Analog Heat +FX, manual DOC10069enB (file name: OS 1.01, 2024-03-25), Appendix A `[doc]` {heatfx-manual}

- **Analog Heat +FX Amp, EQ, filter (MIDI CH MAIN):** AMP Circuit Select CC 108, NRPN 1:108; AMP Drive CC 109 (LSB 37), NRPN 1:109; AMP Level CC 110 (LSB 39), NRPN 1:110; AMP Mix CC 111 (LSB 40), NRPN 1:111; PST Volume CC 112, NRPN 1:112; EQ Low CC 28 (LSB 41), NRPN 1:28; EQ High CC 29 (LSB 42), NRPN 1:29; VCF Mode CC 30, NRPN 1:30; VCF Frequency CC 22 (LSB 43), NRPN 1:22; VCF Frequency Pan CC 26 (LSB 47), NRPN 1:26; VCF Resonance CC 23 (LSB 44), NRPN 1:23; VCF Dirt CC 27, NRPN 1:27; ENV to Filter CC 24 (LSB 45), NRPN 1:24; LFO to Filter CC 25 (LSB 46), NRPN 1:25.
- **Analog Heat +FX Envelope follower (MIDI CH MAIN):** ENV Threshold CC 12 (LSB 32), NRPN 1:12; ENV Attack CC 13, NRPN 1:13; ENV Release CC 14, NRPN 1:14; ENV Base CC 15, NRPN 1:15; ENV Width CC 16, NRPN 1:16; ENV Mode CC 17, NRPN 1:17; ENV Destination CC 18, NRPN 1:18; ENV Depth CC 19 (LSB 33), NRPN 1:19; ENV Destination 2 CC 20, NRPN 1:20; ENV Depth 2 CC 21, NRPN 1:21.
- **Analog Heat +FX LFOs (MIDI CH MAIN):** LFO1 Waveform CC 66, NRPN 1:66; LFO1 Speed CC 67, NRPN 1:67; LFO1 Multiplier CC 68, NRPN 1:68; LFO1 Fade CC 69, NRPN 1:60; LFO1 Mode CC 70, NRPN 1:70; LFO1 Start Phase CC 71, NRPN 1:71; LFO1 Destination CC 72, NRPN 1:72; LFO1 Depth CC 73 (LSB 34), NRPN 1:73; LFO1 Destination 2 CC 74, NRPN 1:74; LFO1 Depth 2 CC 75, NRPN 1:75; LFO2 Waveform CC 76, NRPN 1:76; LFO2 Speed CC 77, NRPN 1:77; LFO2 Multiplier CC 78, NRPN 1:78; LFO2 Fade CC 79, NRPN 1:79; LFO2 Mode CC 80, NRPN 1:80; LFO2 Start Phase CC 81, NRPN 1:81; LFO2 Destination CC 82, NRPN 1:82; LFO2 Depth CC 83 (LSB 35), NRPN 1:83; LFO2 Destination 2 CC 84, NRPN 1:84; LFO2 Depth 2 CC 85, NRPN 1:85; LFO3 Waveform CC 86, NRPN 1:86; LFO3 Speed CC 87, NRPN 1:87; LFO3 Multiplier CC 88, NRPN 1:88; LFO3 Fade CC 89, NRPN 1:89; LFO3 Mode CC 90, NRPN 1:90; LFO3 Start Phase CC 91, NRPN 1:91; LFO3 Destination CC 92, NRPN 1:92; LFO3 Depth CC 93 (LSB 36), NRPN 1:93; LFO3 Destination 2 CC 94, NRPN 1:94; LFO3 Depth 2 CC 95, NRPN 1:95.
- **Analog Heat +FX CV, expression, gate (MIDI CH MAIN):** CV A Destination CC 100, NRPN 1:102; CV A Depth CC 101, NRPN 1:103; Expr. A Destination CC 102, NRPN 1:104; Expr. A Depth CC 103, NRPN 1:105; CV B Destination CC 104, NRPN 1:106; CV B Depth CC 105, NRPN 1:107; Expr. B Destination CC 106, NRPN 1:108; Expr. B Depth CC 107, NRPN 1:109; GATE Threshold CC 113, NRPN 1:113; GATE Hold CC 114, NRPN 1:114; GATE Release CC 115, NRPN 1:115; GATE Range CC 116, NRPN 1:116.
- **Analog Heat +FX FX blocks: bits, chorus, delay (CC on MIDI CH FX, NRPN on MIDI CH MAIN):** BITS SRR CC 88, NRPN 2:88; BITS BR CC 89, NRPN 2:89; BITS Filter CC 90, NRPN 2:90; BITS Mix CC 91, NRPN 2:91; CHORUS Depth CC 102 (LSB 36), NRPN 2:102; CHORUS Speed CC 103 (LSB 37), NRPN 2:103; CHORUS Width CC 105, NRPN 2:105; CHORUS Mix CC 106, NRPN 2:106; DELAY Time CC 107 (LSB 39), NRPN 2:107; DELAY Pingpong CC 108, NRPN 2:108; DELAY Width CC 109, NRPN 2:109; DELAY Feedback CC 110, NRPN 2:110; DELAY HPF CC 111 (LSB 40), NRPN 2:111; DELAY LPF CC 112 (LSB 41), NRPN 2:112; DELAY Amount CC 113, NRPN 2:113; DELAY Mode CC 114, NRPN 2:114.
- **Analog Heat +FX FX blocks: reverb, compressor, warble, bass (CC on MIDI CH FX, NRPN on MIDI CH MAIN):** REVERB Pre-delay CC 12, NRPN 2:12; REVERB Decay T. CC 13, NRPN 2:13; REVERB Freq CC 14, NRPN 2:14; REVERB Gain CC 15, NRPN 2:15; REVERB HPF CC 16, NRPN 2:16; REVERB LPF CC 17, NRPN 2:17; REVERB Amount CC 18, NRPN 2:18; REVERB Mode CC 19, NRPN 2:19; COMP Threshold CC 20, NRPN 2:20; COMP Attack CC 21, NRPN 2:21; COMP Release CC 22, NRPN 2:21; COMP Makeup Gain CC 23, NRPN 2:23; COMP Ratio CC 24, NRPN 2:24; COMP S.Chain Filter CC 26, NRPN 2:26; COMP Mix CC 27, NRPN 2:27; WARBLE Mix CC 28, NRPN 2:28; WARBLE Depth CC 29, NRPN 2:29; WARBLE Speed CC 30, NRPN 2:30; WARBLE Base CC 31, NRPN 2:31; WARBLE Width CC 32, NRPN 2:32; WARBLE Stereo CC 33, NRPN 2:33; WARBLE Noise Lev. CC 34, NRPN 2:34; WARBLE Noise HPF CC 35, NRPN 2:35; BASS XFreq CC 115, NRPN 2:115; BASS HP Level CC 116, NRPN 2:116; BASS LP Level CC 117, NRPN 2:117; BASS Bass CC 118, NRPN 2:118.

The Heat's first table is received on MIDI CH MAIN. For the FX blocks the manual puts the CC numbers on MIDI CH FX and the NRPN numbers on MIDI CH MAIN, which is why CC numbers repeat between the two tables. The appendix also lists the allowed values of selector parameters (circuit, filter mode, LFO waveform and mode); those are not transcribed here.

## Where the official MIDI tables live (forum reports from before the manuals were read)
- Digitakt (mk1) manual: **Appendix A** lists sound parameters with CC numbers; high-resolution control needs NRPN, which is **four CC messages** (CC 99 = NRPN MSB, CC 98 = NRPN LSB, CC 6 = data MSB, CC 38 = data LSB), the MSB/LSB per parameter come from the manual; "Receive CC/NRPN" must be enabled under SETTINGS > MIDI CONFIG > PORT CONFIG. Digitone (mk1): Appendix B (MIDI implementation), ratio offsets are in a table B.3, CC 70-77 drive the MIDI track's CC value parameters. A forum user reports that the Digitakt II manual lists no CC values for the Euclidean sequencer parameters and that some Euclidean NRPNs misbehaved before OS 1.10 ("Some NRPN parameters regarding the Euclidean sequencer didn't work as intended" is in the 1.10 notes). The Octatrack is said to be the only Elektron device that answers a CC request. Manuals are updated with every OS - always use the one for the OS in hand. `[?]` {elektronauts-dt2-sample-slot} {elektronauts-heat-midi} {elektron-dt2-notes}

