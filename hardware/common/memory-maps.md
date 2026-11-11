# Memory maps and mod areas per device (from elekloader's `docs/DEVICES.md`, v0.9.0 era)

elekloader's device profiles are the most systematic public record of "where is free memory, where may the container end, how does recovery work" per device. Read 2026-10-31, second-hand; the page reports evidence per device but numbers can change with each core version (core 2.x had a 128 KB mod area on Digitakt mk1, 4.0 cores have larger ones). Tags as in `../README.md`. Keys: {elekloader-devices}; repo overview and release list: {elekloader-main}.

| Device | OS | Maturity (as stated) | Mod RAM area | Flash budget | Recovery |
|---|---|---|---|---|---|
| Digitakt mk1 | 1.53, 1.54 | example profile; core 2.1 checked in emulator on both | `0x47BC0000-0x47C00000` (`core_ddr`, core 4.0) | container at `0x80000`, ends by `0x380000` (~3 MB), no protected range | FUNC at power-on |
| Digitone mk1 | 1.43, 1.44 | 1.43 checked in emulator; 1.44 "not yet" in emulator | `0x43EC0000-0x44000000` (1.25 MB, core 4.0) plus `bulk` `0x44000000-0x47BE0000` | not stated | FUNC at power-on, startup menu |
| Digitakt II | 1.17 (digikit mapped 1.15C, 1.16) | experimental; a sealed build booted on a unit (4 Oct 2026) | `0x47F00000-0x47F40000` (256 KB) | `flash_limit 0x380000` (3 MB; stock 1.48 MB) | FUNC at power-on, TRIG 4, MIDI only |
| Digitone II | 1.12 | experimental; stock and recovery proven on a unit; CO02 and DS03/DH03 ran on a unit | `0x47F00000-0x47F40000` (256 KB) | `flash_limit 0x380000` (3 MB; stock 1.80 MB) | FUNC at power-on, TRIG 4, MIDI DIN |
| Octatrack MKI/MKII | 1.40C | core built and run on an MKII (3 Oct 2026), not yet on an MKI | audio arena bottom pages `0x40a955e0-0x41495de0` (10 MB, up to 1,707 pages) | container at `0x4000`, must end below `0x200000` | not stated |
| Model:Cycles / Samples | 1.13 | builds run on both units | `0x47E00000-0x47E40000` (256 KB) | container at `0x20000`, below `0x1E0000` (1.75 MB; stock 0.70 MB) | FUNC at power-on, TRIG 4, 5-pin MIDI |
| Analog Rytm MKII | 1.73, 1.74 | core-ar2 0.2 on 1.73 and 0.3+ on 1.74 run on a unit | `0x47BE0000-0x47C00000` (128 KB) | `flash_limit 0x300000` | STARTUP menu (FUNC), TRIG 4, MIDI DIN |
| Analog Four MKII | 1.56 | proof of concept; several builds run on a unit | `0x47BE0000-0x47C00000` (128 KB) plus `0x456472C0-0x47BE0000` (37.6 MB) unused | `flash_limit 0x300000` | STARTUP menu (FUNC), TRIG 4, MIDI DIN |
The page does not mention Analog Heat or any other planned device. `[doc]` {elekloader-devices}

