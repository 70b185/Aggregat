# Syntakt

Coverage: **medium** (platform, memory map, audio path and modding rules from SyntHack OS; 1.42 container from digikit). Projects: [../../catalog/syntakt.md](../../catalog/syntakt.md)

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
- **Mod data written for defaults slows project load and save (Synfact, OS 1.41):** a user saw a project load slowly when switched to from another project and save more slowly than usual; a reboot straight into it loaded normally. The export was valid. The ARP mod wrote and sealed a 320-byte carrier for every kit even with default settings, so load checked all 1,664 bindings; leaving default carriers absent cut the emulated serialization from 24.8 M to 4.8 M instructions (81 % fewer). The slowness is a user report; the cost is `[emu]`, the wall-clock gain not yet measured. `[doc]` {synfact-lifecycle} ([I50](../INCIDENTS.md#i50-mod-data-written-for-default-settings-slowed-project-load-and-save))
- **Tested on a unit (Modwerk, 2026-11-04, OS 1.42):** the startup-menu recovery works over MIDI DIN through a generic USB-to-MIDI cable: FUNC at power-on, TRIG 4 (OS UPGRADE), stock 1.42 sent from Transfer's legacy SysEx page; the unit booted and showed 1.42. This run recovered a working unit; recovery of a unit that does not boot is still untested. USB does not work for this path. `[hw]` {modwerk-st-probe} ([I46](../INCIDENTS.md#i46-syntakt-startup-menu-recovery-tested-over-din))
- **A modified 1.42 image boots and runs (same run):** Modwerk's boot probe (version shown `MW01`, flashed over USB with Transfer) booted to the live UI, played a stock project, came back after two power cycles, held every sample slot filled with no hang or exception screen, and played ten minutes cleanly; flashing stock 1.42 over USB restored the unit. Not tested: OS 1.40, the probe under Outbox 8, an SRAM-tail signature. `[hw]` {modwerk-st-probe}

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
  | 8 | the shared ARM Cortex-M image (not a second FPGA; CONFLICTS S15) | 159,948 B | identical in size to the DT1/DN2/Rytm/A4 image whose hash is known |

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
- **Hardware lesson `[hw]`:** SyntHack up to v0.8.0 kept mod code at `0x46000000`. Projects with SP TWINSHOT samples then crashed at boot. Since v0.8.1 the mod code (compressed, appended to section 3 at `0x40348000`) is unpacked into a 64 KB block that a hook at the end of heap init (`0x4010358E`) reserves first. ([I20](../INCIDENTS.md#i20-mod-code-at-a-free-address-crashed-projects-with-certain-samples))
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

## CPU #2 (the voice CPU, section 7) - memory map from SynCrackd (OS 1.41 and 1.42) {syncrackd-mm} `[doc]`
- **Section 7 is byte-identical in 1.41 and 1.42** (SHA-256 `daf6451c...783bc2`). It is ColdFire ISA-C with EMAC, MCF5441x-class: compile with `-mcpu=54418`, disassemble with `-m m68k:isa-c:emac`. CPU #2 has **its own 128 MB SDRAM** at `0x40000000` (SP `0x48000000`, entry `0x40001070`). `[doc]`
- **Only 39.8 KB is code** (`0x40000404-0x40009f88`: boot, audio interrupt, voice loop, 12 engines, sample loader), followed by 284 KB of tables and data. Code room for mods is almost nil: ~318 bytes in small pieces remained after SynCrackd's images.
- **CPU #2 configures its own FPGA:** a packed bitstream at `0x40041060` is unpacked to `0x40042000` (54,664 bytes) at init. That is the same size as the Analog Heat +FX FPGA section, so it may be the same part `[?]`. Keep away from it (rule A22).
- **The sample pool is in CPU #2's RAM:** 64 MB from `0x4004f750`, in BSS zeroed at boot. A 64-entry slot table `{u32 frames, u32 pointer}` is at `0x4404f754`.
  - Format: 64 times `u32 frames` + big-endian int16 mono.
  - The main CPU fills it at boot in 2 KB chunks through the shared window `0x800`, with an unchecked 16-bit index. This is the slow boot the manual mentions.
  - Per slot at most 524,287 frames (10.9 s; positions are 20.12 fixed point). The stock UI limits slots to 5 s and "32 MB".
- **Above the BSS, `0x4404f980-0x48000000` (63.7 MB) is not referenced by any section-7 instruction** and is used for SynCrackd's state. Leave the top megabyte for the stack (its depth is not measured). This is CPU #2's RAM, not the main CPU's region that sample loading overwrites (CONFLICTS O2). `[hw]` (alpha, one unit)
- **Shared window** (CPU #2 `0x0-0x1000` = main CPU `0x10000000`, chip select 0, 16-bit, one wait state):
  - `0x000-0x1b0`: the parameter block, copied to `0x80008000` every block;
  - `0x1b0-0x5b0`: 8 mono track buffers, sent by eDMA 47;
  - `0x5b0-0x800`: unused by stock;
  - `0x800-0x1000`: the sample chunk at boot.
- SRAM `0x80000000`: 8 voices of 1,800 B, 8 mono int32 output buffers, 8 parameter blocks of 142 B. The highest static reference is `0x8000f670`, so treat SRAM as full.
- **Twinshot (engine 11, machine type 44)** reads the parameter slots 18-25: TUN1, SMP1, FLT1, MIX, TUN2, SMP2, loop flag, DEC1. **A sample select below the centre plays the slot in reverse.** `[emu]`
- SynCrackd replaces Twinshot (and CY ALLOY) with a 64-slot stereo sampler, loops, slices, time stretch and transient triggers. It is OS 1.42 only, alpha, tested in emulation and on one unit, MIT.
- Synfact (OS 1.41) adds DT mk1 sample machines, a per-project pool, polyphony across tracks and a third LFO.
  - It ships its firmware change as a **zlib-compressed XOR mask** against the official file, pinned by hash.
  - It needs a second mods file (515,808 B) sent with its own transfer tool after the flash. Boot is confirmed on a unit (core 1.4 and 1.7.2, 2026-11-09); the safe-boot rollback is not yet tested on hardware. `[hw]` {synfact} {synfact-core}

## How mods are built on the Syntakt (SyntHack modding guide, worth copying) {synthack-guide} `[doc]`
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
- **Where mod code lives at run time (SyntHack modarea, v0.8.1+):**
  - The OS image has only ~2 KB free, and everything after it is zeroed at boot. So mod code is appended to section 3 compressed (SHLZ, at `0x40348000 + offset`).
  - At boot it is unpacked into the **first 64 KB block of the OS heap**: buddy allocator `0x4010350C`, 16 MB pool at `0x444E38C0`.
  - The block is reserved by a call right after heap initialization, so it always gets index 0, and the OS never hands it out again.
  - The earlier home above the BSS (`0x46000000`) was overwritten whenever samples loaded (SyntHack issue 4), which settles conflict O2. `[hw]` {synthack-mods}
- **Kit and project storage that round-trips through stock code** (SyntHack kitstore/projstore):
  - Kit words 41-43 of the 12 per-track blocks go into 6 file bytes that stock's writer zeroes and its reader ignores.
  - 256 bytes go into the project settings block (`+0x227..+0x3FF` is zeroed by the writer and ignored by the reader), behind an `SH` marker.
  - Tests run the real writer and reader with and without the hooks.
  - Zero must mean "default", because stock-saved files load as zero. `[emu]` {synthack-mods}
- **Controlling the analog side digitally** (SyntHack master-comp): a feed-forward compressor detects on ADC 6/7 (the FX-track bus before its VCAs) and applies gain through those VCAs' control voltages (CV 35/36), once per block (~1.5 kHz). Its UI uses the Digitakt MIDI-track "CC Select" ids 262-268, which the Syntakt never uses. Cost: ~100 instructions per block when off, ~600 when on. Checked on the device (v0.9). `[hw]` {synthack-mods}
- Projects: SyntHack OS (9 mods on hardware, MIT); SY FM4 (4-operator FM replacing SY TONE, which also patches CPU #2); Syntakt Firmware Workbench.
  - The Workbench replaces SY CHORD's waves: 31 slots of 257 big-endian Q31 samples, measured on a unit within 1 %. It adds a Deja Vu LFO, DV-H. It refuses any file but 1.41 and checks that only the declared regions changed. `[hw]` {syntakt-workbench}

## Syntakt OS 1.42 container and CPUs (digikit finding 70, static reading, 2026-10) {digikit-f70} `[doc]`
- `Syntakt_OS1.42.syx`: ELE3, 2,029,486 bytes, META stamp 2026-09-30 (same day as DT2 1.17 and DN2 1.12), SHA-256 `ded3c59f...7f37c1`; SysEx transport id `0x16`, OS-stream byte `0x11`; same packing codec as DT2/DN2; per-packet checksum constant K = 0x11. `[doc]` {digikit-f70}
- **No HMAC trailer - the Syntakt OS file is not signed** (last 32 bytes zero, no SHA-256 constants in sections 2-4); only the content checksum applies. `[doc]` {digikit-f70}
- Sections: 5 META; 2 bootstrap (dest word `0x04000000`, ColdFire code at `0x8000xxxx`, 30,782 B); **1 present only on Syntakt: `0xFF` padding then a bitstream-like blob (149,516 B) - the FPGA configuration** (the bootstrap configures a Xilinx-style FPGA via INIT_B/DONE; MAIN only reads a status word); 3 MAIN at `0x40000400` (3,442,576 B, same reset path as DT2: entry `0x400004e8`, SP `0x48000000`); 4 UPDATER at `0x80000400` (32,768 raw); 6 present only on Syntakt (a 5-entry trap/jump table plus SPI helper code, 1,744 B); **7 is not a SHARC stream here but a standalone ColdFire program** linked at `0x40000400` (entry `0x40001070`, 383,760 B) driving a DSPI-like block at `0xFC05C000` - consistent with a second ColdFire that runs the digital machines `[?]`; 8 byte-identical to DT2/DN2's section 8. `[doc]` {digikit-f70}
- **Peer link ("DSP boot"):** a mailbox in the FlexBus window at `0x10000000` ("HO" hello / "NO" -> DSP_MEM error; `0xA5A5` at +4 for OK), a doorbell on GPIO PA bit 4, EPORT IRQ4 handshake, 2 KB chunks to `0x10000800`, DSPI2 with eDMA channel 29; status values WAIT, init fail, TIMEOUT, BUFSIZE, DSP_MEM, CF_MEM, OK; the OS shows "DSP BOOT FAILURE (TIMEOUT/CF/DSP/BUF)". Peer states include LOAD_OS, BOOT, RUNNING, UPLOAD_SAMPLES. `[doc]` {digikit-f70}
- Only 27 of 172 digikit anchor rules hit on Syntakt 1.42 (vs 111/111 on DT2 1.17) - the Syntakt is a different platform, DT2 tooling does not carry over.
- **digikit's scope rule, adopt it: never modify section 1 or the bootstrap, never reconfigure or emulate the FPGA (risk to the analog circuitry).** `[doc]` {digikit-f70}
- Correction to earlier forum talk ("two ColdFires and an FPGA"): digikit's reading supports an FPGA and a second ColdFire program; SY FM4's "CPU #2" fits that.

## What the Syntakt shares with other boxes (merged from analog-emu's Syntakt port, OS 1.42, static plus emulator) {analog-emu-syntakt}
- **The analog tracks reuse the Analog Rytm MKII's voice design.**
  - The voice control records have the Rytm MKII's format (command/depth word, start and target bytes, mode nibble, rate exponent and mantissa).
  - The cymbal oscillator banks use the Rytm's scale (43.62 units per Hz) and load the Rytm's CH/CB CLASSIC values.
  - So Rytm voice research applies here and back. `[doc]` (inferred from the shared formats)
- **Digital tracks:** rendered on CPU #2, then handed over by mailbox and eDMA channel 47 to CPU #1, which mixes them and sends them to the SSI1 codec. This agrees with SyntHack's audio path above. `[emu]`
- **An emulator now boots 1.42 with both CPUs** (analog-emu: stage 1 the main screen with a stand-in for CPU #2, stage 2 CPU #2 running for real). It is the only Syntakt 1.42 emulator in the catalogue; SyntHack's Unicorn harness targets 1.41. `[emu]`

## Synfact core and SMZ4 banks (OS 1.41, 2026-11-10) {synfact-core} {synfact-safeboot}
- **Bank store:** two 8 MiB slots inside the old 16 MiB `/mods` reservation, metadata sectors at eMMC `0x02bffe00` and `0x033ffe00`; the legacy record at `0x03400000` is still read. `[doc]`
- **Safe boot:** a bank moves CANDIDATE -> TRYING (written before any bank code runs) -> GOOD, set once AUDIO and the sample pool are ready and 150 UI ticks (about 5 s) have passed; a crash or power-off before that boots the previous GOOD bank or stock machines. Each bank names an exact core contract, and the core checks the stock bytes that LFO3 and MODULATION SKIP patch before any initializer runs. `[doc]`, rollback `[?]` (not yet tested on hardware). The first trial crashed every boot (I62).
- **Filter table:** the stock base-width filter reads Q31 poles from `0x40040060` (508 poles, then a zero tail; indices up to 1023 are read). A mod window in that tail made BASE+WDTH of 128 or more read code as poles; core 1.7.2 bounds the index. `[hw]` (I63)
- **Load:** MAIN is about 88 % with a plain pattern and 91-92 % with three POLY voices; code fetched from DDR costs far more than its instruction count (I64). `[hw]` {synfact-chorus}
- **Load after the MAIN optimisation (owner's unit, OS 1.41, stock pattern, 2026-11-13/14):** a minimal bank (System Info + Modulation Skip) reads 81 % MAIN, the full bank 86 % before and 83 % after the optimisation release; about 2 points sat in LFO3's per-block callback, about 1 in the stereo audio callbacks. The meter rounds to whole percent; at 48 kHz and 32-sample blocks one MAIN point is about 6.7 µs per block. `[hw]` {synfact-main-opt}
- **Appended boot storage is wiped at startup:** on OS 1.41 the storage appended after the MAIN image is cleared and reused once the early resident copy is done, so code placed there is gone when the application runs; only the resident reserve (64 KiB in Synfact's core) is safe for code called after boot (I104). `[hw]` {synfact-main-opt}
- **Stock track types:** every stock digital track type has bit 6 clear; Synfact's machines use types 64-79, so a mod can tell that all tracks are stock from the type bytes alone. The MAIN audio interrupt calls the stock modulation routine `0x40097afc` for every track on every block (about 6,600 emulated instructions for the full body). `[doc]` / `[emu]` {synfact-main-opt}
- **Build and voices:** builds use `-mcpu=54415` (an MCF5441x part), SMZ bank code `-fno-jump-tables`. Each track has one stock voice block at `0x80000000 + t*0x708`; the stock voice reset rewrites +`0x570`-`0x708` and zeroes 48 bytes at the pointer in +`0x56c`. `[doc]` {synfact-machine-ref}
- **Free memory, checked on a unit (2026-11-10):** a probe machine (type 70, MEM PROBE) filled the shared-window gap `0x5b0..0x7df` (AUDIO `0x5b0`, MAIN `0x100005b0`) and the AUDIO SRAM tail `0x8000f398..0x8000ffff` (after FM TONE's scratch; the stock boot leaves it zero) with a pattern and checked it every block: nothing else wrote either area over several minutes. Synfact core 1.8 uses both for stereo tracks. `[hw]` {synfact-memprobe}

## SY SWARM read from the audio program (model27 notes/84, OS 1.42 section 7, same in 1.41, 2026-11-16) {model27-maxsaw}
- **Engine 10 (SY SWARM):** update `0x400092ec`, render `0x400096e8`. Seven sawtooths from band-limited tables, one per octave (`0x40006588` picks the table by note, `0x40006434` reads it with linear interpolation); a centre that SUB moves down 0, 1 or 2 octaves (its increment shifted right and its table picked again, nothing else), six detuned oscillators driven by six tables indexed by DET; ANIM is three slow sines (about 1, 2 and 5 Hz, `0x40006074`) that phase-modulate oscillator pairs in opposite directions; NMOD is a noise generator (`0x40003eb4`) that phase-modulates the six; MIX uses two gain tables; every oscillator gets a random phase at a trig. `[doc]`
- **Its six detune tables equal Adam Szabo's published Super Saw model** (his offsets times his 11th-degree detune polynomial, KTH 2010) to 0.000 cents over all 128 × 6 values; its mix curves are not his. `[doc]` (computed by model27, static reading)

## Synfact findings: sequencer, kit slots, views, mixer (OS 1.41, 2026-11-14/16) {synfact-1117}
- **Sequencer step per track (MAIN):** the sequencer runs in a forced interrupt at `0x4008c924` (24 ticks a quarter note) for 13 tracks (12 = FX). Per track `t`: next step `0x43bd73fc+t`, step before `0x43bd7416+t`, ticks into the step `0x43bd7409+t`, steps toward the bar `0x43bd753c+t`. The step advances at `0x4008d0e4..0x4008d120`; length is the track's (track record `+969`, a word; record = pattern + `0x499*t`) when pattern byte `+0x21379` is set, else the pattern's (`+0x21374`). Trig preparation `0x4008b882` at tick 0 (call sites `0x4008cf00`, `0x4008cf14`; `0x4008c204` for a pattern started mid-way). UI copies `0x444e2370+t` (last) and `0x444e237d+t` (step), copied each tick at `0x4008d1a8`; live recording reads `0x444e2370`. `[doc]` / `[emu]` (Unicorn)
- **The trig LEDs' playhead reads another copy:** the accessor `0x4008b734(t)` (read by `0x400c20ee`). playhead-st build 2 reversed the sound on a unit, but the LED playhead still ran forwards until this accessor was patched too. `[hw]` (I116)
- **Pattern and kit pointers:** playing pattern `0x43bd7430` with kit `0x43bd743c`, next `0x43bd7438` with `0x43bd7444`; live kits at `0x41ad5134 + k*0x1618`, k < 128. `[doc]`
- **Free tail in a kit slot:** an encoded kit slot is `0x1600` bytes; the native codec uses `[0, 0x14d2)`, LFO3 `[0x14e0, 0x15d0)`, playhead-st `[0x15e0, 0x15f8)`. Stock never reads the tail, so a project saved with mod data there still opens on a stock unit. `[doc]`
- **Unsaved kit changes reach a power cycle only through the mirrors:** a native kit edit ends in `KitActive::kitChanged` (`0x40172250`, vtable `0x401c33f4` +`0x5c`; object at `0x40a38b18 + 0x378d8`), which re-encodes the kit into its mirror slots (job at `0x4001082e`). Mod data written only on a project save came back after save + power cycle but not after a power cycle without save. `[hw]` (I116)
- **Key IDs beyond core-st's list:** TRK = 2, UP = 14, DOWN = 15, LEFT = 16, RIGHT = 17. The MainScreen header (`0x40032b0e..0x40032b72`) draws the tempo right-aligned to x 125 and the metronome left of it, rows 55..62. `[doc]`
- **View manager (UI controller +`0x40`):** list sentinel +`0x14`, tail +`0x18`, highest opaque node +`0x1c`; a node holds its view at +`0x8`; a view's closed flag is a **byte** at +`0x30`. Native close `0x400ffd02` sets it and requests deferred cleanup (manager +`0x22`); it does not destroy the view, and a shared owner can keep it alive after removal. Push `0x40100bc2` calls visibility `0x40100ade` before the new view's attach callback; visibility composes the UI synchronously (`0x4000a0e6`) and runs mod tick code. `[emu]`
- **Stock deferred cleanup drops a close raised during composition:** cleanup `0x40100ea4` clears manager +`0x22` at `0x40100f2c..0x40100f3e` after the visibility call, so a close requested by a tick inside that call is lost and the closed view stays in the list (key walks skip it but nothing removes it). Synfact core 1.8.2 moves the clear before the call. Mods that close views from tick code are exposed. `[emu]` (reproduced; the related unit symptom is I115)
- **MainScreen children:** MainScreen show `0x40033b74` publishes, in order, `+0x228`, the current parameter view `+0xc0`, `+0xe8`, `+0x218`, `+0xf0`, `+0x220`, so the parameter view is normally not the stack tail; permanent mute is a separate transparent child at `+0x230`. The stock LED setter `0x40008220` keeps the first write per LED. The native TRIG key advances the page index on release. `[emu]`
- **MAIN mixer call:** `0x400a4fce` calls `0x4008f1ca` with three stack words (the third is the mixer record); its frame is 556 bytes. The tail `0x4008fb38` combines ADC `0x8000ded0` with the preview bus `0x8000dfd0` and runs USB and codec output; six 256-byte buses start at `0x8000dad0`. Native transport STOP is `0x4008c288`. `[emu]` (analog-emu interpreter)
- **Load figures:** the whole mixer call is about 33,449 instructions per block in Synfact's fixture with preview (8,195 with only the preview path); recording MAIN LR stereo POST FX read 92 % MAIN in PLAY and 99 % while recording on a user's unit before Recorder 1.3. `[emu]` / `[hw]` (meter)
- **Resident reserve:** Synfact core 1.9.0 fills 65,524 of its 65,536-byte resident reserve. `[doc]`

## Modwerk's Syntakt plan and limits (GOAL.md, OS 1.42, 2026-11-16) {modwerk-st-goal}
- **Freeing RAM for mods:** Modwerk's pull request #1411 lowers the stack by 128 KB on OS 1.42 to free `0x47fe0000-0x48000000`; that build ran on one unit, also through a sample reload. Still open: fill the whole gap at boot, load samples, play and read it back. `[hw]` (one unit) / `[?]` (gap free)
- **Build margins:** the in-place depack margin of Modwerk's 1.42 boot probe is 16,679 bytes, and the container may not exceed 2 MB (the upgrade's receive buffer; flash geometry not read from a unit). A depack overrun hangs the unit at the logo. `[doc]`
- **SysEx message ids (product byte `0x16`):** stock answers `0x50-0x6f`, `0x7e` and `0x7f`; `0x00-0x0f`, `0x11-0x4f`, `0x70-0x77` and `0x79-0x7d` do nothing in stock. Whether Elektron's host tools send them is unknown. `[doc]`
- **No memory fence:** the MMU is off and the access-control windows are 16 MB wide. USB does not work in the startup menu, so recovery needs MIDI DIN; it has recovered a working unit, not yet one that fails to boot. `[doc]`
- **Located hook sites (1.40 and 1.42):** UI tick, key and encoder delivery, a SETTINGS menu row and the audio block; the display's draw path, project load and save and the sequencer step are still unknown. digiemu's Syntakt port (open upstream pull request) boots to the UI without the FPGA or the analog tracks. `[doc]`

## Gaps
- **Signing:** the HMAC presence in 1.41 versus 1.42 is a conflict, see above.
- **Free executable storage on CPU #2:** unresolved (machine-45 research).
- **OS 1.42 addresses:** all mod projects target 1.41 (SY FM4 targets 1.40A). digikit's 1.42 reading shares only 27 of 172 anchors with the DT2.
- **The FPGA's role.** (Section 8 is now known to be the shared ARM image found on other devices, not a second FPGA: CONFLICTS S15.)
