# RAM tenancy: who uses which memory (Digitone II, Digitakt II)

Task T23 of the [research map](../RESEARCH-MAP.md), first full pass 2026-11-11. Every mod platform puts its code and
data in RAM that stock leaves alone, and each picked its own addresses. This page lists every range we could find, so a
new project can pick free space and two mods can be checked for a clash before anyone flashes them. Read with rule area
G8 (mods that coexist) and [`common/memory-maps.md`](common/memory-maps.md), which explains how the ranges were found.

**Declare yours.** If you ship a mod or a platform for these units, open a pull request that adds your ranges here (or
a [test result](https://github.com/70b185/Aggregat/issues/new?template=test-result.yml) issue). The table is
machine-readable: the MCP server's `check_address` and the website's Addresses tab read it, and
[ADDRESS-MAP.md](ADDRESS-MAP.md) lists the overlaps it finds.

How to read the tables
- One row per range: start (inclusive), end (exclusive), user, what it holds, OS version, evidence and source.
- `end` is `?` where the project names a start but no size; overlap checks treat such a row as a single address.
- **envelope** means the project uses several chunks inside the range and publishes no per-chunk size; the envelope
  is the smallest range we can vouch for from the published addresses, not a claim that every byte is used.
- Addresses are the cached view (`0x4.......`). Stock reaches some buffers through the uncached alias
  (`0x4e......` = `0x46......` + `0x08000000`); both name the same bytes.
- **OS matters.** Two rows overlap only on the same OS version: a 1.11 mod and a 1.12 mod cannot run together anyway
  ([rule A10](AGENT-RULES.md)). `both` means the row holds on 1.11 and 1.12 (DN2) or 1.16 and 1.17 (DT2).

## Digitone II ColdFire DDR (`digitone-2`)

The reset clears `0x402fd000-0x466b84d0` (1.12; 1.11: to `0x466b74d0`). Everything above that is outside stock's
static map; it is where every platform below lives. Stock's DMA buffers sit just above the clear and must be avoided.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x402fd000` | `0x466b84d0` | stock | cleared at reset: data, BSS, the 32 MiB heap `0x4464abf0-0x4664abf0` | 1.12 | `[doc]` {dn2-cfw-t13} {elekloader-dn2-device} |
| `0x466b8000` | `0x46701340` | stock | DMA section, including the MMC bounce buffer `0x466f1300-0x46701300` that carries every project save and load | 1.11 | `[doc]` {dnfw-mem-regions} {dn2-cfw-prior} |
| `0x466c0000` | `0x46709340` | stock | DMA buffers, including a 64 KB MMC bounce buffer | 1.12 | `[doc]` {dn2-cfw-t13} {elekloader-dn2-profile} |
| `0x47fe0000` | `0x48000000` | stock | stack reserve, 128 KiB below the reset SP `0x48000000` (convention of dnfw and digikit; the stack's real depth is unmeasured) | both | `[doc]` {dnfw-mem-regions} {dn2-cfw-t19} |
| `0x46708000` | `0x46708140` | dnfw | bootscreen (320 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x4670a000` | `0x4670f000` | dnfw | Waverider pages chunk | 1.11 | `[doc]` {dnfw-mem-regions} {dn2mk2-ram} |
| `0x46710000` | `0x46740000` | dnfw | the platform's data window (runtime of data chunks) | 1.11 | `[doc]` {dnfw-mem-regions} {dn2-caves} |
| `0x46740000` | `0x467a0000` | dnfw | lfowaves, envelope (chunks at `0x46740000`, `0x46750000`, `0x46780000`; 11,716 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467a0000` | `0x467a0910` | dnfw | arpmodes (2,320 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467a8000` | `0x467a8688` | dnfw | arpscale (1,672 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467b0000` | `0x467b0104` | dnfw | lfolength (260 B; at `0x467f8000` until 2026-10-15) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467b8000` | `0x467b8684` | dnfw | degreetranspose (1,668 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467c0000` | `0x467d0000` | dnfw | arpplocks, envelope (chunks at `0x467c0000`, `0x467c4900`, `0x467c8000`; 20,936 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467d0000` | `0x467d0250` | dnfw | midiarp (592 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467d8000` | `0x467d8144` | dnfw | layermidi (324 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467e0000` | `0x467e04b8` | dnfw | reloadconfirm (1,208 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x467f0000` | ? | dnfw | Waverider, second chunk | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x46800000` | `0x46900000` | dnfw | LFO4 code and extension table, envelope (`0x46800000` to `0x468fffcc`; 30,724 B); the C code of every dnfw mod links here | 1.11 | `[doc]` {dnfw-mem-regions} {dn2-caves} |
| `0x46a00000` | `0x46a70000` | dnfw | Waverider, envelope (chunks at `0x46a00000`, `0x46a60000`; with the two chunks above 458,144 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x46e00000` | ? | dnfw | the platform, second chunk | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x46f00000` | `0x46f00900` | dnfw | usbprobe scratch: request, reply, packed reply (2,304 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x46700000` | `0x46702a00` | dn2mk2 | LFO4 state LIVE, SECOND, BACKUP (3 x 2,560 B), as declared in its `lfo4.py`. dn2mk2 forked dnfw on 2026-10-06; dnfw moved this state into stock's heap on 2026-10-11 because the range is inside stock's bounce buffer and corrupted saved projects. dn2mk2's README lists no LFO4, so whether a shipped build contains it is not stated | 1.11 | `[?]` {dn2mk2-ram} {dnfw-mem-regions} |
| `0x4670c000` | `0x4670f000` | dn2mk2 | Waverider pages assembly | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x4670f800` | `0x46710000` | dn2mk2 | Waverider ColdFire chunk | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46710000` | ? | dn2mk2 | the platform runtime (data chunks run here, as in dnfw) | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46800000` | ? | dn2mk2 | compiled C (the `CODE` chunk the loader copies at boot) | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46ac0000` | `0x46af0000` | dn2mk2 | Waverider renderer C (span `0x30000` since v0.41) | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46af0000` | `0x46af8000` | dn2mk2 | Machinedrum screen graphics (6.8 KB) | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46b00000` | `0x47000000` | dn2mk2 | sampler: the ColdFire's 5 MB mirror of the sample pool, fed to the DSP | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x47000000` | ? | dn2mk2 | sampler machine tables (a `CODE` chunk: magic, length, data) | 1.11 | `[doc]` {dn2mk2-ram} |
| `0x46800000` | ? | cfmod / cfkit | code (default link address) | 1.11 | `[doc]` {dn2-skill-scripts} |
| `0x46a00000` | ? | cfmod / cfkit | stacks, rings and scratch | 1.11 | `[doc]` {dn2-skill-scripts} |
| `0x46800000` | `0x47ad0000` | armio T1E2 / R012 / R022 | the transplanted Digitakt II runtime, envelope: graft base `0x46800000`, private state `0x46816f8c-0x47a19ca0` (BSS flag at `0x46b9608c`), extension `0x47a36000`, scratch `0x47a58000`, startup status `0x47a9cd7c`, R022's autosave helper at `0x47acee98`; the end moves with each build | 1.11 | `[doc]` {armio-ram} {armio-r012} |
| `0x46800000` | `0x47e00000` | dn2-cfw (Digiwerk) | mod area | 1.12 | `[doc]` {dn2-cfw-t13} {dn2-cfw-t19} |
| `0x47d00000` | `0x47d05a00` | dn2-cfw (Digiwerk) | grown parameter table, 384 rows of 60 B (inside the mod area) | 1.12 | `[hw]` {dn2-cfw-param-table} |
| `0x47e00000` | `0x47f00000` | dn2-cfw (Digiwerk) | core run image (the core's boot copies it here and zeroes `.bss`) | 1.12 | `[doc]` {dn2-cfw-t13} |
| `0x47f00000` | `0x47f40000` | elekloader | core-dn2 and every elekloader mod (256 KB, the same area as on the Digitakt II) | 1.12 | `[doc]` {elekloader-dn2-device} {elekloader-dn2-profile} |

What this shows (2026-11-11)
- **On 1.11, `0x46800000` has four claimants**: dnfw (and its fork dn2mk2), cfmod, and armio's transplanted runtime,
  which spans most of the space up to `0x47ad0000`. armio's builds therefore cannot be combined with any dnfw, dn2mk2
  or cfmod mod without moving one of them. `[doc]`
- **On 1.12 the two platforms are disjoint**: dn2-cfw ends at `0x47f00000`, where elekloader starts. Nothing in the
  sources says whether their boot hooks chain. `[doc]`
- **Open: dn2mk2's LFO4 state at `0x46700000`.** If any dn2mk2 build includes the LFO4 code it inherited, it would
  write into stock's bounce buffer, which is what corrupted projects saved on dnfw's LFO4 units until 2026-10-11 (see
  [`common/memory-maps.md`](common/memory-maps.md)). dn2mk2's own docs do not say whether LFO4 ships; its maintainer
  could settle it in one line. `[?]`
- Free on both OS versions, as far as these tables go: `0x47e00000-0x47f00000` on 1.11 (above armio's envelope; check
  stock's use first, rule A43), and nothing large on 1.12 outside the two platforms' own areas.

## Digitone II SHARC L2 (`digitone-2`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x20090000` | `0x20098000` | elekloader | SHARC mod area (32 KiB) | 1.12 | `[doc]` {elekloader-dn2-profile} |
| `0x200e9000` | `0x200fa000` | dn2mk2 | unused in dn2mk2's image (68 KB), listed as room | 1.11 | `[doc]` {dn2mk2-fascia-plan} |

## Digitakt II ColdFire RAM and flash (`digitakt-2`)

From the six-project comparison of 2026-11-02 in [`common/memory-maps.md`](common/memory-maps.md) (task T21). The reset
copies `0x40312000-0x4031ff60` to SRAM and clears `0x40312000-0x47e28470`; stock's DSP buffers are `0x47e30000-0x47e7ae80`
in the cached view.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x40312000` | `0x47e28470` | stock | cleared at reset | 1.17 | `[doc]` {elekloader-dt2-profile} |
| `0x47e30000` | `0x47e7ae80` | stock | DSP buffers (reached through the uncached alias) | 1.17 | `[doc]` {elekloader-dt2-profile} |
| `0x403117c4` | `0x40312000` | digikit patchkit | `flash_cave`: the last 2,108 flashed bytes below the clear, home of its reset loader and shared by the rows below | 1.17 | `[hw]` {digikit-f01} |
| `0x403117c4` | `0x40311fb2` | Deja Vu | payload | 1.17 | `[hw]` {dt2-aio-src} |
| `0x40311fb4` | `0x40311fd0` | 70b185 (private) | 28 bytes between Deja Vu's payload and its latches | 1.17 | `[hw]` {own-dt2-notes} |
| `0x40311fe4` | `0x40311ff4` | Deja Vu | run-time latches | 1.17 | `[hw]` {dt2-aio-src} |
| `0x40311c92` | ? | All-in-One (digitakt-ii-research) | its loader, copied within the cave | 1.17 | `[doc]` {dt2-aio-src} |
| `0x40311944` | `0x40311ac4` | dt2-machine-lab | control tables | 1.16 | `[doc]` {dt2-lab-cpu} |
| `0x40311b80` | `0x40312000` | dt2-machine-lab | Plaits rows and code | 1.16 | `[doc]` {dt2-lab-cpu} |
| `0x47e8b000` | `0x47fe0000` | digikit | `cf.expansion`: modules (1.33 MiB of unreferenced RAM above the DSP buffers) | both | `[doc]` {digikit-patching} |
| `0x47e8b000` | ? | All-in-One (digitakt-ii-research) | zoom and Musical WAVE code | 1.17 | `[doc]` {dt2-aio-src} |
| `0x47e91000` | ? | All-in-One (digitakt-ii-research) | One-Shot Zoom V11 code | 1.17 | `[doc]` {dt2-aio-src} |
| `0x47e8b000` | `0x47e9b000` | dt2-machine-lab | opt-in 64 KiB | 1.16 | `[doc]` {dt2-lab-cpu} |
| `0x47f00000` | `0x47f40000` | elekloader | core-dt2 and every elekloader mod (digitakt2-perform's among them) | 1.17 | `[doc]` {elekloader-dt2-profile} {dt2-perform} |
| `0x47fe0000` | `0x47fe1000` | digikit | keep area: crash and hang records that survive a soft reset | both | `[doc]` {digikit-f46} |

## Digitakt II SHARC L2 (`digitakt-2`)

Stock loads up to `0x2001ab7c`; `0x200fa000-0x200fdfff` is referenced by stock.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x2001ab7c` | `0x200fa000` | digikit | L2 offered to modules | both | `[doc]` {digikit-f100} |
| `0x20020000` | `0x200fa000` | 70b185 (private) | linked range; data kept at or below `0x200f5a74`, because going past it gave clicks and leaks into the delay on a unit | 1.17 | `[hw]` {own-dt2-notes} |
| `0x20080000` | ? | dt2-machine-lab | Plaits code | 1.16 | `[doc]` {dt2-lab-capicola} |
| `0x200a0000` | ? | dt2-machine-lab | Capicola cold code | 1.16 | `[doc]` {dt2-lab-capicola} |
| `0x200e0000` | `0x200e8000` | dt2-machine-lab | voice state | 1.16 | `[doc]` {dt2-lab-capicola} |
