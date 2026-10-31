# Digitakt II

Coverage: **medium**. Projects: [../../devices/digitakt-2.md](../../devices/digitakt-2.md)

## Hardware (as reported by digikit's author)
- Control CPU: Freescale ColdFire **MCF54415**, big-endian, runs UI, sequencer, files, MIDI. `[doc]` {digikit-old}
- Audio DSP: Analog Devices **ADSP-21569 SHARC+** running FreeRTOS, shipped as ADI loader records. `[doc]` {digikit-old}
- Display 128x64. Storage: eSDHC controller + eMMC. `[doc]` {digikit-old}
- A forum user notes the Digitone II PCB looks near identical (same P/N PCBA0109B, 32 GB eMMC). `[?]` {elektronauts-dn2-pcb}

## OS versions in use
| OS | Used by | Note |
|---|---|---|
| 1.11 | earlier digikit decoder could read it | |
| 1.16 | current digikit runs it as its default file | |
| 1.17 | current digikit **target** | |
| (1.17 or 1.16) | dn2mk2 uses the user's Digitakt II file only as a source of sample-reading tables for the Digitone II | not a Digitakt II mod |
| 1.15C | earlier digikit README (**only build stated as tested then**), lalzart's research; kept for old analysis in the current digikit | other builds "will likely fail to boot" in the emulator |
| 1.16 | digitakt-ii-research builder, dt2-machine-lab | no longer listed on elektron.se; author suggests asking Elektron support |
| 1.17 | digitakt-ii-research builder (recommended), digitakt2-perform, DigiSplash-II | 1.18+ would need addresses found again |

`[doc]` {digikit-old} {digitakt-ii-research} {digitakt2-perform}

## Bootstrap/recovery facts
- Startup menu: FUNC at power-on; **SysEx over MIDI DIN only, not USB**. `[doc]` {digikit-old}
- Bootstrap = section 2, updater = section 4; DSP program = ADI boot stream in section 7; patchkit refuses to change sections 2, 4 and 8. Recovery via the bootstrap menu is stated as **not tested on hardware** by digikit's author. `[doc]` {digikit}
- BOOTSTRAP UPGRADE (irreversible) runs only for a strictly higher bootstrap version; bootstrap version 0x0200 in 1.15C. `[doc]` {digikit-old}
- 1.15C address facts: depacker `0x80000432`, CRC-32 routine `0x80001bd0`, bootstrap upgrade gate `0x80001c72`, content checksum `0x40003ca6`, HMAC-SHA256 trailer check `0x80005e2a` (last two not emulated). `[doc]` {digikit-old}
- Install generated builds via Elektron Transfer; the builders never connect to or flash the instrument. `[doc]` {digitakt-ii-research}

## Hardware test evidence for the mods
- Déjà Vu LFOs (digitakt-ii-research): LFO waveforms DV-F (WAVE 7, free-running random loop) and DV-T (WAVE 8, loop resets on track trigger) on all three LFOs; WAVE 0-6 stay on stock paths. Hardware testing "initial only": normal boot, DV-F/DV-T modulation, DV-T retrigger. Save/reload/power-cycle persistence unverified. `[hw]` {digitakt-ii-research}
- digitakt2-perform: `perform-levels` and the key swap work on a unit, the combination only linted/built. `[hw]`/`[emu]` {digitakt2-perform}
- digi-roll writes patterns over SysEx, gated by a per-device OS-build allowlist; hardware-verified 2026-08-09. `[hw]` {digi-roll}

## Gaps
Memory map beyond the numbers above, DSP memory, machine API, parameter-table layout: not collected yet (see `../MINING.md`).
