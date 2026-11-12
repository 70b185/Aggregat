# Model:Cycles and Model:Samples - OS 1.13

Coverage: **first profile** (phase 2). Source: 18nelli18/Modded-Cycles (`RECOVERY.md`, `.agents/skills/*/references/os-map.md`
and `free-space.md`, French lab notes `notes/00`-`notes/56`), read 2026-11-02. Facts the project marks `[FAIT]` (measured or read
from the image) are `[doc]` here, hardware rows `[hw]`. Key {modded-cycles}. Projects: [../../catalog/model-cycles.md](../../catalog/model-cycles.md),
[../../catalog/model-samples.md](../../catalog/model-samples.md).

## Platform
- **CPU: ColdFire MCF54415CMJ250** (chip marking read 2026-09-30): MCF5441x, V4 core with EMAC, 250 MHz, **no separate DSP**. All audio is ColdFire assembly. It is the same CPU family as Digitakt mk1, Digitone mk1, Rytm and A4; the Octatrack is the exception. The MCF54418 reference manual applies. `[hw]`
- Audio: 6 tracks, rendered per 32-sample block (0.67 ms) in the audio interrupt. **The stock OS already takes about 77 % of each block, even when stopped**, because all tracks and effects are computed every block. Peaks reach 99 % with heavy added engines. `[hw]`
- **EMAC runs with MACSR = `0xa0` (signed fractional)**, and Unicorn gets it wrong (the same pitfall as Syntakt, Octatrack and DN2). The project ships its own EMAC model. `[doc]`
- Container: ELE3, text header plus section table (16-byte aligned), with a trailer of zero padding, 4 zero bytes and an **HMAC-SHA256** at a 16-byte-aligned offset. The **key is re-derived from the image itself**, so checksums and HMAC can be recomputed. `[doc]`

