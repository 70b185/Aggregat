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
