# Digitone II

Coverage: **medium-good** - the most documented small box right now (dn2_firmware_explore, dn2-cfw, Overtone, dn2mk2, the modding skill).
Projects: [../../devices/digitone-2.md](../../devices/digitone-2.md)

## The OS-version split (read this first)
| OS | Who targets it | Consequence |
|---|---|---|
| 1.10E | dnfw/digikit examples | |
| **1.11** | dn2mk2, digitone-2-modding-skill | dn2mk2 refuses anything else; units on 1.12 must go back to 1.11 |
| **1.12** | Overtone, dn2-cfw, DigiRust | Overtone refuses anything else |
Mods for different OS versions cannot be combined and flashing between them can leave projects unreadable. `[doc]` {overtone} {dn2mk2} {dn2-cfw}

## Architecture
- ColdFire main CPU (big-endian code, GCC-built, C++ RTTI names remain); SHARC+ audio DSP. `[doc]` {dn2-cfw} {dn2-firmware-explore}
- `MAIN OS` section: 3,085,696 bytes, loads at `0x40000400`. `[doc]` {dn2-firmware-explore}
- Container **signed with HMAC-SHA256**, key derived from material inside the image; a modified image can be signed correctly (the tools do it). `[doc]` {dn2-firmware-explore}
- DSP works per block; the stock handler can be interpreted offline (sharcvm); new effects are portable C, compiled with selache/selcc and spliced into the DSP section. `[doc]` {dn2-cfw}

## Parameter table
- 1.12: one OS table of **321 rows**, no free space after it. dn2-cfw's patch GT00 copies it at start-up into free memory with room for **384 rows**; GT01 adds 17 hidden rows (3-band compressor). `[hw]` {dn2-cfw}
- **Projects store values by slot, not by row**, so moving the table keeps the saved format; new rows follow `docs/parameter-table-growth.md` (not read yet). Table growth was first done on 1.11 for the LFO4 mod in dn2_firmware_explore. `[doc]` {dn2-cfw}
- Overtone: LFO 3's storage holds ARP 2, so a sound that used LFO 3 loses it; ENV3/LFO3 no longer exist in Overtone. `[doc]` {overtone}

## Limits and budgets
- **USB upgrade limit 2 MiB**, not checked by the receiver; oversized images stall at the end, nothing written, power cycle clears. `[hw]` {dn2mk2-firmware-md}
- **DSP image limit 1,048,575 bytes**; recent dn2mk2 builds sit at ~1,017,000-1,018,000. `[doc]` {dn2mk2-firmware-md}
- DSP time: SETTINGS > SYSTEM > DSP LOAD shows it; **at 100 % the audio crackles.** Heavy machines can push it over. `[hw]` {overtone}
- dn2mk2 cost figures: a PERC voice up to ~41,000 instructions per block, P-I machines ~9,000-19,000; Monomachine budget about two SIDs, four DPRO Waves, one DDRW and one DENS, or two VO-6 at once. A frame guard silences voices that no longer fit (limit 0.6 of the frame, estimated, not measured). `[doc]` {dn2mk2-firmware-md}
- Fast on-chip DSP memory vs DDR: voice state moved to fast memory in dn2mk2 v0.32; Monomachine tables and P-I delay lines remain in DDR. Savings can only be measured on a unit. `[doc]` {dn2mk2-firmware-md}
- Overtone: LOOP records 8 s stereo per track; LOOP in STRC mode, P-I and many SOPHIE voices can push DSP over 100 %. `[doc]` {overtone}

## Sample memory (dn2mk2)
- Pool of 400 MB (368 MB user samples + 32 MB recordings, ~5.5 min), up to 122 slots, RAM-checked at power-on (~0.7 s); +Drive library ~20 GB in a region the stock OS does not touch, up to 2,048 samples; slices up to 64 per sample, stored in a 128 KB area. Power-on load grows with stored samples (~30 s for 20 MB). **The 400 MB pool has never run on hardware** per FIRMWARE.md v0.22. `[emu]` {dn2mk2-firmware-md}

## Recovery
- FUNC at power-on -> TRIG 4 (OS UPGRADE) -> Elektron Transfer **LEGACY OS UPGRADE** over **5-pin DIN MIDI to MIDI IN; USB does not work in this mode**; takes ~12-15 min, do not interrupt. The bootstrap that holds this menu must stay byte-identical (the brick checker refuses changes). `[hw]` {overtone} {dn2mk2} {dn2-cfw}
- Known: Overtone 1.0 could stall on "Receiving"/"PREPARING..." when an OS was sent with Transfer; power-cycle and use the STARTUP menu, install 1.0.1. `[hw]` {overtone}
- Pre-flash safety kit: back up +Drive, keep the stock OS file for the exact version, volume down, DIN cable ready, check the file's SHA-256 against the gate record (`certutil -hashfile FILE SHA256` on Windows). `[doc]` {dn2mk2-firmware-md}
- dn2_firmware_explore: own rebuilt images stall at ~80% in the recovery path (fix built, untested). `[doc]` {dn2-firmware-explore}

## Hardware test evidence
- dn2-cfw: EF01 (renamed stock 1.12) proved rebuild/seal/flash; FLG1 (flanger), FTD1, DH01 (hook bus), FTN1, GT00, GT01 ran on the unit. `[hw]` {dn2-cfw}
- Overtone 1.0.1: played on a Digitone II, Transfer installs tested on the unit. `[hw]` {overtone}
- dn2mk2: v0.21-v0.33 mostly emulator-only, hardware checks outstanding; user reports of p-lock clicks and silence were the reason for the DSP guard (v0.27) and AMD fix (v0.30.1). `[emu]` {dn2mk2-firmware-md}
- Emulators do not model the two chips' timing: overruns show only on a unit. `[doc]` {dn2mk2-firmware-md}

## Official OS list (elektron.se release notes, page updated 2026-10-01)
Newest **1.12** (adds routing of the Main outputs through Outbox 8 and FUNC+UP/DOWN channel navigation in the Outbox 8 configuration menus), then 1.11, 1.10E, 1.10D, 1.10C, 1.10B, 1.10A, 1.10, 1.00A. No dates per version. So Overtone (1.12) targets the **current** OS and dn2mk2 (1.11) a one-version-old OS. `[doc]` {elektron-dn2-notes}
Digitone II reached Overbridge streaming with OS 1.10 (plugin followed later). `[doc]` {gearnews-dn2-overbridge}

## Control from outside
SysEx/MIDI facts, the SYXGRID format map (45 mappings, confidence levels) and digitone-syx-toolkit are in [`../common/sysex-and-midi.md`](../common/sysex-and-midi.md). elekloader's simonjohansson fork supports Digitone II 1.12 as experimental (whole builds, linkable mods, SHARC mods, selectable synth/filter mods; UI events and remote input checked on a unit). {elekloader-simonjohansson}

## Gaps
`docs/flashing.md`, `docs/mainos-image.md`, `docs/parameter-table-growth.md`, dn2mk2 `docs/SAFETY.md`, and the skill's "hardware rules the emulators cannot check" are the next reads (see `../MINING.md`).
