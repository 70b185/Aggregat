# Analog Rytm (MKI, MKII) - OS 1.73 / 1.74

Coverage: **first profile** (phase 2). Source: ethernet8023/rytm-fw-re (`STATUS.md`, `docs/flash-driver.md`, `docs/usb-reflash.md`),
read 2026-11-02, plus the phase-2 catalogue. Key {rytm-fw-re}. MK1 section: hugz202/AE-analog-rytm-mods (`docs/HAZARDS.md`, `docs/MANUAL.md`, `re/`, mod design notes), key {rytm-mk1-mods}, and analog-emu's `MK1-PORT.md`, key {analog-emu-mk1}. Projects: [../../devices/analog-rytm.md](../../devices/analog-rytm.md).
Most mods target **MKII OS 1.73** (MrScruff's rytm-mods, Chopshop) or **1.74** (rytm-fw-re, analoghealth); elekloader has a core for the
Rytm MKII (`core-ar2`).

## Platform (MKII, OS 1.74)
- CPU: **ColdFire MCF5445x** (`-mcpu=54455`, big-endian) - like the Octatrack's family, not the MCF5441x of the small boxes. DDR from `0x40000000`, the OS at `0x40000400`, stack region `0x48000000`. `[doc]`
- Sections of 1.74: 2 bootstrap (42,302 B, loads at `0x07020000`, runs in SRAM `0x80000000`), **1 FPGA** (Xilinx bitstream, 149,516 B, sync `AA99`), 3 MAIN OS (3,005,432 B), 8 unknown (159,948 B, `0xFF`-padded, the same size as on the Syntakt and DT2/DN2), 5 meta. `[doc]`
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
- **Container pitfall:** elektron-firmware-tool padded ELE2 containers to 2 bytes; the stock MK1 file pads to 4. A "no change" rebuild therefore came out 2 bytes short and failed the null-repack check. hugz202 patches the tool to pad to 4. **Always run a null repack of the stock file first** (rule A23). `[hw]`
- **Load (measured with a probe build on a MK1, OS 1.73):**
  - Stock audio alone is about **77 % of the CPU with nothing playing**.
  - One readout showed CPU 78.3 %, the audio interrupt at 61.2 % average and 74.0 % peak.
  - With a first chorus-plus-comb send on, the CPU reached **100 %**.
  - The CPU runs at roughly 120 MIPS. A one-to-one port of the A4's chorus (~8,000-9,000 instructions per block) would cost ~10 % of the unit and was rejected.
  - Same lesson as A34: replace work, and keep added effects idle when no track sends. `[hw]`
- **Cached vs uncached DRAM:** the chorus's delay line moved to a cached DRAM address (`0x428a0000`) in v2. The same rule applies as on the A4 MK1: don't touch uncached memory per sample. `[doc]`
- **RAM is not cleared at power-up** in the regions the mods use: clear your own buffers before use. `[hw]`
- **Dead code to reuse:**
  - The machine table (53 entries at `0x402543d0` on 1.73) holds **19 hidden machines** whose voice-mask byte is 0, so no list offers them. They look like earlier development versions of the shipped machines, and none has been played on hardware.
  - TEST machines (SD/RS/CY/CB) also exist.
  - hugz202 reuses their code space. Its only reference is its own table entry, which the mod repoints, and the build checks the stock bytes. A kit received over SysEx that names a hidden machine then plays the mod's machine or nothing. `[hw]` (the `full` image ran on a MK1)
- **Recovery:** FUNC at power-on, TRIG 4 (OS UPGRADE), stock `.syx` over **DIN MIDI** (Transfer's legacy mode). `[doc]`

