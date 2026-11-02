# Feature overlap: the same idea built more than once

Many features have been built independently on several Elektron boxes, often by people who never looked at each other's work. This page lines them up, so a new project can start from the closest existing solution instead of from zero, and so the community can see where a shared piece (a portable engine, a table, a measured rule) would serve everyone.

Compiled 2026-11-02 from the catalogue notes and the documents read for [`hardware/`](hardware/README.md). It is not exhaustive. "Unit" means the project reports it running on a real device; "emulator" means it has only been shown in an emulator so far. Project details: [MODS.md](MODS.md); which entries are forks or copies of each other: [PROJECT-FAMILIES.md](PROJECT-FAMILIES.md).

---

## Engines carried from one Elektron box to another

The most common pattern. The engines come from the source device's own code or from open re-implementations, and the target box supplies the voice slot, the filter, amp and effects path.

| Engine family | Built for | Project | State | Shared piece worth knowing |
|---|---|---|---|---|
| **Machinedrum** (TRX, EFM, P-I...) | Digitone II | dn2mk2 (PERC, 34 machines), Overtone (MACHINEDRUM) | unit | |
| | Analog Rytm MK1 | hugz202's Rytm mods (TX-8/TX-9 machines) | unit | |
| | Model:Cycles | Elektron-Model-Machinedrum (TRX-B2, TRX-SD, TRX-CH) | TRX-B2/SD on a unit | |
| | Digitakt mk1 (via a Pi) | digitakt-sidecar (TRX-B2) | prototype | |
| | Machinedrum itself | MDX, Kitbasher, em's firmware, Machinedrum USR machines | unit | |
| | plug-ins and other hardware | MModule, Machinemodule, ModuleDrum, OP-XY MNMD | - | **mdkit**: EFM/TRX/P-I voices as standalone C99, **CC0** - the easiest legal starting point for any port |
| **Monomachine** | Digitone II | dn2mk2 (Monomachine machines) | unit | |
| | plug-ins | Monomodule and its ports, Monomachine Lab | - | |
| **Digitakt II sample machines** (ONESHOT, WERP, STRETCH, REPITCH, GRID, SLICE) | Digitone II | dn2mk2; armio's T1E2 (dn2-dt2-firmware-research) | unit | dnfw showed 85 % of DT2 SHARC functions have a twin in the DN2, so the port is a transplant, not a rewrite ([digitone-2-internals.md](hardware/devices/digitone-2-internals.md)) |
| **Digitakt mk1 sample machines** | Syntakt | Synfact | experimental | |
| | Digitone mk1 | taktone (runs the whole Digitakt application on Digitone hardware) | unit | |
| **Sampler, other designs** | Syntakt | SynCrackd (replaces Twinshot) | - | |
| | Model:Cycles | Cycles One-Shot, Model-TG, Modded Cycles' sampler | unit | |
| | Digitone mk1 | Sampletone | - | |
| **Syntakt engines** | Model:Cycles | Modded Cycles (needs the user's Syntakt OS file), Supermodel | unit | Supermodel measured that they cost about the same instructions as stock voices but more cache, which slows the unit ([model-cycles-samples.md](hardware/devices/model-cycles-samples.md)) |
| **Sophie** (Matt Estela's percussion algorithm) | Digitakt mk1 | digisophie | unit | **digisophie's fixed-point version** is reused by DT-FM (Digitakt) and taktone-extended (Digitone mk1 second CPU). radiohagen's Octatrack module and Overtone (Digitone II) also ship a Sophie voice; their READMEs don't say which code it came from |
| **Plaits** (Mutable Instruments) | Model:Cycles | plaits-on-models (fixed point) | emulator | a fixed-point Plaits port for ColdFire boxes |
| | Digitakt II | dt2-machine-lab, digitakt-ii-research (lessons in [digitakt-2-dsp-optimizing.md](hardware/devices/digitakt-2-dsp-optimizing.md)) | dt2-machine-lab: first unit trial crashed (a ColdFire-excluded instruction); the correction has not run on a unit yet | |
| **FM** | Syntakt | SY FM4 (in Synthack-OS) | unit | |
| | Digitakt mk1 | DT-FM | - | |
| | Octatrack | octabam FM synth machine, octatrick two-op FM | unit (octatrick on an MKI) | |
| **Granular** | Digitakt mk1 | digigrain, diginular, Vampire Manga OS (GRAIN on Digitone) | digigrain unit | digigrain's lesson: grain length independent of pitch, or the worst case freezes the UI |
| | Digitone mk1 inputs | DigiSwarm | unit | |
| | Model:Cycles | Model-TG (granular mode) | - | |
| **Acid / 303** | Octatrack | aCiDtRacK (OCTA-303) | partly proven | |
| | Digitone mk1 | Phreakoid | - | |
| | Model:Cycles | Modded Cycles (Open303), Supermodel (ACID) | - | |

---

## Sequencer and performance features

| Feature | Device | Project | State | Note |
|---|---|---|---|---|
| **Direct pattern jump** | Digitakt mk1, Digitone mk1 | DIRECT JUMP (ClaidArremer, both devices) | - | |
| | Digitone II | Overtone (instant pattern switch); dn2mk2 (announced "coming next") | Overtone unit | two DN2 implementations; compare before building a third |
| | Octatrack | KYOTI, octatrick | unit (MKI) | KYOTI also keeps notes on Rytm direct jump (`reference/AR_DIRECT_JUMP.md`) |
| **Scales / scale lock** | Analog Four MK1 | hugz202's A4 mods (35 scales, Digitone II style) | unit | the A4 MKII OS itself holds 36 scales with pitch-class tables (analog-emu, [analog-four-keys.md](hardware/devices/analog-four-keys.md)) |
| | Octatrack | PassOS (36 Digitone II scales), octatrick (quantizer), octamax (arp scales), radiohagen MIDI Scales | - | **four Octatrack scale implementations** |
| | Model:Cycles | Chord Keys (scale-locked chord keyboard) | - | |
| | Digitone mk1 | digitone-arp-mod (scale arp), DigiTriad (key detection) | arp: first unit trial failed and was recovered | |
| **Arpeggiator** | Digitone mk1 | digitone-arp-mod | in progress | |
| | Digitone II | Overtone (two arps), Digiwerk (arp on MIDI tracks) | unit | |
| | Model:Cycles | Modded Cycles | - | |
| **Alternative sequencers** | Digitakt mk1, Digitone mk1 | DIGISEQ, DIGISNAKE (both devices), TRIG PAGES (TURING) | - | |
| | Octatrack | TrackPatterns (per-track patterns), Octaplay (playhead modes) | TrackPatterns on one MKII | |
| **Scenes / macros** | Digitakt II, Digitone II | digi-macro | DT2 earlier builds on a unit | |
| | Digitone mk1 (DT application) | taktone-extended (4 scenes) | unit | |
| | Octatrack | midisc / MIDI SCENES in octabam | unit | |
| **Kits instead of parts** | Octatrack | em's Octakit (256 kits) | - | changes saved data: going back to stock can lose kit data |
| **Perform kit fixes** | Digitakt II, Digitone II | digitakt2-perform, DigiRust | partly on a unit | |

---

## Effects and mixing

| Feature | Device | Project | State | Note |
|---|---|---|---|---|
| **Master / bus compressor** | Syntakt | Synthack-OS master-comp (drives the **analog VCAs**) | unit | detects on ADC, applies through control voltages ([syntakt.md](hardware/devices/syntakt.md)) |
| | Digitakt mk1, Digitone mk1 | PUMP (both devices) | - | |
| | Digitone II | Digiwerk 3-band compressor (CMP3) | unit | needed the grown parameter table |
| | Octatrack | KYOTI and octabam sidechain compressor, aCiDtRacK dbx-160-style | unit | |
| | Analog Rytm MK1 | hugz202's DUCK (at the voices' analog VCAs) | unit | |
| | Analog Rytm MKII | rytm-mods-src (compressor preview estimator for the analog compressor) | - | the MKII has no gain-reduction readback |
| | Model:Cycles | Supermodel sidechain | - | |
| **Extra send effect / chorus** | Syntakt | Synthack-OS fx3 (third send) | unit | |
| | Analog Rytm MK1 | hugz202's FX SENDS (A4's chorus controls as a third send) | unit | a one-to-one port of the A4 chorus was rejected as too costly (~10 % of the Rytm) |
| | Digitone II | Digiwerk (flanger in the chorus slot, tape echo, spring reverb) | unit | |
| **Master effect suites** | Digitone mk1 | Tone+FX / RingTone | unit (3-day stress test) | its CPU optimisation log is the best ColdFire load study for the DN1 |
| | Digitone mk1 inputs | DigiPrism, DigiSwarm, the DigiHalo/Triad/Tide/Hoard/Reel family | unit | |
| | Digitakt / Digitone mk1 | Vampire Manga OS (34 insert effects) | public test | |
| **Extra filters** | Digitakt mk1 | DigiFilter | validated (one cosmetic gap) | |
| | Digitone II | digitone-2-mod-hack (LOWPASS) | - | |
| **Bit crush / drive inserts** | Analog Four MK1 | hugz202's digital path (drive, bit, crusher per track) | unit | |

