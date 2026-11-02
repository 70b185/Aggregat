# Research map

**What is known, what is proven, what is open and what nobody has looked at yet - per device, plus a shared to-do.**

The aim: whoever starts a research session (alone or with an AI agent) starts where the community's knowledge ends, instead of re-deriving what is already settled. Every line points to where the details and sources are. Phase 1 devices first (Digitakt MKI/II, Digitone MKI/II, Syntakt, Analog Heat); phase 2 follows.

Last reviewed: 2026-11-02. Details and sources: [hardware/](hardware/README.md) (rules A1-A41, device files, [CONFLICTS.md](hardware/CONFLICTS.md)). Projects: [MODS.md](MODS.md), [DEV-TOOLS.md](DEV-TOOLS.md).

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
| G1 | **Every device has a recovery path somebody has actually used** | ✅ DN2, DT mk1, Octatrack, A4/Rytm MK1; documented for Syntakt (SyntHack) and Heat +FX (official). ❓ DT2: the bootstrap-menu recovery is not reported tested on hardware. ❓ Digitone mk1: the buttons are not stated anywhere we read. | T1, T2 |
| G2 | **An honest load/headroom measure per device** (rules A25, A34, A37) | ✅ DT2 (idle-task measure on a unit), DN2 (elekloader busy meter, with the "busy is not headroom" caveat). ❓ Syntakt (two readings conflict, O3). ⬜ Heat +FX, Digitone mk1 voice CPU. | T4, T9, T10 |
| G3 | **Shared-silicon knowledge transfers between devices** | At least six phase-1 boxes use MCF5441x-family ColdFires (DT, DN, DT2, DN2, Syntakt, Heat +FX); DT2 and DN2 share the SHARC and 85 % of its functions. Many rules were found on one box and are only assumed for the others (e.g. A39 USB, A28 cache write-back). | T3, T12, T19 |
| G4 | **Emulators you can trust for more than "it boots"** | ✅ known gaps: no memory stalls (device cycles ~2x emulator), no pipeline model, EMAC fractional-mode bugs in stock Unicorn. ❓ digikit: real-time DSP audio. | T14 |
| G5 | **Mods that survive OS updates** | Every mod pins one OS version; address translation between versions is done ad hoc. | T6, T8 |
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
| Machine-ID registry across mods | 🟡 | Ids used by several mods not collected, so clashes are possible. | T20 |
| USB control-transfer rule (A39) | ⬜ | Found on the Octatrack; untested here. | T3 |
| Board / teardown | ❓ | Only unverified forum reports. | Photos from anyone who opened one. |

## Digitone (MKI) / Digitone Keys - OS 1.43 / 1.44

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Container | ✅ | Unsigned (trailer is 32 zero bytes). | - |
| Recovery | ❓ | Not stated by any source; assumed like the Digitakt (FUNC, TRIG 4). | **T2** (cheap, high value) |
| CPU and audio | 🟡 | A **second ColdFire** (section 7) runs only the FM voices; the main ColdFire runs effects and mix. From code census and a third-party board list. | Confirm the board; measure the voice CPU's load. |
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
| Unsafe encodings | ✅ | Same-DAG stores, SIMD moves, negative shift immediates: run in the emulator, hang the unit (A33, A41). | - |
| "Bitcrush until reboot" | ❓ | Not caused by missed blocks; appears only with several custom-engine tracks at extreme settings. Cause unknown. | T7 |
| Free L2 on 1.17 | ❓ | Static says up to `0x200fa000`, a unit clicked past `0x200f5a74` (O7). | T15 |
| "Rung C" halt | ❓ | digikit lists no confirmed cause. | digikit findings |
| Bootstrap-menu recovery | ❓ | Accepts SysEx over DIN only (static reading); **not reported tested on hardware**. | **T1** |
| OS version gate | ✅ | DT2 refuses OS below "0060" (S8). | - |
| Sample path to a voice | 🟡 | Via link port 0 (digikit finding 15, emulator). | Confirm on a unit. |
| Memory map, machine API, parameter table | 🟡 | Partial; many DN2 findings likely transfer (85 % shared SHARC functions). | T19 |
| Project file format (`.dt2prj`) | 🟢 | Song slots: LZ4 32 KiB blocks (dt-song-mgmt). Rest ⬜. | T18 |

