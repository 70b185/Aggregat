# Analog Heat (MKI, MKII, +FX)

Coverage: **official facts only. We found no community firmware mod and no reverse-engineering notes.**
Projects/tools: [../../devices/analog-heat.md](../../devices/analog-heat.md)

## Official facts (elektron.se, read 2026-10-31)
- Analog Heat MKI and MKII: latest OS **1.22** (2024-10-16, "added support for Overbridge 2.13"). `[doc]` {elektron-heat-mkii-page}
- The **+FX** has its own OS and release notes (last updated 2024-10-16). **The MKII file is rejected on +FX** ("Incompatible OS" in Transfer). `[doc]` {elektron-heat-fx-notes} {elektronauts-heatfx}
- Minimum OS for updating via Transfer: 1.20. Product IDs from Elektron's FAQ: Analog Heat 000A, Analog Heat MKII 0016 (meaning of the field not shown). `[doc]`/`[?]` {elektron-support} {elektron-faq}
- Update/recovery MKI/MKII: hold ACTIVE (MKI) or ON (MKII) while powering on -> STARTUP menu -> [LFO] = OS UPGRADE -> send the SysEx file via MIDI In (or USB MIDI In from within the OS). `[doc]` {elektron-heat-notes}
- Update/recovery +FX differs: hold ACTIVE, then **MOD** = OS UPGRADE (see below). `[doc]` {elektron-heat-fx-notes}
- Elektron Transfer 1.10.4 (2026-06-23) covers Heat +FX; Overbridge integration since OS 1.2 (USB audio streaming, MKII Overbridge). `[doc]` {elektron-heat-mkii-page} {synthanatomy-heat}

## Analog Heat +FX (official, elektron.se release notes, page updated 2024-10-16)
- OS **1.02** is the newest listed (adds Overbridge 2.13 support); **1.01** added a momentary mode for ACTIVE (SETTINGS > OPTIONS), OUTPUT GAIN (PRESET SETUP), FX TO USB (AUDIO ROUTING), randomize/reset on parameter pages, LFO RND slew, and fixed MIDI input on further channels, modulation matrix DEPTH resolution, BANK/SBANK MIDI support, LFO trigger timing and VU/clip display. 1.00 is only the baseline. No release dates are given per version. `[doc]` {elektron-heat-fx-notes}
- 1.01 was announced as exclusive to the +FX: not compatible with Analog Heat MKI/MKII. `[doc]` {gearnews-heatfx}
- Product facts from reviews/shops (not firmware): released 2023-05 (Superbooth), $999 / EUR 999; the analog "heat block" keeps 8 stereo distortion circuits, a 7-mode analog filter and a 2-band EQ, adds a noise gate and a chain of digital effects (reverb, delay, chorus, warble, bits, compressor, bass focus) with reorderable routing; 128x64 OLED; MIDI In/Out/Thru; two CV/expression/footswitch inputs; class-compliant USB audio and Overbridge. `[doc]` {synthtopia-heatfx} {sos-heatfx} {musicradar-heatfx}
- A forum post says the +FX is "just an iterative upgrade to the MKII" (opinion, no hardware evidence). `[?]`
- **No teardown, PCB photo, chip list or reverse-engineering note for any Analog Heat was found** in two search rounds (2026-10-31).

## More Heat facts from listings and forum posts (marketing/forum level, not firmware evidence)
- **+FX modulation and storage** (CDM listing): 1 assignable envelope generator/follower with two destinations, **3 assignable LFOs** (two destinations each), **512 user preset slots**, 128x64 OLED, MIDI In/Out/Thru with DIN Sync out, 24-bit/48 kHz converters, 215 x 184 x 63 mm, ~1.5 kg. The MKII has 1 assignable LFO, 1 envelope/follower and **128 user presets** (listings); the +FX ships with PSU-3c, the MKII with PSU-3b. Headphone out peak +19 dBu (+FX listing). Two CV/expression/footswitch input jacks. `[?]` {heat-fx-specs}
- **MIDI behaviour (forum users citing the manual):** the Heat can send MIDI clock and program change (manual p.18 of the MKI-era manual); forwarding notes received over USB to MIDI Out is reported as not possible; the MKI-era manual recommended a TM-1 TurboMIDI interface for sending OS upgrades to the MIDI In port (the current +FX notes recommend the C6 - SysEx Tool). `[?]` {elektronauts-heat-midi}
- **Signal path (+FX):** forum users quoting the manual: the digital effects form an "FX block"; an **analog-only mode turns off all digital effects and gives a pure analog path with no AD/DA**. So the +FX digitises the signal only when digital effects are in use - relevant for anyone modelling its processing chain. Headphone peak level is given as +19 dBu (one listing) and +22 dBu (Equipboard) - unresolved. `[?]` {kvr-heatfx} {equipboard-heatfx}
- **Third-generation naming:** a merchant calls the +FX "the third generation"; Elektronauts users joke about an "Analog Heat III+FX". Not a hardware statement. `[?]`
- 2026-10-31, second attempt: the elektron.se +FX support page and the explorer page returned a site error (client_error); still unread.
- Needed but not read (the first fetch was not approved): the elektron.se support pages for Analog Heat +FX, the explorer/spec page and the manuals (MIDI implementation, modulation matrix, OS upgrade steps). See [`../MINING.md`](../MINING.md).

## Tooling that already lists the Heat
- elektron-firmware-tool names Analog Heat MKI, MKII and +FX among supported devices (container tool, not a mod). {elektron-firmware-tool}
- Elektroid (sample/SysEx manager) lists Analog Heat MKI, MKII and +FX. Overwitch (Overbridge audio on Linux) lists Analog Heat, MKII and +FX. {elektroid} {overwitch}
- screendump lists Analog Heat as known but **not implemented**. {screendump}
- Neither the Lapin list nor altstrument.org carries a firmware entry for any Analog Heat.

