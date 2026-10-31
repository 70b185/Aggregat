# Syntakt

Coverage: **medium** (platform, memory map, audio path and modding rules from SyntHack OS; 1.42 container from digikit). Projects: [../../devices/syntakt.md](../../devices/syntakt.md)

## Ecosystem snapshot (altstrument 2026-10-31: 4 firmware/tool entries + 2 tools; elektronmods: 4 Syntakt entries)
Listings: {alt-syntakt}. Entries: **SyntHack OS** (upstream, Angelo-politek, v0.9.0 2026-10-19; {synthack-upstream}), **Syntakt MAX** (fork with a Windows builder; see the data file), **SY FM4** (Rxuting; OS 1.40A), **Syntakt Firmware Workbench** (browser; OS 1.41), **syntakt-machine45-research** (documentation) and **Sympakt** (sample packs). Brick-risk flags are set on SyntHack OS, Syntakt MAX and SY FM4. Syntakt MAX integrates an SY FM4 engine for 1.41.

## OS versions seen
**1.40A** (SY FM4 only; SHA-256 starts `266a5a30`), **1.41** (SyntHack OS, Syntakt MAX, Workbench, machine-45 research), and an **os-1.42 branch exists in SyntHack OS** (SY FM4 points to it as the porting reference; a forum user asked on 2026-10-01 for Modded-Cycles' flasher to accept 1.42). So OS 1.42 exists; mods are per-version. `[doc]` {syfm4-readme} {modded-cycles-thread}

## SY FM4 facts (README, Syntakt OS 1.40A)
Replaces SY TONE in place on the digital tracks: ALGO 0 is SY TONE itself (sample-identical to the stock machine, so existing projects sound the same), ALGO 1-8 the classic Yamaha 4-op set, ALGO 9-11 tree, diamond, ring; the second parameter page SYN 2/2 adds operator-3 (ALGO, RAT3, LEV3, DEC3) and operator-4 (DET, RAT4, LEV4, DEC4) controls, DET detunes operators 2-4 by +/-16 semitones; page 2/2 is saved with the sound and p-lockable (sounds saved by stock open with page 2/2 at SY TONE defaults). Patchers read the user's own OS and check the SHA-256 of each byte range they overwrite. **Hardware:** tested on a real Syntakt 1.40A - installs, all parameters including p-locks work, an 8-track load test ran 47 s without audible clicks, dropouts or clipping; sound/pattern-lock save-reload and CPU cost were only checked in an emulator (digiemu with a Syntakt port). **CPU:** ~8.9k cycles per voice per block vs 7.2k-9.8k for stock engines; 8 SY FM4 voices ~66 % voice CPU. **Limits:** section 7 has a size limit (`0x60000 - 5` bytes in 1.40A); page 2/2 reuses descriptors 1-5 and 12-14, which were MIDI-CC placeholders in 1.40A and are removed. Porting to 1.41/1.42 means remapping every 1.40A address and rechecking the section 7 limit, main OS layout and the placeholders. `[hw]/[emu]` {syfm4-readme}

## Facts
- Only OS **1.41** is targeted (Synthack-OS "Syntakt MAX", SY FM4 builder; syntakt-firmware-workbench refuses other files). A user asked on 2026-10-01 for Modded-Cycles' flasher to accept Syntakt OS 1.42; support is not confirmed. `[doc]` {synthack-os} {syntakt-workbench} {modded-cycles-thread}
- Mod code lives in a **64 KB RAM area**, stored compressed and unpacked at boot. `[doc]` {synthack-os}
- Each Synthack mod is a `patch.json` (target location, hash of expected original bytes, replacement bytes). `build.py` combines the stock OS with chosen mods into a `.syx`, refusing a wrong OS, overlapping patches and protected sections. Firmware is unpacked/repacked with a wrapper around elektron-firmware-tool. `[doc]` {synthack-os}
- Install: Elektron Transfer over USB (Drop page); revert by flashing the stock OS the same way. Read the author's `RECOVERY.md` first (not yet read by us). `[doc]` {synthack-os}
- Planned custom engines (RISER/DOWNFILTER, SY SWARM+) would need custom audio-engine code on "CPU #2". `[doc]` {synthack-os}
- Syntakt engines can be extracted from Syntakt OS 1.41 and loaded into Model:Cycles (Modded-Cycles needs a Syntakt_OS1.41.syx). `[doc]` {modded-cycles-thread}
- Forum claim: the Syntakt board resembles the original Digitone minus analog parts, with two ColdFires and an FPGA in similar positions. `[?]` {elektronauts-dn2-pcb}
- Status: Synthack-OS reports seven mods running on real hardware (v0.8.0); each is tested in the emulator against the original code before flashing. `[hw]` {synthack-os}

## Recovery (SyntHack OS `RECOVERY.md`)
Normal case: Drop page in Transfer. If the OS does not boot: DIN MIDI, FUNC at power-on, TRIG 4, SYSEX TRANSFER "OS Upgrade via device startup menu", tens of minutes at 31.25 kbit/s; **avoid TRIG 2 and TRIG 3 (erase data)**; do a dry run with stock first; only flash files whose `eft.py info` shows `checksums : ok`. No hardware results reported on that page. `[doc]` {synthack-recovery}

## Syntakt OS 1.41 static-analysis facts (Humgic/syntakt-machine45-research - README {machine45} and handoff dated 2026-10-28; no hardware run, no firmware)
- Address rule `VA = file offset + 0x40000400`; ColdFire big-endian (ISA-C/EMAC). MAIN is 3,438,480 bytes, section 7 is 383,760 bytes. `[doc]` {machine45-handoff}
- **Stock public Machine IDs are 0-44**, stored as a BYTE in each track's machine payload (`P[t]+0xA2`); runtime records `R[t] = model + 0x6C + 0x3C0*t`, `P[t] = *(R[t]+0x10)`; the setter is at `0x40025594` (store at `0x40025620`). 505 parameter descriptors of 52 bytes; only MAIN digital tracks 0-7. `[doc]` {machine45-handoff}
- Section 7 selector: a signed BYTE with a 46-entry map (negative -> 0, 0-45 kept, above 45 clamped to 45); stock maps 0-7 to the same-numbered engine family and 36->8, 37->9, 38->10, 44->11, everything else (incl. 45) to family 0. Stock tables: render pointers `0x400148F0` (12 entries), prep pointers `0x40014920`, the 46-byte map at `0x40014950`. A compact handoff moves MAIN `[0x80002000,0x800021B0)` through a 27x16-byte eDMA transfer (TCD47, channel 47); each track then receives a 20-byte copy into `T[t] = 0x80003C40 + 0x8E*t`. Dslot is 8 x `0x708` = 14,400 bytes. `[doc]` {machine45-handoff}
- Persistence confirmed statically: the current-kit Sound-v7 save/load keeps the machine byte (raw 0-45 and 255 retained, 46-254 map to 0); Pattern-v11 stores the byte at row `+0x2EC` and its restoration is **not closed**; Sound locks, p-locks, held trigs, migration, clipboard and undo not qualified. Evidence labels in that repo: confirmed by static analysis / verified in emulator (none for the whole device) / verified on hardware (none) / hypothesis. `[doc]` {machine45-handoff}
- Open: safe executable storage for native DSP on "CPU 2" (the loader boundary is unresolved); composition with SY FM4 (engine 4, A-table entry overlap) and other descriptor mods; resource IDs 254-261 are unclaimed in the registry but have MIDI CCs, 505+ have no native allocation. `[doc]` {machine45-handoff}

## Platform: two ColdFires, an FPGA, an analog mixer (SyntHack OS docs, OS 1.41) {synthack-docs}
- **Two ColdFire MCF5441x** (V4, EMAC, **no FPU**, ~250 MHz, so **166,667 cycles per 32-sample block**), with 64 KB SRAM at `0x80000000`. RAM shared between the CPUs is at `0x10000000`. `[doc]`
- **Sections of OS 1.41**, stored in the order 5, 2, 1, 3, 4, 6, 7, 8:
  | Section | Content | Size | Note |
  |---|---|---|---|
  | 1 | FPGA bitstream | 149,516 B | never touch |
  | 2 | bootstrap with the STARTUP menu | 30,782 B | never touch |
  | 3 | MAIN OS for CPU #1, at `0x40000400` | 3,438,480 B | patched by mods |
  | 4 | updater | 32,776 B | raw; never touch |
  | 5 | meta | | |
  | 6 | ColdFire boot stub | 1,744 B | raw; never touch |
  | 7 | **voice engine for CPU #2**, at `0x40000400`, entry `0x40001070` | 383,760 B | raw; patchable |
  | 8 | "second FPGA?" (SyntHack) | 159,948 B | digikit: identical to DT2/DN2's section 8 `[?]` |

  Stock 1.41 SHA-256: `8e2488f4...b9ed19e`.
- **Signing conflict `[?]`:** SyntHack describes an HMAC-SHA256 over the container for 1.41, with the key derived from the image. digikit found no HMAC trailer in 1.42 (the last 32 bytes are zero). Check the trailer of your own file before you decide.
- **Boot unpack limit:** the bootstrap loads compressed section 3 at `0x40200000` and unpacks it to `0x40000400`. The margin (decompressed minus compressed) must stay below ~`0x1FFC00` at every point of the stream.
  - Stock 1.41 has a margin of +99,938 B.
  - A build padded with zeros to `0x40350000` (-8,751 B) **did not boot, tested twice** and hung on the logo.
  - Zero padding is the worst case; already-compressed payloads raise the margin. SyntHack refuses builds under 4 KB of margin. `[hw]`
- The Syntakt accepts rebuilt images (recompressed section 3) over USB and DIN. `[hw]`

## Memory map of CPU #1 (OS 1.41) {synthack-docs}
| Range | What |
|---|---|
| `0x40000400-0x40347B90` | section 3 image |
| `0x40338740-0x40339000` | linker fill, **free** (used by SyntHack's splash, dual-mono and loader; nearly full) |
| `0x40339000-0x45565490` | BSS, zeroed at boot (`0x400004B2`, called once) |
| `0x444E38C0-0x454E38C0` | OS heap (buddy allocator `0x4010350C`, free `0x40103712`, 16 MB, 16-byte units). The first 64 KB block is SyntHack's **mod area** |
| `0x45565490-0x48000000` | **no code reference, but the OS writes all over it when it loads samples** |
| `0x48000000` | boot stack top |
| `0x4D570000`, `0x4FC00000` | delay and reverb lines |
| `0x80000000-0x8000FFFF` | SRAM: audio buffers, DMA rings, engine parameter arrays |
| `0x10000000` | RAM shared with CPU #2 |
- **Hardware lesson `[hw]`:** SyntHack up to v0.8.0 kept mod code at `0x46000000`. Projects with SP TWINSHOT samples then crashed at boot. Since v0.8.1 the mod code (compressed, appended to section 3 at `0x40348000`) is unpacked into a 64 KB block that a hook at the end of heap init (`0x4010358E`) reserves first.
- **Conflict to watch `[?]`:** SY FM4 (OS 1.40A) copies its code to `0x47000000`, which it describes as "above the BSS end, below the stack, addressed by nothing". That is the region SyntHack found to be overwritten by sample loading on 1.41. Treat any use of RAM above the BSS as unsafe until it is tested with sample-heavy projects.
- Boot: entry `0x400004E8`; static constructors loop `0x40082500` (136 entries); the intro animation task `0x40087E6A` gates boot, so **never make the intro longer**. Screen: 128x64 1 bpp, column-major, double buffer at `0x402D6DC4`/`0x402D6DC0`; frame loop `0x4000A0E6` redraws when `*(0x444E1334)+96` is set. `[doc]`

## Audio path {synthack-docs}
- **CPU #2 (section 7):** all work runs in the audio interrupt `0x40000934` (vector 96, DMA timer 0 capture).
  - Per block it copies `0x1B0` bytes of parameters from shared RAM and renders **8 digital voices** (`0x40004324`).
  - It returns 8 x 32 int32 over eDMA channel 47 and does no mixing.
  - 12 engines: tables at `0x400148F0` (render), `0x40014920` (update), `0x40014950` (machine id -> engine). Order: BD MODERN, SD BASIC, CY ALLOY, PC CARBON, SY TONE, SY CHORD, SD VINTAGE, CP VINTAGE, SY TOY, SY BITS, SY SWARM, SP TWINSHOT. SY CHORD reads a 512 x int32 wave at `0x4001A300`. `[doc]`
- **CPU #1 (section 3):** the per-block routine `0x400A3856` runs CV/gain, ADC deinterleave, then master/FX `0x4008F1CA`. Delay `0x40096890` and reverb `0x40096E3C` are the same code as on the Digitakt mk1.
  - Buffers: digital tracks from CPU #2 at `0x80003D50`. ADC channels at `0x80003950`: 0-3 analog tracks, 4-5 external in, 6-7 the FX-track bus.
  - USB/Overbridge: 20 channels per frame at `0x80004760`.
  - **The final mix is analog:** digital buses go out through DACs into an analog mixer, with nothing digital after them. 40 control voltages go out over DSPI1 with eDMA channel 15; CV 35/36 are the FX-track bus VCAs. `[doc]`
- **CPU #1 load: ~89 % at rest** (sequencer stopped), measured on the device with DTIM0 (`0xFC07000C`) at interrupt entry and exit. The UI gets the rest, so **a few thousand instructions per block make the UI lag**. `[hw]`
  - SY FM4 reports its main-CPU render at 85.8k of 166.7k cycles per block (stock 85.0k). That is a different span of the same interrupt. `[?]`
- Digital filter and amp run on CPU #2; the cutoff is computed on CPU #1. Analog voices and the FX track drive a **hardware envelope generator** with 20-bit rate codes. Measured curves: the digital biquad f0 = 4.918 Hz x e^(0.0655 x FREQ); the analog filter f = 14.645 Hz x e^(0.0574 x FREQ). Tempo is at `0x402D7010` (BPM x 120). `[hw]` (analog curves measured)

## How mods are built on the Syntakt (SyntHack modding guide, worth copying) {synthack-guide}
- **Each change is stored with the SHA-256 of the original bytes**, so a different OS version fails the build instead of crashing. Every mod runs in a Unicorn emulator next to the original code before flashing.
  - **Stock Unicorn gets signed fractional EMAC wrong** (the audio comes out silent), so EMAC instructions are trapped and executed in Python from the NXP manual.
  - Use CPU model "ANY" (the code needs FF1, MVS/MVZ, SATS).
- Hooks: replace at least 6 bytes with `jsr` plus `nop` padding, and the trampoline replays the replaced instructions.
  - Save every register; replay replaced EMAC instructions first.
  - If your code uses EMAC, set MACSR yourself and **leave ACC0 at 0**, because the OS sum routines start from it.
  - One-time setup goes in a hook in the page initializer (`0x401885D2...`), never in boot time.
- Mod code: gcc/as with `-mcpu=54418`, no `.bss` (put variables in `.data`), no libgcc (`nm -u` empty).
  - ColdFire limits: `muls.l` takes no absolute address, there is no `exg`, `movem` takes only `(An)`/`d16(An)`, short branches reach ±127 B.
- **Spare storage the OS saves without knowing:**
  - per track: engine word +106 (hidden id 72);
  - per kit: unused words of the pattern kit at `*0x800030BC` (ids 0, 0x1A, 0x24, 0x27, 0x29, 0x2A, 0x37, 0x46, 0x38). Store values XOR their default, so old projects load with defaults;
  - kit words 41-43 of the 12 per-track kit blocks (Digitakt MIDI-track data, unused here);
  - 256 bytes in the project settings file.
  - A "free" parameter id can be an alias the OS shows in some modes, so audit it.
- UI internals: parameter descriptors at `0x4022D59C + 52*id`; page objects at `0x41B9F3C8` (44 B, 8 slots); per-parameter `std::function` objects at `0x41B9FA24 + 84*id` (+20 text, +36 icon, +68 style). Page 25 ("OB8") is a free Digitakt leftover. **Rewrite a `std::function` only from UI code, never from the audio interrupt.**
- **Audio mods:**
  - Hook the mix function; keep the OS's EMAC `msac` sign convention (the result is -Σ g·x).
  - Do nothing when there is nothing to do. Compute at 24 kHz where the sound allows it.
  - Ramps must snap to their target or the effect never goes idle.
  - Limit how far a modulated delay moves per block.
  - Keep a cost-per-block regression test (count instructions with `UC_HOOK_CODE` after `ctl_flush_tb()`).
- Projects: SyntHack OS (9 mods on hardware, MIT); SY FM4 (4-operator FM replacing SY TONE, which also patches CPU #2); Syntakt Firmware Workbench.
  - The Workbench replaces SY CHORD's waves: 31 slots of 257 big-endian Q31 samples, measured on a unit within 1 %. It adds a Deja Vu LFO, DV-H. It refuses any file but 1.41 and checks that only the declared regions changed. `[hw]` {syntakt-workbench}

## Syntakt OS 1.42 container and CPUs (digikit finding 70, static reading, 2026-10)
- `Syntakt_OS1.42.syx`: ELE3, 2,029,486 bytes, META stamp 2026-09-30 (same day as DT2 1.17 and DN2 1.12), SHA-256 `ded3c59f...7f37c1`; SysEx transport id `0x16`, OS-stream byte `0x11`; same packing codec as DT2/DN2; per-packet checksum constant K = 0x11. `[doc]` {digikit-f70}
- **No HMAC trailer - the Syntakt OS file is not signed** (last 32 bytes zero, no SHA-256 constants in sections 2-4); only the content checksum applies. `[doc]` {digikit-f70}
- Sections: 5 META; 2 bootstrap (dest word `0x04000000`, ColdFire code at `0x8000xxxx`, 30,782 B); **1 present only on Syntakt: `0xFF` padding then a bitstream-like blob (149,516 B) - the FPGA configuration** (the bootstrap configures a Xilinx-style FPGA via INIT_B/DONE; MAIN only reads a status word); 3 MAIN at `0x40000400` (3,442,576 B, same reset path as DT2: entry `0x400004e8`, SP `0x48000000`); 4 UPDATER at `0x80000400` (32,768 raw); 6 present only on Syntakt (a 5-entry trap/jump table plus SPI helper code, 1,744 B); **7 is not a SHARC stream here but a standalone ColdFire program** linked at `0x40000400` (entry `0x40001070`, 383,760 B) driving a DSPI-like block at `0xFC05C000` - consistent with a second ColdFire that runs the digital machines `[?]`; 8 byte-identical to DT2/DN2's section 8. `[doc]` {digikit-f70}
- **Peer link ("DSP boot"):** a mailbox in the FlexBus window at `0x10000000` ("HO" hello / "NO" -> DSP_MEM error; `0xA5A5` at +4 for OK), a doorbell on GPIO PA bit 4, EPORT IRQ4 handshake, 2 KB chunks to `0x10000800`, DSPI2 with eDMA channel 29; status values WAIT, init fail, TIMEOUT, BUFSIZE, DSP_MEM, CF_MEM, OK; the OS shows "DSP BOOT FAILURE (TIMEOUT/CF/DSP/BUF)". Peer states include LOAD_OS, BOOT, RUNNING, UPLOAD_SAMPLES. `[doc]` {digikit-f70}
- Only 27 of 172 digikit anchor rules hit on Syntakt 1.42 (vs 111/111 on DT2 1.17) - the Syntakt is a different platform, DT2 tooling does not carry over.
- **digikit's scope rule, adopt it: never modify section 1 or the bootstrap, never reconfigure or emulate the FPGA (risk to the analog circuitry).** `[doc]` {digikit-f70}
- Correction to earlier forum talk ("two ColdFires and an FPGA"): digikit's reading supports an FPGA and a second ColdFire program; SY FM4's "CPU #2" fits that.

## Gaps
- **Signing:** the HMAC presence in 1.41 versus 1.42 is a conflict, see above.
- **Free executable storage on CPU #2:** unresolved (machine-45 research).
- **OS 1.42 addresses:** all mod projects target 1.41 (SY FM4 targets 1.40A). digikit's 1.42 reading shares only 27 of 172 anchors with the DT2.
- **The FPGA's role** and section 8's meaning.
