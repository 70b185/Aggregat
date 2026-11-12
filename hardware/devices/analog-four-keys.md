# Analog Four / Analog Keys (MKI, MKII) - OS 1.56

Coverage: **first profile** (phase 2). Read 2026-11-02 from:
- hugz202/AE-analog-four-mods (`docs/HAZARDS.md`, `docs/FLASHING.md`, `docs/research/digital-path-findings.md`, README), the first public firmware mods for the A4 MK1. Key {a4mods}. Its builds have run on units.
- trigcondition/analog-emu (`docs/A4-PORT.md`, `docs/MK1-PORT.md`), an emulator for the Rytm, A4 and Syntakt. Keys {analog-emu-a4} and {analog-emu-mk1}. These are mostly static analysis and emulator runs; the author tags each claim measured / inferred / community.
- Iced-Cream/analoghealth (README), a diagnostics mod that passed on an A4 MKII unit. Key {analoghealth}.

Projects: [../../catalog/analog-four-keys.md](../../catalog/analog-four-keys.md).

**The short version:** a ColdFire-only machine. There is no DSP chip; the effects and every digital part of the audio run on the ColdFire's EMAC inside one audio interrupt. The voices are analog. The interrupt is ~71 % busy before you add anything. Same platform family as the Analog Rytm (see [analog-rytm.md](analog-rytm.md)).

## Silicon and memory
- **CPU:** ColdFire V4e with EMAC, no FPU, on both generations. analog-emu identifies MCF5441x by code and peripheral use. The A4 MK1 mods assemble with `-mcpu=5475 -mno-float`: that is a V4e ISA setting, and with `-mno-float` an FPU instruction becomes an assembly error instead of a crash on the unit. `[hw]` {a4mods} {analog-emu-a4}
- **No DSP.** No DSP56k strings, no second-CPU loader, no DSP firmware section. `[doc]` {analog-emu-a4}
- **MK1 vs MKII board** (both static analysis, `[doc]` {analog-emu-mk1}):

| | A4 MKII | A4 MK1 / Analog Keys |
|---|---|---|
| OS file | ELE3 container, 5 sections | **ELE2, one section (MAIN OS)** |
| DDR | 128 MB (ACR0 `0x4007e020`) | **64 MB** (ACR0 `0x4003e020`) |
| Boot/config flash | SPI NOR on DSPI0 | parallel NOR on FlexBus CS0, 8 MB at 0 |
| Voice SPI | DSPI1, eDMA ch 15 | DSPI2, eDMA ch 29 |
| Voice frame | 100 x 16-bit words | 100 words, same format |
| Codec | SSI1, 8 words per frame | SSI1, 8 words |
| Display | 128x64 OLED | 122x32 LCD |
| USB | high-speed capable | **full speed only** |

