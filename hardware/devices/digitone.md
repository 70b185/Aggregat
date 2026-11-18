# Digitone (mk1) / Digitone Keys

Coverage: **good** (almost entirely through the elekloader family). Projects: [../../catalog/digitone.md](../../catalog/digitone.md)

## Basics
- OS targets: **1.43** and **1.44**. `[doc]` {elekloader-readme}
- Same OS file for Digitone and Digitone Keys (`Digitone_and_Digitone_Keys_OS1.43.syx`); several mods say "nothing has run on a Keys" - treat Keys as untested. `[doc]` {tone-fx} {digicosm}
- Container is **unsigned**, unlike Digitone II; `MAIN OS` loads at `0x40000400` as on DN2 ([`../common/firmware-container.md`](../common/firmware-container.md)). `[doc]` {dn2-firmware-explore}
- Official minimum OS for Transfer-based update: 1.30. `[doc]` {elektron-support}
- **Recovery, used on a unit** (digitone-arp-mod, 2026-10-08, OS 1.44):
  - A test build finished its upgrade but hung on the Elektron logo: the logo did not dissolve, with "H" at bottom left and "1.44" at bottom right.
  - The owner held **FUNC** at power-on, chose **TRIG 4 (OS UPGRADE)**, and sent stock 1.44 via Transfer's *SYSEX TRANSFER -> OS Upgrade via device startup menu* over **DIN** (a Rubix22 interface). The unit worked again.
  - EMPTY RESET and FACTORY RESET are not rollbacks; don't pick them.

  `[hw]` {dn1-arpmod-e04}

## The board and the second ColdFire (taktone, DN1 1.43 with DT1 1.53/1.54 applications) {taktone-docs}
- **The Digitone mk1 is a Digitakt mk1 plus six keys, a second ColdFire and an FPGA.**
  - taktone runs Digitakt 1.53/1.54 main OS builds on Digitone hardware by replacing only section 3 and adapting the panel, LEDs, codec start-up, autosave GPIO and shutdown copy. Four 1.53-based builds were reported working on hardware. `[hw]`
  - Both main CPUs set up **128 MiB DDR at `0x40000000-0x48000000`** (cached and uncached aliases are the same RAM). `[doc]`
