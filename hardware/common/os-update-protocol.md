# How Digitakt II and Digitone II take an OS update from the running OS (DT2 1.17, DN2 1.12)

Source: digikit finding 75, "The MAIN OS upgrade receive path" (read from a git clone, 2026-10-31). Everything is **[D]** in digikit's
terms - read statically and run in their emulator, **not on hardware** unless stated; the emulator does not model the USB host, the real clock
or real flash timing. Second-hand. Key: {digikit-f75}. Recovery from the bootstrap (FUNC + TRIG 4, DIN) is a different path: see
[`recovery.md`](recovery.md) and the bootstrap section of [`../devices/digitone-2-internals.md`](../devices/digitone-2-internals.md).

## Two routes into one receiver
1. **Menu route (plain `.syx` stream):** SETTINGS > SYSTEM > OS UPGRADE shows "Waiting for SysEx" and opens a gate; only then does the raw
   receiver accept the stream (at the main screen the stream is ignored). Both DIN and USB MIDI queues reach it (USB run in the emulator, DIN not).
2. **RPC route (what Elektron Transfer, Elektroid and the community flashers use):** MidiRpc requests `0x50` Start, `0x51` Write, `0x52` End are
   handled without the menu; Start opens the OS UPGRADE screen by itself; Write carries bytes of the same `.syx`.

## Stream format (both devices)
Messages are exactly 128 bytes `F0 00 20 3C 14 00 <cmd> ... F7`. Header `cmd 0x7f` (byte 7 = 1, byte 8 = stream id: **`0x0f` Digitakt II, `0x10` Digitone II**;
any other id refuses the stream - that is why a DT2 image fails on a DN2 already at the header), bytes 9..11 start counter, then the announced message count.
Data `cmd 0x7e`: sequence number (bytes 7..9) must be the next one, checksum `(key + sum(b ^ (key + i))) & 0x7f` over 0x77 bytes (key = stream id) must
match byte 0x7e, then 0x65 (101) bytes are staged. Footer byte 7 = 2: counts must match. A wrong sequence number or checksum resets the receiver
**silently**; a new header restarts at any time. DT2 1.17 announces 14,703 messages, DN2 1.12 18,674 (about 1.49 MB and 1.89 MB staged); the staging
buffer size and the announced-count bound check were not found. (Syntakt 1.42 uses transport id 0x16 and OS-stream byte 0x11 - digikit finding 01.)

## Acknowledgement and buffering
- **The menu route sends no SysEx reply at all**; only the screen shows progress. Pace by time: digikit uses 128-byte messages every 2 ms (about 29 s DT2,
  37 s DN2) - 12x slower than the emulated ceiling; not run on hardware.
- The whole container is staged **in RAM**; flash is untouched until the last message. A transfer cut before the footer leaves the screen on "Receiving"
  and nothing validated, erased or written. Power loss **during the flash phase** leaves the container area partly erased; the bootstrap (`0x40000`) is
  never written by this path, so FUNC boot menu and DIN OS UPGRADE stay usable (emulated).

## Validation (before any erase; run up to three times)
| Step | Digitakt II 1.17 | Digitone II 1.12 | Result on failure |
|---|---|---|---|
| Content checksum (sum of index XOR word, compared with the word at +4) | yes | yes | "Checksum error!" |
| **Build floor**: build word at +0x10 must be >= "0060" | yes | **no** | "Downgrade not possible" |
| HMAC-SHA256 trailer (key derived from a string in the image) | yes | yes | "Checksum error!" |
The product is told apart by the HMAC key and the stream id, not by a product-byte compare. Other messages: "Missing data!", "No power adapter". Nothing is erased on a failure.
- **No "UPGRADE OS NOW?" on the menu route in the emulator:** the delegate returns "do not ask", so after the last message the screen goes ERASING FLASH... ->
  SUCCESS! REBOOTING -> reset with no key pressed. Real hardware may differ (no derived delegate class was found). NO while receiving asks "CANCEL OS UPGRADE?".
- **The flash writer ignores erase/program return codes - "Success" is shown whatever the chips did.** It erases sector by sector from flash `0x80000`
  (default sector 0x10000) and programs 0x100-byte pages, waits 3 s, soft-resets via `0x80 -> 0xec090000`.

## RPC route details (emulated; DT2 also flashed on hardware with 2,048-byte Writes)
| Request | Payload | Reply |
|---|---|---|
| Start `0x50` | stream length (bytes of the `.syx`), `sysex\0`, flag (0 = wait for End, 1 = continue after the last byte) | status 0 ok / 1 refused + text ("Unsupported file type", "OS Upgrade is already in progress", "Could not initiate OS upgrade") |
| Write `0x51` | CRC-32 of the data (zlib `crc32(data)`), data length, stream offset, data | bytes taken (u32), status 0 ok, **1 complete (last Write; image validated)**, 2 CRC mismatch, 3 error + text |
| End `0x52` | commit byte (1 = flash) | 0 ok (flashes and restarts), 2 refused/cancelled (screen returns to main after ~0.8 s; a new Start works) |
Framing: MidiRpc envelope `F0 00 20 3C 10 00`, 8-in-7 packed `seq16 0000 type payload`, `F7`, no checksum, all numbers u32 big-endian, strings NUL-terminated,
reply type = request OR 0x80. A Write whose offset is below the bytes taken is acknowledged and ignored. digikit's host state machine: Start (5 s timeout) ->
Writes of 2,048 bytes, one in flight (2 s timeout, 15 s for the last because validation takes ~2 s) -> only status 1 means "validated" -> End 1. **Every failure
or cancel before End 1 sends End 0**; nothing is written before End 1; after End 1 nothing can be cancelled. In the emulator stock and patched images flashed
with no panel key (DT2 patched 1,531,152 bytes = 24 erases/5,982 programs; DN2 patched 1,947,984 bytes).
Compare the skill's practice (Start without auto-commit, End(1) after a pause, because the "complete" event can be lost on the first upload after boot):
[`../devices/digitone-2-os111-firmware-map.md`](../devices/digitone-2-os111-firmware-map.md).

## The factory console's #UPGRADE is a different, unchecked path (DN2 1.11, dnfw `os-update-path.md`) {dn2-osupdate}
In maintenance mode (entered with a power-on key combination), the service console's `#UPGRADE` / `#FULL_UPGRADE` take a bootstrap and then an OS over USB-CDC. It checks **only the ELE3 magic and the device type** (52), not the checksum or the HMAC, before it erases and writes from `0x80000`. `#FULL_UPGRADE` also writes the bootstrap. **Never script this path.** The normal path validates fully before any erase. `[doc]`

## Rules that follow
- Prefer the RPC route with explicit End; send End 0 on every abort. Do not resend Writes blindly; a failed run costs only a new Start.
- A "Success!" screen does not prove the flash was written correctly - verify by version string / behaviour after reboot.
- Never rely on the in-OS path for recovery; it needs a working MAIN OS. The bootstrap route (DIN) is the recovery.
- Digitone II has no build floor in the validator - an older signed image is accepted; Digitakt II refuses builds below 0060.
