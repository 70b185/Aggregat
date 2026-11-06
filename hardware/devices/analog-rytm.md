# Analog Rytm (MKI, MKII) - OS 1.73 / 1.74

Coverage: **first profile** (phase 2). Source: ethernet8023/rytm-fw-re (`STATUS.md`, `docs/flash-driver.md`, `docs/usb-reflash.md`),
read 2026-11-02, plus the phase-2 catalogue. Key {rytm-fw-re}. MK1 section: hugz202/AE-analog-rytm-mods (`docs/HAZARDS.md`, `docs/MANUAL.md`, `re/`, mod design notes), key {rytm-mk1-mods}, and analog-emu's `MK1-PORT.md`, key {analog-emu-mk1}. Projects: [../../devices/analog-rytm.md](../../devices/analog-rytm.md).
Most mods target **MKII OS 1.73** (MrScruff's rytm-mods, Chopshop) or **1.74** (rytm-fw-re, analoghealth); elekloader has a core for the
Rytm MKII (`core-ar2`).

## Platform (MKII, OS 1.74)
- CPU: **ColdFire MCF5445x** (`-mcpu=54455`, big-endian) - like the Octatrack's family, not the MCF5441x of the small boxes. DDR from `0x40000000`, the OS at `0x40000400`, stack region `0x48000000`. `[doc]`
- Sections of 1.74: 2 bootstrap (42,302 B, loads at `0x07020000`, runs in SRAM `0x80000000`), **1 FPGA** (Xilinx bitstream, 149,516 B, sync `AA99`), 3 MAIN OS (3,005,432 B), 8 the shared ARM Cortex-M image (159,948 B, identical across several devices; see [firmware-container.md](../common/firmware-container.md)), 5 meta. `[doc]`
- **The display is driven through the FPGA:** a byte-FIFO bridge at `0xec07xxxx` (status `0xec070004`, data `0xec07000c`). The 128x64 panel uses two static 1,024-byte planes with diff flush. `0xec074xxx` is the MIDI UART (divisor 132 MHz / (31,250 x 32)). The LED engine is fed through the same FPGA SRAM family. `[doc]`
- Boot contract:
  - The bootstrap unpacks MAIN to `0x40000400`, sets VBR = `0x40000000` and calls the word at `0x40000400` as an **entry function pointer** with one stack argument. It is not a reset SP/PC header.
  - The stock entry sets SP to `0x48000000`, fills 256 vectors, sets up INTC/GPIO and caches (CACR `0xa50ce100`), then starts the kernel. `[hw]` (a from-source replacement OS booted on a unit)
- **Which ColdFire is open:** rytm-fw-re builds with `-mcpu=54455` (MCF5445x), while analog-emu identifies the Rytm MKII as MCF5441x (same entry code, CACR/ACR values and peripheral blocks as the A4 MKII). Both are V4 cores with EMAC and no FPU, so code built for either runs; peripheral addresses are what to check. See CONFLICTS O14. `[?]`
- **A 16.3 MB unreferenced hole at `0x41ad0000`** passed a memory probe on a unit (7 candidate regions all passed). `[hw]`

## Flash and recovery
- SPI NOR on DSPI `0xfc05c000`; layout: `0x00000-0x7FFFF` bootstrap + FPGA (**never write**), `0x80000+` the MAIN OS image. Images are staged in DDR at `0x3FF80008` with the same `size / checksum (i ^ word[i])` header as the small boxes. `[doc]`
- **The bootstrap supports several flash vendors and picks the geometry from the RDID:**

  | Vendor | Page | Erase block |
  |---|---|---|
  | Spansion `0x01 2018` | 0x200 | 0x40000 |
  | Winbond `0xEF` | 0x100 | 0x10000 |
  | Macronix `0xC2` | 0x100 | 0x10000 |
  | ISSI `0x9D` | 0x100 | 0x10000 |
  | EON `0x1C` | 0x100 | 0x10000 |

  The geometry therefore differs per unit. This very likely explains the two geometries reported for DT2/DN2 (CONFLICTS O8) and why a Spansion-only protection command does nothing on a Winbond unit (O9). `[doc]`
- The bootstrap also gates on a version-date field (image +0x10, 4 ASCII chars) per chip family, and refuses older versions. `[doc]`
- **Recovery is FUNC at power-on, OS UPGRADE, DIN MIDI only.** The startup-menu receiver never enumerates USB (verified: no USB events while it shows READY TO RECEIVE). USB updates are received only by the running OS. **Once a custom OS that does not implement the USB update is on the unit, the only way back is DIN** ("one USB shot per custom-OS cycle"). `[hw]`
  - rytm-fw-re rebuilt a DIN sender from an FT232RL (2 x 200 ohm) and streamed stock 1.74 back in about 10 minutes. `[hw]`
- Rule for every device: a replacement or heavily modified OS should keep the in-OS USB update working, or the user needs a DIN interface. See rule A36 in [`../AGENT-RULES.md`](../AGENT-RULES.md).

## Analog Rytm MK1 (OS 1.73 / 1.74) {rytm-mk1-mods} {analog-emu-mk1}
- **Board** (static analysis, `[doc]`):
  - same CPU family and OS framework as the MKII;
  - **ELE2 file with one section** (MAIN OS);
  - 128 MB DDR, boot/config flash as parallel NOR on FlexBus CS0 (8 MB at 0);
  - voice SPI on DSPI2 with eDMA ch 29 (492-word frame, as the MKII);
  - codec on SSI0 + SSI1 (8 words each);
  - 122x32 LCD, 1-bit LEDs;
  - **USB full speed only**.
- **The bootstrap is inside MAIN OS, as on the A4 MK1** (rule A38):
  - On 1.74 its version words are at `0x4028c768` and its image at `0x4028c770..0x402a1b84` (87,068 B, ending in its USB descriptors). On 1.73 the same image sat 0x60 lower.
  - At every boot the startup code compares that version with the one in flash at `0x1fff8`. If the embedded one is newer, the OS shows BOOTSTRAP UPGRADE and rewrites the bootstrap sectors. `[doc]`
- **Container pitfall:** elektron-firmware-tool padded ELE2 containers to 2 bytes; the stock MK1 file pads to 4. A "no change" rebuild therefore came out 2 bytes short and failed the null-repack check. hugz202 patches the tool to pad to 4. **Always run a null repack of the stock file first** (rule A23). `[hw]` ([I40](../INCIDENTS.md#i40-a-no-change-rebuild-came-out-2-bytes-short))
- **Load (measured with a probe build on a MK1, OS 1.73):**
  - Stock audio alone is about **77 % of the CPU with nothing playing**.
  - One readout showed CPU 78.3 %, the audio interrupt at 61.2 % average and 74.0 % peak.
  - With a first chorus-plus-comb send on, the CPU reached **100 %**.
  - The CPU runs at roughly 120 MIPS. A one-to-one port of the A4's chorus (~8,000-9,000 instructions per block) would cost ~10 % of the unit and was rejected.
  - Same lesson as A34: replace work, and keep added effects idle when no track sends. `[hw]`
  - **Idle mods add up (Modwerk, 2026-11-06, OS 1.74, sequencer stopped, block timed on DTIM0):** in a 16-module set the idle block took **72.9 %**; making three modules return early when they have nothing to do (Ping Pong Loop's voice gates in stock's sample prefetch, Sample Playback Rate's block handler, QPERF) brought it to 70.6-71.1 %. Each module's idle path is part of the budget. `[hw]` {modwerk-rytm-idle} ([I49](../INCIDENTS.md#i49-idle-paths-of-sixteen-mods-cost-two-percent-of-a-rytm-block))
- **Cached vs uncached DRAM:** the chorus's delay line moved to a cached DRAM address (`0x428a0000`) in v2. The same rule applies as on the A4 MK1: don't touch uncached memory per sample. `[doc]`
- **RAM is not cleared at power-up** in the regions the mods use: clear your own buffers before use. `[hw]`
- **Dead code to reuse:**
  - The machine table (53 entries at `0x402543d0` on 1.73) holds **19 hidden machines** whose voice-mask byte is 0, so no list offers them. They look like earlier development versions of the shipped machines, and none has been played on hardware.
  - TEST machines (SD/RS/CY/CB) also exist.
  - hugz202 reuses their code space. Its only reference is its own table entry, which the mod repoints, and the build checks the stock bytes. A kit received over SysEx that names a hidden machine then plays the mod's machine or nothing. `[hw]` (the `full` image ran on a MK1)
- **Recovery:** FUNC at power-on, TRIG 4 (OS UPGRADE), stock `.syx` over **DIN MIDI** (Transfer's legacy mode). `[doc]`

## More from the MKII mod and research projects (rytm-mods-src OS 1.73, analog-rytm-mkii-research OS 1.72) {rytm-mods-src} {ar-mkii-research}
- **A zero run is not a free cave until it survives a hard run on the unit.** octatrack-mods had shipped code into a region that came from someone else's survey. The mod worked with the sequencer stopped and failed during playback, because the region was really `.bss` that the audio engine wrote. rytm-mods-src's check: fill the candidate with a known pattern, flash, run playback, sampling, Overbridge and +Drive access, then read it back. See rule A43. `[hw]`
- **Pick the narrowest assembler target that assembles.** The project went from `-mcpu=5407` (ISA_A) to `-mcpu=5475` (ISA_B + EMAC) only when a mod needed EMAC, and checked that the earlier mods rebuilt byte-identically. Too narrow a target fails at assembly time; too wide a one silently accepts instructions the chip lacks (rule A42). `[doc]`
- **Sections 5, 2, 1 and 8 must come back byte-identical**, and the bootstrap (section 2, 42,302 B at `0x07020000`) is checked by hash. Elektron's own bootstrap upgrade, which runs on the first restart after some OS updates, is the one moment the safety net is down: don't cut power then. `[doc]`
- **The master compressor is analog** (after the analog mix and the master distortion). The MKII firmware never reads its gain back (the MK1 did, through the on-chip ADC input AN1), so any gain-reduction display on the MKII is an estimate. A CC beyond an enumeration's last value makes the unit show ERR instead of clamping. `[doc]`
- **Sample bit reduction is not done on the ColdFire.**
  - The BR knob becomes a per-voice command word, `0xB31407FF + ceil(BR x 0x40000 / 127)`, sent over DSPI1/eDMA to the external audio hardware.
  - The main OS contains no mask or shift that would apply it to PCM.
  - So sample playback processing on the Rytm MKII likely sits in the FPGA/voice hardware: a lead for research map T12. Static and emulator work only.

  `[doc]`
- A third reading of the CPU: analog-rytm-mkii-research models the Rytm MKII as MCF5441x (conflict O14), with MAIN at `0x40000400` (2,903,032 B on 1.72) and the stack at `0x48000000`. `[doc]`
- **Porting MKII mods to the MK1: same code base, different data** (gdeo607/rytm1_mods, OS 1.73) {rytm1-mods}:
  - Most routines are byte-identical, but the parameter info record is 88 bytes on the MK1 and 84 on the MKII.
  - UI glyphs and the screen differ (122 px wide on the MK1, 128x64 on the MKII), so anything that draws its own pixels needs a redesign, not new addresses.
  - Every RAM address (`0x41xxxxxx`, `0x8000xxxx`) has to be found again.

  Each of these would have been a silent bug. `[doc]`