## Platform facts from the firmware itself (Digitakt II / Digitone II, digikit finding 08 and 59)
- CPU fingerprint: NXP MCF5441x (ColdFire V4m with EMAC) - UART8 `0xEC070000`, GPIO `0xEC094000`, eDMA `0xFC044000` (TCDs +0x1000), INTC0-2 `0xFC048000/0xFC04C000/0xFC050000`, DSPI0 `0xFC05C000`, PIT0-3 `0xFC080000-0xFC08C000`, EPORT `0xFC090000`. Stock Ghidra misdecodes EMAC line-A words; digikit uses a separate language spec. `[doc]` {digikit-f08}
- **DDR is 128 MiB** (DDRMC writes in the bootstrap; earlier 64 MiB claims are wrong): `0x40000000-0x47FFFFFF` cached (ACR0), `0x48000000-0x4FFFFFFF` an uncached alias of the same DDR used for DMA buffers; reset SP `0x48000000`; 32 MiB C++ heap above `0x44000000`. `[doc]` {digikit-f08}
- **NOR flash 16 MiB**, S25FL127S-class (RDID mfg 0x01, id 0x2018); the bootstrap's flash loop uses 512-byte pages and 256 KB erase blocks. The in-OS writer (finding 75) uses 0x100-byte pages and 0x10000 sectors from flash `0x80000` - two code paths, two geometries `[?]`. `[doc]` {digikit-f08} {digikit-f75}
- UART8 receive is done by eDMA (channel 34), not by reading the data register - an emulator must model eDMA, not just the UART. `[emu]` {digikit-f08}
- **No ColdFire watchdog.** Neither MAIN OS (DT2 1.16/1.17, DN2 1.11/1.12) nor the bootstrap names the core watchdog registers (CWCR `0xFC040016`, CWSR `0xFC04001B`), and the watchdog is off after reset. A ColdFire hang therefore stays hung until a power cycle; nothing resets the unit for you. Static reading; computed addresses are not excluded. Third-party MCF5441x code agrees that the core watchdog stays off after a power cycle unless software enables it, and CWCR can be written only once after reset (so a bootstrap write of 0 would also lock it off). `[doc]` {digikit-f17} {netburner-cwt} {nxp-mcf5441x-rm}
- **eMMC part table:** DT2 1.16 (`0x402b4a24`) and DN2 1.10E/1.11 (`0x4029f554`) accept the same seven 32-byte entries: Kingston parts `TX2932` and `TS0A32`, both 32 GB, matching the Kingston EMMC32G-TX29 on a DN2 board photo. Shared ColdFire storage code: the block driver, the MmcFs slot store and the transfer routing; the sample filesystem, its request handler and the sample manager are DT2-only. `[doc]` {dn2-drive}
- **eMMC card (both, about 32 GB part, 0x2E1A000 sectors assumed):** sectors `0x0-0x457FFF` belong to the firmware (boot, tables, projects, pools, presets); **MmcFs refuses writes at `0x457FFF` and above**. DT2 1.17: factory sample table "MaGj" at `0x458000` and 1,265 factory samples to `0x5D7FFF` - never touch; +Drive (ekFS) `0x5D8000-0x2DF017F`; `0x2DF0180` to the end unused. DN2 1.12: nothing stock writes at `0x458000` and up; FORMAT trims only up to `0x457FFF`. Unchecked bank ids in the Data API can reach every sector **below `0x800000`** over USB - put any private store above that line (digikit: DT2 `0x2DF1000+`, DN2 `0x800000+`). Not checked on a real card. `[doc]` {digikit-f59}
- **Card pools inside the firmware area (MmcFs)** `[emu]` {digikit-samples}:
  - Fixed slots: projects 0-127 (16 MiB each on both), sounds 0-2047 (DT2 4 KiB, DN2 1 KiB), kits 0-1023 (DT2 64 KiB, DN2 32 KiB).
  - The bitmaps at sector `0x800` are **write-protect padlocks, not occupancy**.
  - The boot project (magic "COKi") has two copies at sectors `0x40000` and `0x48000`. The working project is at `0x50000` and is rewritten from the boot copy at every start.
  - **The DT2 has a path filesystem (ekFS +Drive) for samples. The DN2 has none**: only the MmcFs pools. Card layouts are device data (digikit `devices/<device>.toml`).

## Measuring ColdFire load without a timer (digikit finding 41) {digikit-f41}
The boot thread ends in an empty loop at the lowest priority. Replace its last call with a jump to a loop that counts iterations, and close a window every 1,500 DSP blocks. Load = 100 % - iterations / best window since boot. This measures the time the interrupts leave to tasks, not the whole CPU. An absolute calibration needs the device. The digihealth alternative (DMA timer counter at entry and exit) is in `devices/digitakt.md`. `[emu]`

