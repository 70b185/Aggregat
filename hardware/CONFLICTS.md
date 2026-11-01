# Open conflicts and settled corrections - check here before you rely on a number

Sources disagree in places. This page lists every known disagreement with a pointer to the file that holds the details, so that an
agent sees it before building on one side. **Open** means nobody has settled it: measure it yourself or ask. **Settled** means a
later, stronger source decided it; the losing value still circulates in older notes and repos. Last reviewed 2026-11-01.

## Open
| # | Topic | Side A | Side B | Details |
|---|---|---|---|---|
| O1 | Syntakt OS signing | SyntHack OS: 1.41 carries an HMAC-SHA256, with the key derived from the image | digikit finding 70: 1.42 has no HMAC trailer (the last 32 bytes are zero) | [`devices/syntakt.md`](devices/syntakt.md) |
| O2 | Syntakt RAM above the BSS | SY FM4 (1.40A) keeps code at `0x47000000`, "addressed by nothing" | SyntHack (1.41): sample loading overwrites `0x45565490-0x48000000`; mods there crashed | [`devices/syntakt.md`](devices/syntakt.md) |
| O3 | Syntakt CPU #1 load | ~89 % of the audio interrupt at rest (SyntHack, measured with DTIM0) | the render is 85.8k of 166.7k cycles per block (SY FM4) | Different spans of the same interrupt; [`devices/syntakt.md`](devices/syntakt.md) |
| O4 | Syntakt section 8 | "second FPGA?" (SyntHack) | identical to DT2/DN2 section 8 (digikit) | [`devices/syntakt.md`](devices/syntakt.md) |
| O5 | SHARC L1/L2 labels | Digitone 2 modding skill: `0x28xxxxxx` = L2, `0x20000000` = L1 | digikit (with the ADI manuals): `0x28xxxxxx` = L1, `0x20000000` = L2 | The formulas agree; only the names differ. Trust the numbers. [`devices/digitone-2-os111-firmware-map.md`](devices/digitone-2-os111-firmware-map.md) |
| O6 | DN2 1.11 parameter table base | `0x401f7fc8` (skill's map) | `0x401f7fc4` (dnfw memory map) | 4 bytes apart: one counts the record start, the other a field. 1.12: `0x401f83a4`. [`devices/digitone-2-os111-firmware-map.md`](devices/digitone-2-os111-firmware-map.md) |
| O7 | Free SHARC L2 on DT2 1.17 | static: free up to `0x200fa000` (digikit finding 100) | the owner's unit: clicks and delay leaks past `0x200f5a74` | Treat `0x200f5a74` as the practical limit. [`common/dt2-dn2-limits-and-audio-chain.md`](common/dt2-dn2-limits-and-audio-chain.md), [`devices/digitakt-2-sharc-measured.md`](devices/digitakt-2-sharc-measured.md) |
| O8 | DT2/DN2 NOR flash geometry | bootstrap: 512-byte pages, 256 KB erase | in-OS writer: 0x100-byte pages, 0x10000 sectors from `0x80000` | **Likely explained:** the Rytm MKII bootstrap picks page/erase size from the flash vendor's RDID (Spansion 0x200/0x40000; Winbond, Macronix, ISSI, EON 0x100/0x10000), so the geometry differs per unit. Not yet checked in the DT2/DN2 code. [`devices/analog-rytm.md`](devices/analog-rytm.md), [`common/memory-maps.md`](common/memory-maps.md) |
| O9 | Bootstrap write protection | DYB lock on sector `0x40000` (Spansion S25FL command) | the DN2 board photographed carries a Winbond W25Q128JV, on which that lock does nothing | Do not count on hardware protection. [`devices/digitone-2.md`](devices/digitone-2.md) |
| O10 | Ghidra and EMAC | stock Ghidra misdecodes the EMAC line-A words (digikit) | Ghidra knows EMAC since GP-2197 (Heat research) | Use digikit's language spec (`68000:BE:32:ColdfireEMAC`) or check the decode. [`common/toolchain-and-emulators.md`](common/toolchain-and-emulators.md) |
| O11 | digitakt-ii-research licence | MIT (README) | AGPL (altstrument listing) | Check the repo's LICENSE file before you reuse code. `data/projects.yml` |
| O12 | DN2 load model | Digiwerk: load = (1.30 x instructions + 11k) / 666,667, predicted ~74 % | the unit showed ~50-60 % | The model overestimates. [`devices/digitone-2-internals.md`](devices/digitone-2-internals.md) |
| O13 | Free top of the SHARC L1 blocks (DN2) | static: L1 block 3 tail and block 1/2 tails are free (Digiwerk T3.2) | the startup enables the caches there, so `0x39c000-0x39ffff`, `0x2ec000-0x2effff` and `0x31c000-0x31ffff` are cache | The later reading wins; still unverified on silicon. [`devices/digitone-2-internals.md`](devices/digitone-2-internals.md) |

## Settled (the old value is wrong; you may still meet it)
| # | Old claim | Correct | Settled by |
|---|---|---|---|
| S1 | DT2/DN2 SHARC at ~975 MHz, ~650k cycles per block | **1.000 GHz, 666,667 cycles per block** | the owner's idle counter on a DT2; digikit finding 103 on DT2 and DN2 |
| S2 | DT2 DDR is 64 MiB | **128 MiB** | digikit finding 08 (DDRMC values, reset stack); the DN2 board shows 128 MB DDR2 |
| S3 | DN2 CPU is a ColdFire V4e (inherited from the Octatrack) | **MCF5441x (MCF5441SCMJ250)** | dnfw `hardware.md` (board photos) |
| S4 | DN2's SHARC program is not in the update file | **section 7 is its ADI boot stream** | dnfw principle 19 |
| S5 | Reply word 0 misreads the DSP load | **true on DN2, but on DT2 word 0 tracks the idle measure within ~6.5k cycles** | DT2: the owner's measurements; DN2: dn2_firmware_explore |
| S6 | DT2 reply words 1-6 or 677+ can carry mod data | **only 670-676 arrive untouched**; word k is at `base + 4k` | the owner's DT2 probe runs |
| S7 | Missed blocks cause the sticky "bitcrush until reboot" | **not by themselves:** 54 missed blocks without it; stock at 100 % never misses | the owner's DT2 task-map runs |
| S8 | The DN2 has a minimum-version gate on OS upgrade | **only the DT2 has one ("0060")**; DN2 1.11/1.12 accept older signed builds | dnfw `version-gate.md`; digikit finding 75 |
| S9 | L1 block 2 is free because the image leaves it empty | **the PM data cache lives there**; code at the last written word can trap on parity | dnfw `waverider-dsp-silence.md` |
| S10 | The PRM: reading MR keeps / clears the flags; NaN results set AN | **silicon keeps the multiplier flags on an MR read, and leaves AN clear on an invalid float result** | digikit finding 103 |
| S11 | Encodings with a stock precedent are safe | **necessary, not sufficient:** a same-DAG store and SIMD L2 moves hung a real DT2 | digitakt-ii-research PLAITS H-opt1 |

When you find a new disagreement: add a row here and mark the fact `[?]` in the device file. When one is settled, move it to the second table and say what settled it.
