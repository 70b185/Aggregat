# Model:Cycles and Model:Samples - OS 1.13

Coverage: **first profile** (phase 2). Source: 18nelli18/Modded-Cycles (`RECOVERY.md`, `.agents/skills/*/references/os-map.md`
and `free-space.md`, French lab notes `notes/00`-`notes/56`), read 2026-11-02. Facts the project marks `[FAIT]` (measured or read
from the image) are `[doc]` here, hardware rows `[hw]`. Key {modded-cycles}. Projects: [../../devices/model-cycles.md](../../devices/model-cycles.md),
[../../devices/model-samples.md](../../devices/model-samples.md).

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