## ColdFire code caves and mod RAM (dnfw `code-caves.md`, `mod-memory-regions.md`, DN2 1.11) {dn2-caves}
- **RAM aliases every `0x08000000`:** a byte answers at nine addresses up to `0x8c000000`. ACR0 caches only the first window, and stock reaches its DMA buffers through the second (`0x4e......`). **Scan all nine windows** before you call RAM unreferenced. `[doc]`
- **Flashed bytes above the reset clear do not survive a reset** (DT2 1.16 clears from `0x40312000`; on the DN2 about 3,200 B separate the end of MAIN OS from the clear). Code placed there must be copied up by a loader *after* the clear. digikit, dnfw and elekloader all do this. `[hw]` (bytes lost on a DT2)
- **The DN2's code region has no free run of even 24 bytes.** Zero runs exist in the constants region, and **code there does execute** (a boot-path cave printed "CAVE RAN!!!" on a real DN2). One "free" run was an array the code fills at run time: patching it crashed the unit, and the emulator watch read zeros. Two static checks catch most cases: a fixed stride between equal gaps marks an array, and `lea`/`pea`/`move.l #` operands mark referenced space. On 1.11 only 13 runs (4,207 B) pass both, not the "~29 KB" first assumed. `[hw]` ([I19](../INCIDENTS.md#i19-patching-a-free-zero-run-crashed-the-unit))
- Displaced stock instructions are replayed at another address, so **no PC-relative instructions in the displaced bytes**. Pick hook sites whose first instructions are absolute. `[doc]`
- dnfw's mods take fixed RAM chunks in `0x46700000-0x47fe0000` (waverider 436 KB at `0x4670c000`/`0x467f0000`/`0x46a00000`, lfo4 `0x46800000`/`0x46900000`, ...). The alternative is the stock 32 MiB buddy heap (`0x4464abf0`), where the allocator records the use but a 12.9 MB project load takes half. Mods that store settings in unused pattern bits must not claim the same bits. `[doc]`

## Digitone II: who uses the RAM above the reset clear (compared across five projects, 2026-11-02)

The DN2 clears `0x402fd000-0x466b84d0` at reset (1.12); everything above is outside stock's static map, and every mod platform puts its code and data there. The projects agree on what stock leaves alone, but each picked its own addresses, and several picked the same ones.

| Range | User | OS | Evidence |
|---|---|---|---|
| `0x466c0000-0x46709340` (cached view of the uncached `0x4e6c0000-0x4e709340`) | **stock DMA buffers**, including a 64 KB MMC bounce buffer | 1.12 | static, two projects agree {dn2-cfw-t13} {elekloader-dn2-profile} |
| `0x466f1300-0x46701300` | stock MMC bounce buffer (only transfers over 60,672 bytes reach the top 4,864 bytes) | 1.11 | static {dn2-cfw-prior} |
| `0x46700000-0x46f00000` (fixed chunks: data window `0x46710000-0x46740000`, midiarp `0x467d0000`, lfo4 code `0x46800000`, parameter table `0x46900000`, Waverider `0x46a00000`, usbprobe `0x46f00000`) | **dnfw** mods | 1.11 only (no 1.12 port) | {dn2-caves} {dn2-cfw-prior} |
| code at `0x46800000`; stacks, rings and scratch from `0x46a00000` | **cfmod / cfkit** (digitone-2-modding-skill) | written for 1.11 | {dn2-skill-scripts} |
| mods `0x46800000-0x47e00000`; core run image `0x47e00000-0x47f00000` | **dn2-cfw** (Digiwerk) | 1.12 | {dn2-cfw-t13} {dn2-cfw-t19} |
| `0x47f00000-0x47f40000` (256 KB), the same area as on the DT2 | **elekloader** core-dn2 and its mods | 1.12 | {elekloader-dn2-profile} |
| down from `0x48000000` | stock stack (boot stack never below `0x47ffffcc` in emulation; run-time depth unmeasured) | both | {dn2-cfw-t19} |

