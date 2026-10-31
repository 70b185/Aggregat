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
