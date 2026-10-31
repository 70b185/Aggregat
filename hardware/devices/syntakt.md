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

## Recovery (SyntHack OS `RECOVERY.md`)
Normal case: Drop page in Transfer. If the OS does not boot: DIN MIDI, FUNC at power-on, TRIG 4, SYSEX TRANSFER "OS Upgrade via device startup menu", tens of minutes at 31.25 kbit/s; **avoid TRIG 2 and TRIG 3 (erase data)**; do a dry run with stock first; only flash files whose `eft.py info` shows `checksums : ok`. No hardware results reported on that page. `[doc]` {synthack-recovery}

## Syntakt OS 1.41 static-analysis facts (Humgic/syntakt-machine45-research, handoff dated 2026-10-28; no hardware run, no firmware)
- Address rule `VA = file offset + 0x40000400`; ColdFire big-endian (ISA-C/EMAC). MAIN is 3,438,480 bytes, section 7 is 383,760 bytes. `[doc]` {machine45-handoff}
- **Stock public Machine IDs are 0-44**, stored as a BYTE in each track's machine payload (`P[t]+0xA2`); runtime records `R[t] = model + 0x6C + 0x3C0*t`, `P[t] = *(R[t]+0x10)`; the setter is at `0x40025594` (store at `0x40025620`). 505 parameter descriptors of 52 bytes; only MAIN digital tracks 0-7. `[doc]` {machine45-handoff}
- Section 7 selector: a signed BYTE with a 46-entry map (negative -> 0, 0-45 kept, above 45 clamped to 45); stock maps 0-7 to the same-numbered engine family and 36->8, 37->9, 38->10, 44->11, everything else (incl. 45) to family 0. Stock tables: render pointers `0x400148F0` (12 entries), prep pointers `0x40014920`, the 46-byte map at `0x40014950`. A compact handoff moves MAIN `[0x80002000,0x800021B0)` through a 27x16-byte eDMA transfer (TCD47, channel 47); each track then receives a 20-byte copy into `T[t] = 0x80003C40 + 0x8E*t`. Dslot is 8 x `0x708` = 14,400 bytes. `[doc]` {machine45-handoff}
- Persistence confirmed statically: the current-kit Sound-v7 save/load keeps the machine byte (raw 0-45 and 255 retained, 46-254 map to 0); Pattern-v11 stores the byte at row `+0x2EC` and its restoration is **not closed**; Sound locks, p-locks, held trigs, migration, clipboard and undo not qualified. Evidence labels in that repo: confirmed by static analysis / verified in emulator (none for the whole device) / verified on hardware (none) / hypothesis. `[doc]` {machine45-handoff}
- Open: safe executable storage for native DSP on "CPU 2" (the loader boundary is unresolved); composition with SY FM4 (engine 4, A-table entry overlap) and other descriptor mods; resource IDs 254-261 are unclaimed in the registry but have MIDI CCs, 505+ have no native allocation. `[doc]` {machine45-handoff}

## Gaps
Memory map, DSP, container signing for Syntakt, startup-menu recovery buttons: none collected. Syntakt engines in the OS container: not read.