What the comparison settles and what it does not:
- **Stock does not touch `0x46710000-0x47ffffcc` in emulation.** Three independent checks agree: dn2-cfw's write watches over `0x46800000-0x47f00000`, elekloader's canary over `0x46710000-0x48000000` (cold boot, two panel sessions), and digikit's reference scan (`0x4671a000-0x47fe0000` unreferenced, [`dt2-dn2-limits-and-audio-chain.md`](dt2-dn2-limits-and-audio-chain.md)). All three ran in an emulator, so rule A43 (canary on a unit) still applies. `[emu]`
- **The range from `0x46700000` up to `0x46710000` is not free.** On 1.12 it holds the end of the DMA buffers; on 1.11 the MMC bounce buffer reaches `0x46701300`. dnfw's lfo4 state sat at `0x46700000` until 2026-10-11 and corrupted every project saved on an LFO4 unit (the bounce buffer carries each piece of a project on save and load); it now lives in the first block of stock's heap (`0x4464abf0`). dnfw's remaining `0x4670xxxx` chunks (from `0x46708000`) are above the 1.11 DMA section (`0x466b8000-0x46701340`) but inside the 1.12 one, so they must move for a 1.12 port. The "25.3 MB unclaimed above BSS" figure in dnfw's memory map missed these alias references. The skill's "`0x46700000..0x46900000` unused, hardware-confirmed" disagrees: see [CONFLICTS S17](../CONFLICTS.md). `[doc]`
- **The platforms collide.** dnfw's lfo4 code, cfmod's default link address and the start of dn2-cfw's mod area are all `0x46800000`; cfkit's scratch at `0x46a00000` is Waverider's chunk. Only elekloader's `0x47f00000` and dn2-cfw's core `0x47e00000` are disjoint from the rest. A mod built for one platform cannot be dropped into another's image without moving its RAM (and its hooks: [`dt2-dn2-limits-and-audio-chain.md`](dt2-dn2-limits-and-audio-chain.md) section 6, [`agent-workflow.md`](agent-workflow.md)). Before picking an address, check this table and declare every range you use. The full register, with every platform's ranges per OS and the overlaps, is [`../RAM-TENANCY.md`](../RAM-TENANCY.md) (task T23).

## Digitakt II: who uses which memory and hook site (compared across six projects, 2026-11-02)

Task T21. Read from each project's own docs and code; addresses are DT2 1.17 unless a row says 1.16. The reset copies `0x40312000-0x4031ff60` to SRAM and clears `0x40312000-0x47e28470`; stock reaches its DSP buffers only through the uncached alias, so `0x47e30000-0x47e7ae80` in the cached view; the stack runs down from `0x48000000` {elekloader-dt2-profile}.

**ColdFire RAM and flash space**