## Digitone II - OS 1.10E / 1.11 / 1.12

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Container and signing | ✅ | ELE3, HMAC-SHA256 with the key derived from the image, so tools can re-sign; section 7 is the SHARC's ADI boot stream (S4). | [digitone-2.md](hardware/devices/digitone-2.md) |
| Recovery | ✅ | FUNC at power-on, TRIG 4, DIN; tested on units. OS writer has no length clamp (A30). | [flash-procedure.md](hardware/common/flash-procedure.md) |
| SHARC load | ✅ | Measured on a unit: ~80 % "busy" idle, 65 % with 64 notes; **not headroom** (A37). | - |
| Load prediction model | ❓ | Instruction-count model overestimates (O12). | T9 |
| Free SHARC memory | ❓ | The L1 tails are cache, not free (O13); proven code room 83,838 B over four regions. | Silicon check of O13. |
| ColdFire -> DSP frame | ✅ | 0xabc-byte frame, data in the first 0xa80; the tail and reply word 2 are free (one owner per build). | [digitone-2-internals.md](hardware/devices/digitone-2-internals.md) |
| Adding machines, linking DSP code | 🟢 | elekloader (1.12) and dn2mk2 (1.11) ship machines; DT2 sample machines run on DN2. | [digitone-2-machines-sampler-sharc.md](hardware/devices/digitone-2-machines-sampler-sharc.md) |
| OS 1.11 <-> 1.12 addresses | ❓ | Projects split between versions; the parameter table base differs by 4 bytes between two maps (O6). | **T8** |
| Grown parameter table vs stock | ❓ | Whether a project saved with extra parameters loads on stock is untested. | T16 |
| Overbridge with modified OS | ❓ | dn2-cfw builds show "incompatible OS version". | T17 |
| Real-time DSP audio in an emulator | ❓ | Open in digikit. | T14 |
| Project file format (`.dn2prj`) | 🟡 | DNX reads parts of it; the deobfuscator repo is unreachable. | T18 |

## Syntakt - OS 1.40A / 1.41 / 1.42

| Area | Status | What is known | Next step / where |
|---|---|---|---|
| Platform | 🟢 | Two MCF5441x at 250 MHz (166,667 cycles per block); CPU #2 is the voice CPU with its own 128 MB RAM, a 64 MB sample pool and its own FPGA; analog mixer. | [syntakt.md](hardware/devices/syntakt.md) |
| Recovery | 🟢 | Documented by SyntHack: Transfer over USB normally; if it doesn't boot, FUNC + TRIG 4 over DIN (tens of minutes). Avoid TRIG 2/3. | - |
| Signing | ❓ | 1.41 carries an HMAC (SyntHack); 1.42 has a zero trailer (digikit) (O1). | **T5** |
| CPU #1 load | ❓ | ~89 % of the audio interrupt at rest vs. 85.8k of 166.7k cycles - probably different spans (O3). | **T4** |
| Free RAM above the BSS | ❓ | One mod keeps code at `0x47000000`; another found sample loading overwrites that range (O2). | Write-watch with samples loading. |
| Free executable storage on CPU #2 | ❓ | Unresolved. | machine-45 research notes |
| Section 8 | ❓ | "Second FPGA?" vs. identical to DT2/DN2 section 8 (O4). | T12 |
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
| +FX FPGA role | ⬜ | Loaded by the OS; role unknown. Section size is 54,664 B, **the same size as the A4 MKII's FPGA section** - a lead, not a finding. | T12 |
| +FX preset format, latency, flash budget | ⬜ | Not looked at. | - |
| Community | - | No public Heat firmware project; the repo owner's research is paused. | - |

---

## Shared to-do

Pick one, check the status above, and go. **S** = an evening, **M** = a few sessions, **L** = a project. "Value" says why the community gains from it.

