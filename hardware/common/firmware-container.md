# Firmware container (.syx) - facts shared by the devices

All facts are second-hand (see evidence tags). Device-specific differences are in `devices/`.

## Transport and container
- The OS update is a `.syx` file: SysEx transport around a container of compressed sections. `[doc]` {elektron-firmware-tool}
- Transport packing: 8-in-7 and 2+7+7. Container types seen by the tool: ELE3, ELE2, ELEK, AD, and pre-ELE
  (Machinedrum / Monomachine). `[doc]` {elektron-firmware-tool}
- Digitakt II / Digitone II use ELE3 with a section table; the decoder reverses 8-in-7 first. `[doc]` {digikit-old}
- ELE3 containers get a version string and an HMAC trailer applied at transport encode. `[doc]` {elektron-firmware-tool}
- Elektron identifies devices in the update path by a product ID. Table published on elektron.se (meaning of the
  field not shown on the page we read): Analog Heat 000A, Digitakt 000C, Digitone 0014, Analog Heat MKII 0016,
  Model:Samples 0019, Model:Cycles 001B, Digitone Keys 001C. `[?]` {elektron-faq}

## Compression
- Sections use an aPLib-style codec (LZ77 + Elias-gamma). `[doc]` {elektron-firmware-tool} {dn2-firmware-explore}
- Section 4 (updater) is stored raw and carries its own depacker copy (Digitakt II). `[doc]` {digikit-old}
- Re-compressing with `-c` is not byte-identical to stock even when content is unchanged, but preserves the
  decompressed content. Verbatim repack (`-r`) matched on 22 of 23 test images (one stray byte after the final
  SysEx terminator). `[doc]` {elektron-firmware-tool}
- dn2_firmware_explore: decode + re-encode byte-identical on both images; repacked sections smaller than stock on every section. `[doc]` {dn2-firmware-explore}

## Checksums and signing
- CRC-32 (poly 0xEDB88320, residue 0xDEBB20E3) verified on Digitakt II. `[doc]` {digikit-old}
- Algorithms in the containers: SHA-256, HMAC-SHA256, CRC-32, key derivation. Modifying a section means recomputing
  every checksum; the tools do it and re-verify. `[doc]` {elektron-firmware-tool}
- **Digitone II (DN2) containers are signed with HMAC-SHA256; the key is derived from material inside the image, so a
  modified image can be signed correctly.** `[doc]` {dn2-firmware-explore}
- **Digitone mk1 (DN1) containers are unsigned** (trailer = 32 zero bytes). `[doc]` {dn2-firmware-explore}
- Digitakt II also checks a content checksum and an HMAC-SHA256 trailer in the bootstrap; digikit has not emulated them yet. `[doc]` {digikit-old}

## Sections
- Digitakt II: section 2 = bootstrap, section 4 = updater (never modify); the DSP program is an ADI boot stream in **section 7**; ElekLabs digikit's patchkit refuses to change **sections 2, 4 and 8**. The earlier README named sections 3 and 7 as patch targets. `[doc]` {digikit} {digikit-old}
- Digitone II: the `MAIN OS` section is 3,085,696 bytes of big-endian ColdFire code, built with GCC, still containing
  C++ RTTI names. `[doc]` {dn2-firmware-explore}
- `MAIN OS` loads at `0x40000400` on both DN1 and DN2 (as stated by dn2_firmware_explore). `[doc]` {dn2-firmware-explore}
- elekloader (Digitakt mk1): output must equal the stock file with only the main OS section changed; the header may
  differ only in its 4-character version field and the framing only in its message count. `[doc]` {elekloader-readme}

## Tools
- `elektron-firmware-tool` (mischa85, C, MIT): inspect, extract (`-d`), compress (`-c`), repack verbatim (`-r`). No firmware in the repo. {elektron-firmware-tool}
- `dnfw` (dn2_firmware_explore): build/patch with verify-after-write; Gates A-E proven (codec, rebuild, re-sign, recovery, normal update path), Gate F (disassembler check) passes with Ghidra, fails with Capstone. {dn2-firmware-explore}