| Range | User | Evidence |
|---|---|---|
| `0x403117c4-0x40312000` (2,108 B, the last flashed bytes below the clear: digikit's `flash_cave`) | digikit patchkit's reset loader; Deja Vu's payload (`0x403117c4-0x40311fb2`) and its run-time latches (`0x40311fe4-0x40311ff3`); the All-in-One's loader (copied within the cave to `0x40311c92`); dt2-machine-lab's Plaits rows and code (`0x40311b80-0x40312000`, 1.16) and its control tables (`0x40311944-0x40311ac4`, 1.16); 70b185's private DT2 project: 28 bytes at `0x40311fb4` between Deja Vu's payload and latches | {digikit-f01} {dt2-aio-src} {dt2-lab-cpu} {own-dt2-notes} |
| `0x47e8b000-0x47fe0000` (1.33 MiB, digikit's `cf.expansion`, unreferenced RAM above the DSP buffers) | digikit modules; the All-in-One's code (zoom and Musical WAVE from `0x47e8b000`, One-Shot Zoom V11 from `0x47e91000`); dt2-machine-lab's opt-in 64 KiB `0x47e8b000-0x47e9b000` (1.16) | {digikit-patching} {dt2-aio-src} {dt2-lab-cpu} |
| `0x47f00000-0x47f40000` (256 KB) | **elekloader** core-dt2 and every elekloader mod (digitakt2-perform's two mods among them) | {elekloader-dt2-profile} {dt2-perform} |
| `0x47fe0000-0x47fe1000` | digikit's keep area (crash and hang records that survive a soft reset) | {digikit-f46} |
| from the stock 32 MiB heap at start-up (no fixed address) | digitakt-ii-research's start-up allocation (one 8 KiB block, 1.16) | {dt2-research-heap} |

**Boot and UI hook sites**

| Site | User |
|---|---|
| `0x40000538` (`jsr 0x400019b0`) | elekloader core-dt2 `boot` |
| `0x4000053e` (`jsr copy; jsr clear`, replaced by `jsr loader; nop`) | digikit patchkit's loader, used by the All-in-One and dt2-machine-lab |
| `0x40032ad4`, `0x40032b3a`, `0x40033d94`, `0x40033dde`, `0x400a5eac`, `0x4009e2a2` | elekloader's events `ev_tick`, `ev_draw`, `ev_key`, `ev_enc`, `ev_settings`, `ev_personalize` |
| `0x40064ba6` | digitakt2-perform's perform-levels (on top of elekloader) |
| `0x400181fe`, `0x400184ea`, `0x4001706a`, `0x4010ee84`, `0x4010ecd0`, `0x401398f8` | the All-in-One's One-Shot Zoom and Musical WAVE |

**SHARC L2** (stock loads up to `0x2001ab7c`; `0x200fa000-0x200fdfff` is referenced): digikit offers `0x2001ab7c-0x200fa000` to modules {digikit-f100}; dt2-machine-lab places Plaits code at `0x20080000`, Capicola cold code at `0x200a0000` and voice state at `0x200e0000-0x200e8000` (1.16) {dt2-lab-capicola}; 70b185's private project links `0x20020000-0x200f9fff` and keeps its data at or below `0x200f5a74`, because going past it gave clicks and leaks into the delay on a unit {own-dt2-notes}.

What the comparison shows:
- **The flash cave is the most contested 2 KB on the DT2.** Five users share it, and they fit only because each checked the bytes the others left: Deja Vu leaves 50 bytes between its payload and its latches, and 70b185's project uses 28 of them. One report says the cave froze a unit at the logo ([CONFLICTS O18](../CONFLICTS.md)); Deja Vu's releases and 70b185's builds boot from it on units. `[hw]` ([I18](../INCIDENTS.md#i18-the-flash-cave-reportedly-froze-a-unit-at-the-logo))
- **elekloader's area lies inside digikit's `cf.expansion`.** An image built with both loaders would place two code blocks in the same RAM unless one moves. The two boot hooks are adjacent and disjoint (`0x40000538` returns to `0x4000053e`), so they could chain, as on the DN2. `[doc]`
- **The listed UI sites do not overlap.** elekloader's six event sites, perform-levels' site and the All-in-One's zoom and WAVE sites are disjoint bytes; the All-in-One has more sites (Plaits, DX7, panels) that this table does not compare. Disjoint bytes do not prove that two mods work together ([`agent-workflow.md`](agent-workflow.md)). `[doc]`
- **Three projects replace the STRETCH machine's DSP:** dt2-capicola, dt2-machine-lab's port of it, and 70b185's private project. They are alternatives, not combinable. `[doc]`
- **digikit's module L2 reaches above `0x200f5a74`,** where one project measured clicks on a unit. Treat `0x200f5a74-0x200fa000` as unproven until task T15 settles it. `[hw]`

## Details per device
- **Digitakt mk1:** ELE3, device byte `0x0A` (elekloader's page says `0x14`, which is the Digitakt II's byte; settled by taktone, see the table in [firmware-container.md](firmware-container.md)), six-plus sections, main OS staged at `0x40200000`. DDR is free RAM. Hook sites: no numeric list on the page; the first eight sites of the Digitone mk1 are described as the Digitakt mk1's.
- **Digitone mk1:** ELE3, seven sections, stock gap 403,540 bytes. The OS clears `0x4028E000-0x43229E60`; operands end before `0x43EB0000`; stack from `0x48000000`. First eight hook sites match the Digitakt mk1; the ninth is `ev_voice_on` at `0x4009e928`; render frame `0xB8`. Core `mods/core-dn1`, up to 4.0 (1.44 ported at its own addresses).
- **Digitakt II:** device byte `0x14`, six sections, sealed (HMAC-SHA256). Clear `0x40312000-0x47E28470`; the core takes `0x47F00000-0x47F40000`; SRAM free at `0x80006E80-0x80008000` and `0x8000F100-0x80010000`. Hook events `ev_tick`, `ev_draw`, `ev_key`, `ev_enc`, `ev_settings`, `ev_personalize` (no numeric addresses). Core `mods/core-dt2`; DTIM0 not started.
- **Digitone II (OS 1.12):** device byte `0x15`, six sections, sealed. Hook sites: boot `0x40000538`, `ev_tick` `0x4002e464`, `ev_draw` `0x4002e4ca`, `ev_key` `0x4002f20c`, `ev_enc` `0x4002f256`, `ev_settings` `0x4009ff88`, `ev_personalize` `0x400987a2`. Clear `0x402fd000-0x466b84d0` with a 32 MB heap inside it; SHARC mod area 32 KiB at `[0x20090000,0x20098000)`. **USB cap `update_max = 0x200000` (2 MiB, preamble plus container, conservative): CO02 (1,915,960 bytes) was accepted, a 2,147,448-byte build stalled.** The page is inconsistent on the core version (0.2 in the file list, 0.1 in the core section).
- **Octatrack:** one image for MKI and MKII (`.syx` and `.bin`); `stage` is `None`, so the in-place unpack is unsimulated. Protected `0x400de1e0-0x400e21e0`. Six hook events (sys tick, composed frame, keys, encoders, MIDI in, frame interrupt); boot site `0x4000050c`; draw gate `0x400c45b0`; image free runs `0x400c45b0-0x400c4702`, `0x400d24e0-0x400d2ce0`, `0x400d64e0-0x400d7c3c`. DSP payload A `0x136cb` bytes, payload B `0x12d05` bytes; the SPATIALIZER range P:0xaa8-0xbac (261 words) is used for mods. Arena 14,602 pages of 6,144 B.
- **Model:Cycles / Samples:** ELE3 sealed, version field at `0x0C`; DDR `0x47E00000-0x47E40000`; SRAM tail `0x8000F700-0x80010000` (2,304 bytes); section 3 is read to `0x40200000` and unpacked to `0x40000400`; core-mc / core-ms.
- **Analog Rytm MKII:** device byte `0x0C`, no trailer, five sections; loader `0x80000590`, stock gap 401,995 bytes (1.74 repack 436,273); stores at `0x300000-0x380000` and `0x380000-0x400000`; 1.74 repack ends at `0x1F2BB0`; core-ar2 (1.73 up to 0.2, 1.74 from 0.3).
- **Analog Four MKII:** device byte `0x0B`, version at `0x14`, no trailer; stock gap 540,192 bytes (repack 563,703); calibration record `RBOW` (0xE56 bytes) in the `0x300000` area; settings store `0x380000-0x400000`; repack ends at `0x18DF70`; OS clears `0x40253000-0x448B6D50`; 16 MB allocator arena `0x41872230-0x42872230`; core-a4 up to 0.4.

## Adding a device (what elekloader requires - a good checklist for any new target)
1. A profile (`releases`, `sysex_id`, `main_section`, `stage`, `flash_at`, `flash_limit`, `areas`, `recovery`, ...). 2. Sealing, if any: find the seed in the bootstrap and confirm the writer reproduces the **stock file, seal included**. 3. Packing: the device's depacker must accept the codec output, and the in-place simulation must hold for its `stage`. 4. A CPU decoder in `isa/` (`reader()`, `decode()`, flags). 5. Tests: `test_writer_no_change_is_stock`, and a cold boot in an emulator if one exists. For a **new OS version**: compare non-main sections, add the release, check memory facts, port cores under `ports`, run an emulator build, tell mod authors. `[doc]` {elekloader-devices}

## Implication for Analog Heat
Analog Heat +FX OS 1.02 now has a first profile from the owner's own research: MCF5441x, 64 MB DDR, MAIN OS at `0x40000400` staged at `0x40200000`, custom code only below `0x40206000`, audio on the ColdFire via SSI1/eDMA and no DSP. See [`../devices/analog-heat.md`](../devices/analog-heat.md). `[doc]` {own-heatfx-notes} Still nothing for MKI/MKII. A first profile would need: container type and sealing of the Heat OS file, CPU/DSP architecture, loader/stage behaviour, free-memory evidence and the startup-menu recovery path (known officially: ACTIVE/ON + [LFO] on MKI/MKII, ACTIVE + MOD on +FX). See [`../devices/analog-heat.md`](../devices/analog-heat.md).
