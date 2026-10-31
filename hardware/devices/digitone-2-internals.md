# Digitone II - internals collected from the research repos (OS 1.10E / 1.11 / 1.12)

Complements [`digitone-2.md`](digitone-2.md) (overview) and [`digitone-2-os111-reference.md`](digitone-2-os111-reference.md) (modding-skill reference, OS 1.11). Sources are the docs of dnfw (dn2_firmware_explore), dn2-cfw/Digiwerk, digikit and DigiRust, read 2026-10-31 and all **second-hand**. Evidence tags as in `../README.md`; digikit's own labels are kept where it gives them: **[V]** verified by running, **[D]** documented by prior research, **[O]** open, **[C]** corrects an earlier claim. Addresses differ between OS versions - each line says which one it was measured on (unknown = not stated).

## Image identity
- MAIN OS = section id 3 of the ELE3 container; **load address `0x40000400`** on Digitone II and Digitone mk1; big-endian; 16-byte header, first instruction `46 FC 27 00` (`MOVE #$2700,SR`) at `0x40000410`. Depacked size: DN2 1.10E **3,085,696 B**, DN2 1.11 about 3.19 MB (3,192,192 B per the modding skill), DN1 1.42A 2,420,912 B. CPU ColdFire V4e (octabam loads MAIN OS at the same address). Mutable state lives in SDRAM at `0x80000000`; the bootstrap (section 2) is read at load base `0x800003fc`. `[doc]` {dn2-mainos-image} {dn2-skill-firmware}
- Internal C++ namespace: `Digisharc` on DN2, `Digitone` on DN1; 454 Itanium-ABI type names recovered from DN2 1.10E (candidates only - the symbol script gives false positives such as `3VVE`). `[doc]` {dn2-mainos-image}
- Landmarks (1.10E/1.11): frame ISR `0x40025e0a`; modulation module `0x400daed2-0x400db32e`, kernel `0x400db1dc`, driver `0x400db22c`, MSAC-with-load at `0x400db1f6`; string pool file offset `0x1F7000-0x202000` (load `0x401F7400`+); LFO page labels `LFO1-LFO3` only, `LFO3` at `0x40201cb0`; SETTINGS menu block `0x40200b09`; the unique cosmetic string `PERSONALIZE` at `0x40200b2e` was used as a harmless patch target in dnfw's "Gate E". `[doc]` {dn2-mainos-image}
- Product/build/version strings in the container header: DN2 product code 52, build `0059`, version `1.11`; DT2 43, `0079`, `1.16`; DN1 54, `0104`, `1.43`. **The "(0059)" etc. in digi-roll-studio's OS list are these build strings.** `[doc]` {dn2-ele3}

## Stock files (SHA-256, first 8 ... last 8 hex), as pinned by dn2-cfw's FIRMWARE.md
| OS | hash |
|---|---|
| 1.00A | `3b044824...53d5fc7d` |
| 1.10A | `4dcc46fa...ff0090cc` |
| 1.10B | `e8fb540a...78e66853` |
| 1.10C | `8db03f84...583d30b1` |
| 1.10E | `9881ee5c...56cac504` (pinned by digikit) |
| 1.11 | `2af43e65...628472e0` (pinned by digikit) |
| 1.12 | `7e5b8a73...c02ceb35` (pinned by digikit) |
The older files in that project's archive came from an archive.org item and passed elektron-firmware-tool's checksums on 2026-10-05. `[doc]` {dn2-cfw-firmware}

