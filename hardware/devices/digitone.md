# Digitone (mk1) / Digitone Keys

Coverage: **good** (almost entirely through the elekloader family). Projects: [../../devices/digitone.md](../../devices/digitone.md)

## Basics
- OS targets: **1.43** and **1.44**. `[doc]` {elekloader-readme}
- Same OS file for Digitone and Digitone Keys (`Digitone_and_Digitone_Keys_OS1.43.syx`); several mods say "nothing has run on a Keys" - treat Keys as untested. `[doc]` {tone-fx} {digicosm}
- Container is **unsigned**, unlike Digitone II; `MAIN OS` loads at `0x40000400` as on DN2 ([`../common/firmware-container.md`](../common/firmware-container.md)). `[doc]` {dn2-firmware-explore}
- Official minimum OS for Transfer-based update: 1.30. `[doc]` {elektron-support}
- **Recovery, used on a unit** (digitone-arp-mod, 2026-10-08, OS 1.44):
  - A test build finished its upgrade but hung on the Elektron logo: the logo did not dissolve, with "H" at bottom left and "1.44" at bottom right.
  - The owner held **FUNC** at power-on, chose **TRIG 4 (OS UPGRADE)**, and sent stock 1.44 via Transfer's *SYSEX TRANSFER -> OS Upgrade via device startup menu* over **DIN** (a Rubix22 interface). The unit worked again.
  - EMPTY RESET and FACTORY RESET are not rollbacks; don't pick them.

  `[hw]` {dn1-arpmod-e04}

## The board and the second ColdFire (taktone, DN1 1.43 with DT1 1.53/1.54 applications) {taktone-docs}
- **The Digitone mk1 is a Digitakt mk1 plus six keys, a second ColdFire and an FPGA.**
  - taktone runs Digitakt 1.53/1.54 main OS builds on Digitone hardware by replacing only section 3 and adapting the panel, LEDs, codec start-up, autosave GPIO and shutdown copy. Four 1.53-based builds were reported working on hardware. `[hw]`
  - Both main CPUs set up **128 MiB DDR at `0x40000000-0x48000000`** (cached and uncached aliases are the same RAM). `[doc]`
