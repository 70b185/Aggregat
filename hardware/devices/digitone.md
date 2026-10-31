# Digitone (mk1) / Digitone Keys

Coverage: **good** (almost entirely through the elekloader family). Projects: [../../devices/digitone.md](../../devices/digitone.md)

## Basics
- OS targets: **1.43** and **1.44**. `[doc]` {elekloader-readme}
- Same OS file for Digitone and Digitone Keys (`Digitone_and_Digitone_Keys_OS1.43.syx`); several mods say "nothing has run on a Keys" - treat Keys as untested. `[doc]` {tone-fx} {digicosm}
- Container is **unsigned** (trailer = 32 zero bytes), unlike Digitone II. `[doc]` {dn2-firmware-explore}
- `MAIN OS` loads at `0x40000400` (shared with DN2 per dn2_firmware_explore). `[doc]` {dn2-firmware-explore}
- Official minimum OS for Transfer-based update: 1.30. `[doc]` {elektron-support}
- Recovery: the sources we read do not state it separately; assume the Digitakt pattern (FUNC at power-on, TRIG 4) and verify. `[?]`

## Where the audio runs (Digiwerk prior-art survey, 2026-10) {dn2-cfw-prior}
- **The Digitone mk1's "DSP" is a second ColdFire.** Section 7 is ColdFire code running only the FM voices; the main ColdFire runs the effects and the mix. Master-effect mods (RingTone, Tone+FX) are therefore ColdFire C hooked through elekloader. `[doc]`
- dnfw's instruction census fits this: DN1 1.43 has 613 MAC/MSAC instructions in a tight ~20 KB region against 50 in DN2 1.11. A third-party board list names two MCF54415 plus a Spartan XC3S50A. `[?]` {dn2-hw}

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