## ELE3 container in detail (dnfw `docs/ele3-format.md`, read 2026-10-31)
| Offset | Field |
|---|---|
| 0x00 | magic `ELE3` |
| 0x04 | u32 **product code**: DN2 = 52, DT2 = 43, DN1 = 54 (the device checks it before flashing) |
| 0x08 | build string: DN2 `0059`, DT2 `0079`, DN1 `0104` (an earlier note had put it at 0x07) |
| 0x13 | version string: DN2 `1.11`, DT2 `1.16`, DN1 `1.43` |
| 0x1C | u32 section count |
| 0x20 | section table, 16 bytes per entry: id, offset, stored length, destination address; sections sit on 16-byte boundaries in ascending offset order |
`[doc]` {dn2-ele3}
- **Preamble** of the decoded byte stream: u32 container size + u32 content checksum, then the container (magic at offset 8). Container size: DN2 1,743,120, DN1 1,102,352 (the sizes of the file pair dnfw analysed). The content checksum is not a standard algorithm: a running 32-bit sum over big-endian words, each word XORed with its one-based index; trailing bytes that do not fill a word are excluded. Compressed sections carry a header with the stream length and a u32 sum of the stream bytes (padding excluded). `[doc]` {dn2-ele3}
- **SysEx transport:** each message is `F0 ... F7`; the body is either a 126-byte data packet or a 14-byte marker; it starts with the manufacturer ID and a **device ID: DN2 `0x15`, DT2 `0x14`, DN1 `0x0D`**. Payloads use 8-in-7 encoding (116 encoded bytes carry 101 decoded bytes, last packet zero-padded); packet count = stream length / 101 + 1 (an exact division still adds a packet); a block and sequence counter starts from values in the start marker and wraps at 7 bits; the 7-bit packet checksum sits in the last body byte and uses a base value taken from the start marker, not a constant. `[doc]` {dn2-ele3}
- **Trailer:** the last 32 bytes of the declared container are an HMAC-SHA256 on the first 16-byte boundary at least 4 bytes past the last section (gap zeroed); it covers everything before it, padding included; the key is derived from material inside the image (a printable string in a decompressed section, found in the bootstrap, plus a fixed constant) - **never edit that key material**, the device likely verifies with its installed copy. DN1 1.42A is unsigned (trailer all zeros). `[doc]` {dn2-ele3}
- **Compression:** each section is raw or aPLib-variant compressed (not flagged - inferred by whether the bytes depack): LZ77 with interlaced Elias-gamma codes, a biased offset, a last-offset reuse code and a length bonus for far matches, minimum match 2; Elektron's streams keep the furthest match within 1 MiB and the longest at 2,048 bytes. `[doc]` {dn2-ele3}
- **DN1 vs DN2:** bootstrap load address DN2 `0x02000000` / DN1 `0x02000800`; blob (id 7) compressed on DN2, raw on DN1; boot (id 6) absent on DN2, present (raw) on DN1; section 5 (meta) is 15 bytes, stored raw, no destination address, identical size on both; section 8 appears in OS 1.11 compressed (it is the Outbox 8 accessory firmware). `[doc]` {dn2-ele3} {dn2-cfw-handoff}
- **After patching, recompute:** re-encoded section data and its stream length/sum (+ padding to 4 bytes, table length includes the padding), section table offsets/lengths and 16-byte placement (and the count if sections change), the preamble (container size, content checksum), SysEx packet checksums/counters/packet count, and on DN2 the HMAC over everything before the trailer. The page does not say whether the product code, build string or version string must change, nor whether ids must be renumbered. `[doc]` {dn2-ele3}
- Update/version gates: flash addresses and loader margins for Digitone II are in [`../devices/digitone-2-internals.md`](../devices/digitone-2-internals.md).