- **MK1: only `0x40000000-0x43ffffff` is cached.** ACR0 covers that range and the default is cache-inhibited, so the effect delay lines (`0x468xxxxx` and up) and any mod state placed beside them are uncached: every access is a full bus round trip. An early chord-oscillator build made ~1,000 such accesses per block per voice; the UI slowed and the unit could crash. **Copy state to the stack once per block, work there, write it back.** `[hw]` {a4mods} ([I11](../INCIDENTS.md#i11-uncached-state-in-a-chord-oscillator-slowed-the-ui-and-could-crash-the-unit))
- **On-chip SRAM is fully used.** The OS fills the whole 64 KB SRAM from its image at boot, so the Digitakt mk1 trick of running audio code from free SRAM (digihealth's FAST AUDIO) has no room here. `[doc]` {analoghealth}
- MKII flash part on one unit: Winbond W25Q64 (8 MB, 256-byte pages, 64 KB sectors), reported by the factory console; the Rytm MKII uses an S25FL128S. Compare conflict O8 in [../CONFLICTS.md](../CONFLICTS.md). `[hw]` {analog-emu-a4}

## Audio engine (MK1 OS 1.55 names; layout the same on 1.56)
- **One interrupt does all digital audio**, per 32-sample block (`[doc]` code reading, confirmed by a probe build on a unit) {a4mods}:
  1. pick the DMA buffer;
  2. run the control block: envelopes, LFOs and per-track levels, which turn each volume into (a) a send gain plus pan and (b) the analog dry VCA words;
  3. generate the four digital noise sources;
  4. run the FX block: the codec's receive frames (eight slots per sample, six used: four voices and the stereo input) are mixed into three stereo send buses, then chorus, delay and reverb run, and only their summed returns go out to the DAC;
  5. send the CV/voice frame to the hardware.
- **The dry voice is analog to the outputs.** The digital side gets a captured copy and returns only the effects.
- **The capture point is before the analog output VCA** (`[hw]`, a probe build that muted track 1's dry in software while its sends still carried the voice). A mod can therefore silence a track's dry path and process its digital copy instead. hugz202's "digital path" mod does exactly that. {a4mods}
- The MKII has the same structure: RX slots 0-3 are the four voices before their VCA, RX 4/5 most likely EXT IN, TX 4/5 the effect returns. `[emu]` {analog-emu-a4}

## Load budget (measured on an A4 MK1 with a probe build, 2026-10-09) {a4mods}

| state | average | peak |
|---|---|---|
| sequencer stopped | 71.1 % | 76.5 % |
| one track playing, reverb send | 71.3 % | 79.4 % |
| one track, all three sends | 71.3 % | 80.9 % |
| all tracks, all sends, reverb decay near max | 71.3 % | 82-89 % |

- The effects run whether anything plays or not, so the cost is mostly fixed; the peaks come from block-to-block variation and preemption. Worst case left: ~11 %, and the UI and sequencer run in that remainder too. `[hw]`
- **Their budget rule:** stay well under ~5 % at peak for new blocks, and prefer *replacing* work (the chorus slot) to adding it. A per-track drive/bit-crush insert is ~1-2 % per processed track. `[hw]` Same lesson as rule A34.

## Where mod code can live (MK1 OS 1.56) {a4mods}
- **Almost no free space.** Mods use the padding between the C++ constructor table and `__bss_start`, a 1 KB gap between chorus lookup tables that no index can reach, and **runs of code the firmware contains but never calls**.
- Treat dead code as free only with both kinds of evidence:
  - static: no call, branch, pointer, vtable entry or switch case reaches it;
  - dynamic: emulator coverage never ran it (seven long sessions, 540 KB of code reached).

  Hash the stock bytes before writing there. `[hw]` (these builds have run on units)
- Most "free" candidates that a cave scan finds turn out to be the ends of tables still in use. `[doc]`
- Keep a registry with every patched address, its expected stock bytes and its owner. Refuse to build when the stock bytes don't match, and verify every detour's return path on the finished `.syx`. This is the same method as rule A31: prove both sides. `[doc]`

## The bootstrap is inside MAIN OS (MK1) - never write into it {a4mods}
- The MK1 `.syx` has one section. The bootstrap (STARTUP menu plus DIN-MIDI OS UPGRADE) is carried **inside MAIN OS**: on 1.56 its version words are at `0x40226958` and its image at `0x40226960..0x40233a30` (53,456 B).
- **At every boot** the startup code compares that version with the one in flash at `0xfff8`. If the embedded one is newer, it **erases the bootstrap sectors and writes the embedded image**. So a mod byte in that range could one day become the recovery path. `[doc]` (code reading)
- 1.56's embedded bootstrap grew 1,424 B over 1.55 and filled a code cave that 1.55 builds used. **Per-version caves are not portable.**
- Don't power off during the first boot after flashing: coming from an OS older than 1.55, that boot may be a genuine bootstrap upgrade. `[doc]`
- Rule A38.

## OS update and recovery
- **Normal:** send the `.syx` with Transfer over USB; this runs inside the installed OS.
- **Recovery:** hold FUNC at power-on, choose `4 ... OS UPGRADE` (TRIG 4), then send the stock `.syx` over **DIN MIDI** (Transfer's legacy OS-upgrade mode). It is served by the bootstrap in flash. Rule A36 holds. `[hw]` {a4mods}
- Builds that keep version 1.56 make going back a same-version reinstall. Kits saved on the modded OS load on stock (stock ignores the extra fields). `[hw]` {a4mods}
- **MKII update in the emulator** (`[emu]` {analog-emu-a4}):
  - The OS saves its working state to the card, erases 17 x 64 KB from flash `0x80000` and programs the container page by page, then resets.
  - From the first erase to the last page **there is no bootable OS in flash**; a power cut then needs the DIN recovery.
  - The power-fail handler waits for a running erase.
- The A4 MKII bootstrap never sets the boot-flag bit that 1.56 reads as "Analog Keys" (31 places), so the unit names itself Analog Four. `[doc]` {analog-emu-a4}

## Calibration (MKII, code reading) {analog-emu-a4}
- Read from SPI flash `0x300000`, 3,670 B, magic `RBOW`, the Rytm's checksum rule, **one copy only** (the Rytm keeps two). It holds analog (oscillator levels, PWM, filter), CV-out and keyboard trims. `[doc]`
- **Never write that flash range from a mod**: a lost record means a recalibration. A missing record shows "MISSING CAL". `[doc]`

## elekloader's core on the MKII (core-a4mk2 0.6, OS 1.56) {elekloader-core-a4}
- **Mods' area `0x45650000-0x47C00000` (37.7 MB)** from core-a4mk2 0.6: the gap above the OS's fixed buffers, from its first 64 KB boundary. ddr-canary saw no word change there on a unit through normal use (Overbridge included) and a power cycle (21 Oct 2026). Builds with core 0.5 or older keep the 128 KB at `0x47BE0000`. The flash budget, not RAM, limits a payload. `[hw]`
- **The modified mark:** stock marks the project modified with `0x400a5bba(model, 1)` and keeps the mark in byte `0x4045c8c2`; a load reads it (`0x4003df98`) and asks ANY CHANGES WILL BE LOST or SAVE ... BEFORE LOADING. Stock sets it on every page or track key and after every load; only a save clears it. `[doc]`
- **Every whole save of the live project** ends in `0x400a771a(model, slot, progress)` (file save at `0x400a77e4`); on success it makes the slot active (`0x400a5b74`) and clears the mark. Callers: the save job `0x4003da46` (front-panel saves through `0x4003ecbe`) and the load job `0x4003daf0` (CREATE NEW, then save, for an empty slot; no panel action reaches it on 1.56). `[doc]`
- **Brain::key (`0x40098b36`) drops the view controller's answer**, so a mod cannot tell whether a view took a key, only that stock had it. LEVEL / DATA is encoder 10, or 11 on an Analog Keys (bit 20 of the boot word `0x401ff54c`). `[doc]`

## Open
- Which analog quantity each calibration table trims (inferred from strings only).
- TX slots 0-2, 6, 7 and RX 6/7 on the MKII.
- A4 MKII load figures under its own OS (only the MK1 has been measured).