## Analog Heat +FX OS 1.02 - first firmware facts (findings by 70b185, owner of this repo)
Source: the owner's own private Heat +FX research, notes as of 2026-10-28. {own-heatfx-notes} Static facts were read from the stock file
`Analog-HeatFX_OS1.02.syx` (1,229,088 B, SHA-256 `85abe773c9e2284cd1b2aaaf1f599ec0f800f56f4b34127214fe998f1a2cfe63`, build 2024-10-08) with
elektron-firmware-tool, elekloader's codec and a ColdFire disassembler. Facts marked `[hw]` were seen on the owner's unit. Nothing here is copied from other devices.

**Container and sections** `[doc]`
- SysEx device byte **0x13**. Container **ELE3**, build "S0063", version "1.02", 969,776 B. **No trailer and no HMAC seal.** The byte-exact round trip works, and a second, independent unpacker (digikit elz) agrees.
- Sections:
  - 5 meta: 15 B, timestamp "241008 20:29:59", not packed.
  - 2 bootstrap: 26,638 B, runs from SRAM `0x80000400`, stack `0x80010000`, entry `0x80000ddc`. **It holds the STARTUP MENU** (TEST MODE, EMPTY RESET, FACTORY RESET, OS UPGRADE) and the bootstrap upgrade.
  - 1 **FPGA: Xilinx bitstream**, 54,664 B, sync `aa 99`. It is loaded by the OS ("INITB WENT LOW..."); its role is unknown.
  - **3 MAIN OS:** 2,174,964 B, destination `0x40000400`, entry `0x40001384`.
  - 4 updater: 29,384 B, not packed, destination `0x80000400`.
- There is **no DSP section**. Section hashes are in the owner's notes.

**CPU, memory and audio path** `[doc]`
- CPU: **ColdFire MCF5441x**. 1,036 of 1,037 peripheral accesses hit MCF5441x modules.
- 64 MB DDR: the updater tests `0x40000000-0x44000000`, and the stack starts at `0x44000000`.
- The updater copies section 3 with its 8-byte header to **`0x40200000`** and unpacks it in place to `0x40000400` (aPLib). The image ends at `0x402133F4`. The smallest write/read pointer gap is 825,529 B for stock and 774,349 B for a repack.
- After boot:
  - `0x40000400-0x40206000` stays in DDR.
  - `0x40206000-0x4020b4fc` is copied to SRAM `0x80000000`, and `0x4020b4fc-0x402133f4` to SRAM `0x80008000`.
  - DDR from `0x40206000` up to `0x426383d0` is then cleared.
  - **Custom code therefore only lives below `0x40206000`.** Unreferenced zero runs of 2 KB or more: `0x402057c4-0x40206000` (2,108 B) and `0x4019efbc-0x4019f7cf`.
- VBR is in RAM at `0x40000000`. Device handlers are installed at run time.
- **Audio runs on the ColdFire itself:**
  - SSI1 with eDMA channels 52 and 54. Channel 54 raises the interrupt (vector 174, priority 6).
  - Its handler (`0x400a3e84`) timestamps the block, counts it and raises a software interrupt (vector 191, priority 5, handler `0x400a3ee6`).
  - The software interrupt processes a 4 x 512-byte ring in SRAM.
  - Hypothesis, not verified: 32 frames x 4 channels x 4 bytes = 1,500 blocks/s.
- The MAIN OS contains a **factory console** (`#UPGRADE`, "READY FOR BOOTSTRAP", `#FULL_UPGRADE`, `#FACTORY_DUMP`, `#DUMP_CALIBRATION_BLOB`, `#ERASE_CALI...`). **Never touch it.** There is no copy of the bootstrap in the MAIN OS.
- UI pages are built on first open and then reused. Title strings are copied at that point, so a live display needs a different path.

**On the unit** `[hw]`
- test01: a 12-byte text change in the MAIN OS only, everything else stock, repacked by the owner's own packer and installed through OS UPGRADE over DIN. It boots, shows the change, and sound and presets are normal (2026-10-26).
- test02: a 42-byte hook in the audio software interrupt, placed in the `0x402057c4` cave, wrote a digit into a page title. **Own code ran on the unit.** Whether it runs persistently is still open.

**Process the owner adopted** (worth copying for any new device)
- Only the MAIN OS may differ from stock. A build gate refuses anything else: bootstrap, updater, FPGA and meta stay byte-identical, and the version string and checksums stay as stock.
- Two independent unpackers are used as a cross-check.
- Patch scripts check the stock hash and the expected bytes before each write.
- A pre-commit hook and CI keep firmware out of git. A synthetic, unflashable test container (device id 0x7D) is used for tests.
- Toolchain: binutils 2.43.1 and gcc 14.2.0 built for `--with-cpu=54418`. A disassembler wraps QEMU's m68k tables, which cover ISA_A/A+/B and EMAC but are incomplete for ISA_C, so elekloader's decoder serves as a cross-check.

**Open**
- The flash budget for a larger MAIN OS, the real CPU reserve with all FX (a forum post claims 79 %), latency, the preset format, and the role of the FPGA.
- Context: there is still no public Heat +FX firmware research, and Elektron ended firmware-mod discussion on Elektronauts on 2026-09-23. The owner has paused further firmware-internals work.

## Unknown / to do
**+FX OS 1.02 now has a first profile (section above).** For MKI and MKII nothing is verified: CPU/DSP architecture, container specifics, signing, memory map. First step would be running elektron-firmware-tool on the user's own Heat OS files (not by an agent without the user's files).