## Hardware map and budgets (OS 1.12 unless noted)
- Flash layout: bootstrap `0x40000-0x80000`, container from `0x80000`, test-flag record `0x380000`, serial record `0x3c0000`, persistence from `0x400000`. Receive buffer **2 MiB**; the stock 1.12 container is `0x1CC740` bytes. `[hw]` {dn2-cfw-handoff}
- **The in-place loader is the hidden size limit.** Section 4's loader (`0x8000357c`, stage `0x40200000`) has a stock margin of **+31,182 bytes**; elektron-firmware-tool's default compression level (`-l 3`) gives **-39,318** and corrupts the image. Every build needs a margin >= 0 at both loader stages; elekloader's default packer produced a container too large for the receive buffer, so the DN2 build uses a dense packer (`codec/dense.py`). Stock Digitakt II 1.17 also fails the in-place path (margin -31,912). `[hw]` {dn2-cfw-handoff}
- Elektron's own streams keep the furthest match within a 1 MiB window and the longest match at 2,048 bytes; a packer that exceeds them is refused by the build tool. Compressed streams are padded to a multiple of 4 B. `[doc]` {dn2-ele3}
- Panel MCU blob at `0x402F7D40` (version word `0x402f7d44`) and its updater must stay stock. **Section 8 is the Outbox 8 accessory firmware and must also stay stock.** The bootstrap holds the recovery menu and signing-key material. `[doc]` {dn2-cfw-handoff} {dn2-ele3}
- Free ColdFire/DDR memory measured by dn2-cfw: DDR `0x46800000-0x47F00000`, SRAM `0x8000F980-0x80010000`. DSP: **no code in `0x315f8c-0x318000`** (a build's DSP stop was traced there); free DSP memory candidates (not confirmed at run time): L1 block 2, the L2 tail `0x2008823c-0x200f9fff`, DDR above the image at `0x8052fbe0`. `[hw]` {dn2-cfw-roadmap} {dn2-cfw-handoff}
- digikit: Section 7 may be stored at most `0x100000` and depacked at most `0xfffff`; the boot ROM workspace is 8 KB and a block may not target it; the DSP run-time code area is 512 KiB allocated first-fit; the UI task stack is 160 KiB (3.3 KiB used inside a load). `[doc]` {digikit-findings}
- Interrupt/peripheral facts: DIN MIDI is UART9 (31,250 baud), panel LEDs are UART8; the audio SSI0 request rate is 96 kHz; forced INTC sources 44 and 57 (vectors 108 and 121) drive the sequencer; vector 191 needs forcing even once the RTOS runs. `[doc]` {dn2-cfw-handoff} {digikit-findings}
- Boot sequence: DSP boot -> eMMC -> boot record -> project decode -> mount -> frame interrupt -> main-OS task. A boot-time hook can sit at the main-OS task entry. Safe mode is triggered by a boot counter plus a flag; the counter clears after 30 s of the firmware's block counter; a CPU exception halts the device. `[doc]` {digikit-findings}

## Audio/DSP side
- SHARC+ ADSP-2156x running FreeRTOS; the **1.12 DSP program is byte-identical to 1.11's**. `[doc]` {dn2-cfw-handoff}
- DSP effect entry points (SHARC, 1.12): chorus `0xb84d5c`, delay `0xb8482c`, reverb `0xb836bc`, compressor `0xb8541d`; FX bus `0x1c1738`; render `0x1c2712`; effect parameters at TX frame offsets `0x9fa-0xa53`. Stock per-block cost about **5.4k instructions (delay)** and **16.6k (compressor)**; the replacement versions measured 18.6k and 47.7k, so hand-assembling five loops is needed to get below stock. Stock DSP load measures 63-65 % on the unit. `[hw]` {dn2-cfw-handoff} {dn2-cfw-roadmap}
- Owner's DSP budget for new work: typical about 70 %, worst case under about 75 %, measured on the unit. `[doc]` {dn2-cfw-roadmap}
- Frame link: the unused frame tail works as a **DSP code channel** on both devices (+23 DSP instructions per block on DT2, +26 on DN2; throughput 964 KB/s on DT2 1.16/1.17 vs 71.6 KB/s on DN2 1.11/1.12; byte-exact at 4 and 64 KiB). `[doc]` {digikit-findings}
- Trig mask in the frame on 1.16 is `0x22`, release mask `0x24` **[C]**; the 1.16 sample slot is `0xE0 + 0x60*t` **[C]**; the SPI-slave driver control block is at DM `0x261a10`; the Digitakt II selector table at `0x2567c0`. `[doc]` {digikit-findings}
- SHARC tooling facts: the ADSP-214xx Ghidra SLEIGH cannot parse this stream (wrong core generation, VISA-compressed); a project emulator had no semantics for 48.7 % of instructions; dn2-cfw's `sharcvm` passes 2,036 of 2,039 selache test cases (the 3 failures are selcc output problems); selcc miscompiles `fx_exp2` and `fx_log2` at every `-O` level and re-evaluates a local initialised with a comparison at each use. `[doc]` {dn2-cfw-handoff}
- Denormal results are returned as zero (per-rule table, **[V]**). A Digitone II 1.11 trig-retrigger distortion is deterministic **[V]** - the voice velocity writer is still **[O]**. `[doc]` {digikit-findings}

## ColdFire / MIDI side findings
- The 4-note MIDI limit is code only (NOTE/NOT2-NOT4 rows, `FUN_40055606`, a 4-byte default chord, 4-note SHAPE chords); the engine and pattern format are not limited; the note pool is 8,192 six-byte entries. Traps: the lock-clear path writes -1 to notes 1-4; the 8-bit MIDI output counter at `0x44600ca0` can wrap on large note-off bursts and leave notes stuck. The arp is kept off MIDI tracks by structure (not fully confirmed). `[doc]` {dn2-cfw-handoff}
- Hook events in dn2-cfw's core: `ev_midi_step` (sequencer, interrupt level), `ev_midi_note` (MIDI task before note-on); `ev_tick` at `0x4002e464`, `ev_key` at `0x4002f20c`. `[doc]` {dn2-cfw-handoff}
- Machine dispatch: Digitakt II limits an added machine to **one SRC page** (a second page is not possible); Digitone II supports an added machine with its own SYN page at run time. A run-time unload is refused with code -26 on both. `[doc]` {digikit-findings}

## +Drive and storage (digikit findings 14, 23-24, 35, 43-47)
- +Drive block records are 128 bytes; the real filesystem uses 32 KB extent-mapped pages with hierarchical directories; MmcFs has fixed-capacity project, sound and kit pools; its bitmaps at sector `0x800` are **write-protect bits, not occupancy**; a panel SAVE lands in project slot 0 and does not update the MmcFs bitmaps. digikit's card module store uses sectors `0x38000-0x3E000` (blank on a real DT2 card when checked); DT2 modules can live as files in a `/digikit` folder; the USB SysEx store is version 2 with a receive ceiling of 1.0-1.4 MB/s (about 100 instructions per byte). `[doc]` {digikit-findings}
- Native sample content hash and container integrity are covered in digikit's findings 14 and 01 (not read in detail).

## Disassembly pitfalls (agents will hit these)
- Reference disassembler: `m68k-linux-gnu-objdump` 2.42, `-m m68k:cfv4e -z`; objdump prints indexed-mode displacements in hex without `0x` and `d16(An)` displacements in decimal - confirm against raw bytes. Padding `0x0000` words appear as clusters. Bootstrap needs `--adjust-vma=0x800003fc`. `[doc]` {dn2-mainos-image} {dn2-cfw-handoff}
- Capstone has no ColdFire mode: 98.95 % of boundaries right over `0x40001000` + 64 KB with 201 divergences (it assigns two bytes to each failed instruction and desyncs; it decodes `00 00 2f 0a` as `ori.b`, which ColdFire removed). Stock Ghidra `68000:BE:32:Coldfire` reached 99.76 % over 512 KB but lacks `movclr.l ACCy,Rx` (flow stops at words `a1c0 a3c1 a5c2 a7c3`, so decompilations of the frame ISR and modulation module may be truncated) and gets MSAC-with-load wrong (accumulator selection inverted). digikit's `68000:BE:32:ColdfireEMAC` module fixes this - re-import rather than switching language on an existing program. Auto-analysis of the 3.19 MB 1.11 MAIN OS takes about 128 s; close the Ghidra GUI before headless runs; some large switches report "Could not recover jumptable" and must be read as assembly. `[doc]` {dn2-mainos-image}
- The emulator drops keys for modded files because digikit identifies the panel layout by SHA-256; plain Unicorn gets EMAC fractional mode wrong. `[doc]` {dn2-cfw-handoff}

## Known unknowns recorded by the authors
- dn2-cfw: Overbridge shows "incompatible OS version" with its builds (open as of 2026-10-22); Space Echo merged with the 3-band compressor stopped the DSP on the unit (parked); whether a project saved on a grown parameter table loads on stock is untested. `[hw]` {dn2-cfw-roadmap}
- digikit: real-time DSP audio in the emulator is **[O]**; the DT2 "Rung C" halt has no confirmed cause **[O]**. `[doc]` {digikit-findings}
- DigiRust (Digitone II OS 1.12, MIT): browser patcher in a worker plus a macOS app (ad-hoc signed, needs APFS/HFS+ for hard links); generators for Patch, Kit, Pattern and Phrase with defaults Density 30 % and Brutality 35 %, "Control All" macros, a live drone latch and Perform Kit restoration; output `Digitone_II_OS1.12_DigiRust.syx`; the developer reports it runs on a real unit without issues, "not a safety guarantee". `[doc]` {digirust-readme} {digirust-features}