## Recovery
- The startup menu lives in flash that OS updates never write. **Hold FUNC at power-on, TRIG 4 = OS UPGRADE, "READY TO RECEIVE".** It listens to **MIDI IN only, never USB**.
- **Model:Cycles' MIDI IN is a 3.5 mm TRS jack** (type A and B both work). A mono TS cable does not work. Use the supplied DIN adapter if your interface has DIN.
- Takes 5-10 minutes; the unit restarts by itself.
- If it stays on "RECEIVING..." a packet was lost: power cycle and send slower (Modded Cycles' flasher pace 1.4 by default, 2.0 when it fails). `[hw]`

## OS 1.13 map (starting points; re-read the project's note before hooking)
| What | Address |
|---|---|
| Section 3 base | `0x40000400` |
| SRAM: 6 track render blocks (32 x 32-bit, stride `0x80`) | `0x80000000`; blocks at `0x80001858` |
| Smoothed parameter words (33 x 6 tracks) | `0x8000100c` |
| End limit for the decompressed image + payloads | `0x40200000` |
| Audio interrupt body | `0x40058ca0-0x40059382` |
| Per-block audio function (smoothing, LFO, voice loop) | `0x4005979e` |
| Voice loop of the 6 tracks `(out, params, trig_mask, release_mask)` | `0x400a7d4a` |
| Machine update / render tables | `0x40118628` / `0x40118610` |
| Parameter descriptors, 56 bytes each | `0x4010dce0` |
| LFO update; LFO state `0x40fde838 + 32*track` | `0x40091ab2` |
| Sequencer event builder (one step = 5,400,000 ticks) | `0x400548ce` |
| Tempo pending / applied (1/120 BPM) | `0x40058bb4` / `0x40058b62` |
| Key debounce interrupt (1 kHz); front panel PIT3 at 12 kHz with seven 74HC373 latches | `0x40059e64` |
| DMA timer 0 counter (135.168 MHz) | `0xfc07000c` |
`[doc]` {modded-cycles}

## Free space and payloads
- **Free space is scarce.** The project's main source of code room is **freed sprite masks**:
  - Groups of byte-identical `0xFF` bitmap masks are each referenced by one 32-bit constant. Redirecting that constant to a kept copy renders identically and frees the others.
  - 10 groups, 164 freeable masks, 104-1,024 bytes each.
  - Never write into a kept copy. A registry tool tracks which mod owns which mask.
- Other `0xFF` caves are refused when stock code points into them.
- **Large code is appended to the image and copied to SDRAM at boot** by one shared boot hook (Syntakt engines and MACRO at `0x43000000`, Model-TG at `0x46700000`). A new payload joins the chain rather than adding its own hook. `[doc]`
- Settings that must survive a save go into **proven-unused** bytes of the pattern, project or sound structures (examples: pattern-track byte +512, sound slots 18/27/30/31), declared in a registry so that two mods cannot claim the same bytes. `[doc]`
- **Syntakt engines run on a Model:Cycles:** Modded Cycles reads them from a Syntakt 1.41/1.42 file at build time and places them as a payload. The Syntakt's CPU #2 and the Cycles' CPU are the same core family. `[doc]`
- **The same OS can be installed on a Model:Samples**; the project marks this route experimental. Returning from the Cycles OS on a Samples needs a MIDI interface. `[doc]`

## Load and USB lessons from Supermodel / Modded Cycles (AveyCole, OS 1.13; notes 23 and 35, in French) {supermodel-notes}
- **Every stock voice is rendered every block, playing or not:** about 7,600 instructions each, so six idle voices cost ~45,800 per block. Stock audio takes **~77 % of the CPU at rest**, measured on a unit with a diagnostic load counter (the same figure as in Modded-Cycles' notes). Skipping silent voices cut 77 % of the voice-loop instructions in the emulator; the unit test is still open. `[hw]` / `[emu]`
- **Ported Syntakt engines cost about the same instructions as stock voices (-7 % to +43 %), yet three or more made the unit slow and glitchy.** The likely cause is their much larger memory footprint (cache misses), which the emulator does not time. Another case of rule A34. `[hw]` (symptoms) / `[?]` (cause)
- Units report peaks of 101-108 % of the block budget, with clicks, while the average sits around 73-77 %. **Peaks, not averages, decide.** `[hw]`
- **Stock voices start accumulating into ACC0 without clearing it**, so they rely on an empty accumulator at entry. Leave ACC0 at 0 (as on the Syntakt). `[emu]`
- **USB multitrack glitches** (reported on Reddit after 15-20 minutes):
  - Cause: the OS sends each block to USB right after rendering it, and the 6-channel mod's queue tolerated only 0.2 ms of jitter. With variable engine load (muted tracks, effects off) frames went missing.
  - Fix: send at a fixed time at the start of the next interrupt, align the queue at start-up, and use a 9-slot ring instead of 8. Zero defects in the simulator afterwards.
  - **General rule for USB streaming mods:** decouple the send time from a variable render time. `[emu]` (cause read in the OS, fix simulated)

## A load governor that works, and one that didn't (Supermodel notes 30 and 36, Model:Cycles OS 1.13) {supermodel-notes}
Supermodel's Syntakt-engine bridge measures the audio function every block and fades out a voice when time runs short.
- **Thresholds seen on units:**
  - the sound crackles when a block nears 100 % of its time;
  - a single block at 91 % did *not* crackle;
  - the UI was still fluid at ~86 % sustained load and slows above that.

  `[hw]`
- **Mistake 1: reacting to one heavy block.**
  - Peaks are isolated: a step where several tracks start (the sequencer takes up to ~7 % of a block), or caches the UI flushed between blocks (+4.6 points).
  - By the time the governor sees such a block, it is already over; cutting a voice can't rescue it and is audible.
  - The fix reacts only to a peak that lasts two blocks, or to sustained load. On a unit: "works well", 6 tracks with effects at 89 % peak / 78 % average, no crackle. `[hw]`
- **Mistake 2: an integer moving average that never moves.**
  - `slow += (load - slow) >> 8` with load and average in whole percent rounds every step to 0, or to -1 below the average. The "sustained load" rule therefore never fired on a unit.
  - The emulator test hid it because it pre-set the average.
  - **Keep fixed-point averages in scaled units** (e.g. load << 8), and test them from a cold start. `[emu]`
- **Mistake 3: stealing the quietest voice before the mixer.** That ignores track volume, sends and mute, so a naturally quiet but loud-mixed track (hi-hat, a long tail) always went first, and a muted but still computed track was never preferred. Pick by audibility after the mixer, and prefer muted tracks. `[doc]`
- **EMAC wrappers are not free:** wrapping the reverb kernels in helpers that saved ACC3 and MACSR around every product cost +20-48 % instructions. Save the EMAC state once per block. `[emu]`
- **Finding the worst block on the unit** (note 217, results pending):
  - Seven markers in the audio interrupt read the DMA timer (`0xFC07000C`), and the stages of the worst block are kept for display.
  - One block is 90,112 timer ticks.
  - The same method as digihealth (Digitakt mk1) and dnfw's loadmap (DN2): measure before optimising. `[doc]`


## MIDI map, voice internals and SOLID (model27 notes 65, 71-73, OS 1.13, 2026-11-11) {model27-solid}
- **CC lookup (Model:Cycles):** the CC-to-descriptor table is built at `0x4005a8ce`; CC 16-23 are looked up only in the row of the track's machine, so a shared descriptor on CC 20-23 is never reached, while CC 75-78 reach shared descriptors on all six tracks (`[emu]`, interpreter). CC values are not scaled: the handler `0x4000b568` writes value x 256 and the setter `0x4000b274` clamps to the descriptor's range. Edits send their CC through `0x4000b942`, which reads the stock table at `0x4010dce0`. `[doc]`
- **Stock MIDI map (Model:Cycles):** CCs that reach a track descriptor: 3, 7, 10, 12-19, 65-67, 70, 80, 93 (Solo, by code reading), 102-110; on the FX channel 3, 14, 15, 85-88, 102-110. Stock NRPNs: 1:26-1:30, 1:32-1:39, 3:0, 1:100-1:103. Free next to 74/71: CC 72, 73, 75-79. `[doc]`
- **Model:Samples knob CCs** from its descriptor table at `0x40109048`: Pitch 16, Loop 17, Flip 18, Start 19, Length 20, Cutoff 74, Reso 71, Decay 80. `[doc]` (code reading, not run)
- **No CC goes out** for a knob until TRACK SETUP MOUT is on for that track (with ENCS at I+E); stock behaviour, not a bug. `[hw]`
- **Voice internals (Model:Cycles):** amp envelope `0x400a9252`, decay table `0x4011d84c` (DECAY 127 is about 15 s to -60 dB); the VCA `0x400a9430` clears the level in a trig's block, which clicks on a retrig; PUNCH `0x400a967a` (with PUNCH off a TONE track's output is x1/8); the voice loop `0x400a7d4a` keeps trig and release flags for one block only, runs the EMAC with MACSR `0xa0` and leaves acc0 uncleared; per-track velocity gain at `0x40fe4c90 + 2*track`. `[doc]`
- **Cost per 32-frame block** in Unicorn (instructions, not cycles): TONE 5,291, PERC 6,079, METAL 6,431, KICK 7,429, SNARE 7,158, CHORD 8,300; model27's SOLID (an eight-mode struck-body machine on the EMAC) 3,588 for one ringing voice, 51,589 for six tracks of sustained noise. `[emu]`
- **On a unit (2026-11-11):** SOLID with every other model27 card ran on a Model:Cycles; six SOLID tracks, each with a Track FX, and POTS on the delay send averaged about 60 % CPU with peaks up to 75 %. Track FX answered CC 75/76 and NRPN 1:22/1:23. `[hw]`
- **Where SOLID sits:** at `0x43000000` when it is the only added machine (13,216 bytes of code, 2,832 of variables), or as machine 7 at `0x43009680` beside SAMPLE; this is the same SDRAM payload area the Syntakt engines and MACRO use ([RAM-TENANCY.md](../RAM-TENANCY.md)). It takes 80 bytes of the shared freed mask at `0x4016cae8`, now 1,016 of 1,024 bytes used. `[doc]`

## The +Drive sample store (model27's sample uploader, OS 1.13) {model27-uploader}
- **A sample in use is locked.** Once a track uses a sample, the Model:Cycles refuses to delete it; a restart unlocks it only if no track uses it anymore (tried on a Model:Cycles with one SAMPLE track, 2026-11-10). An uploader should delete what it can and name the locked files rather than stop. `[hw]`
- Uploads become 48 kHz mono samples; Chromium decodes neither AIFF nor 64-bit float WAV, so model27's page converts those itself before handing them on. `[doc]`
