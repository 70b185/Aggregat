# Digitone II

Coverage: **medium-good** - the most documented small box right now (dn2_firmware_explore, dn2-cfw, Overtone, dn2mk2, the modding skill).
Projects: [../../devices/digitone-2.md](../../devices/digitone-2.md)

> Machines, SHARC link, sampler/+Drive layout and field incidents: [`digitone-2-machines-sampler-sharc.md`](digitone-2-machines-sampler-sharc.md). Memory/mod areas of all devices: [`../common/memory-maps.md`](../common/memory-maps.md).
>
> Internals from the research repos (image identity, stock hashes, flash layout, loader margins, DSP landmarks, +Drive, disassembly pitfalls): [`digitone-2-internals.md`](digitone-2-internals.md).
>
> Deep dive for OS 1.11 (addresses, frame format, free memory, ColdFire/SHARC rules, emulator limits): [`digitone-2-os111-reference.md`](digitone-2-os111-reference.md). Working method for agents: [`../common/agent-workflow.md`](../common/agent-workflow.md).

## Official support page (read 2026-10-31)
OS **1.12** dated 2026-10-01 ("adds some Outbox 8-related features"; distributed as `Digitone_II_OS1.12_dist.zip`); English manual for OS 1.12 dated 2026-10-08; Japanese manual only for OS 1.00A; Elektron Transfer 1.10.3 (2026-03-04). The page allows personal use of its files and prohibits editing, modifying or redistributing them - one more reason never to commit stock files. `[doc]` {elektron-dn2-support}

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

### Parameter table details (OS 1.12; dn2-cfw `docs/parameter-table-growth.md`)
- Each parameter is one **60-byte row**. Table base `0x401f83a4`, stock 321 rows. Offsets: `+0x00` group (set/page family), `+0x04` k (the slot that holds the value in its set), `+0x08..0x14` min/max/default/bipolar, `+0x18` MIDI CC, `+0x1c` NRPN, `+0x20` Overbridge id, `+0x28..0x38` names/formatter/suffix. A separate RAM display table holds glyph, lock flags and randomiser data. `[doc]` {dn2-cfw-param-table}
- Row ids are **not saved**; projects store values by slot k through fixed k-to-stored-id tables. Slot maps and CC/NRPN maps are rebuilt from the table at each boot (`0x400dc634`); page records are built at boot from code constants (`0x400c2c4e`). Moving the table does not change project storage; **new rows do**, via their k and display flags. `[doc]` {dn2-cfw-param-table}
- Grown table at `0x47D00000`, room for 384 rows (`0x180`), copied at boot by `pg_boot` (called from `0x40000568`). New row ids `0x141`-`0x17f` (63 ids); the same-length-edit ceiling is `0x1e0` (480 rows). 56 address operands in 53 functions had to be redirected; 57 row-count compares changed (`#0x141`->`#0x180`, `#0x140`->`#0x17f`; five look similar and stay). The display-table reader at `0x400c257c` has its first 10 bytes turned into a jump plus two nops. The MIDI input cache (33 constants in five functions) grows by 12,852 bytes. `[doc]` {dn2-cfw-param-table}
- Map builders hold 101 entries each, so k must stay in range (0..100 for sound/FX/MIDI, 0..25 for trig). Stock saves FX k 25-69 only; FX k 70+ and sound k 65 and 100 are **not saved**. `[doc]` {dn2-cfw-param-table}
- Rules for a new row: use a free k in the set's table, **one row per k** (the last row written wins and can silently replace a stock knob); value 0 must keep classic behaviour (existing projects store 0 in slots stock has no row for); send-FX rows set `flags_set = 8` so they are never lockable; synth rows use free saved k values (FM Tone 34, 49; WaveTone 50-64; FM Drum 55-64; Swarmer 33-64); no randomiser; MIDI: no CC already in the set's map, none in 32-63, none taken by the CC parser (1, 2, 6, 64, 66, 94, 98, 99, 110, 120, 121, 123), NRPN 398 at most; Overbridge id outside stock's 0..387 (e.g. `0x400`+n, untested with the plugin). `[doc]` {dn2-cfw-param-table}
- **P-lock trap:** a row is lockable when display flag bits 0 and 3 are clear; locks are stored as (track, k), so an FX row with k 70 could create a lock on a sound's slot 70, which stock would play back. A bad row can write past map tables, replace a stock knob, or leave stray p-locks that persist after returning to stock. A project saved on a grown build and loaded on stock 1.12 is **untested on hardware**. `[doc]` {dn2-cfw-param-table}
- Checks used: brick checker 12/12 for GT00/GT01 ("a pass is not proof for code changes"), `scripts/t65_build.py check_rows` for FX rows, `pg_boot` only skips ids outside `0x141`-`0x17f` (it does not check k, flags, CCs or Overbridge ids), an emulator run of 7,100 MIDI messages giving the same 991 parameter sets as baseline. Never flash `param-test-dn2` or `fx-page2-dn2`. `[doc]` {dn2-cfw-param-table}

