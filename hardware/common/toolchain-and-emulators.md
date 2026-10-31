# Toolchains and emulators

Second-hand facts (tags as in `../README.md`). Names in braces are source keys.

## Hardware architectures reported
| Device | Control CPU | Audio DSP | Source |
|---|---|---|---|
| Digitakt mk1 | m68k-family (toolchain: m68k binutils + gcc) | not stated by what we read | `[doc]` {elekloader-adapting} |
| Digitakt II | Freescale ColdFire MCF54415 (big-endian) | Analog Devices ADSP-21569 SHARC+, FreeRTOS, ADI loader records | `[doc]` {digikit-old} |
| Digitone II | ColdFire (big-endian code, GCC-built) | SHARC+ (compiler: selache/selcc) | `[doc]` {dn2-cfw} {dn2-firmware-explore} |
| Syntakt | forum claim: two ColdFires + FPGA, board resembles the original Digitone minus analog parts. Synthack-OS mentions "CPU #2" for custom engine code | | `[?]` {elektronauts-dn2-pcb} {synthack-os} |
| Analog Heat | unknown to us | unknown to us | `[?]` |

## Compilers and builders
- m68k (Digitakt/Digitone mk1): m68k binutils and gcc; prefix override `ELEKLOADER_CROSS`. Sections `.run`, `.fast`, `.bss`. {elekloader-adapting}
- ColdFire C for Digitone II: GCC m68k toolchain, `dnfw` loader/builder (AGPL). {dn2-firmware-explore} {dn2-modding-skill}
- SHARC+ DSP code in portable C: **selache** (SHARC+ C compiler/assembler by js216, GPL-3.0); dn2-cfw compiles effects with `selcc` and splices them into the DSP section with `tools/dspsplice`. `[doc]` {dn2-cfw} {dn2mk2}
- `tools/sharcvm` (dn2-cfw) interprets the stock DSP handler to render chorus/delay/reverb/master compressor offline. `[doc]` {dn2-cfw}

## Generic ColdFire MCF5441x facts (not Elektron-specific)
Source: {coldfire-rs}. These describe the chip family that digikit names as the Digitakt II control CPU (MCF54415); nothing here says the Elektron firmware uses a given peripheral or mode. `[doc]`
- Family covered: MCF54410 and MCF54415-MCF54418. Peripherals with drivers: GPIO, PIT, INTC, eDMA, UART, DSPI, eSDHC (eMMC block **reads** via eDMA), SSI (I2S/network audio, full-duplex eDMA rings), USB OTG device mode (high speed via ULPI PHY; 54415-54418 only). Not implemented there: eSDHC writes, EPORT, DMA timers, I2C, RTC, PWM, ADC/DAC, FlexCAN, Ethernet, NAND, USB host.
- Vector table goes at the region origin, which must be **1 MB aligned** (VBR keeps bits 31..20 only); code starts at origin + 0x400.
- Boot modes: cold boot (serial/NOR/NAND, image sets up PLL and DDR) or via a bootloader.
- Rust for this chip: rustc_codegen_gcc with libgccjit targeting `m68k-elf`; default CPU in that toolchain is the 54418. Potential route for writing ColdFire-side mod code in Rust instead of C - unproven for Elektron firmware.

## Emulators
- **digiemu** (irpina): Digitakt/Digitone mk1 emulator, runs the user's own OS behind a clickable panel. {digiemu}
- **digikit** (current home ElekLabs/digikit, `[doc]` {digikit}): native Rust emulator running ColdFire and SHARC+ firmware together with front panel, display and audio; web panel (WASM) and Tauri desktop app; `patchkit` applies modules to the user's own `.syx` and refuses to change sections 2, 4 and 8; headless scenario runner with pinned PCM hashes; control socket for patch injection; ColdFire/DSP analysis databases and Ghidra tooling. Targets: Digitakt II 1.17 (also runs 1.16; 1.15C for old analysis), Digitone II 1.12 (also runs 1.11; 1.10E for old analysis). Caveats: DSP not real-time yet; browser host parked on `wip/browser-host`; no patched firmware installed on a device by the author; bootstrap-menu recovery untested on hardware. AGPL-3.0-or-later with NOTICE terms asking for the credit "digikit by Em D".
- **Earlier digikit README (m-dwyer/digikit, {digikit-old}) described a Python/Unicorn design:** ColdFire emulator for Digitakt II / Digitone II; patched Unicorn m68k (SR read, CCR sync, EMAC MAC with load; stock Unicorn refused); ColdFire-aware disassembler because Capstone misses MVS/MVZ and FF1; first run needs a cold boot of a few minutes to build snapshots; about 10M instructions/s. Works: core, interrupt controllers, PIT, DMA timers, eDMA, front-panel TX, display, SD/MMC up to identification. Missing then: DSP (no audio), input path, block storage - partly superseded by the Rust version above. `[doc]` {digikit-old}
- dn2-cfw's fork (branch `dn2-1.12`): 1.12 boots to the main screen, PLAY runs the sequencer, DIN MIDI works incl. virtual ports on Mac, live play ~0.8x real time. `[doc]` {dn2-cfw}
- A whole-DSP SHARC emulator (Overtone, the modding skill): used with digikit for ~160 checks per build. `[doc]` {overtone} {dn2-modding-skill}
- **Emulators do not model the timing of the two chips or the link between them** (dn2mk2 FIRMWARE.md) - so DSP-time overruns are only found on a unit. `[doc]` {dn2mk2-firmware-md}
- gearmulator (dsp56300): Machinedrum/Monomachine emulation, used by Overtone for comparisons. {overtone}