---

## Modulation

| Feature | Device | Project | State | Note |
|---|---|---|---|---|
| **Déjà Vu LFO** (repeatable random loop) | Digitakt II | digitakt-ii-research (DV-F, DV-T) | unit (1.17 initial validation) | Kari Gardarsson's design |
| | Digitone II | Digiwerk base 0.2 (Déjà vu LFO, in the track's key) | unit | |
| | Syntakt | Syntakt Firmware Workbench (DV-H) | - | |
| **Extra LFO** | Digitone mk1 | LFOX (third LFO) | - | |
| | Model:Cycles | Modded Cycles, Supermodel (second LFO) | - | |
| | Digitone II | dnfw's LFO4 plans; Overtone reuses LFO 3's storage for ENV2/ARP2 | - | |
| **Random / generative** | Analog Four MK1 | hugz202 (random track) | unit | |
| | Analog Rytm | rytm-mods-src, rytm1_mods (euclid accents, humanise, random LFO) | - | |
| | Model:Cycles | Supermodel (sequence generator) | - | |

---

## Platform pieces and tools

| Feature | Device | Project | State | Note |
|---|---|---|---|---|
| **Load meter / diagnostics on the unit** | Digitakt mk1, Digitone mk1 | digihealth | unit | DMA-timer method; the template for most others |
| | Analog Rytm MKII, Analog Four MKII | analoghealth (port of digihealth) | unit | |
| | Digitone II | elekloader dspbusy, dnfw USB probe and loadmap, dn2mk2 FUNC-held meter | unit | the two DN2 idle measures disagree (CONFLICTS O15) |
| | Digitakt II | digikit, the repo owner's probe and telemetry builds | unit | |
| | Analog Four MK1, Rytm MK1 | hugz202's probe builds | unit | |
| | Octatrack | Modwerk stats, octabam LOAD METER, KYOTI load audit | unit | |
| | Model:Cycles | Supermodel's counter and worst-block profiler | unit | |
| | Machinedrum | Kitbasher CPU indicator | unit | |
| **Boot splash** | Digitakt mk1, Digitone mk1 | DigiSplash, digisplash-ii | - | |
| | Digitakt II | digitakt-ii-splash-screens | - | |
| | Digitone II | dn2mk2 start-up animation | unit | |
| | Syntakt | Synthack-OS splash | unit | |
| **USB multichannel audio** | Model:Cycles, Model:Samples | ms-multi-output (6 ch), elektron-model-tweaks (16 ch), Modded Cycles | unit | Supermodel's fix: send at a fixed time, not right after a variable render |
| | Octatrack | octatrick (20 ch), octemu's USB audio (used by PassOS) | MKI tested | octemu loads its USB-audio payload from the CF card |
| **Patcher / loader platforms** | many | elekloader, Modwerk, octabam, Spokes, Cycles Engines, Kitbasher, Digiwerk Patcher | - | see the loader section of [MODS.md](MODS.md) |

---

## What this suggests

- **Portable engine cores already exist:** mdkit (Machinedrum voices, CC0), digisophie (Sophie, fixed point), plaits-on-models (Plaits, fixed point) and digigrain (bounded granular). A new port should start from one of these rather than from the original source.
- **Two or more parallel implementations** of the same feature on the same device: direct jump on the DN2, scale handling on the Octatrack (four), load meters on the DN2 (three, which disagree). Comparing these is cheap and likely to find bugs in one of them.
- **Measured rules travel better than code:** a ColdFire or SHARC lesson found by one project (cache, ISA, load governor, USB timing) applies to all boxes with the same chip. Those are collected as rules A1-A44 in [hardware/AGENT-RULES.md](hardware/AGENT-RULES.md).
