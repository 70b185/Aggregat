# Research map

**What is known, what is proven, what is open and what nobody has looked at yet - per device, plus a shared to-do.**

The aim: whoever starts a research session (alone or with an AI agent) starts where the community's knowledge ends, instead of re-deriving what is already settled. Every line points to where the details and sources are. Phase 1 devices first (Digitakt MKI/II, Digitone MKI/II, Syntakt, Analog Heat); phase 2 follows.

Last reviewed: 2026-11-02 (second pass the same day: Digiwerk T5.3/T6.5/PB01, dn2mk2 dsp-time/dsp-cost, lalzart's DT2 architecture). Details and sources: [hardware/](hardware/README.md) (rules A1-A41, device files, [CONFLICTS.md](hardware/CONFLICTS.md)). Projects: [MODS.md](MODS.md), [DEV-TOOLS.md](DEV-TOOLS.md).

## How to read the status column

| Mark | Meaning |
|---|---|
| ✅ | **Settled:** shown on real units, or by several independent sources that agree. Build on it. |
| 🟢 | **Shown once:** seen on one unit or by one project. Probably right; a second confirmation is welcome. |
| 🟡 | **Static or emulator only:** read from the code or seen in an emulator, never checked on a unit. |
| ❓ | **Open:** sources disagree or a question is explicitly unanswered. Good research target. |
| ⬜ | **Unknown:** nobody has looked, as far as we found. Greenfield. |

"Needs" in the to-do says what a contributor must have: **files** (your own stock OS file and a computer), **unit** (a device you are willing to flash, plus a DIN MIDI interface for recovery), or **PDF/web** (manuals, reading only).

---

## Start a research session with this

Paste this into a new agent session (Claude Code or similar) that has this repo checked out:

```text
Read RESEARCH-MAP.md, then hardware/README.md and hardware/AGENT-RULES.md.
I own a <device> on OS <version> and I have <a DIN MIDI interface / only my OS file / only the manual>.
Pick one item from the "Shared to-do" that I can do with what I have, or a ❓/⬜ row of my device.
Before researching anything, search hardware/ (and hardware/CONFLICTS.md, hardware/READING-LEDGER.md)
for what is already known about it, and tell me in a few lines what is settled and what is actually open.
Then propose a plan of small, checkable steps. Follow the rules: no firmware in git, recovery practised
before any flash, every fact with an evidence tag and a source.
When done, update the matching row here and the device file under hardware/devices/.
```

**Before you spend tokens on a topic:** `grep -ri "<topic>" hardware/` takes seconds. Read [READING-LEDGER.md](hardware/READING-LEDGER.md) to see which sources were already mined. If two sources disagree, the topic is in [CONFLICTS.md](hardware/CONFLICTS.md).

**When you find something:** add it to the device file with `[hw]`/`[emu]`/`[doc]`/`[?]`, move this map's row to its new status, and close or open a conflict. A negative result ("X is not there") counts too: say what the search covered (rule A31).

---

## Shared goals (worth more than any single mod)

| # | Goal | Where it stands | What would move it |
|---|---|---|---|
| G1 | **Every device has a recovery path somebody has actually used** | ✅ DN2, DT mk1, Octatrack, A4/Rytm MK1; 🟢 DT2 (one report, OS 1.16); documented for Syntakt (SyntHack) and Heat +FX (official). 🟢 Digitone mk1 (one report, OS 1.44). Every phase-1 device now has a used or official recovery path. | T1 |
| G2 | **An honest load/headroom measure per device** (rules A25, A34, A37) | ✅ DT2 (idle-task measure on a unit), DN2 (elekloader busy meter, with the "busy is not headroom" caveat). ❓ Syntakt (two readings conflict, O3). ⬜ Heat +FX, Digitone mk1 voice CPU. | T4, T9, T10 |
| G3 | **Shared-silicon knowledge transfers between devices** | At least six phase-1 boxes use MCF5441x-family ColdFires (DT, DN, DT2, DN2, Syntakt, Heat +FX); DT2 and DN2 share the SHARC and 85 % of its functions. Many rules were found on one box and are only assumed for the others (e.g. A39 USB, A28 cache write-back). | T3, T12, T19 |
| G4 | **Emulators you can trust for more than "it boots"** | ✅ known gaps: no memory stalls (device cycles ~2x emulator), no pipeline model, EMAC fractional-mode bugs in stock Unicorn. ❓ digikit: real-time DSP audio. | T14 |
| G5 | **Mods that survive OS updates** | Every mod pins one OS version; address translation between versions is done ad hoc. Good news for DSP work: the SHARC sections are **byte-identical** between DT2 1.16 and 1.17 and between DN2 1.11 and 1.12 (digikit finding 53), so only the ColdFire side moves. | T6, T8 |
| G6 | **Official numbers instead of guesses** (MIDI CC/NRPN tables, startup menus) | The manuals' appendices were beyond what our fetcher extracts. | T13 |

---

## Digitakt (MKI) - OS 1.53 / 1.54

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Modified OS accepted | ✅ | Many elekloader mods run on units. Whether the container carries a (non-blocking) signature is not stated. | Quick check with your own file: T5-style. [digitakt.md](hardware/devices/digitakt.md) |
| Recovery | ✅ | FUNC at power-on, TRIG 4, stock `.syx` over DIN. | - |
| CPU and audio | ✅ | ColdFire, **no DSP**: all audio in the render interrupt (vector 191). | - |
| Mod platform | ✅ | elekloader core with a hook bus (tick, draw, key, encoder, settings, render in/out); core-owned sites listed. | - |
| Memory budget for mods | ✅ | 128 KB `.run`+`.bss`, 2,304 B fast SRAM (core 2.x); 256 KB area on core 4.0. | - |
| Load measurement | ✅ | DMA-timer method (digihealth); FAST AUDIO runs the render from SRAM. | - |
| Machine-ID registry across mods | ✅ | Nine ids collected (4, 5, 6, 7, 9, 10, 27, 69, 77) in `hardware/devices/digitakt.md`; check new mods' `mod.json`. | T20 |
| USB control-transfer rule (A39) | ⬜ | Found on the Octatrack; untested here. | T3 |
| Board / teardown | ❓ | Only unverified forum reports. | Photos from anyone who opened one. |

## Digitone (MKI) / Digitone Keys - OS 1.43 / 1.44

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Container | ✅ | Unsigned (trailer is 32 zero bytes). | - |
| Recovery | 🟢 | **Used on a unit:** FUNC at power-on, TRIG 4, stock `.syx` over DIN restored OS 1.44 after a build hung on the logo (digitone-arp-mod, 2026-10-08). The startup receiver always expects Digitone-addressed SysEx, even under a Digitakt-based OS (taktone). | - |
| CPU and audio | 🟢 | A **second ColdFire** (section 7) renders the FM voices into shared FlexBus SRAM; the main ColdFire (250 MHz) runs effects and mix. taktone booted that CPU with its own engine and documents the whole board interface; the board is a Digitakt mk1 plus six keys, the second CPU and an FPGA. | Measure the voice CPU's load. |
| Mod platform | ✅ | elekloader core-dn1 with hook sites; effect and audio-input mods (DigiSwarm, DigiPrism) ran on units. | - |
| Digitone Keys | ❓ | Same OS file, but several mods say "never run on a Keys". | Any Keys owner running a mod's test list. |
| Voice-CPU load | ⬜ | Nobody has measured it. | T10-style probe on CPU #2. |

## Digitakt II - OS 1.16 / 1.17

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| SHARC timing | ✅ | 1.000 GHz, 666,667 cycles per 32-sample block, 1,500 blocks/s (conflict S1 settled). | - |
| Silicon costs | ✅ | Taken jump ~7 cycles, CALL+RTS ~14, L2 miss ~58; device cycles ~2x emulator counts (A35). | [digitakt-2-dsp-optimizing.md](hardware/devices/digitakt-2-dsp-optimizing.md) |
| RTOS and missed blocks | ✅ | FreeRTOS on the SHARC; a late block is a whole missed block; stock never misses on its own (A25). | [digitakt-2-sharc-measured.md](hardware/devices/digitakt-2-sharc-measured.md) |
| ColdFire <-> SHARC reply words | ✅ | Words 670-676 arrive untouched; word 0 is a true load figure on DT2 (A26, S5, S6). | - |
| Unsafe encodings | ✅ | Same-DAG stores (two independent unit cases), SIMD moves, negative shift immediates: run in the emulator, hang the unit (A33, A41). digikit's patchkit refuses same-DAG stores at build time. | - |
| "Bitcrush until reboot" | ❓ | Not caused by missed blocks; appears only with several custom-engine tracks at extreme settings. Cause unknown. | T7 |
| Free L2 on 1.17 | ❓ | Static says up to `0x200fa000`, a unit clicked past `0x200f5a74` (O7). | T15 |
| Mod routes side by side | 🟡 | Six projects compared (T21): five users share the 2 KB flash cave at `0x403117c4`; elekloader's RAM `0x47f00000` lies inside digikit's `cf.expansion`; the listed UI hook sites are disjoint. One report says the cave froze a unit (O18). | [memory-maps.md](hardware/common/memory-maps.md) |
| Section 7 size | ✅ | Decoded size must stay under `0xfffff`: the check runs only after depacking into a 1 MiB buffer, and an oversized stream crashed a unit (A46). | [firmware-container.md](hardware/common/firmware-container.md) |
| ColdFire watchdog | ✅ | Not configured (static): a ColdFire hang stays hung until a power cycle. | [memory-maps.md](hardware/common/memory-maps.md) |
| "Rung C" halt | ✅ | Solved: 17 stores of a DAG register through its own DAG (excluded by the ISA, accepted by assembler and emulator); without them the build played on a unit. The same rule the repo owner found independently (A33). | - |
| Bootstrap-menu recovery | 🟢 | **Used on a unit:** after a crashing build, official OS 1.16 was restored over DIN via Transfer's recovery mode (dt2-machine-lab, 2026-10-06). A cheap USB-MIDI cable adapter delivered nothing. One report; more welcome. | T1 (a second report, ideally on 1.17) |
| OS version gate | ✅ | DT2 refuses OS below "0060" (S8). | - |
| Sample path to a voice | 🟡 | Via link port 0 (LP0/DMA30), fed from a ColdFire Rapid-GPIO endpoint - two independent static/emulator readings agree (digikit f15, lalzart). The physical bridge is unknown. | Confirm on a unit. |
| ColdFire <-> SHARC frame | 🟡 | A full-duplex `0xabc`-byte DSPI2 frame, 16 records of `0x60` bytes, the **same shape as on the DN2** (lalzart, static). Return content open. | T19 |
| Memory map, machine API, parameter table | 🟡 | Sample pool, heap, slot table and voice records mapped for 1.16 (dt2-machine-lab, emulator); the rest partial; many DN2 findings likely transfer (85 % shared SHARC functions). | T19 |
| Project file format (`.dt2prj`) | 🟢 | Song slots: LZ4 32 KiB blocks (dt-song-mgmt). Rest ⬜. | T18 |

## Digitone II - OS 1.10E / 1.11 / 1.12

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Container and signing | ✅ | ELE3, HMAC-SHA256 with the key derived from the image, so tools can re-sign; section 7 is the SHARC's ADI boot stream (S4). | [digitone-2.md](hardware/devices/digitone-2.md) |
| Recovery | ✅ | FUNC at power-on, TRIG 4, DIN; tested on units. OS writer has no length clamp (A30). | [flash-procedure.md](hardware/common/flash-procedure.md) |
| SHARC load | ❓ | Two unit measurements disagree at idle: ~63-65 % (idle-task, dnfw/Digiwerk) vs ~80 % falling to 65 % with 64 notes (elekloader) - O15. Both agree it is **not headroom** (A37). | T9 |
| Load prediction model | ❓ | Instruction-count model overestimates (O12). | T9 |
| Free SHARC memory | ❓ | Contested L2 range `0x200918c0-0x200c2000` (O19, T24). Proven code room 83,838 B over four regions. L1 block 1 adds ~12 KB, not 45; block 3's tail is I-cache; `0x315f8c-0x318000` stopped the DSP (PM cache size open); two L2 candidates (38.5 KB, 229 KB); code in dead stock-FX spots in L2 stopped the DSP (O13). | A probe build (Digiwerk's planned PB01). |
| ColdFire -> DSP frame | ✅ | 0xabc-byte frame, data in the first 0xa80; the tail and reply word 2 are free (one owner per build). | [digitone-2-internals.md](hardware/devices/digitone-2-internals.md) |
| ColdFire RAM above the reset clear | 🟡 | Five projects compared: dnfw, cfmod and Digiwerk all start at `0x46800000`; `0x46700000` up to `0x46710000` is not free (O17). | T23, [memory-maps.md](hardware/common/memory-maps.md) |
| SHARC filter accelerators | 🟢 | IIR0/FIR0 read on a unit: three differences from the hardware reference; stock uses neither. | [digitone-2-internals.md](hardware/devices/digitone-2-internals.md) |
| Persisting a mod's parameters | ✅ | Unsaved edits survive a power cycle through `Sound::updateMirror`; a mod's own parameters persist when it sends the stock whole-sound event (E2, on the unit). | [AGENT-RULES.md](hardware/AGENT-RULES.md) |
| Adding machines, linking DSP code | 🟢 | elekloader (1.12) and dn2mk2 (1.11) ship machines; DT2 sample machines run on DN2. | [digitone-2-machines-sampler-sharc.md](hardware/devices/digitone-2-machines-sampler-sharc.md) |
| OS 1.11 <-> 1.12 addresses | ❓ | Projects split between versions; the parameter table base differs by 4 bytes between two maps (O6). | **T8** |
| Grown parameter table | 🟢 | Grown to 0x180 rows and running on a unit, +Drive save/load fine (Digiwerk GT00/GT01); a 3-band compressor ships on it. Open: does such a project open cleanly on a **stock** OS? | T16 |
| Overbridge with modified OS | ✅ | Cause found and fixed: the container's version field is sent to the computer; keep `1.12` in what is sent (Digiwerk OB01, on the unit). Open: what the plugin does with parameter ids of `0x400`+ from grown tables. | [overbridge-usb.md](hardware/common/overbridge-usb.md); T17 |
| Real-time DSP audio in an emulator | ❓ | Open in digikit. | T14 |
| Project file format (`.dn2prj`) | 🟡 | DNX reads parts of it; the deobfuscator repo is unreachable. | T18 |