## Limits and budgets
- **USB upgrade limit 2 MiB**, not checked by the receiver; oversized images stall at the end, nothing written, power cycle clears. `[hw]` {dn2mk2-firmware-md}
- **DSP image limit 1,048,575 bytes**; recent dn2mk2 builds sit at ~1,017,000-1,018,000. `[doc]` {dn2mk2-firmware-md}
- DSP time: SETTINGS > SYSTEM > DSP LOAD shows it; **at 100 % the audio crackles.** Heavy machines can push it over. `[hw]` {overtone}
- dn2mk2 cost figures: a PERC voice up to ~41,000 instructions per block, P-I machines ~9,000-19,000; Monomachine budget about two SIDs, four DPRO Waves, one DDRW and one DENS, or two VO-6 at once. A frame guard silences voices that no longer fit (limit 0.6 of the frame, estimated, not measured). `[doc]` {dn2mk2-firmware-md}
- Fast on-chip DSP memory vs DDR: voice state moved to fast memory in dn2mk2 v0.32; Monomachine tables and P-I delay lines remain in DDR. Savings can only be measured on a unit. `[doc]` {dn2mk2-firmware-md}
- Overtone: LOOP records 8 s stereo per track; LOOP in STRC mode, P-I and many SOPHIE voices can push DSP over 100 %. `[doc]` {overtone}

## Sample memory (dn2mk2)
- Pool of 400 MB (368 MB user samples + 32 MB recordings, ~5.5 min), up to 122 slots, RAM-checked at power-on (~0.7 s); +Drive library ~20 GB in a region the stock OS does not touch, up to 2,048 samples; slices up to 64 per sample, stored in a 128 KB area. Power-on load grows with stored samples (~30 s for 20 MB). **The 400 MB pool has never run on hardware** per FIRMWARE.md v0.22. `[emu]` {dn2mk2-firmware-md}

## Sections
Protected: sections **2, 4, 5 and 8** (bootstrap, updater and others) must stay byte-identical to stock in dn2mk2's gate; mods change only **3 (MAIN OS) and 7 (DSP)**. Five stock machines; 16 track buffers. 1.10E rebuilt the bootstrap and moved its load address, 1.11 changed it again. `[doc]` {dn2mk2-safety}

## Recovery (full procedure in [`../common/flash-procedure.md`](../common/flash-procedure.md))
- FUNC at power-on -> TRIG 4 (OS UPGRADE) -> Elektron Transfer **LEGACY OS UPGRADE** over **5-pin DIN MIDI to MIDI IN; USB does not work in this mode**; takes ~12-15 min, do not interrupt. The bootstrap that holds this menu must stay byte-identical (the brick checker refuses changes). `[hw]` {overtone} {dn2mk2} {dn2-cfw}
- Known: Overtone 1.0 could stall on "Receiving"/"PREPARING..." when an OS was sent with Transfer; power-cycle and use the STARTUP menu, install 1.0.1. `[hw]` {overtone}
- Pre-flash safety kit: back up +Drive, keep the stock OS file for the exact version, volume down, DIN cable ready, check the file's SHA-256 against the gate record (`certutil -hashfile FILE SHA256` on Windows). `[doc]` {dn2mk2-firmware-md}
- dn2_firmware_explore: own rebuilt images stall at ~80% in the recovery path (fix built, untested). `[doc]` {dn2-firmware-explore}

## dn2-cfw working set (README "Getting started")
Prerequisites: macOS on Apple silicon (Linux likely for most), Python 3, the user's own `Digitone_II_OS1_12.syx` in `elektron-firmware/`. Upstream tools are cloned into `vendor/` at the commits in `VENDOR.md`; digikit and elekloader come as the author's forks on branch `dn2-1.12` (digikit: 1.12 support, audio clock, DIN MIDI, LEDs, live play; elekloader: a Digitone II 1.12 profile and the `core-dn2` hook bus). Every candidate image must pass `tools/brickcheck` (12 checks) before it is flashed; compile C to SHARC code with selache/selcc and splice with `tools/dspsplice`; use elektron-firmware-tool for the `.syx` format and rebuild. The README does not give a flashing procedure (see `../common/flash-procedure.md`). `[doc]` {dn2-cfw}
Build ladder, all reported as run on the unit: EF01 (renamed stock: proves rebuild/seal/flash), FLG1 (flanger in place of chorus), FTD1 (+ one-head tape delay with loop filters, wow/flutter, wear, pitch bends on TIME), DH01 (core + MIDI test mod), FTN1 (screens renamed), GT00 (parameter table moved, +63 knob ids), GT01 (+17 hidden rows, 3-band compressor prerequisite). Not yet on the unit: the 3-band compressor and a Space-Echo-style delay. `[hw]` {dn2-cfw}
Notes in the repo mark each claim `[verified]` or `[inferred]` - copy that convention. `[doc]` {dn2-cfw}

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
