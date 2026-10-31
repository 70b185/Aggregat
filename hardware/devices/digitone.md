# Digitone (mk1) / Digitone Keys

Coverage: **good** (almost entirely through the elekloader family). Projects: [../../devices/digitone.md](../../devices/digitone.md)

## Basics
- OS targets: **1.43** and **1.44**. `[doc]` {elekloader-readme}
- Same OS file for Digitone and Digitone Keys (`Digitone_and_Digitone_Keys_OS1.43.syx`); several mods say "nothing has run on a Keys" - treat Keys as untested. `[doc]` {tone-fx} {digicosm}
- Container is **unsigned** (trailer = 32 zero bytes), unlike Digitone II. `[doc]` {dn2-firmware-explore}
- `MAIN OS` loads at `0x40000400` (shared with DN2 per dn2_firmware_explore). `[doc]` {dn2-firmware-explore}
- Official minimum OS for Transfer-based update: 1.30. `[doc]` {elektron-support}
- Recovery: the sources we read do not state it separately; assume the Digitakt pattern (FUNC at power-on, TRIG 4) and verify. `[?]`

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

## Notes
- digihealth 1.1 brings SYSTEM INFO only; FAST AUDIO is not ported to Digitone. {digihealth}
- DigiSplash and DigiCandy support Digitone mk1 + Keys at OS 1.43. {digisplash} {digicandy}