## Syntakt - OS 1.40A / 1.41 / 1.42

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Platform | 🟢 | Two MCF5441x at 250 MHz (166,667 cycles per block); CPU #2 is the voice CPU with its own 128 MB RAM, a 64 MB sample pool and its own FPGA; analog mixer. | [syntakt.md](hardware/devices/syntakt.md) |
| Recovery | 🟢 | Documented by SyntHack: Transfer over USB normally; if it doesn't boot, FUNC + TRIG 4 over DIN (tens of minutes). Avoid TRIG 2/3. | - |
| Signing | ❓ | 1.41 carries an HMAC (SyntHack); 1.42 has a zero trailer (digikit) (O1). | **T5** |
| CPU #1 load | ❓ | ~89 % of the audio interrupt at rest vs. 85.8k of 166.7k cycles - probably different spans (O3). | **T4** |
| Where mod code can live | ✅ | Not above the BSS: sample loading overwrites `0x45565490-0x48000000` (settled S13). SyntHack reserves the first 64 KB heap block at boot; kit and project files carry spare bytes that round-trip through stock code. | [syntakt.md](hardware/devices/syntakt.md) |
| Free executable storage on CPU #2 | ❓ | Unresolved. | machine-45 research notes |
| Section 8 | ✅ | A shared ARM Cortex-M firmware image, the same on several devices, not an FPGA (S15). Which accessory it serves is open (O16): Outbox 8 is the likely candidate. | - |
| FPGA role | ⬜ | Unknown on every device that has one. | T12 |
| OS 1.42 | ⬜ | All mods target 1.41 (SY FM4: 1.40A); only 27 of 172 anchors shared with the DT2. | **T6** |
| Mod building method | ✅ | SyntHack's modding guide (patch.json, protected sections). | - |