## Tools by purpose
| Purpose | Tool |
|---|---|
| Inspect/extract/repack `.syx` | elektron-firmware-tool (C), dnfw |
| Build linkable mods (DT1/DN1) | elekloader SDK (`python -m elekloader.sdk.build`), lint (`elekloader.lint`), patch (`elekloader.patch`) |
| Disassembly | Ghidra passes dnfw's check, Capstone fails; dsp56300 Ghidra module exists but is not tied to Elektron by its own README |
| Send OS / backups | Elektron Transfer (USB; legacy OS upgrade mode for DIN MIDI recovery) |
| Linux Overbridge | Overwitch; sample/SysEx manager Elektroid |

## Copies and forks of digikit seen in search results
Several repos carry the digikit tooling: Bezronczek/digikit (README title "Digitakt II firmware research"), naturarum/digikit ("Never change section 2 (bootstrap) or section 4 (updater)", firmware table: DT2 1.16 and 1.15C, DN2 1.11), simonjohansson/digikit (supported: Digitakt II 1.17 and Digitone II 1.12; "device work so far is on the Digitakt II"; flash flow: drop the image on Transfer while the main screen is shown, press YES). Their docs index `docs/TOOLS.md` and `docs/findings/` (indexed from `docs/FINDINGS.md`) are the next reads. Treat the ElekLabs repo as the reference; check forks for divergent claims. `[doc]` {digikit-forks}

## digikit tool index in short (docs/TOOLS.md) - what an agent can reuse
- Entry point for firmware questions: `coldfire/fw.py` (commands `fn`, `decomp`, `disasm`, `callers`, `callees`, `xref`, `path`, `str`, `class`, `port`, `search`, `atlas`, `sql`, `batch`) on top of `coldfire/atlas.py build IMAGE...`, which builds a SQLite atlas (machines, parameters, classes, UI strings, structs, manual terms; every row with provenance and confidence). Ghidra helpers: `ghidradump.py`, `ghidraq.py` (read-only queries, `pcode`, `slice`, `stores`, `loads`), `refscan.py`, `rttiscan.py`, `hwlookup.py` (resolves MCF5441x addresses, vectors, eDMA channels against a cited hardware contract). Patching: `patchkit/patchimg.py` (byte-exact, preconditioned patches), `machineprofile.py` (identify a known MAIN OS by hash and report anchors), `isacheck.py` (rejects instructions outside ColdFire V4e ISA_A/B/C + EMAC). Device side: `device/dkupload.py` (module upload over USB SysEx), `dklog.py` (runtime debug log over USB SysEx), `dksettings.py`. `[doc]` {digikit-tools}
- Workflow rules from that file: confirm raw references with `refscan.py` because an empty Ghidra caller list does not prove absence; check port candidates with `machineprofile.py` before carrying an address between images; for SHARC+ treat `sharc_candidates.py` and `sharcstrings.py` results as hypotheses until a real data reference confirms them; verify that `out/sections/<image>/.source-sha256` matches your `.syx` before trusting emulator runs and bound runs with an instruction limit. `[doc]` {digikit-tools}
- Facts: sections `section_3_MAIN_OS.bin` (ColdFire) and `section_7_BLOB.bin` (SHARC+ loader stream); the DSP firmware is a stream of writes to mapped memory, not one flat executable - address mapping and **last-write order matter**; SHARC import uses `SHARC_VISA:LE:32:default`, DM data addresses are byte addresses; default DSP stack range DM `[0x26f000, 0x2c0000)` (derived from an untouched gap, an assumption); example eDMA facts: `TCD50.CITER` at `0xfc045654`, DMA channel 50 connects SSI0 TFE0 to vector 170, vector 191 is an unassigned source with an `INTFRCH1` software-force bit; images named `dt2-1.16`, `dt2-1.17`, `dn2`. `[doc]` {digikit-tools}
- Repository rule worth copying: firmware and everything derived from it (`.syx`, extracted sections, dumps, databases, disassembly, mapped strings) stays out of git under `out/`; verified results go in `docs/FINDINGS.md`, current state in the newest handover; only public SHARC+ references in documentation. `[doc]` {digikit-tools}

