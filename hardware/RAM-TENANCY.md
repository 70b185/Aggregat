# RAM tenancy: who uses which memory (Digitone II, Digitakt II, Model:Cycles, Octatrack, Analog Rytm, Syntakt)

Task T23 of the [research map](../research/RESEARCH-MAP.md), first full pass 2026-11-11. Every mod platform puts its code and
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
| `0x402fd000` | `0x466b84d0` | stock | cleared at reset: data, BSS, the 32 MiB heap `0x4464bbf0-0x4664bbf0` (1.11: `0x4464abf0`, S22) | 1.12 | `[doc]` {dn2-cfw-t13} {elekloader-dn2-device} |
| `0x466b8000` | `0x46701340` | stock | DMA section, including the MMC bounce buffer `0x466f1300-0x46701300` that carries every project save and load | 1.11 | `[doc]` {dnfw-mem-regions} {dn2-cfw-prior} |
| `0x466c0000` | `0x46709340` | stock | DMA buffers, including a 64 KB MMC bounce buffer | 1.12 | `[doc]` {dn2-cfw-t13} {elekloader-dn2-profile} |
| `0x47fe0000` | `0x48000000` | stock | stack reserve, 128 KiB below the reset SP `0x48000000` (convention of dnfw and digikit; the stack's real depth is unmeasured) | both | `[doc]` {dnfw-mem-regions} {dn2-cfw-t19} |
| `0x46708000` | `0x46708140` | dnfw | bootscreen (320 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x4670a000` | `0x4670f000` | dnfw | Waverider pages chunk | 1.11 | `[doc]` {dnfw-mem-regions} {dn2mk2-ram} |
| `0x46710000` | `0x46740000` | dnfw | the platform's data window (runtime of data chunks) | 1.11 | `[doc]` {dnfw-mem-regions} {dn2-caves} |
| `0x46740000` | `0x467a0000` | dnfw | lfowaves, envelope (chunks at `0x46740000`, `0x46750000`, `0x46780000`; 11,716 B) | 1.11 | `[doc]` {dnfw-mem-regions} |
| `0x46790000` | `0x467904ac` | dnfw | directjump code (1,196 B; inside the lfowaves span above, whose chunks end lower) | 1.11 | `[doc]` {dnfw-mem-regions} {dnfw-directjump} |
| `0x467e8000` | `0x467e8140` | dnfw | bootscreen (320 B) on 1.12, moved out of 1.12's DMA section | 1.12 | `[doc]` {dnfw-mem-regions} {dnfw-osport} |
| `0x46798000` | ? | dnfw | MODS page: code, then a count and 32 B per row (at most 64 rows); in every dnfw build (inside the lfowaves span above) | 1.11 | `[doc]` {dn2fe-sendloop} |
| `0x405cd8ae` | `0x405cd8c2` | dnfw | mod switches in spare bytes of the stock settings block (reloadconfirm `+0`, arpscale `+1`, directjump `+0x13`; early degreetranspose builds `+2..+0x12`) | 1.11 | `[doc]` {dnfw-directjump} |
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
| `0x402fc7a8` | `0x402fd000` | digikit patchkit | `cf.flash_cave` (2,136 B at the end of the flashed MAIN) | 1.12 | `[doc]` {digikit-1118} |
| `0x402fb7a8` | `0x402fc000` | digikit patchkit | `cf.flash_cave` | 1.11 | `[doc]` {digikit-1118} |

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
| `0x200c4000` | `0x200d9000` | RIFT | fascia.asm (84 KB, FASCIA/ORGAN/SILT; end computed from the size), moved into the PERC code's former room | 1.11 | `[doc]` {dn2-rift-1118} |

## Digitone II SHARC DDR (`digitone-2`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x81000000` | ? | dn2mk2 / RIFT | DSP tables (W5 tables), in a span measured clear of stock's init | 1.11 | `[doc]` {dn2-rift-1118} |
| `0x82200000` | `0x82220000` | dn2mk2 / RIFT | Machinedrum P-I delay lines (128 KB) | 1.11 | `[doc]` {dn2-rift-1118} |
| `0x82400000` | `0x824c0000` | RIFT | SILT waveguide and filament delay lines, 48 KB per track slot x 16 (v0.6) | 1.11 | `[doc]` {dn2-rift-1118} |
| `0x84000000` | ? | dn2mk2 / RIFT | sample pool (directory magic `SMP1`, then frames) | 1.11 | `[doc]` {dn2-rift-1118} |

## Digitakt II flash cave (`digitakt-2`)

From the six-project comparison of 2026-11-02 in [`common/memory-maps.md`](common/memory-maps.md) (task T21). The cave
is the last 2,108 flashed bytes below the reset clear, the most contested 2 KB on the unit: five users fit only
because each checked the bytes the others left.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x403117c4` | `0x40312000` | digikit patchkit | `flash_cave`: the last 2,108 flashed bytes below the clear, home of its reset loader and shared by the rows below | 1.17 | `[hw]` {digikit-f01} |
| `0x403117c4` | `0x40311fb2` | Deja Vu | payload | 1.17 | `[hw]` {dt2-aio-src} |
| `0x40311fb4` | `0x40311fd0` | 70b185 (private) | 28 bytes between Deja Vu's payload and its latches | 1.17 | `[hw]` {own-dt2-notes} |
| `0x40311fe4` | `0x40311ff4` | Deja Vu | run-time latches | 1.17 | `[hw]` {dt2-aio-src} |
| `0x40311c92` | ? | All-in-One (digitakt-ii-research) | its loader, copied within the cave | 1.17 | `[doc]` {dt2-aio-src} |
| `0x40311944` | `0x40311ac4` | dt2-machine-lab | control tables | 1.16 | `[doc]` {dt2-lab-cpu} |
| `0x40311b80` | `0x40312000` | dt2-machine-lab | Plaits rows and code | 1.16 | `[doc]` {dt2-lab-cpu} |

## Digitakt II ColdFire RAM (`digitakt-2`)

The reset copies `0x40312000-0x4031ff60` to SRAM and clears `0x40312000-0x47e28470`; stock's DSP buffers are
`0x47e30000-0x47e7ae80` in the cached view. Same comparison as above.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x40312000` | `0x47e28470` | stock | cleared at reset | 1.17 | `[doc]` {elekloader-dt2-profile} |
| `0x47e30000` | `0x47e7ae80` | stock | DSP buffers (reached through the uncached alias) | 1.17 | `[doc]` {elekloader-dt2-profile} |
| `0x47e8b000` | `0x47fe0000` | digikit | `cf.expansion`: modules (1.33 MiB of unreferenced RAM above the DSP buffers) | both | `[doc]` {digikit-patching} |
| `0x47e8b000` | ? | All-in-One (digitakt-ii-research) | zoom and Musical WAVE code | 1.17 | `[doc]` {dt2-aio-src} |
| `0x47e91000` | ? | All-in-One (digitakt-ii-research) | One-Shot Zoom V11 code | 1.17 | `[doc]` {dt2-aio-src} |
| `0x47e8b000` | `0x47e9b000` | dt2-machine-lab | opt-in 64 KiB | 1.16 | `[doc]` {dt2-lab-cpu} |
| `0x47e8b000` | `0x47fe0000` | dt2-machine-lab (Sketch OS 1.17) | placed by digikit inside `cf.expansion`; exact range not published | 1.17 | `[doc]` {dt2-lab-sketch} |
| `0x47f00000` | `0x47f40000` | elekloader | core-dt2 and every elekloader mod (digitakt2-perform's among them) | 1.17 | `[doc]` {elekloader-dt2-profile} {dt2-perform} |
| `0x47fe0000` | `0x47fe1000` | digikit | keep area: crash and hang records that survive a soft reset | both | `[doc]` {digikit-f46} |
| `0x406658c0` | `0x4066d8c0` | stock | 32 KiB scratch of the +Drive close (firmware-owned) | 1.17 | `[doc]` {digikit-f124} |
| `0x4066d8c0` | `0x406758c0` | stock / digikit | the firmware's 32 KiB close-hash scratch; digikit's core/plusdrive-write borrows it while it holds the filesystem mutex | 1.17 | `[doc]` {digikit-f124} |

## Digitakt II SHARC L2 (`digitakt-2`)

Stock loads up to `0x2001ab7c`; `0x200fa000-0x200fdfff` is referenced by stock.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x2001ab7c` | `0x200fa000` | digikit | L2 offered to modules | both | `[doc]` {digikit-f100} |
| `0x20020000` | `0x200fa000` | 70b185 (private) | linked range; data kept at or below `0x200f5a74`, because going past it gave clicks and leaks into the delay on a unit | 1.17 | `[hw]` {own-dt2-notes} |
| `0x20080000` | ? | dt2-machine-lab | Plaits code | 1.16 | `[doc]` {dt2-lab-capicola} |
| `0x200a0000` | ? | dt2-machine-lab | Capicola cold code | 1.16 | `[doc]` {dt2-lab-capicola} |
| `0x200e0000` | `0x200e8000` | dt2-machine-lab | voice state | 1.16 | `[doc]` {dt2-lab-capicola} |

## Model:Cycles SDRAM payload area (`model-cycles`)

The area where Model:Cycles mods place added machines; the Syntakt engine ports and MACRO use the same area (see [`devices/model-cycles-samples.md`](devices/model-cycles-samples.md)).

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x43000000` | `0x43003eb0` | model27 | SOLID machine when it is the only added machine (13,216 B code + 2,832 B variables; end is our sum; release 0.64 grows SOLID's image part to 20,512 B, so the end moves) | 1.13 | `[doc]` {model27-solid} {model27-perform} |
| `0x43009680` | ? | model27 | SOLID as machine 7, beside SAMPLE | 1.13 | `[doc]` {model27-solid} |
| `0x43000000` | ? | model27 | CHIPS code when it is the only added machine (image payload 15,776 B, code 7,846 B, tables about 2 KB) | 1.13 | `[doc]` {model27-chips} |
| `0x43036000` | `0x430363e0` | model27 | CHIPS variables when it is the only added machine (992 B for six voices; end is our sum) | 1.13 | `[doc]` {model27-chips} |
| `0x43000000` | `0x43002162` | model27 | MAXSAW code when it is the only added machine (8,546 B in release 0.69; end is our sum; image payload 16,468 B) | 1.13 | `[doc]` {model27-maxsaw} |
| `0x43000000` | `0x43033000` | model27 | code window for added machines and the builder's parts (204 KiB, `gs.STUBS`); the registrar's part follows | 1.13 | `[doc]` {model27-1118} |
| `0x43000000` | `0x43004aea` | model27 | TERRA code when it is the only added machine (19,178 B) | 1.13 | `[doc]` {model27-1118} |
| `0x43036000` | `0x43042780` | model27 | TERRA far table (50,688 B of Plaits wavetable data) and variables, 51,072 B, when it is the only added machine | 1.13 | `[emu]` {model27-1118} |
| `0x43000000` | `0x43176c58` | model27 | the whole payload with every offered card and TERRA (release 0.72) | 1.13 | `[doc]` {model27-1118} |
| `0x43400000` | ? | model27 | CHORD Tables' RAM claim | 1.13 | `[doc]` {model27-1118} |
| `0x43800000` | ? | model27 | SAMPLE's (Cycles One-Shot) sample pool | 1.13 | `[doc]` {model27-1118} |
| `0x43036000` | `0x43036344` | model27 | MAXSAW variables when it is the only added machine (836 B, among them 92 B of state a track and a 128-byte shared buffer; end is our sum) | 1.13 | `[doc]` {model27-maxsaw} |

## Octatrack DSP X memory (`octatrack`)

DSP56300 X-memory words, written `$xxxx` in the projects' notes.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x2840` | `0x2841` | octabam / Modwerk | core-1 load counter | 1.40C | `[doc]` {modwerk-analogbd} |
| `0x2841` | `0x3201` | Modwerk (Analog BD 0.1.7) | 909 tables and voices | 1.40C | `[doc]` {modwerk-analogbd} |
| `0x2900` | `0x3d55` | octabam (DLCOPY) | demand-loader staging; doorbell word at `0x2900` = `0xa55a` (overlaps Analog BD's range above in a different build) | 1.40C | `[doc]` {octabam-1115} |
| `0x3dc0` | `0x3e3f` | octabam (DLCOPY) | guard state words and base cells | 1.40C | `[doc]` {octabam-1115} |
| `0x3f00` | `0x3f4f` | octabam (DLCOPY) | stub tables | 1.40C | `[doc]` {octabam-1115} |
| `0x3fd0` | `0x3fea` | octabam (DLCOPY) | reverb trampoline words, guard scratch, the copier's saved b | 1.40C | `[doc]` {octabam-1115} |
| `0x28f0` | `0x28f4` | elekloader (dspload-ot 0.2) | core 1's kept registers for the copier | 1.40C | `[emu]` {elekloader-1117} |
| `0x2900` | `0x2db2` | elekloader (dspload-ot 0.2) | core 1's staging for run-time DSP code; doorbell `0xa55a` at `0x2900` (the same layout as octabam's DLCOPY, so the two cannot share a build) | 1.40C | `[emu]` {elekloader-1117} |
| `0x33da3` | `0x34000` | elekloader (dspload-ot 0.2; TELOS card mods) | shared window (P/X/Y aliased): four slot pairs at `0x33da3`, code gap `P:0x33dab..0x33fff` (597 words); a reverb past its default knobs can reach it | 1.40C | `[emu]` {elekloader-1117} |

## Octatrack ColdFire DDR (`octatrack`)

The sample arena (6,144-byte pages, 14,602 of them) starts at `0x40a955e0`; DRAM units take its first pages, and the
MEMORY page does not show the loss.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x40a955e0` | `0x40aa5de0` | KYOTI | KYOTI V1.8: RELOAD_FROM_PROJECT and DIRECT JUMP DRAM units, 11 arena pages (end is our sum) | 1.40C | `[doc]` {kyoti-1117} |
| `0x40a955e0` | `0x41498de0` | KYOTI | KYOTI V1.8C and the CLYPS image: Clyps and DIRECT JUMP code (32,496 B) plus Clyps' buffers (every bank's originals, temp saves, Part shadow), 1,709 arena pages (end is our sum) | 1.40C | `[doc]` {kyoti-1117} {kyoti-clyps-scope} |

## Octatrack battery RAM (`octatrack`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x100ff800` | `0x100ff900` | Modwerk | crash record (end: where the next record starts) | 1.40C | `[doc]` {modwerk-ot-driving} |
| `0x100ff900` | `0x100ffb30` | Modwerk | DSP stall record | 1.40C | `[doc]` {modwerk-ot-driving} |
| `0x100ffb30` | ? | Modwerk | timings of the 128 frames before a stall | 1.40C | `[doc]` {modwerk-ot-driving} |
| `0x100f85a0` | ? | Modwerk Kits / octabam KITS | Kits' battery record (`KCS1`, RESID); same address in octabam | 1.40C | `[hw]` {modwerk-ot-kits} |
| `0x100f9800` | `0x100fbf00` | Modwerk MIDI Scenes | current bank's packed MIDI scene locks (`SCS2`, 9,984 B) | 1.40C | `[hw]` {modwerk-ot-midiscenes} |
| `0x100f8600` | `0x100fbdc0` | octabam PLOCKS P2 | current bank's page-2 locks (`P2NV`, 4,752 locks, 14,272 B; was to `0x100fbdf0` before 2026-11-17) | 1.40C | `[doc]` {octabam-1118} |
| `0x100fbdc0` | `0x100fbdf0` | octabam PATTERN MUTE | current bank's PATTERN-layer mutes (`PMCS`, 48 B, since 2026-11-17) | 1.40C | `[doc]` {octabam-pmute-1118} |
| `0x100ffe00` | `0x100fff00` | octabam KITS | ASSIGN (256 B); stock references nothing in `0x100f859c..0x100fff00` per octabam | 1.40C | `[doc]` {octabam-1118} |
| `0x100b14dd` | `0x100b14de` | octabam PATTERN MUTE | bit 0 = layer (mirror of `0x80000011`, unused by stock) | 1.40C | `[emu]` {octabam-pmute-1118} |
| `0x100fbdf0` | `0x100ffe00` | octabam MIDI SCENES | power-cycle copy of the MIDI scene locks (16,400 B; per Modwerk's notes, under Modwerk's own records) | 1.40C | `[doc]` {modwerk-ot-midiscenes} |
| `0x100fbf00` | ? | Modwerk Kits | Kits' pattern assignments (ASSIGN), moved from octabam's `0x100ffe00` | 1.40C | `[doc]` {modwerk-ot-kits} |
| `0x100ffd40` | ? | Modwerk base 0.7.3+ | machine map (each machine's module and name); covers octabam KITS' ASSIGN at `0x100ffe00` | 1.40C | `[doc]` {modwerk-1117} |

## Analog Four MKII DDR (`analog-four-keys`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x45650000` | `0x47c00000` | elekloader (core-a4mk2 0.6+) | mods' area: flashed mods' code and `.bss`, then the +Drive area from the build's RAM end (4 KB aligned) to the top; no `resources.regions` for +Drive mods | 1.56 | `[doc]` {elekloader-core-a4} {elekloader-1118} |
| `0x47be0000` | `0x47c00000` | elekloader (core-a4 0.5 and older) | the old 128 KB mods' area | 1.56 | `[doc]` {elekloader-core-a4} |

## Analog Rytm MKI DDR (`analog-rytm`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x47be0000` | `0x47c00000` | elekloader | mods' area reserved by the MKI profile; no core uses it yet (a canary read back unchanged on a unit) | 1.74 | `[hw]` {elekloader-ar1} |
| `0x47b00000` | `0x47f00000` | Modwerk (MW02 canary) | test fill address ^ 0xC0DEF00D, never written by stock with sample memory full, locks, play and save | 1.74 | `[hw]` {modwerk-rytm-1118} |
| `0x47be0000` | `0x47c00000` | Modwerk (MKI base, core-ar2 0.7 at MKI addresses) | module area, the same range as elekloader's MKI profile | 1.74 | `[hw]` {modwerk-rytm-1118} |

## Analog Rytm MKII DDR and SRAM (`analog-rytm`)

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x47be0000` | `0x47c00000` | elekloader (core-ar2) / Modwerk / Sidecar | the shared 128 KiB mod area (Sidecar's rui_key at `0x47bedd14` lies inside) | 1.74 | `[hw]` {modwerk-rytm-link} {sidecar-mods-1116} |
| `0x47bfffbc` | `0x47c00000` | Modwerk development link | RAM-boot diagnostics in the top 68 B of the mod area (the top 8 B are reset marks); development bases built before 2026-11-17 only (later bases use `0x47feffbc`, {modwerk-rytm-1118}); nothing checks that a set leaves these bytes free | 1.74 | `[hw]` {modwerk-rytm-link} |
| `0x403c8b00` | `0x403c8b20` | Modwerk development link | RAM-boot mailbox written over the header of stock's upload buffer just before the software reset (transient) | 1.74 | `[hw]` {modwerk-rytm-link} |
| `0x8000f774` | ? | Sidecar 0.5.0 | adds offsets to the effective sound words (index 26 + 42 x track + word) every audio block; another mod that writes these words after stage A collides | 1.73/1.74 | `[emu]` {sidecar-mods-1116} |
| `0x479372e0` | `0x47b47480` | stock | end of heap allocations, 352 B bookkeeping, fixed buffers (mostly a factory test console) to `0x47b47440`, a 16-word DMA list | 1.74 | `[doc]` {modwerk-rytm-1118} |
| `0x47b50000` | `0x47c00000` | Modwerk (own linker) | 704 KiB module area for sets over 128 KiB (includes the shared 128 KiB area) | 1.74 | `[hw]` {modwerk-rytm-1118} |
| `0x47c00000` | `0x47f00000` | Modwerk (own linker, no send-bus base) | extends the 3.7 MiB area; the send bus's work area otherwise ends at `0x47c00000` | 1.74 | `[hw]` {modwerk-rytm-1118} |
| `0x47feffbc` | `0x47ff0000` | Modwerk development link | RAM-boot diagnostics (68 B) moved here from the top of the mod area; `ident` names the place | 1.74 | `[doc]` {modwerk-rytm-1118} |

## Syntakt MAIN DDR (`syntakt`)

OS 1.42, from digikit's static reading (2026-11-18). The reset clears `0x4033a000-0x45566490`; nothing above it.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x444e48c0` | `0x454e48c0` | stock | OS heap (buddy allocator, 16 MiB) | 1.42 | `[doc]` {digikit-st-1118} |
| `0x4584f2c0` | `0x4784f2c0` | stock | sample stage buffer before the upload to the voice CPU (extent inferred) | 1.42 | `[?]` {digikit-st-1118} |
| `0x4784f2c1` | `0x478af2cb` | stock | section-7 transmit buffer (the voice CPU's program) | 1.42 | `[doc]` {digikit-st-1118} |
| `0x4584f2c5` | `0x4759b3c5` | stock | sample blob of the 64 stock slots, built at boot (64 frame counts + PCM16; 29.30 MiB when every slot holds 5 s; uncached alias `0x4d84f2c5`); not built by Synfact core 2.0.1 | 1.42 | `[emu]` {synfact-1118} |
| `0x46000000` | `0x46010000` | Synfact core-st | 64 KiB resident core; safe only with core 2.0.1, which stops stock building the blob above | 1.42 | `[hw]` {synfact-1118} |
| `0x478c0000` | `0x47bf0000` | digikit | `cf.expansion`: runtime object (981,036 B used); emulator only, no canary run | 1.42 | `[emu]` {digikit-st-1118} |
| `0x47bf0000` | `0x47bf1000` | digikit | keep area (crash records across a reset) | 1.42 | `[doc]` {digikit-st-1118} |
| `0x47c00000` | `0x48000000` | stock | 4 MiB ring (through `0x4fc00000`), cleared at boot, written every frame | 1.42 | `[doc]` {digikit-st-1118} |
| `0x47fe0000` | `0x48000000` | Modwerk | freed by lowering the stack 128 KB; overlaps the ring (O35) | 1.42 | `[hw]` {modwerk-st-goal} |
| `0x40339730` | `0x4033a000` | digikit | loader in the flash cave after the init table (56 of 2,256 B) | 1.42 | `[emu]` {digikit-st-1118} |

## Syntakt voice CPU DDR (`syntakt`)

The second ColdFire's own RAM (section 7), a separate address space from MAIN's.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x4004f750` | `0x4404f750` | stock | sample pool (64 MB), filled at boot from MAIN's sender | 1.42 | `[doc]` {syncrackd-mm} {synfact-1118} |
| `0x42100750` | `0x42101750` | Synfact core-st | service code and 128 PCM descriptors (inside the stock pool's span) | 1.42 | `[doc]` {synfact-1118} |
| `0x42101750` | `0x4404f750` | Synfact core-st | HZFS long-sample PCM, about 31.30 MiB; the SMZ machine region ends below at `0x42100000` | 1.42 | `[doc]` {synfact-1118} |

## Syntakt MAIN SRAM (`syntakt`)

Synfact's optional mods share two windows of CPU #1's internal SRAM. The source says exclusive use has not been proven
on hardware; samplers checks its code there every 60 UI ticks and falls back to DDR on a mismatch.

| start | end | user | use | OS | evidence |
|---|---|---|---|---|---|
| `0x800077c0` | `0x80008000` | Synfact | Chorus window; when Chorus is absent and the window is zero, samplers' stereo code takes all 2,112 bytes | 1.41 | `[doc]` {synfact-main-opt} |
| `0x8000fc20` | `0x8000ff94` | Synfact | Chorus window; without Chorus the samplers' stereo mix kernel uses 790 of its 884 bytes | 1.41 | `[doc]` {synfact-main-opt} |