## Analog Heat - MKI / MKII / +FX

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| MKI / MKII firmware | ⬜ | **Nothing beyond official facts.** Container, CPU, DSP, signing: all unknown. | **T11** (files only, beginner-friendly) |
| +FX container | ✅ | ELE3, no HMAC, byte-exact round trip with two independent unpackers (70b185). | [analog-heat.md](hardware/devices/analog-heat.md) |
| +FX recovery | ✅ | Hold ACTIVE at power-on, **MOD** = OS UPGRADE, DIN (official); the bootstrap holds the menu. | - |
| +FX CPU and audio | 🟡 | MCF5441x, **no DSP section**, audio on the ColdFire (SSI1, eDMA, a software interrupt) - static. | - |
| +FX own code on a unit | 🟢 | A text change and a 42-byte hook in the audio software interrupt ran (70b185, test01/test02). Code must stay below `0x40206000` (A27). | - |
| +FX persistence of hooks | ❓ | Whether the hook keeps running is open. | - |
| +FX CPU reserve with all FX | ❓ | A forum post claims 79 %; not measured. | **T10** |
| +FX FPGA role | ⬜ | Loaded by the OS; role unknown. Section size is 54,664 B, **the same size as the A4 MKII's FPGA section and the Digitone mk1's bitstream** - a lead, not a finding. | T12 |
| +FX preset format, latency, flash budget | ⬜ | Not looked at. | - |
| Community | - | No public Heat firmware project; the repo owner's research is paused. | - |

