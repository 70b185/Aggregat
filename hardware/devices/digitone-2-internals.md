# Digitone II - internals collected from the research repos (OS 1.10E / 1.11 / 1.12)

Complements [`digitone-2.md`](digitone-2.md) (overview) and [`digitone-2-os111-reference.md`](digitone-2-os111-reference.md) (modding-skill reference, OS 1.11). Sources are the docs of dnfw (dn2_firmware_explore), dn2-cfw/Digiwerk, digikit and DigiRust, read 2026-10-31 and all **second-hand**. Evidence tags as in `../README.md`; digikit's own labels are kept where it gives them: **[V]** verified by running, **[D]** documented by prior research, **[O]** open, **[C]** corrects an earlier claim. Addresses differ between OS versions - each line says which one it was measured on (unknown = not stated).

## Main-OS memory facts for loaders (Digiwerk note T1.3, DN2 1.12, emulator write-watch) {dn2-cfw-t13}
- Reset entry `0x400004e8`, stack top `0x48000000`.
- SRAM copies: `0x402fd000-0x40305000` -> `0x80000000-0x80008000` and `0x40305000-0x4030c980` -> `0x80008000-0x8000f980`. The rest of SRAM is zeroed. **The free SRAM tail is only `0x8000f980-0x80010000` (1,664 B).** The DT2 has 3,840 B and a free block in the first half; the DN2 has none.
- The DDR clear runs `0x402fd000-0x466b84d0`. DMA buffers are reached only through the uncached alias (`0x4e6c0000-0x4e709340`).
- **Free DDR `0x46800000-0x47f00000` (23 MB).** It was never mapped or written in the emulated runs. `[emu]`

## DSP code room and load on the DN2 (Digiwerk DT01, DC01/DC02, SC01) {dn2-cfw-dc01}
- Proven room for added DSP code: **83,838 B over four regions** (L1 block 1 17,974 B, three code regions 9,798 / 31,606 / 24,460 B). Each function is placed first-fit.
  - Packs that fit: compressor + flanger 48 KB; with the tape echo 80 KB.
  - All four effects together (95 KB) do not fit.
  - L2 code runs through the I-cache like stock L2 code. `[hw]` (builds ran on the unit)
- **selcc output is about 10 % larger than needed** (field accesses cost 5 instructions). Digiwerk's peephole pass saves ~5-6 KB.
- **Their safety lesson:** stock code never puts a load into an I register directly before a 48-bit instruction that uses it (0 of ~14 cases; there is always work in between). The SHARC emulator does not model the pipeline, so the cautious pass refuses that pairing. Copy the rule: **do not create instruction pairings the stock code never has.** `[doc]`
- Load model used: load = (1.30 x emulated instructions + 11k) / 666,667. For one build it predicted ~74 % where the unit showed ~50-60 %, so the model overestimates. `[?]`

