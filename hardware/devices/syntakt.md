# Syntakt

Coverage: **thin**. Projects: [../../devices/syntakt.md](../../devices/syntakt.md)

## Facts
- Only OS **1.41** is targeted (Synthack-OS "Syntakt MAX", SY FM4 builder; syntakt-firmware-workbench refuses other files). A user asked on 2026-10-01 for Modded-Cycles' flasher to accept Syntakt OS 1.42; support is not confirmed. `[doc]` {synthack-os} {syntakt-workbench} {modded-cycles-thread}
- Mod code lives in a **64 KB RAM area**, stored compressed and unpacked at boot. `[doc]` {synthack-os}
- Each Synthack mod is a `patch.json` (target location, hash of expected original bytes, replacement bytes). `build.py` combines the stock OS with chosen mods into a `.syx`, refusing a wrong OS, overlapping patches and protected sections. Firmware is unpacked/repacked with a wrapper around elektron-firmware-tool. `[doc]` {synthack-os}
- Install: Elektron Transfer over USB (Drop page); revert by flashing the stock OS the same way. Read the author's `RECOVERY.md` first (not yet read by us). `[doc]` {synthack-os}
- Planned custom engines (RISER/DOWNFILTER, SY SWARM+) would need custom audio-engine code on "CPU #2". `[doc]` {synthack-os}
- Syntakt engines can be extracted from Syntakt OS 1.41 and loaded into Model:Cycles (Modded-Cycles needs a Syntakt_OS1.41.syx). `[doc]` {modded-cycles-thread}
- Forum claim: the Syntakt board resembles the original Digitone minus analog parts, with two ColdFires and an FPGA in similar positions. `[?]` {elektronauts-dn2-pcb}
- Status: Synthack-OS reports seven mods running on real hardware (v0.8.0); each is tested in the emulator against the original code before flashing. `[hw]` {synthack-os}

## Gaps
Memory map, DSP, container signing for Syntakt, startup-menu recovery buttons: none collected. Syntakt engines in the OS container: not read.