---

## Shared to-do

Inferred facts waiting for a test on a unit, sorted by effort (stock, probe, build): [hardware/HYPOTHESES.md](hardware/HYPOTHESES.md).

Pick one, check the status above, and go. **S** = an evening, **M** = a few sessions, **L** = a project. "Value" says why the community gains from it.

| # | Task | Device | Needs | Effort | Value |
|---|---|---|---|---|---|
| T1 | ~~First DT2 recovery report~~ **one exists** (OS 1.16). Still useful: a second report on **1.17**, with timings and the interface used | Digitakt II | unit + DIN | S | Confirms the path on the current OS (G1). Low risk: stock file only. |
| T2 | ~~Digitone mk1 recovery~~ **done** (one report, digitone-arp-mod). Still useful: the same on a **Digitone Keys** | Digitone Keys | unit + DIN | S | Keys share the OS file but are untested by most mods. |
| T3 | Test rule A39 (no EP0 stage of a multiple of 64 bytes) on a small box with a vendor request. The DT2 has the same EHCI-style controller with EP0 max packet 64 and its own EP0 vendor requests (digikit 42), so it is the best candidate | DT2 (or DN2, DT/DN mk1) | unit + a USB mod | M | Confirms or limits a rule found on the Octatrack (G3). |
| T4 | Measure CPU #1 load with the digihealth DMA-timer method over the whole interrupt, at rest and busy | Syntakt | unit + SyntHack | M | Settles O3; gives Syntakt modders a budget (G2). |
| T5 | Check the trailer and HMAC of 1.40A/1.41/1.42 with your own files (elektron-firmware-tool, digikit) | Syntakt (also DT mk1) | files | S | Settles O1; tells modders whether 1.42 needs re-signing. |
| T6 | Translate SyntHack/machine-45 anchors from 1.41 to 1.42 (byte patterns, not addresses) | Syntakt | files | M | Opens the current OS to mods (G5). |
| T7 | Find the cause of the sticky "bitcrush until reboot" | Digitakt II | unit + custom engine | L | A hidden state bug that any DT2 engine can trigger. |
| T8 | Build an address-translation table DN2 1.11 <-> 1.12 from shared anchors | Digitone II | files | M | Lets dn2mk2 (1.11) and elekloader/dn2-cfw (1.12) share work (G5); settles O6. |
| T9 | Measure DN2 load with both meters (dnfw idle-task and elekloader dspbusy) in the same states, then calibrate a cost model (dn2mk2's instructions + 4 x L2 + 10 x DDR is a start) | Digitone II | unit | M | Settles O15 and O12; predict cost before flashing (G2). |
| T10 | Port a DMA-timer load probe (digihealth / A4 0011-style) to the Heat +FX and measure all FX on | Analog Heat +FX | unit | M | First budget for the only fresh platform in phase 1 (G2). |
| T11 | Unpack the MKI and MKII OS files: sections, container, CPU (peripheral census), any DSP section | Analog Heat MKI/MKII | files | S | Turns two ⬜ devices into mapped ones. Good first task. |
| T12 | Compare FPGA bitstreams across devices (sizes, SHA-256, header) and the OS code that talks to them. **Leads:** on the Rytm MKII, sample bit reduction is a command word sent to the external audio hardware, not PCM work on the ColdFire; and three bitstreams are exactly 54,664 bytes - Heat +FX section 1, A4 MKII section 1, and the Digitone mk1's (inside section 7, loaded by the second CPU) | Heat +FX, A4 MKII, DN mk1, Syntakt, DT2/DN2, Rytm | files | M | First step on "what does the FPGA do" everywhere (G3). |
| T13 | Transcribe the official MIDI CC/NRPN tables from the manuals' appendices into `hardware/common/sysex-and-midi.md` | DT2, DN2, Heat +FX | PDF | S | Official numbers for every control tool (G6). |
| T14 | Fix or document digikit's EMAC fractional-mode emulation against a unit measurement | DT2/DN2 (all ColdFire boxes) | unit + emulator | M | Fewer "works in the emulator" surprises (G4). |
| T15 | Probe free SHARC L2 on DT2 1.17 between `0x200f5a74` and `0x200fa000` on a unit | Digitakt II | unit | M | Settles O7; more room for engines. |
| T16 | Save a project on a grown parameter table, load it on stock, record what happens | Digitone II | unit | S | Tells users whether modded projects stay safe. |
| T17 | ~~Find why Overbridge rejects modified DN2 builds~~ **done** (Digiwerk OB01: the version field). Remaining: how the plugin treats parameter ids `0x400`+ from a grown table | Digitone II | unit + Overbridge | S | Grown-table mods with Overbridge automation. |
| T18 | Document the project file formats (`.dt2prj`, `.dn2prj`) beyond song slots | DT2, DN2 | files | M | Librarians and converters for musicians. |
| T19 | ~~Check which DN2 SHARC findings hold on the DT2 (and back)~~ **done as a comparison** (2026-11-02, [dt2-dn2-sharc-crosscheck.md](hardware/common/dt2-dn2-sharc-crosscheck.md)): silicon facts hold on both (digikit's probe on both units), firmware facts do not carry over. Remaining unit tests: SIMD L2 access on a DN2, reply-record arrivals on a DN2, single late blocks on a DN2 | DT2, DN2 | unit | S each | Doubles the value of every SHARC finding (G3). |
| T20 | ~~DT mk1 machine-id registry~~ **done** (nine ids). Keep it current: add each new machine mod's id from its `mod.json` | Digitakt mk1 | reading | S | Prevents clashes between mods. |
| T21 | ~~Cross-check the three Digitakt II mod routes~~ **done** (2026-11-02, six projects: [memory-maps.md](hardware/common/memory-maps.md)). Found: five users share the flash cave, elekloader's RAM lies inside digikit's `cf.expansion`, the listed UI sites are disjoint. Remaining: settle O18 (canary in the flash cave on a unit) and agree one RAM split between digikit and elekloader | Digitakt II | files, then unit | S | Lets DT2 mods be combined instead of competing. |
| T22 | ~~Compare libanalogrytm's Rytm SysEx container/encoding with Digitakt II and Digitone II~~ **done** (2026-11-02, [sysex-and-midi.md](hardware/common/sysex-and-midi.md)): same frame, packing, checksum and count on both generations; the type bytes differ; three device-id namespaces tabulated. Remaining: the Rytm MKII's dump byte, and what a Rytm does with the index byte on receive | Rytm, DT2, DN2 | files | S | One shared description of Elektron's SysEx data encoding. |
| T23 | Keep a DN2 RAM tenancy table: every mod platform's and mod's ranges above the reset clear, per OS version (start: [memory-maps.md](hardware/common/memory-maps.md), five projects compared 2026-11-02); then a unit canary at `0x46700000` after a large +Drive sample load (settles O17) | Digitone II | reading, then unit | S | dnfw, cfmod and dn2-cfw all start at `0x46800000`; without a table, mods from different platforms cannot be combined. |
| T24 | Watch DN2 SHARC L2 `0x200918c0-0x200c2000` for stock writes during playback, pattern changes and a save (emulator write watch first, then a canary on a unit); settles O19 | Digitone II | emulator, then unit | S | Decides whether 160 KB of L2 that two projects use and one avoids is really free. |

### Where new findings are most likely

- **Analog Heat (all three):** almost untouched. Every hour of careful static work (T11, T12) produces new facts.
- **Syntakt 1.42:** the current OS has no mods yet. T5 and T6 unlock it.
- **Rules from other platforms:** the Octatrack and A4/Rytm communities found USB, cache and boot rules on the same ColdFire family (A38-A41). Checking them on the small boxes (T3) is cheap and high-value.
- **DT2 <-> DN2:** the two share most of the SHARC code, but their research communities are separate. T19 connects them.

---

*Maintenance:* this file is hand-written. When a row changes, update the status and the date at the top. Phase 2 devices (Octatrack, Rytm, A4/Keys, Model:Cycles/Samples, Machinedrum, Monomachine) will get their sections next; until then, their device files under [hardware/devices/](hardware/devices/) end with "Open" or "Gaps" lists.
