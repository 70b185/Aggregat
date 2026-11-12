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
- **selache pitfalls that halt a real DSP but run in the emulator** (elekloader ADAPTING.md, Nov 2026; the first matches 70b185's DT2 finding):
  - A shift by a negative immediate (`LSHIFT R1 BY -16`) is encoded without sign extension. Put the count in a register (`R2 = -16; R1 = LSHIFT R1 BY R2;`). elekloader's lint flags candidates, but it cannot see instruction boundaries, so check each one in the listing.
  - **A C function whose locals sit more than ~63 words from the frame pointer is compiled wrongly.** One large local array is enough. Keep large buffers static or in the voice state.

  `[hw]` {elekloader-adapting} {own-dt2-notes}
- **Two projects compared selache's VISA decoder with digikit's table decoder on the DN2 stock program, and agree on where each is wrong.** The test: walk instruction by instruction between known starts (branch targets, `cjump` sites, DO-loop ends) and see who lands exactly. `[doc]` {dn2-selache} {dn2-cfw-t31}
  - selache's disassembler gives some 48-bit forms as 32-bit (Type 3a `59be`, Type 4a `6a3e`, Type 7a `043e`, Type 16a `9980`) and one 32-bit form as 48-bit (Type 3b `593e`); DO-loop ends land on the table decoder's starts 85 of 85 times, on selache's 64 of 85, and selache prints most DO offsets with bit 23 set.
  - digikit's table had Type 2b wrong (the programming guide's `000000011`, not the reference's `110000000`; selache won 119 to 0) and wrongly ruled out `Type10a_rel` in VISA; both fixed in digikit#31. Its `undoc16/48` forms are still provisional.
  - A two-byte-late start still lands 94.9 % of spans, because VISA resynchronises within a few instructions. A decoder's score means something only against that control.
- **Disassembled text is not a patch format.** 11,440 distinct encodings from the DN2's L2 program, each disassembled with selmap and reassembled alone with selas: 83.9 % came back identical; 1,265 kept their width but lost register fields the text does not show (`bitrev`, `modify`, `dm` moves); 216 changed width; 320 printed forms could not be parsed; 40 crashed the assembler. A 48-bit `nop` reassembles as the 16-bit one. Patch from source, and compare bytes (rule A41). `[doc]` {dn2-selache}
- `tools/sharcvm` (dn2-cfw) interprets the stock DSP handler to render chorus/delay/reverb/master compressor offline. `[doc]` {dn2-cfw}

## Generic ColdFire MCF5441x facts (not Elektron-specific)
Source: {coldfire-rs}. These describe the chip family that digikit names as the Digitakt II control CPU (MCF54415); nothing here says the Elektron firmware uses a given peripheral or mode. `[doc]`
- Family covered: MCF54410 and MCF54415-MCF54418. Peripherals with drivers: GPIO, PIT, INTC, eDMA, UART, DSPI, eSDHC (eMMC block **reads** via eDMA), SSI (I2S/network audio, full-duplex eDMA rings), USB OTG device mode (high speed via ULPI PHY; 54415-54418 only). Not implemented there: eSDHC writes, EPORT, DMA timers, I2C, RTC, PWM, ADC/DAC, FlexCAN, Ethernet, NAND, USB host.
- Vector table goes at the region origin, which must be **1 MB aligned** (VBR keeps bits 31..20 only); code starts at origin + 0x400.
- Boot modes: cold boot (serial/NOR/NAND, image sets up PLL and DDR) or via a bootloader.
- Rust for this chip: rustc_codegen_gcc with libgccjit targeting `m68k-elf`; default CPU in that toolchain is the 54418. Potential route for writing ColdFire-side mod code in Rust instead of C - unproven for Elektron firmware.

## Writing fast ColdFire C (digigrain's measured notes, Digitakt mk1, gcc `-mcpu=54455 -O2`) {digigrain-skills}
These hold for every ColdFire V4/V4e box here. Instruction counts come from the patched-Unicorn emulator; confirm the margins on a unit (A34). `[emu]`
- **Shift immediates only reach 8.** A shift by 14 or 15 costs a `moveq` plus a register shift; a shift by 16 is `swap` (+ `ext.l`). Arrange fixed-point products to land on a 16-bit boundary (e.g. store tables as unsigned Q16 so that `(s*w16) >> 16` equals `(s*w15) >> 15` exactly).
- `muls.l` and hardware divide are there; libgcc is not linked, so avoid 64-bit math (hand-write it).
- **Prove the bounds once per block, then run a loop without checks**, with state in locals. Keep the checked loop as the fallback near buffer ends.
- Mark hot loops `noinline`: an inlined, merged loop kept a branch inside and spilled to the stack (~45 instructions per sample). `do { } while (--n)` saves the count test.
- Specialise on loop-invariant cases: unity-speed grains skip interpolation (13 vs ~26 instructions per sample); a cached per-voice window table replaces per-sample shape blending.
- **EMAC in fractional mode** (MACSR `0x20`: signed fractional, truncating, no saturation): save and restore MACSR, ACC0 and ACCEXT01, and clear ACC0 first. Bit-exact Python models must truncate each product as `floor(x*y/2^23)`, keeping 8 bits below the LSB.
- **Hooks must preserve every register the caller relies on.** Real bugs: a chord hook missed a4-a6, a callee clobbered a0, and a restoring `movem` lost a decision kept in d7. Test hooks with a stub that junks all scratch registers.
- Write a C reference and a bit-exact Python model first, and optimise only while the model's tests stay green.

## Emulators
- **digiemu** (irpina): Digitakt/Digitone mk1 emulator, runs the user's own OS behind a clickable panel. {digiemu}
- **digikit** (current home ElekLabs/digikit, `[doc]` {digikit}): native Rust emulator running ColdFire and SHARC+ firmware together with front panel, display and audio; web panel (WASM) and Tauri desktop app; `patchkit` applies modules to the user's own `.syx` and refuses to change sections 2, 4 and 8; headless scenario runner with pinned PCM hashes; control socket for patch injection; ColdFire/DSP analysis databases and Ghidra tooling. Targets: Digitakt II 1.17 (also runs 1.16; 1.15C for old analysis), Digitone II 1.12 (also runs 1.11; 1.10E for old analysis). Caveats: DSP not real-time yet; browser host parked on `wip/browser-host`; no patched firmware installed on a device by the author; bootstrap-menu recovery untested on hardware. AGPL-3.0-or-later with NOTICE terms asking for the credit "digikit by Em D".
- **Earlier digikit README (m-dwyer/digikit, {digikit-old}) described a Python/Unicorn design:** ColdFire emulator for Digitakt II / Digitone II; patched Unicorn m68k (SR read, CCR sync, EMAC MAC with load; stock Unicorn refused); ColdFire-aware disassembler because Capstone misses MVS/MVZ and FF1; first run needs a cold boot of a few minutes to build snapshots; about 10M instructions/s. Works: core, interrupt controllers, PIT, DMA timers, eDMA, front-panel TX, display, SD/MMC up to identification. Missing then: DSP (no audio), input path, block storage - partly superseded by the Rust version above. `[doc]` {digikit-old}
- dn2-cfw's fork (branch `dn2-1.12`): 1.12 boots to the main screen, PLAY runs the sequencer, DIN MIDI works incl. virtual ports on Mac, live play ~0.8x real time. `[doc]` {dn2-cfw}
- A whole-DSP SHARC emulator (Overtone, the modding skill): used with digikit for ~160 checks per build. `[doc]` {overtone} {dn2-modding-skill}
- **Emulators do not model the timing of the two chips or the link between them** (dn2mk2 FIRMWARE.md) - so DSP-time overruns are only found on a unit. `[doc]` {dn2mk2-firmware-md}
- **dsp56kEmu quirks seen by KYOTI:**
  - `move x:(rN+$disp),a` (two-word displacement form into accumulator a) read the wrong word in the emulator, while destination b was fine.
  - Short immediates into data ALU registers are left-aligned, and `asr` leaves bits in acc0 that `tst`/`cmp` see; the hardware behaves the same for these two.

  Route displaced loads through b. `[emu]` {kyoti-fw}
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

## More emulators and directory snapshots (2026-10-31)
- **Elektron Emu** (xerydian): five VST3 plug-ins (Mac, Windows) running each machine's real OS in an emulated CPU - Digitakt II, Syntakt, Analog Rytm MKII, Digitone II, Model:Cycles; the user supplies the `.syx` in a per-machine folder; +Drive emulated and persisted, WAV loading on DT2/Rytm/DN2; **Digitone II's DSP is compiled locally on first open (needs a C compiler; otherwise a slow interpreter that renders offline only)**; limits: Rytm analog voices are a custom model that does not sound like the machine, Syntakt analog tracks 9-12 missing; 2 commits, no licence stated. `[doc]` {elektron-emu}
- **digiemu** patches Unicorn (six patches) - details in [`../devices/digitakt.md`](../devices/digitakt.md); dn2mk2 reports that stock Unicorn's destructive SR read corrupts condition flags, so a patched Unicorn is mandatory for any ColdFire work. `[doc]` {digiemu-readme} {dn2mk2-emulator}
- **Stock Unicorn 2.1.4 (and QEMU master as of 2026-09-15) gets ColdFire wrong in ways that change results** (emu-elektron's patch notes) `[doc]` {emu-elektron-patches}:
  - **Condition codes:** they are committed lazily, so a hook or a counted stop in mid-block sees stale flags, and the next branch goes the wrong way.
  - **MAC/MSAC with load is decoded wrongly in four ways:**
    - Ry with bit 0 or 1 set faults as "dual accumulate" on a CFV4E;
    - Rx is always D2;
    - MSAC adds instead of subtracting (this also hits MSAC without load);
    - MASK is applied to every load address.

    The DT2 main OS reaches one of these at `0x400db9e0`.
  - EMAC fractional and signed arithmetic is wrong (as found by SyntHack and octabam).
  - **EMAC saturation with MACSR.OMC** gets its sign and constants wrong.

  Any ColdFire emulator built on Unicorn needs these fixes before its audio or branch results mean anything. emu-elektron carries all of them as patches for five devices.
- Directory views of the tools: {alt-tools} lists digikit, elekloader, digiscreen (Android page mirroring the 128x64 screen over USB MIDI), Elektron Emu, digiemu, ghidra-dsp56300, digi-roll, Elektroid, Overwitch and elektron-firmware-tool (the page names no source for the last one). elektronmods' Mod List ({em-list}) has 59 entries; its Analog Heat filter shows only Overwitch and elektron-firmware-tool.
- **Unicorn's `emu_start(count=N)` puts a hidden code hook on every address.** With a code hook covering every address, every instruction also walks all other code hooks (dn2mk2's gate has about 330). Replacing `count=` with a budget in translated blocks took dn2mk2's longest ColdFire gate step from 3,250 s to 161 s, with every report byte-identical; running out of the budget now raises instead of stopping silently. Not usable where the instruction count is the measurement (digikit's boot counts instructions on purpose). `[emu]` {dn2mk2-gatespeed}
- **A pure-Python SHARC emulator runs about 4x faster under PyPy** (dn2mk2's ten SHARC runner parts: about 181 to 44 min) with every emulated value identical; only numpy results computed after the run differ in the last digits. dn2mk2 re-runs those steps under CPython after each release as a cross-check. `[emu]` {dn2mk2-gatespeed}
- **CPU readings from an instruction-counting emulator sit far under the unit's.** analog-emu's unit timing (`DTEMU_TIMING`, "unit" sampled at about real time, "exact" at about 0.6x) charges the core's cycles and memory waits. On the Rytm MKII the unit's readings were all taken with the Sidecar Pi streaming Overbridge both ways (about 6,857 blocks of 368 bytes a second each way), and elekloader's core 0.10/0.11 memcpy/memset wrappers also run for that stream's handlers. Without the stream the emulator read core 0.11 builds about 14 points low; with it, nine of eleven calibration builds came within about 3.6 points of the unit. elkbench fails an emulator run at 95 % CPU or more and warns above 90 %. `[emu]`, calibrated against units {elkbench-timing}
- **Ghidra and EMAC `[?]`:** digikit found that stock Ghidra misdecodes the EMAC line-A words of the MCF5441x and uses a separate language (`68000:BE:32:ColdfireEMAC`). The owner's Heat research notes that Ghidra has known EMAC variants since GP-2197. Check the EMAC decode of your Ghidra version on a known MAC instruction before you trust it. {digikit-f08} {own-heatfx-notes}
