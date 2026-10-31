# Overbridge over USB (what Overwitch's README reveals) - the only deep source on Analog Heat +FX so far

Source: dagargo/overwitch README (JACK clients for Overbridge 2 devices, GPL-3.0; protocol work based on Stefan Rehm's USB reverse engineering in `dtdump`), read 2026-10-31. It does **not** document the USB protocol in detail (no class, endpoint or control-request tables); the facts below are what it states. Second-hand; tags as in `../README.md`. Key: {overwitch-readme}.

## USB device side of Digitakt II / Digitone II (digikit finding 42, static, DT2 1.16)
- Controller: MCF5441x USB OTG at `0xFC0B0000`, device mode, external ULPI PHY, **high speed** (480 Mb/s; descriptors have 512-byte bulk packets; DEVICE_QUALIFIER stalled = HS-only). Only endpoints EP0-EP3 exist. VID `0x1935`. `[doc]` {digikit-f42}
- Modes -> descriptors: **USB MIDI** PID `0x012b` (EP1 bulk pair, 2 cables); **USB AUDIO/MIDI** PID `0x102b` (UAC2 iso on EP2/EP3 + MIDI on EP1); **OVERBRIDGE** PID `0x0b2b` (vendor class 0xFF: interrupt EP3 in/out, EP2 OUT bulk 512 + EP2 IN interrupt 64, plus MIDI on EP1); a **service** mode PID `0xffff` with CDC-ACM. No MS-OS/BOS descriptors - Windows will not bind WinUSB on its own. `[doc]` {digikit-f42}
- SysEx throughput is limited by the ColdFire's per-byte handling (about 32 instructions per wire byte just to split USB-MIDI events, two 512-byte receive buffers in flight); digikit estimates 0.8-1.4 MB/s at best for an own SysEx route. Transfer's file-write RPC: OpenFileForWrite `0x40`, WriteFileV1 `0x42` (handle, length, offset, data), CloseFileWriter `0x41`. `[doc]` {digikit-f42}
- **Samples are not converted on the device:** the native file is a 0x40-byte header (+1 stereo flag, +4 length, +8 rate 48000) + big-endian int16 PCM + 16-byte trailer; no WAV parser in the image. The host must resample to 48 kHz and convert. `[doc]` {digikit-f42}

## Overbridge refuses a mod whose version field changed (Digiwerk OB01, DN2 1.12) {dn2-cfw-ob01}
- The container's 4-byte version field (header `+0x14`, `1.12` on stock) is sent to the computer by the main OS. A build that writes its own name there (e.g. `CMP1`) makes the Overbridge plugin answer "Device is not running compatible OS Version" and fail to open. The engine itself connects; the refusal comes from the plugin. `[hw]`
- Fix: patch the two main-OS sites that send the version so they send a header copy with `1.12`. The flash and the power-on screen keep the build's name. Overbridge and Transfer work again on the unit (2026-10-22). `[hw]`
- **Rule: keep the version field the device expects, or patch only what is sent out.** Overbridge logs on macOS: `~/Library/Logs/Elektron Overbridge/`.

## Which devices
- **Overbridge 2 devices supported:** Analog Four MKII, Analog Rytm MKII, Digitakt, Digitakt II, Digitone, Digitone II, Digitone Keys, **Analog Heat, Analog Heat MKII, Analog Heat +FX**, Syntakt. **Not supported:** the Overbridge 1 devices (Analog Four MKI, Analog Keys, Analog Rytm MKI). `[doc]`
- Device IDs are listed as vendor:product: Digitakt `1935:0b2c`; Analog Heat +FX has product id 2899. `[doc]`

## Protocol generations (transfer type, sample size)
| Version | USB transfer | Samples | Devices |
|---|---|---|---|
| 1 | isochronous | - | Analog Rytm MKI, Analog Four MKI and Keys |
| 2 | interrupt | 4-byte | classic Overbridge 2 devices |
| 2.1 | interrupt | 3-byte (some tracks may still use 4) | Digitakt II, Digitone II |
| 3 | isochronous | - | Tonverk |
`[doc]` {overwitch-readme}

## Channel layouts the README shows
- **Digitakt (CLI listing):** 2 inputs (Main L/R input), 12 outputs (Main L/R, Tracks 1-8, Input L/R). `[doc]`
- **Analog Heat +FX (sample JSON):** protocol version "2", **4 inputs (Main L/R input, FX Send L/R)** and **4 outputs (Main L/R, FX Return L/R)**, 4-byte samples. Nothing else Heat-specific is stated. `[doc]`

## Framing numbers (Digitakt debug log, 12 blocks per transfer)
Device-to-host: 48 B USB frame, 368 B block, 4,032 B audio transfer. Host-to-device: 8 B USB frame, 88 B block, 672 B audio transfer. Sample rate 48 kHz. Default 24 blocks of 7 frames (168 frames) per transfer; the README allows 2-32 blocks, recommends at least 10 and warns that values as low as 8 may crash the device. Device-to-JACK latency in the examples about 3-4 ms; a 64-frame JACK buffer (2 periods) showed no xruns, 32 frames occasional ones. USB transfer timeout defaults to 10; `LIBUSB_TRANSFER_TIMED_OUT` means raise the block count and restart the device. `[doc]`

## Clocking
Adaptive resampling with a DLL on both host and Overbridge side (credit to Fons Adriaensen's papers and the zita resamplers); resampler quality 0 (best) to 4; medium recommended; early-startup ring-buffer underflows clear once the engine runs. Under PipeWire use the Pro audio profile and set `node.group`/`node.link-group` to the hardware device so JACK clients do not switch drivers. `[doc]`

## What this means for development
- Overbridge works over a **class-compliant-looking USB link with Elektron-specific framing**; a firmware mod that changes audio routing, channel counts or the USB descriptor could break Overbridge. dn2-cfw's builds show "incompatible OS version" in Overbridge (open issue), so **Overbridge compatibility is checked against the OS version/build** - plan for it. `[doc]` {dn2-cfw-roadmap}
- Official facts: Heat +FX needs OS 1.02 for Overbridge 2.13; Digitakt II OS 1.03 added Overbridge 2.13 support; Digitone II got multitrack streaming with OS 1.10 (plugin later). `[doc]` {elektron-heat-fx-notes} {elektron-dt2-notes} {gearnews-dn2-overbridge}
- Unknown: the USB class/endpoints, the control channel carrying parameters, and whether the Heat's internal DSP/CPU architecture resembles any other Elektron box. Reading Overwitch's source and `dtdump` would answer the first two.