## The ColdFire-to-DSP frame and the panel (Digiwerk T3.2, T3.3, T2.1, T2.4b/c; DN2 1.12) {dn2-cfw-t3}
- **Frame:** 0xa80 bytes from `0x80005e60`, sent by DSPI2 (16-bit DMA, 1,374 halfwords); the reply arrives at `0x800053a4`, every block (1,500/s).
  - **All send-FX, compressor, external-input and master parameters are one block of big-endian words at `0x9fa + 2*(k-25)`** (`k` = the parameter row's mirror index; chorus is k 25-31).
  - Compressor routing is at `0xd4` (track bits) and `0xd6`.
  - 16 per-voice rows of `0x92` bytes start at `0xda`. **A row is a voice, not a track:** a track parameter goes to every row whose owner (`0xa5a + 2r`) is that track. `[emu]`
- **Audio clock:** SSI0 with eDMA 48 (RX) / 50 (TX), 96,000 requests/s. One major loop is one 32-sample block, and vector 170 forces vector 191 (the frame handler). The emulator needs this clock for PLAY to run the sequencer. `[emu]`
- **Panel and MIDI:**
  - Panel MCU on UART8 at 156,250 baud, sent through eDMA 35. LED messages: `B9 i v` (LED i, palette entry v) and `B5 i r g b` (palette entry).
  - DIN MIDI on UART9 at 31,250 baud: out by eDMA 37 (bulk) plus direct writes for realtime bytes, in by eDMA 36. `[emu]`
- **Notes:**
  - MIDI tracks have **no voice limit** in the output engine; the "4 notes" are only the UI's NOT2-NOT4 rows.
  - A pattern's note pool holds 8,192 notes, with at most 16 notes per step.
  - The MIDI note-output length is a byte counter over a 1,024-byte buffer.
  - Stock 1.12 plays more than 4 notes per trig from a modded project. `[doc]`
- **DSP free memory (static):** L1 block 2 is never written by the stream (128 KB), the L1 block 1 tail `0x2dd52c-0x2effff`, and L2 from `0x2008823c`. **Correction:** the startup turns on all three L1 caches, so `0x39c000-0x39ffff`, `0x2ec000-0x2effff` and `0x31c000-0x31ffff` are cache, not free. dnfw's proven code area is `0x2dd600-0x2e7000`. `[doc]`
- **Emulator pitfall:** digikit's Unicorn got EMAC **fractional mode** wrong (MACSR F/I = 1). The frame handler uses it, so values that pass through EMAC can be off in the emulator. `[emu]`

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

## Project/preset file formats seen by DNX (NoiseAndMatter; {dnx-page})
Digitone mk1 projects are `.dnprj`, Digitone II projects `.dn2prj`, sound banks are `.syx`; payloads are **LZ4-compressed inside a ZIP**; SysEx uses 8-in-7 MSB-first encoding; the DN2 product id for probing is `0x15`; the Digitone II +Drive holds 2,048 presets (a DN2 library in digi-roll-studio's test held 1,189, of which 388 were Digitone mk1 files in a second container format). A `.dnx` backup stores all projects, soundbanks and kits plus a manifest but not the global settings (MIDI, sync, audio routing, personalisation). The "Waverider" firmware (dn2mk2) adds wavetables that DNX can view/import. DNX refuses to write to the loaded project and refuses DN2-preset -> DN1 conversion; close Transfer and Overbridge first (shared MIDI ports). `[doc]` {dnx-page} {digi-roll-studio}

## OS release history (dn2-cfw `notes/dn2-release-history.md`, dnfw `docs/os-versions.md`)
| OS | Bootstrap version | Build | What changed (sections) | Impact for mods |
|---|---|---|---|---|
| 1.00A | 0x0107 | - | baseline: MAIN 3,061,120 B, DSP 832,064 B, no Outbox 8 section | - |
| 1.10A | 0x0108 | - | bootstrap, MAIN and DSP changed (DSP 833,060 B) | DSP mods from 1.00A do not carry over |
| 1.10B / 1.10C | 0x0108 | - | MAIN only (freeze fix: Note On/Off on the FX control channel) | MAIN-only |
| 1.10D | - | 40049 (built 2025-07-27) | "updated production process"; bootstrap 28,254 B at `0x01080000` | - |
| 1.10E | **0x0200** | 40050 (built 2025-09-10) | bootstrap almost fully rebuilt (24,934 of the first 28,254 bytes differ; now 30,302 B at `0x02000000`); MAIN +4,096 zero bytes plus 70 changed blocks (dense near `0x402dcb12` and the dispatcher at `0x400cf906`); updater and blob identical; dnfw infers (not confirmed) a hardware revision | bootstrap upgrade runs after the first restart |
| 1.11 | **0x0201** | 40059 (built 2026-09-08) | bootstrap 30,302 B at `0x02010000` (5,666 bytes differ from 1.10E); MAIN 3,192,192 B (+106,496, content shifted throughout); **updater changed for the first time** (14,231 bytes differ); DSP 836,956 B; new section 8 (Outbox 8, 159,948 B); new persisted storage types `bobConfigStorage_v0_t`, `midiSetupStorage_v3_t`, `projectSettingsStorage_v8_t`, `projectStorage_v14_t`, `soundPoolStorage_v3_t` (v2 removed) | DSP changed; ColdFire mods are per release |
| 1.12 | 0x0201 | - | **MAIN only** (3,196,288 B, +4,096); bootstrap, board test, DSP and Outbox 8 identical to 1.11; Outbox 8 main-output routing | a DSP mod verified on 1.12 fits 1.11 too |
`[doc]` {dn2-cfw-release-history} {dn2-os-versions}
- **Porting:** 1.11 and 1.12 MAIN images share only their first 28 bytes; about 48.7 % of 48-byte windows from 1.11 appear verbatim in 1.12 but at 535 different offset shifts - fixed-address patches do not port; locate hook points by masked byte patterns (`find`/`expect` fields) and pin every mod to its build by hash. Units already at bootstrap 0x0201 will not be upgraded again. `[doc]` {dn2-cfw-release-history} {dn2-os-versions}
- **Rules for a new OS version (dnfw):** compare decoded content (`dnfw diff`), never compressed bytes; use `--strings` as a filter only; read the densest change blocks first (a relink gives many small blocks, a rewrite one large one); check bootstrap and updater separately (the updater matters for recovery); re-locate every patch via `find`/`expect` and name the target build; examine unfamiliar sections (id 8) before relying on the image; mangled storage-struct names show which persisted state changed. The compression and signing scheme was unchanged in 1.11 and the codec limits were measured on 1.11. `[doc]` {dn2-os-versions}

## Bootstrap and the recovery path (dnfw `docs/bootstrap.md`, 1.10E image)
- Section 2 is 30,302 bytes; header `[u32 payload_size = 0x7656][u32 0x80010000]` (the second word is not the load base); load base `0x800003fc` incl. the 8-byte header, payload runs at `0x80000404`; status strings READY TO RECEIVE `0x80006603`, RECEIVING... `0x80006614`, UPGRADING... `0x800065e6`, "BOOTSTRAP UPGRADE" at payload offset `0x602c`. `[doc]` {dn2-bootstrap}
- **Receive phase:** start marker `0x7F` (kind 1) records the total packet count and starting sequence number; data packets `0x7E` are sequence-checked, their checksum verified over 119 bytes and 101 decoded bytes copied to the buffer; end marker (kind 2) verifies totals. **The progress bar measures reception only** (`received * 128 / total`). A bad sequence number or checksum sets the state to 0 and the transfer silently stops - no retransmit. Transport is one-way DIN MIDI at 31,250 baud. `[doc]` {dn2-bootstrap}
- **Write phase:** the receive buffer is RAM at `0x40000000` holding `[u32 size][u32 checksum][container]`; the container check sums `(word_index ^ word)` over `size/4` words from `0x40000008`; flash is erased in 256 KB blocks from `0x80000` and the raw container is written in 512-byte chunks. **No decompression happens here** - the updater and MAIN OS decompress sections on the next boot (which is why the in-place loader margin matters). The page does not mention any seal/signature verification in this path. A different routine (`FUN_80011844`) flashes a single small section with a CRC (residue `0xDEBB20E3`) and 64 KB caps - not the recovery path. `[doc]` {dn2-bootstrap}

## Runtime memory map, MAIN OS 1.11 build 40059 (dnfw `docs/memory-map.md`; addresses change on every relink)
| Region | Range | Size / contents |
|---|---|---|
| Program code | ~`0x40000600`-~`0x401d0000` | ~1.95 MB |
| Read-only data | ~`0x401d0000`-~`0x40287000` | parameter tables (table at `0x401f7fc4` on 1.11; `0x401f83a4` on 1.12), vtables, strings |
| Padding / code caves | within ~`0x40287000`-`0x402fc000` | ~29 KB free in 41 runs >= 256 B, largest ~1 KB |
| .data initialisers | `0x402fc000`-`0x40304000` -> copied to `0x80000000`; `0x40304000`-`0x4030b980` -> `0x80008000` | not free |
| Main BSS (SDRAM) | `0x402fc000`-`0x466b74d0` | 104,576,208 B incl. a static heap arena; ParameterSet slot tables at `0x42c6xxxx` |
| **Unclaimed RAM above BSS** | `0x466b74d0`-`0x48000000` | 25.3 MB; only the stack may grow into it (mods there used ~49 KB) |
| Stack | top `0x48000000`, grows down (`moveal #0x48000000,%sp` at `0x400004f2`) | depth unmeasured |
| Fast SRAM | `0x80000000`-`0x80010000` | 64 KB: copied .data and small BSS; the section 4 updater loads at `0x80000400` |
| Peripherals (MBAR) | `0xfc000000`-`0xfc0fffff` | startup writes `0xfc080000` (memory controller) |
dnfw's own mod allocations above BSS: LFO4 tick state `0x46700000` (12,288 B), boot screen `0x46710000`, LFO4 code/tables `0x46800000`, relocated parameter table `0x46900000` (19,808 B). Compare elekloader's 1.12 profile (clear `0x402fd000-0x466b84d0`, core area `0x47F00000-0x47F40000`) and dn2-cfw's free DDR `0x46800000-0x47F00000`. `[doc]` {dn2-memory-map}

## Arpeggiator vs MIDI tracks (dn2-cfw `notes/T2.2-arp-midi-v2.md`, OS 1.12, static analysis only)
- The arp is part of the voice interrupt; its only output is the internal voice allocator `FUN_4002a6a2`, nothing on that path creates a MIDI event. Barriers: UI gating by `FUN_40031274` (isMidiTrack) at the ARP key `0x4005f9b6`, menu auto-close `0x400187ea`, LED `0x40060dde`; the step handler `FUN_400d99de` sends MIDI tracks to `FUN_400d8cbe`; live keys on a MIDI track go straight to the MIDI task via `FUN_4012bb90`. `[doc]` {dn2-cfw-arp}
- Data: arp settings per track sound record at `kit+0x34+t*0x48b` (`+0x15f` mode, `+0x160` speed, `+0x161` range, `+0x162` note length, `+0x164` step mask, `+0x166..0x175` offsets); track MIDI mask s16 at `kit+0x5cda`; events are 0x6c bytes (alloc `FUN_40138cb6`, schedule `FUN_40138e3c`), MIDI events 0x60 bytes, MIDI task queue `0x445ff870`, free list head `0x4460f4b8` (2,048 entries), MIDI output byte count `0x44600ca0` (8-bit). The arp self-tick is a type-9 event every 90,000 units (1/60 step); one interrupt pass is ~0.67 ms. `[doc]` {dn2-cfw-arp}
- Hazards for any MIDI-generating mod: the event allocator `FUN_4012a6e8` does not check for an empty free list (test `0x4460f4b8` first); MIDI events take the untransposed note (the task transposes); source byte `[0xd]` 1 = sequencer (subject to mute/solo), 2 = live; length `0x7f` (INF) hangs notes in the MIDI task; the 8-bit output count wraps above 255 bytes per message; latency ~one pass plus DIN serialisation (~0.96 ms per 3-byte note); vector 191 (voice interrupt) is not modelled by the emulator by default. Design options range from UI-only (~0 bytes) to sequenced trigs with p-locks (~850 bytes). `[doc]` {dn2-cfw-arp}