- **How the main CPU drives the second ColdFire** (board interface, from taktone-extended, which ran its own engine on it):
  - **Reset:** PB6 held low. Releasing it starts a serial boot.
  - **Upload:** the main CPU is DSPI2 **slave** (eDMA 29, vector 149) and the secondary supplies the clock. Section 6 (a 1,504-byte loader stream; dnfw's section table lists it as 1,492 bytes and "unidentified") loads section 7, which runs at secondary `0x40000400` from entry `0x40000B92`.
  - **Shared SRAM:** FlexBus, main at `0x10000000`, secondary at `0x00000000`. Native use is below offset `0x7a0`: a 928-byte parameter packet at `0x000-0x39f`, then eight mono voices of 32 signed 32-bit samples at `0x3a0-0x79f`.
  - **Handshake:** the secondary writes `HO`/`HA`; the main writes 1 to +2 **before** `B0` to +0. The stock secondary then writes `A5A5` at +4.
  - **Render request:** a PA4 edge triggers the secondary's DTIM0 capture (vector 96). The secondary signals back through EPORT4 (vector 68). One block of pipeline: ~0.667 ms.
  - Clear stale shared words at start, because they can survive a main reset. Never wait in the audio IRQ for late output, and bound the start-up polling. `[hw]`
- **The FPGA bitstream is in section 7:** decompressed from `0x400077A0` to `0x40009000`, **54,664 bytes**, sent as 16-bit words over the secondary's DSPI1. This is the same size as the Analog Heat +FX's and Analog Four MKII's FPGA sections, a strong lead for research map T12. Stock FPGA polling can stall forever, so keep a main-side timeout. `[doc]`
- **Two SysEx addressings:** the startup menu's OS UPGRADE receiver always expects Digitone-addressed SysEx (device `0x0d`). A running Digitakt-based application expects Digitakt addressing (`0x0a`). So recovery to stock Digitone always goes through the startup menu over DIN. `[hw]` (first install confirmed over USB)

### Writing your own engine for the second ColdFire (taktone-extended's contract) {taktone-docs}
- **Split the work:** keep sequencer, locks, LFOs, menu and storage on the main CPU; render on the secondary from a complete control snapshot. Compile secondary code for `-mcpu=54418 -msoft-float`, freestanding.
- **Shared protocol** (taktone's, versioned):
  - a ready tag, committed/completed sequence words, eight 28-byte controls and an XOR checksum;
  - outputs as eight 32-frame int32 mono blocks at `0x3a0`;
  - **only aligned longword writes with readback**: no byte writes to shared RAM, and any mismatch disables submission;
  - one packet outstanding, never block the audio callback, and shut down after 64 consecutive misses.
- **Hook points on the main CPU** (Digitakt 1.53 application): triggers are captured at `0x40077F8E`, before stock source processing consumes them; voice PCM is substituted at `0x40077FBA`, before filter, AMP and mix. On the secondary, init is patched at `0x40000B7A` and the stock engine init at `0x40000B80` is skipped.
- **Memory:** taktone shrinks the native buddy heap from 16 to 8 MiB to reserve `0x4319D6B0-0x4399D6B0` for its runtime, with guard words at both ends. The sample pool (`0x43BAF5F0-0x47BAF640`) and the audio-input ring (`0x47C00000-0x48000000`) stay untouched. This is the same heap-reservation idea as SyntHack's modarea on the Syntakt.

`[hw]` (Sophie on the secondary ran on units) / `[doc]` (addresses)

## Caches at startup (digitone-arp-mod, OS 1.44, emulator trace and the NXP manual) {dn1-arpmod-e04}
- The loader hands over to MAIN with CACR `0x0008c000`: the instruction cache is on, the data cache and store buffer are off.
- Stock MAIN then writes CACR `0xa50ce100` at `0x4000055a`, after its copies. That write invalidates the instruction, branch and data caches and turns caching on. The same CACR value appears on the Rytm and A4 MKII.
- **Code your mod copies before that write is safe. Code copied later must be followed by an explicit invalidation**, because instruction-cache contents can even survive a reset. This is the ColdFire twin of rule A28.
- Real cache behaviour and render deadlines have not been measured on a unit.

`[emu]`

## Where the audio runs (Digiwerk prior-art survey, 2026-10) {dn2-cfw-prior}
- **The Digitone mk1's "DSP" is a second ColdFire.** Section 7 is ColdFire code running only the FM voices; the main ColdFire runs the effects and the mix. Master-effect mods (RingTone, Tone+FX) are therefore ColdFire C hooked through elekloader. `[doc]`
- dnfw's instruction census fits this: DN1 1.43 has 613 MAC/MSAC instructions in a tight ~20 KB region against 50 in DN2 1.11. A third-party board list names two MCF54415 plus a Spartan XC3S50A. `[?]` {dn2-hw}

## Load on the main ColdFire, from a master-effects suite (Tone+FX, OS 1.43/1.44) {tonefx-dev}
- **Budget:** 250 MHz, so **166,667 cycles per 32-sample block**. In the emulator's cycle model, stock plus Tone+FX with all effects off peaks at ~101k cycles per block. With its three heaviest effects on it peaks at ~160k, which leaves 4 % at worst (the p99 is better). The mods' RAM pool is 1.25 MB. `[emu]`
- **The emulator and the unit disagreed:**
  - The unit's CPU meter went from ~70 % to ~87 % at idle between two releases, while the emulator's cycle model said the render had become *faster*.
  - Suspects are what the model leaves out: EMAC mode switches (each handler flipped MACSR between integer and fractional, 12 switches per block), DDR bursts for a 24-bit delay line, instruction-cache pressure from inlining, and UI redraws.
  - **Still unresolved.** `[hw]`
- **Measured on the unit:**
  - Hoisting the MACSR switch to once per block helped.
  - An EMAC-off build idled lower but ran worse while processing, so EMAC stayed.
  - A "fused" single-pass insert, meant to save loads and stores, measured **+15 %** on the unit.
  - Every optimisation is A/B'd on hardware before it lands. `[hw]`
- Toolchain notes from the same project: ColdFire instructions are at most 6 bytes, and `lsl.l #N` takes only 1-8. `[doc]`

## Core mods (elekloader)
| Core | Covers | Notes |
|---|---|---|
| core-dn1-2.0a | OS 1.43 | first core, used by RingTone/Tone+FX/digiring |
| core-dn1-2.0a-os1.44 | OS 1.44 | "lints, links and verifies, but the emulator does not boot stock 1.44 yet" at elekloader v0.4.0 |
| core-dn1 3.0 | digitables | newer core |
| core-dn1 3.2 | digicosm, digichroma | newer core |
| core-dn1 3.3 | digichroma source option | **not yet released** |
| core-dn1 4.1 / 4.1.1 | elekloader v0.9.0 | Tone+FX 4.1a is built against 4.1 |
| core-dn1 5.2.1 | elekloader v0.10.0 (2026-11-09) | 5.0, 5.0.1 and 5.2 were never released |
| core-dn1 5.3 | elekloader main | live-note event; note-on/off entries `0x400eae5c`/`0x400eabb4` (1.44), `0x400eabe8`/`0x400ea940` (1.43) {elekloader-core-dn1} |

`[doc]` {elekloader-readme} {digitables} {digicosm} {digichroma}. Later READMEs say 1.43/1.44 were checked in digikit; the v0.4.0 note says the 1.44 emulator boot was not working - newer state wins, but re-check. `[?]`

Mono machines (SDK, core 5.x) collapse a track to one voice and hand its envelope over on retrigger. `[doc]` {elekloader-core-dn1}

Tone+FX stores per-pattern data in MIDI track 4's 64-byte block (pattern + `0x1BB0`, track stride `0x3D0`, block at track + `0x100`), reserved on channel 16 with a magic word. The blocks of MIDI tracks 1-3 look zero only while those tracks are unconfigured; a configured track writes its channel and page there, so stock data and mod values corrupted each other. `[emu]` {tonefx-pattern-storage}

## Core-owned hook sites (1.43)
`0x40000538, 0x4001900c, 0x40019072, 0x40019d9c, 0x40019de4, 0x40072a34, 0x4009d108, 0x4009e51c`. `[doc]` {elekloader-adapting}

## Effect mods and the `bulk` area (altstrument 2026-10-31 lists five Digitone mk1 mods; elektronmods 19 Digitone entries)
Listings: {alt-digitone}. Layout used by the effect mods: code and state share the **128 KB "mods" share** (older cores) while big audio buffers sit in the profile's **`bulk` area `0x44000000-0x47BE0000`** (~60 MB) - the 0.4.0 apps refuse mods that need it ("do not know the bulk area"), elekloader main is required. `[doc]` {digiprism-readme} {digiswarm-readme} {elekloader-devices}
- **DigiPrism** (formerly DigiChroma; stock OS 1.43/1.44; fxkit + core-dn1 4.1; README title says 3.2, body says 4.1): input effects pedal with four reorderable modules (Color, Motion, Ambience, Grit) x five effects, gesture recorder, 30-second CAPTURE looper, MIDI CC control; 59 KB of code/state in the 128 KB share plus ~7 MB audio; project data tag `DCHR` (56 bytes); p-locks live in one synth track's lock table (LOCK TRACK, default T4 - that track should play no notes or arp in a pattern that uses DigiPrism locks); **CPU guard: DMA timer 0 timing every block, bypass when usage stays above 93 % for 0.2 s**; the `DIGITONE` source option needs core-dn1 3.4 insert audio (not released); presets removed in 0.2; emulator has no DMA timer 0 so its CPU meter is unreliable; 0.2 tested on a Digitone mk1 by its author, never on a Keys. `[hw]/[emu]` {digiprism-readme}
- **DigiSwarm** (formerly DigiCosm; core-dn1 3.2+, several effect mods together need 4.0): 11 engines x 4 variations (MIST, SHARDS, GLIDE, CHOPS, STUTTER ...), 60-second stereo looper with one overdub layer, Hold/Reverse/Bypass, resonant filter, pitch modulation, four-room reverb; buffers 26 MB in `bulk` (input history 10.9 s); 30 KB of the 128 KB share; project data 132 bytes (mods share 480 bytes there, digitables uses 328); loops are lost at power-off ("no file storage location known to be free"); CPU guard thresholds 45 % (fewer new grains) / 30 % (more again, up to 16 heads); CCs 22, 45, 46, 93 accepted but inert; no program changes, no expression pedal; 0.1 runs on the author's Digitone mk1, 0.1.2 emulator-only. `[hw]/[emu]` {digiswarm-readme}
- **Tone+FX** packages: core-dn1-2.0a, digimeter-1.1, digieq-1.0, digiring-1.0, digifold-1.0, digifilter-1.0 (per-voice BP/BP2/COMB/TRASH on up to 4 voices), digictl-1.3; master order ring -> EQ -> fold; DSP shared with the FM voices, "dropouts" possible with several COMB/TRASH voices; verify downloads with `SHA256SUMS`; emulator-tested only. `[emu]` {tonefx-readme}
- Memory facts for planning: the Digitone mk1 OS clears `0x4028E000-0x43229E60`; mod RAM area `0x43EC0000-0x44000000` (1.25 MB, core 4.0); see [`../common/memory-maps.md`](../common/memory-maps.md).

## telos store on the +Drive (elekloader telos 0.2, OS 1.43/1.44) {telos-readme}
- telos keeps flashed-once mods in 2 MB of raw +Drive sectors from sector `0x380000`. Per its README every stock card access is below sector `0x180000`, FORMAT +DRIVE erases only below that, and the smallest eMMC part the firmware accepts ends at `0x3A4000`; the area is no project slot and never shows in Transfer. The directory is kept twice with a sequence number and CRC-32, so a cut write leaves the older copy. Mods link at core-dn1's card-ready event, before the project and the UI task exist. Ran on a Digitone mk1 with OS 1.44. `[hw]` (run) / `[doc]` (sector claims)

## core-dn1 5.4 and the stock shadow for +Drive mods (elekloader, OS 1.43/1.44, 2026-11-15) {elekloader-1116}
- core-dn1 5.4 adds what a +Drive loader (TELOS) needs, with no new patch site: `core_param_install`, `core_stock_info` and `core_tasks`. `core_stock_info` copies the OS image to `0x44200000` before the OS runs. `[doc]`
- The build descriptor (ABI 1.2) carries the stock bytes of every range the flashed build writes, plus a region claim for each region a flashed mod claims. TELOS's linker refuses a +Drive mod site that is not stock on the unit or sits over the flashed build or another mod, writes a site only when no task is stopped in it, and refuses a region that overlaps another or lies outside a free area (link codes 21-28). `[doc]`

## Drum Mode and DigiArp notes: LEDs, record modes, pages (OS 1.44, 2026-11-14/16) {drummode-1117}
Addresses are OS 1.44 as morriess/Digitone-mods states them (Drum Mode 0.8 docs, and the DigiArp notes the repo
removed on 2026-11-16).
- **LED setter** `0x40016e62`: `set(mgr, led, layer, colour)`, the LedManager from core's `ev_key_leds`. It refuses an LED already set in this frame, so a handler that sets LEDs before the stock views wins. Trig keys are LEDs 1-16 (key code - 25). Colours are palette indices: 2 dark, 3 red (stock trig), 5 dim red, 20 white, 21 stock dim white. A mod requests an LED frame by setting byte `+0x21` of the view controller. Colours come from the emulator's copy of the palette; not checked on a unit. `[emu]`
- **Record modes**: the recorder's state is `*(0x419f0dd8)`; `+0x167` KEYBOARD on, `+0x168` GRID RECORDING, `+0x169` live recording, valid while `+0x161` is set (stock getter `0x400adcb4`). The trig-key page shown is the long at `0x41368ce8` (0 = steps 1-16); a trig key in GRID RECORDING sets step 16 x page + key. `[emu]`
- **Page records**: 26 records at `0x4136c558 + 44 x index` (short title, title, 8 knob ids, kind). MIDI track pages: 19 TRIG, 20 MIDI Source (on SYN1 and SYN2), 21 CC Value (FLTR), 22 CC Select (AMP), 23 LFO. A mod page placed after 20 breaks FUNC + push A (turning CHAN on); after 19, 21 or 23 it works. Pages with knob ids 0 need none of core's 10 shared mod parameter ids. Shown view's page list: Brain `+0x54`/`+0x5c`, page manager `+8`, view `+0xc0`, list `+124`/`+128`, current `+144`. The parameter-page view class has vtable `0x401c3f34`. `[emu]`
- **Sequencer timing**: `ev_fire_notes` runs one step before the step sounds, so a mod that reacts at the play moment must hold the step's notes back one step. In digiemu the sequencer runs only with audio on (the render clocks it). The stock OS never sends a synth track's sequence as MIDI, only live trig-key notes. `[emu]`
- **Note paths** (DigiArp notes, from disassembly): KEYBOARD note-on `0x4003b198` `(this, source, track, note, velocity)`, note-off `0x4003b26e` `(this, source, track, note)`; held keys are 24-byte entries at `this+172`, each released with the track and note recorded at press. The release-all path `0x4003bc0e` and entries flagged at `a3@(1)` do not all go through `0x4003b26e` (a suspect in I136). The DIN send routine `0x40002a3a` masks interrupts (SR = `0x2700`) while it copies a message. The ARP page reads mode at `+0x10f` and the step mask at `+0x114` through the sound's method 10, the same bytes the engine reads. `[doc]`
- **RTOS priorities**: higher number = higher priority, 0 is the init task; a mod worker at priority 1 shares that level with the stock task at `0x4008cf00`. `[doc]`

## Drum Mode off, DigiArp on core 5.3, mod page slots (OS 1.44, 2026-11-17) {drum-mode-1118}
- **Two routines named `fw_note_on`/`fw_note_off`:** DigiArp names the MIDI send routines `0x400ee232 (channel, note, velocity)` and `0x400ee29e (channel, note)`; core-dn1 5.3 exports the same two names for the track-level note on/off that KEYBOARD mode uses (six and three arguments). elekloader refuses a build where two modules export one name; DigiArp works on core 5.3 once its names are changed (`digiarp_midi_on`/`_off`). `[emu]`
- **core-dn1 5.2.1 moved two of core's own hooks** to make room for DigiArp's sites; the rebuild declares core 5.2.1 as its minimum. `[doc]`
- **Step 1 of a run is prepared when the previous run stops,** not at PLAY (the sequencer prepares each step one step ahead), so `ev_fire_notes` and `ev_fire_vel` see step 1 then: a change made while stopped (a mod's on/off, a mute, a velocity) reaches step 1 only from the following run. The routine that prepares step 1 is not found yet. `[emu]`
- **A MIDI trig has one velocity:** with several lanes on one step Drum Mode sends the loudest unmuted lane's velocity; with Drum Mode off stock plays the pattern data unchanged at the trig's VEL (default 100). `[emu]`
- **Stock on a MIDI track:** with the sequencer stopped and outside KEYBOARD mode, trig key 1 sends nothing. `[emu]`
- **Mod page slots:** Drum Mode uses slots 27 and 28; DigiTables also claims 27 (OS 1.43 only so far); CTRL-PLUS uses 29; core claims slot 30 for a second TRIG page as soon as a mod puts knobs there (DigiChoke, DigiLoop, DigiPCSound). Two mods on one slot cannot be built together. `[doc]`
- **UI hang in the emulator, cause open:** one exact sequence (Drum Mode off, two bars, trig key 1, then the Mod Menu opened with YES right after releasing the track key) stopped digiemu's UI task every time (no UI ticks, draws or keys) while sequencer and audio ran on; not with a 300 ms pause before YES. It may be the emulator, core's Mod Menu, stock or Drum Mode. `[emu]`
- **Emulator trace caveat:** digiemu hooks added after boot never fire for code already translated, so count handler entries from boot. `[emu]`
- **Lane strip vanishes on page switches (unit):** reported on 0.8 when browsing e.g. LFO then SYN1; not seen in digiemu. Suspected: stock repaints the whole page after the mod drew its corner, and the mod redraws only on change. `[hw]` (report) / `[?]` (cause) (I141)

## Where a note's parameter locks are applied (Modwerk `ev_note_locks` proposal, OS 1.44, digiemu only, 2026-10-28) {modwerk-dn-notelocks}
- **Lock list site:** the render (`0x4009d120`, once per note event) loads the event's lock list pointer (`event+0x38`) at `0x4009eae0` (2 instructions, 8 bytes) just before the call that applies it, `0x4009bee8(track, list)`. Not located in OS 1.43. `[emu]`
- **Sequencer note events** are queued through `0x40100178`, each of type 1 with a lock list. `[emu]`
- **A DIN MIDI note** reaches the OS's byte parser and goes on to a worker task, but no event reached the render queue within about 700 ms for notes on channels 1, 2 and 14 (INPUT FROM MIDI+USB). A MIDI note's event layout is still unknown. `[emu]`

## Notes
- digihealth 1.1 brings SYSTEM INFO only; FAST AUDIO is not ported to Digitone. {digihealth}
- DigiSplash and DigiCandy support Digitone mk1 + Keys at OS 1.43. {digisplash} {digicandy}
