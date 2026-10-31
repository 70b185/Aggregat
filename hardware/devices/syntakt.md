# Syntakt

Coverage: **thin**. Projects: [../../devices/syntakt.md](../../devices/syntakt.md)

## Ecosystem snapshot (altstrument 2026-10-31: 4 firmware/tool entries + 2 tools; elektronmods: 4 Syntakt entries)
Listings: {alt-syntakt}. Entries: **SyntHack OS** (upstream, Angelo-politek, v0.9.0 2026-10-19; {synthack-upstream}), **Syntakt MAX** (fork with a Windows builder; see the data file), **SY FM4** (Rxuting; OS 1.40A), **Syntakt Firmware Workbench** (browser; OS 1.41), **syntakt-machine45-research** (documentation) and **Sympakt** (sample packs). Brick-risk flags are set on SyntHack OS, Syntakt MAX and SY FM4. Syntakt MAX integrates an SY FM4 engine for 1.41.

## OS versions seen
**1.40A** (SY FM4 only; SHA-256 starts `266a5a30`), **1.41** (SyntHack OS, Syntakt MAX, Workbench, machine-45 research), and an **os-1.42 branch exists in SyntHack OS** (SY FM4 points to it as the porting reference; a forum user asked on 2026-10-01 for Modded-Cycles' flasher to accept 1.42). So OS 1.42 exists; mods are per-version. `[doc]` {syfm4-readme} {modded-cycles-thread}

## SY FM4 facts (README, Syntakt OS 1.40A)
Replaces SY TONE in place on the digital tracks: ALGO 0 is SY TONE itself (sample-identical to the stock machine, so existing projects sound the same), ALGO 1-8 the classic Yamaha 4-op set, ALGO 9-11 tree, diamond, ring; the second parameter page SYN 2/2 adds operator-3 (ALGO, RAT3, LEV3, DEC3) and operator-4 (DET, RAT4, LEV4, DEC4) controls, DET detunes operators 2-4 by +/-16 semitones; page 2/2 is saved with the sound and p-lockable (sounds saved by stock open with page 2/2 at SY TONE defaults). Patchers read the user's own OS and check the SHA-256 of each byte range they overwrite. **Hardware:** tested on a real Syntakt 1.40A - installs, all parameters including p-locks work, an 8-track load test ran 47 s without audible clicks, dropouts or clipping; sound/pattern-lock save-reload and CPU cost were only checked in an emulator (digiemu with a Syntakt port). **CPU:** ~8.9k cycles per voice per block vs 7.2k-9.8k for stock engines; 8 SY FM4 voices ~66 % voice CPU. **Limits:** section 7 has a size limit (`0x60000 - 5` bytes in 1.40A); page 2/2 reuses descriptors 1-5 and 12-14, which were MIDI-CC placeholders in 1.40A and are removed. Porting to 1.41/1.42 means remapping every 1.40A address and rechecking the section 7 limit, main OS layout and the placeholders. `[hw]/[emu]` {syfm4-readme}

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

## Syntakt OS 1.41 static-analysis facts (Humgic/syntakt-machine45-research - README {machine45} and handoff dated 2026-10-28; no hardware run, no firmware)
- Address rule `VA = file offset + 0x40000400`; ColdFire big-endian (ISA-C/EMAC). MAIN is 3,438,480 bytes, section 7 is 383,760 bytes. `[doc]` {machine45-handoff}
- **Stock public Machine IDs are 0-44**, stored as a BYTE in each track's machine payload (`P[t]+0xA2`); runtime records `R[t] = model + 0x6C + 0x3C0*t`, `P[t] = *(R[t]+0x10)`; the setter is at `0x40025594` (store at `0x40025620`). 505 parameter descriptors of 52 bytes; only MAIN digital tracks 0-7. `[doc]` {machine45-handoff}
- Section 7 selector: a signed BYTE with a 46-entry map (negative -> 0, 0-45 kept, above 45 clamped to 45); stock maps 0-7 to the same-numbered engine family and 36->8, 37->9, 38->10, 44->11, everything else (incl. 45) to family 0. Stock tables: render pointers `0x400148F0` (12 entries), prep pointers `0x40014920`, the 46-byte map at `0x40014950`. A compact handoff moves MAIN `[0x80002000,0x800021B0)` through a 27x16-byte eDMA transfer (TCD47, channel 47); each track then receives a 20-byte copy into `T[t] = 0x80003C40 + 0x8E*t`. Dslot is 8 x `0x708` = 14,400 bytes. `[doc]` {machine45-handoff}
- Persistence confirmed statically: the current-kit Sound-v7 save/load keeps the machine byte (raw 0-45 and 255 retained, 46-254 map to 0); Pattern-v11 stores the byte at row `+0x2EC` and its restoration is **not closed**; Sound locks, p-locks, held trigs, migration, clipboard and undo not qualified. Evidence labels in that repo: confirmed by static analysis / verified in emulator (none for the whole device) / verified on hardware (none) / hypothesis. `[doc]` {machine45-handoff}
- Open: safe executable storage for native DSP on "CPU 2" (the loader boundary is unresolved); composition with SY FM4 (engine 4, A-table entry overlap) and other descriptor mods; resource IDs 254-261 are unclaimed in the registry but have MIDI CCs, 505+ have no native allocation. `[doc]` {machine45-handoff}

## Gaps
Memory map, DSP, container signing for Syntakt, startup-menu recovery buttons: none collected. Syntakt engines in the OS container: not read.