- **How the main CPU drives the second ColdFire** (board interface, from taktone-extended, which ran its own engine on it):
  - **Reset:** PB6 held low. Releasing it starts a serial boot.
  - **Upload:** the main CPU is DSPI2 **slave** (eDMA 29, vector 149) and the secondary supplies the clock. Section 6 (a 1,504-byte loader stream; dnfw's section table lists it as 1,492 bytes and "unidentified") loads section 7, which runs at secondary `0x40000400` from entry `0x40000B92`.
  - **Shared SRAM:** FlexBus, main at `0x10000000`, secondary at `0x00000000`. Native use is below offset `0x7a0`: a 928-byte parameter packet at `0x000-0x39f`, then eight mono voices of 32 signed 32-bit samples at `0x3a0-0x79f`.
  - **Handshake:** the secondary writes `HO`/`HA`; the main writes 1 to +2 **before** `B0` to +0. The stock secondary then writes `A5A5` at +4.
  - **Render request:** a PA4 edge triggers the secondary's DTIM0 capture (vector 96). The secondary signals back through EPORT4 (vector 68). One block of pipeline: ~0.667 ms.
  - Clear stale shared words at start, because they can survive a main reset. Never wait in the audio IRQ for late output, and bound the start-up polling. `[hw]`
- **The FPGA bitstream is in section 7:** decompressed from `0x400077A0` to `0x40009000`, **54,664 bytes**, sent as 16-bit words over the secondary's DSPI1. This is the same size as the Analog Heat +FX's and Analog Four MKII's FPGA sections, a strong lead for research map T12. Stock FPGA polling can stall forever, so keep a main-side timeout. `[doc]`
- **Two SysEx addressings:** the startup menu's OS UPGRADE receiver always expects Digitone-addressed SysEx (device `0x0d`). A running Digitakt-based application expects Digitakt addressing (`0x0a`). So recovery to stock Digitone always goes through the startup menu over DIN. `[hw]` (first install confirmed over USB)

### Writing your own engine for the second ColdFire (taktone-extended's contract) {taktone-docs}
- **Split the work:** keep sequencer, locks, LFOs, menu and storage on the main CPU; render on the secondary from a complete control snapshot. Compile secondary code for `-mcpu=54418 -msoft-float`, freestanding.
- **Shared protocol** (taktone's, versioned):
  - a ready tag, committed/completed sequence words, eight 28-byte controls and an XOR checksum;
  - outputs as eight 32-frame int32 mono blocks at `0x3a0`;
  - **only aligned longword writes with readback**: no byte writes to shared RAM, and any mismatch disables submission;
  - one packet outstanding, never block the audio callback, and shut down after 64 consecutive misses.
- **Hook points on the main CPU** (Digitakt 1.53 application): triggers are captured at `0x40077F8E`, before stock source processing consumes them; voice PCM is substituted at `0x40077FBA`, before filter, AMP and mix. On the secondary, init is patched at `0x40000B7A` and the stock engine init at `0x40000B80` is skipped.
- **Memory:** taktone shrinks the native buddy heap from 16 to 8 MiB to reserve `0x4319D6B0-0x4399D6B0` for its runtime, with guard words at both ends. The sample pool (`0x43BAF5F0-0x47BAF640`) and the audio-input ring (`0x47C00000-0x48000000`) stay untouched. This is the same heap-reservation idea as SyntHack's modarea on the Syntakt.

`[hw]` (Sophie on the secondary ran on units) / `[doc]` (addresses)

## Caches at startup (digitone-arp-mod, OS 1.44, emulator trace and the NXP manual) {dn1-arpmod-e04}
- The loader hands over to MAIN with CACR `0x0008c000`: the instruction cache is on, the data cache and store buffer are off.
- Stock MAIN then writes CACR `0xa50ce100` at `0x4000055a`, after its copies. That write invalidates the instruction, branch and data caches and turns caching on. The same CACR value appears on the Rytm and A4 MKII.
- **Code your mod copies before that write is safe. Code copied later must be followed by an explicit invalidation**, because instruction-cache contents can even survive a reset. This is the ColdFire twin of rule A28.
- Real cache behaviour and render deadlines have not been measured on a unit.

`[emu]`

## Where the audio runs (Digiwerk prior-art survey, 2026-10) {dn2-cfw-prior}
- **The Digitone mk1's "DSP" is a second ColdFire.** Section 7 is ColdFire code running only the FM voices; the main ColdFire runs the effects and the mix. Master-effect mods (RingTone, Tone+FX) are therefore ColdFire C hooked through elekloader. `[doc]`
- dnfw's instruction census fits this: DN1 1.43 has 613 MAC/MSAC instructions in a tight ~20 KB region against 50 in DN2 1.11. A third-party board list names two MCF54415 plus a Spartan XC3S50A. `[?]` {dn2-hw}

## Load on the main ColdFire, from a master-effects suite (Tone+FX, OS 1.43/1.44) {tonefx-dev}
- **Budget:** 250 MHz, so **166,667 cycles per 32-sample block**. In the emulator's cycle model, stock plus Tone+FX with all effects off peaks at ~101k cycles per block. With its three heaviest effects on it peaks at ~160k, which leaves 4 % at worst (the p99 is better). The mods' RAM pool is 1.25 MB. `[emu]`
- **The emulator and the unit disagreed:**
  - The unit's CPU meter went from ~70 % to ~87 % at idle between two releases, while the emulator's cycle model said the render had become *faster*.
  - Suspects are what the model leaves out: EMAC mode switches (each handler flipped MACSR between integer and fractional, 12 switches per block), DDR bursts for a 24-bit delay line, instruction-cache pressure from inlining, and UI redraws.
  - **Still unresolved.** `[hw]`
- **Measured on the unit:**
  - Hoisting the MACSR switch to once per block helped.
  - An EMAC-off build idled lower but ran worse while processing, so EMAC stayed.
  - A "fused" single-pass insert, meant to save loads and stores, measured **+15 %** on the unit.
  - Every optimisation is A/B'd on hardware before it lands. `[hw]`
- Toolchain notes from the same project: ColdFire instructions are at most 6 bytes, and `lsl.l #N` takes only 1-8. `[doc]`

## Core mods (elekloader)
| Core | Covers | Notes |
|---|---|---|
| core-dn1-2.0a | OS 1.43 | first core, used by RingTone/Tone+FX/digiring |
| core-dn1-2.0a-os1.44 | OS 1.44 | "lints, links and verifies, but the emulator does not boot stock 1.44 yet" at elekloader v0.4.0 |
| core-dn1 3.0 | digitables | newer core |
| core-dn1 3.2 | digicosm, digichroma | newer core |
| core-dn1 3.3 | digichroma source option | **not yet released** |

`[doc]` {elekloader-readme} {digitables} {digicosm} {digichroma}. Later READMEs say 1.43/1.44 were checked in digikit; the v0.4.0 note says the 1.44 emulator boot was not working - newer state wins, but re-check. `[?]`

## Core-owned hook sites (1.43)
`0x40000538, 0x4001900c, 0x40019072, 0x40019d9c, 0x40019de4, 0x40072a34, 0x4009d108, 0x4009e51c`. `[doc]` {elekloader-adapting}

## Effect mods and the `bulk` area (altstrument 2026-10-31 lists five Digitone mk1 mods; elektronmods 19 Digitone entries)
Listings: {alt-digitone}. Layout used by the effect mods: code and state share the **128 KB "mods" share** (older cores) while big audio buffers sit in the profile's **`bulk` area `0x44000000-0x47BE0000`** (~60 MB) - the 0.4.0 apps refuse mods that need it ("do not know the bulk area"), elekloader main is required. `[doc]` {digiprism-readme} {digiswarm-readme} {elekloader-devices}
- **DigiPrism** (formerly DigiChroma; stock OS 1.43/1.44; fxkit + core-dn1 4.1; README title says 3.2, body says 4.1): input effects pedal with four reorderable modules (Color, Motion, Ambience, Grit) x five effects, gesture recorder, 30-second CAPTURE looper, MIDI CC control; 59 KB of code/state in the 128 KB share plus ~7 MB audio; project data tag `DCHR` (56 bytes); p-locks live in one synth track's lock table (LOCK TRACK, default T4 - that track should play no notes or arp in a pattern that uses DigiPrism locks); **CPU guard: DMA timer 0 timing every block, bypass when usage stays above 93 % for 0.2 s**; the `DIGITONE` source option needs core-dn1 3.4 insert audio (not released); presets removed in 0.2; emulator has no DMA timer 0 so its CPU meter is unreliable; 0.2 tested on a Digitone mk1 by its author, never on a Keys. `[hw]/[emu]` {digiprism-readme}
- **DigiSwarm** (formerly DigiCosm; core-dn1 3.2+, several effect mods together need 4.0): 11 engines x 4 variations (MIST, SHARDS, GLIDE, CHOPS, STUTTER ...), 60-second stereo looper with one overdub layer, Hold/Reverse/Bypass, resonant filter, pitch modulation, four-room reverb; buffers 26 MB in `bulk` (input history 10.9 s); 30 KB of the 128 KB share; project data 132 bytes (mods share 480 bytes there, digitables uses 328); loops are lost at power-off ("no file storage location known to be free"); CPU guard thresholds 45 % (fewer new grains) / 30 % (more again, up to 16 heads); CCs 22, 45, 46, 93 accepted but inert; no program changes, no expression pedal; 0.1 runs on the author's Digitone mk1, 0.1.2 emulator-only. `[hw]/[emu]` {digiswarm-readme}
- **Tone+FX** packages: core-dn1-2.0a, digimeter-1.1, digieq-1.0, digiring-1.0, digifold-1.0, digifilter-1.0 (per-voice BP/BP2/COMB/TRASH on up to 4 voices), digictl-1.3; master order ring -> EQ -> fold; DSP shared with the FM voices, "dropouts" possible with several COMB/TRASH voices; verify downloads with `SHA256SUMS`; emulator-tested only. `[emu]` {tonefx-readme}
- Memory facts for planning: the Digitone mk1 OS clears `0x4028E000-0x43229E60`; mod RAM area `0x43EC0000-0x44000000` (1.25 MB, core 4.0); see [`../common/memory-maps.md`](../common/memory-maps.md).

## Notes
- digihealth 1.1 brings SYSTEM INFO only; FAST AUDIO is not ported to Digitone. {digihealth}
- DigiSplash and DigiCandy support Digitone mk1 + Keys at OS 1.43. {digisplash} {digicandy}
