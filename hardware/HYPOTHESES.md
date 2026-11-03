# Inferred, not yet shown: a test list for four units

Each entry is a conclusion drawn by comparing projects. It follows from what is documented, but nobody has shown it on the device it is about. The units at hand for testing: **Digitakt II, Digitakt (mk1), Digitone II, Analog Heat +FX**.

How to use this page: pick an entry, run its test, and move the result into the device page with the evidence tag `[hw]`; then delete the entry here (or move it to CONFLICTS if the unit disagrees). Collected 2026-11-03.

**Kinds of test**
- **stock**: a stock OS and normal use, or a read-only tool on the computer. No flashing.
- **probe**: needs a read-only probe build (a USB PEEK, as in digikit, dnfw or 70b185's DT2 probe). The probe build itself is a modified OS, so it belongs in the firmware chat.
- **build**: needs a test build that does something on purpose.

## 1. Stock tests (no flashing)

| # | Inference | From | Unit | Test |
|---|---|---|---|---|
| H1 | Each unit has three different ids: SysEx device byte, product id, Overbridge USB id. Expected: DT2 `0x14` / `0x2A` / USB `0x0B2B`; DT1 `0x0A` / `0x0C` / `0x0B2C`; DN2 `0x15` / `0x2B` / `0x0B34`; Heat +FX `0x13` / `0x20` / `0x0B53`. The USB id's low byte changes with the USB mode (`0x012B` MIDI, `0x102B` audio/MIDI on the DT2). | Elektroid, Overwitch, digikit f42, digi-roll ([sysex-and-midi.md](common/sysex-and-midi.md)) | all four | Read the USB ids in each USB mode (`lsusb` on Linux, System Information on a Mac, Device Manager on Windows). Read the product id with Elektroid's device info. |
| H2 | Unsaved edits survive a power cycle on the DT2 and the DT1 as on the DN2, because the stock edit writer stores each edit in the sound record at once. | dnfw LFO4 (DN2, E2) | DT2, DT1 | On a throwaway project, turn a filter knob, do not save, power-cycle. Is the value still there? Also try a parameter lock. |
| H3 | A received pattern dump lands in the slot armed on the unit, not in the slot its index byte names (shown on the DN2 by syxgrid). | syxgrid, digi-roll | DT2, DT1 | On a throwaway project, send a pattern dump with index A05 while A02 is armed, using Elektroid or digi-roll. Where does it land? |
| H4 | The DT1 recorder holds at most 33.0 s (1,584,000 frames at 48 kHz, mono). | digigrain's recorder skill (static) | DT1 | Record with free length until it stops; time it. |
| H5 | Overbridge rejects a modified OS whose container version field differs from stock (shown on the DN2, Digiwerk OB01). | Digiwerk OB01 | DT2, Heat +FX | No new flash needed if you already have builds: does Overbridge connect to a build whose version field was changed, and to one where it was kept? |
| H18 | The Heat +FX answers the screen request (RPC framing `F0 00 20 3C 10 00`), as the Heat MKII does, so its screen can be mirrored and read without a mod. | Elek View (DT2, M:C, Heat MKII) | Heat +FX, DT1, DN2 | Open Elek View (bluesgl.github.io/Elek_View) with nothing else on the MIDI port, select the unit, Start. |

## 2. Probe tests (read-only builds)

| # | Inference | From | Unit | Test |
|---|---|---|---|---|
| H6 | The DT2's SHARC DDR above the sample pool window (`0x9d22b9c8` up to `0xa0000000`, about 46 MB) is never written by stock, as the DN2's tail `0x80531000-0xa0000000` is not. | dnfw dn2-ddr method; dt2-machine-lab pool window | DT2 | dnfw's method: fill the range with a pattern at boot, then scan it during heavy playback, pattern and kit changes, FX extremes, sample loads and a save. Expect a reserved top part for Capicola builds only. |
| H7 | The DT2's ColdFire runs the same FreeRTOS layout as the DN2: higher priority numbers run first, prio 0 never runs, prio 1 is the idle loop; the main task's stack is barely used. | dnfw coldfire-tasks (DN2) | DT2 | With the USB probe: find the ready table and the running-task pointer, sample them 60 times. |
| H8 | The DN2's digikit flash cave `0x402fb7a8` (2,136 B on 1.11) keeps its bytes through a cold boot, as the DT2's `0x403117c4` does. | digikit f01 (emulator canary) | DN2 | A canary in the cave, read back after a cold boot and after playback. Combine with H9. |
| H9 | The DT2 flash cave `0x403117c4-0x40312000` is safe on a stock image; the freeze report (O18) came from something else in that build. | Deja Vu, 70b185's builds vs dt2-capicola's comment | DT2 | A stock image plus a canary in the cave, read back after a cold start after a long power-off (A40). |
| H10 | DN2 L2 `0x200918c0-0x200c2000` is not written by stock in normal use (O19). | DN2 skill, elekloader vs dnfw, Digiwerk | DN2 | A canary or a write watch over the range during playback, pattern changes and a save (T24). |
| H11 | DN2 RAM `0x46700000-0x46701300` is written by stock only when a +Drive transfer is over 60,672 bytes (O17). | dnfw, Digiwerk | DN2 | A canary at `0x46700000`, read back after loading a large sample or project from +Drive. |
| H12 | DT2 reply words that a hook writes mid-block are lost on the DN2 too (on the DT2 3,995 of 4,000 arrived as 0, because stock rebuilds the record before the DMA). | 70b185 (DT2) | DN2 | Write a counter word from a hook and from the block tail; count arrivals on the ColdFire side. |

## 3. Build tests (something done on purpose)

| # | Inference | From | Unit | Test |
|---|---|---|---|---|
| H13 | SIMD loads or stores into L2 byte space hang the DN2's DSP as they hang the DT2's (same core, same IMASK). | DT2 Plaits port, digikit f103 | DN2 | A one-variable probe image with one SIMD L2 access behind a key press; recovery by power cycle. |
| H14 | The SHARC's IIR0/FIR0 accelerators compute on the DT2 exactly as measured on the DN2 (output from stored word 5, FIR sums in pairs, INIDX/OUTIDX written the other way round). | dnfw accelprobe (DN2) | DT2 | Port the accelprobe image to the DT2 and compare the 76 result words. |
| H15 | On the DN2, a single late DSP block is a one-block dropout that recovers, as on the DT2; the "silence until power cycle" reports came from sustained overload. | 70b185 (DT2), dn2mk2 reports | DN2 | Provoke single late blocks (a burn loop on a key press) and count them on the DSP side; then hold an overload for seconds. |
| H16 | Heat +FX builds need a cold-start test like other ColdFire units: a startup change can pass quick restarts and fail after minutes off (A40). | Octatrack case (A40) | Heat +FX | For the next startup-touching build: power off for 10 minutes before judging. |
| H17 | Code costs on the Heat +FX follow the DT1's ColdFire lessons (EMAC mode switches, D16 hot-path hooks), since both run audio on an MCF5441x ColdFire. | RingTone/Tone+FX (DN1), digigrain (DT1), 70b185's +FX notes | Heat +FX | Measure an audio-ISR hook with and without a MACSR switch per block. |

## Do not test on purpose
- **Section 7 over 1 MiB** (A46): it corrupts the ColdFire heap before it is refused. The static reading and one accidental crash are enough.
- **A ColdFire hang without a watchdog**: expected to need a power cycle. Nothing is gained by provoking it.