| # | Task | Device | Needs | Effort | Value |
|---|---|---|---|---|---|
| T1 | Use the bootstrap-menu recovery once with the **stock** file and write down every step and timing | Digitakt II | unit + DIN | S | Turns the most important unknown on the DT2 into a known path (G1). Low risk: stock file only. |
| T2 | Confirm the startup-menu buttons and the OS-upgrade path | Digitone mk1 / Keys | unit (no flashing) or manual | S | Closes a recovery gap (G1). |
| T3 | Test rule A39 (no EP0 stage of a multiple of 64 bytes) on a small box with a vendor request | DT mk1 / DN mk1 / DT2 | unit + a USB mod | M | Confirms or limits a rule found on the Octatrack (G3). |
| T4 | Measure CPU #1 load with the digihealth DMA-timer method over the whole interrupt, at rest and busy | Syntakt | unit + SyntHack | M | Settles O3; gives Syntakt modders a budget (G2). |
| T5 | Check the trailer and HMAC of 1.40A/1.41/1.42 with your own files (elektron-firmware-tool, digikit) | Syntakt (also DT mk1) | files | S | Settles O1; tells modders whether 1.42 needs re-signing. |
| T6 | Translate SyntHack/machine-45 anchors from 1.41 to 1.42 (byte patterns, not addresses) | Syntakt | files | M | Opens the current OS to mods (G5). |
| T7 | Find the cause of the sticky "bitcrush until reboot" | Digitakt II | unit + custom engine | L | A hidden state bug that any DT2 engine can trigger. |
| T8 | Build an address-translation table DN2 1.11 <-> 1.12 from shared anchors | Digitone II | files | M | Lets dn2mk2 (1.11) and elekloader/dn2-cfw (1.12) share work (G5); settles O6. |
| T9 | Calibrate a DN2 load model against elekloader's busy meter and the deadline margin | Digitone II | unit | M | Predict cost before flashing (G2); settles O12. |
| T10 | Port a DMA-timer load probe (digihealth / A4 0011-style) to the Heat +FX and measure all FX on | Analog Heat +FX | unit | M | First budget for the only fresh platform in phase 1 (G2). |
| T11 | Unpack the MKI and MKII OS files: sections, container, CPU (peripheral census), any DSP section | Analog Heat MKI/MKII | files | S | Turns two ⬜ devices into mapped ones. Good first task. |
| T12 | Compare FPGA sections across devices (sizes, SHA-256, header) and look for the OS code that talks to the FPGA | Heat +FX, A4 MKII, Syntakt, DT2/DN2, Rytm | files | M | First step on "what does the FPGA do" everywhere (G3). |
| T13 | Transcribe the official MIDI CC/NRPN tables from the manuals' appendices into `hardware/common/sysex-and-midi.md` | DT2, DN2, Heat +FX | PDF | S | Official numbers for every control tool (G6). |
| T14 | Fix or document digikit's EMAC fractional-mode emulation against a unit measurement | DT2/DN2 (all ColdFire boxes) | unit + emulator | M | Fewer "works in the emulator" surprises (G4). |
| T15 | Probe free SHARC L2 on DT2 1.17 between `0x200f5a74` and `0x200fa000` on a unit | Digitakt II | unit | M | Settles O7; more room for engines. |
| T16 | Save a project on a grown parameter table, load it on stock, record what happens | Digitone II | unit | S | Tells users whether modded projects stay safe. |
| T17 | Find why Overbridge rejects modified DN2 builds ("incompatible OS version") | Digitone II | unit + Overbridge | M | Mods without losing Overbridge. |
| T18 | Document the project file formats (`.dt2prj`, `.dn2prj`) beyond song slots | DT2, DN2 | files | M | Librarians and converters for musicians. |
| T19 | Check which DN2 SHARC findings hold on the DT2 (and back), item by item, with the 85 % function twin list | DT2, DN2 | files (+ unit) | M | Doubles the value of every SHARC finding (G3). |
| T20 | Collect the machine ids used by DT mk1 mods into one registry | Digitakt mk1 | reading | S | Prevents clashes between mods. |

### Where new findings are most likely

- **Analog Heat (all three):** almost untouched. Every hour of careful static work (T11, T12) produces new facts.
- **Syntakt 1.42:** the current OS has no mods yet. T5 and T6 unlock it.
- **Rules from other platforms:** the Octatrack and A4/Rytm communities found USB, cache and boot rules on the same ColdFire family (A38-A41). Checking them on the small boxes (T3) is cheap and high-value.
- **DT2 <-> DN2:** the two share most of the SHARC code, but their research communities are separate. T19 connects them.

---

*Maintenance:* this file is hand-written. When a row changes, update the status and the date at the top. Phase 2 devices (Octatrack, Rytm, A4/Keys, Model:Cycles/Samples, Machinedrum, Monomachine) will get their sections next; until then, their device files under [hardware/devices/](hardware/devices/) end with "Open" or "Gaps" lists.
