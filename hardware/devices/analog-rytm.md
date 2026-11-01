# Analog Rytm (MKI, MKII) - OS 1.73 / 1.74

Coverage: **first profile** (phase 2). Source: ethernet8023/rytm-fw-re (`STATUS.md`, `docs/flash-driver.md`, `docs/usb-reflash.md`),
read 2026-11-02, plus the phase-2 catalogue. Key {rytm-fw-re}. Projects: [../../devices/analog-rytm.md](../../devices/analog-rytm.md).
Most mods target **MKII OS 1.73** (MrScruff's rytm-mods, Chopshop) or **1.74** (rytm-fw-re, analoghealth); elekloader has a core for the
Rytm MKII (`core-ar2`).

## Platform (MKII, OS 1.74)
- CPU: **ColdFire MCF5445x** (`-mcpu=54455`, big-endian) - like the Octatrack's family, not the MCF5441x of the small boxes. DDR from `0x40000000`, the OS at `0x40000400`, stack region `0x48000000`. `[doc]`
- Sections of 1.74: 2 bootstrap (42,302 B, loads at `0x07020000`, runs in SRAM `0x80000000`), **1 FPGA** (Xilinx bitstream, 149,516 B, sync `AA99`), 3 MAIN OS (3,005,432 B), 8 unknown (159,948 B, `0xFF`-padded, the same size as on the Syntakt and DT2/DN2), 5 meta. `[doc]`
- **The display is driven through the FPGA:** a byte-FIFO bridge at `0xec07xxxx` (status `0xec070004`, data `0xec07000c`). The 128x64 panel uses two static 1,024-byte planes with diff flush. `0xec074xxx` is the MIDI UART (divisor 132 MHz / (31,250 x 32)). The LED engine is fed through the same FPGA SRAM family. `[doc]`
- Boot contract:
  - The bootstrap unpacks MAIN to `0x40000400`, sets VBR = `0x40000000` and calls the word at `0x40000400` as an **entry function pointer** with one stack argument. It is not a reset SP/PC header.
  - The stock entry sets SP to `0x48000000`, fills 256 vectors, sets up INTC/GPIO and caches (CACR `0xa50ce100`), then starts the kernel. `[hw]` (a from-source replacement OS booted on a unit)
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
