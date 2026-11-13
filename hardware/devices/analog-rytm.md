# Analog Rytm (MKI, MKII) - OS 1.73 / 1.74

Coverage: **first profile** (phase 2). Source: ethernet8023/rytm-fw-re (`STATUS.md`, `docs/flash-driver.md`, `docs/usb-reflash.md`),
read 2026-11-02, plus the phase-2 catalogue. Key {rytm-fw-re}. MK1 section: hugz202/AE-analog-rytm-mods (`docs/HAZARDS.md`, `docs/MANUAL.md`, `re/`, mod design notes), key {rytm-mk1-mods}, and analog-emu's `MK1-PORT.md`, key {analog-emu-mk1}. Projects: [../../catalog/analog-rytm.md](../../catalog/analog-rytm.md).
Most mods target **MKII OS 1.73** (MrScruff's rytm-mods, Chopshop) or **1.74** (rytm-fw-re, analoghealth); elekloader has a core for the
Rytm MKII (`core-ar2`).

## Platform (MKII, OS 1.74)
- CPU: **ColdFire MCF5445x** (`-mcpu=54455`, big-endian) - like the Octatrack's family, not the MCF5441x of the small boxes. DDR from `0x40000000`, the OS at `0x40000400`, stack region `0x48000000`. `[doc]`
- Sections of 1.74: 2 bootstrap (42,302 B, loads at `0x07020000`, runs in SRAM `0x80000000`), **1 FPGA** (Xilinx bitstream, 149,516 B, sync `AA99`), 3 MAIN OS (3,005,432 B), 8 the shared ARM Cortex-M image (159,948 B, identical across several devices; see [firmware-container.md](../common/firmware-container.md)), 5 meta. `[doc]`
- **The display is driven through the FPGA:** a byte-FIFO bridge at `0xec07xxxx` (status `0xec070004`, data `0xec07000c`). The 128x64 panel uses two static 1,024-byte planes with diff flush. `0xec074xxx` is the MIDI UART (divisor 132 MHz / (31,250 x 32)). The LED engine is fed through the same FPGA SRAM family. `[doc]`
- Boot contract:
  - The bootstrap unpacks MAIN to `0x40000400`, sets VBR = `0x40000000` and calls the word at `0x40000400` as an **entry function pointer** with one stack argument. It is not a reset SP/PC header.
  - The stock entry sets SP to `0x48000000`, fills 256 vectors, sets up INTC/GPIO and caches (CACR `0xa50ce100`), then starts the kernel. `[hw]` (a from-source replacement OS booted on a unit)
- **Which ColdFire is open:** rytm-fw-re builds with `-mcpu=54455` (MCF5445x), while analog-emu identifies the Rytm MKII as MCF5441x (same entry code, CACR/ACR values and peripheral blocks as the A4 MKII). Both are V4 cores with EMAC and no FPU, so code built for either runs; peripheral addresses are what to check. See CONFLICTS O14. `[?]`
- **A 16.3 MB unreferenced hole at `0x41ad0000`** passed a memory probe on a unit (7 candidate regions all passed). `[hw]`

## Flash and recovery
- SPI NOR on DSPI `0xfc05c000`; layout: `0x00000-0x7FFFF` bootstrap + FPGA (**never write**), `0x80000+` the MAIN OS image. Images are staged in DDR at `0x3FF80008` with the same `size / checksum (i ^ word[i])` header as the small boxes. `[doc]`
- **The bootstrap supports several flash vendors and picks the geometry from the RDID:**

  | Vendor | Page | Erase block |
  |---|---|---|
  | Spansion `0x01 2018` | 0x200 | 0x40000 |
  | Winbond `0xEF` | 0x100 | 0x10000 |
  | Macronix `0xC2` | 0x100 | 0x10000 |
  | ISSI `0x9D` | 0x100 | 0x10000 |
  | EON `0x1C` | 0x100 | 0x10000 |

  The geometry therefore differs per unit. This very likely explains the two geometries reported for DT2/DN2 (CONFLICTS O8) and why a Spansion-only protection command does nothing on a Winbond unit (O9). `[doc]`
- The bootstrap also gates on a version-date field (image +0x10, 4 ASCII chars) per chip family, and refuses older versions. `[doc]`
- **Recovery is FUNC at power-on, OS UPGRADE, DIN MIDI only.** The startup-menu receiver never enumerates USB (verified: no USB events while it shows READY TO RECEIVE). USB updates are received only by the running OS. **Once a custom OS that does not implement the USB update is on the unit, the only way back is DIN** ("one USB shot per custom-OS cycle"). `[hw]`
  - rytm-fw-re rebuilt a DIN sender from an FT232RL (2 x 200 ohm) and streamed stock 1.74 back in about 10 minutes. `[hw]`
- Rule for every device: a replacement or heavily modified OS should keep the in-OS USB update working, or the user needs a DIN interface. See rule A36 in [`../AGENT-RULES.md`](../AGENT-RULES.md).

## Analog Rytm MK1 (OS 1.73 / 1.74) {rytm-mk1-mods} {analog-emu-mk1}
- **Board** (static analysis, `[doc]`):
  - same CPU family and OS framework as the MKII;
  - **ELE2 file with one section** (MAIN OS);
  - 128 MB DDR, boot/config flash as parallel NOR on FlexBus CS0 (8 MB at 0);
  - voice SPI on DSPI2 with eDMA ch 29 (492-word frame, as the MKII);
  - codec on SSI0 + SSI1 (8 words each);
  - 122x32 LCD, 1-bit LEDs;
  - **USB full speed only**.
- **The bootstrap is inside MAIN OS, as on the A4 MK1** (rule A38):
  - On 1.74 its version words are at `0x4028c768` and its image at `0x4028c770..0x402a1b84` (87,068 B, ending in its USB descriptors). On 1.73 the same image sat 0x60 lower.
  - At every boot the startup code compares that version with the one in flash at `0x1fff8`. If the embedded one is newer, the OS shows BOOTSTRAP UPGRADE and rewrites the bootstrap sectors. `[doc]`
- **Container pitfall:** elektron-firmware-tool padded ELE2 containers to 2 bytes; the stock MK1 file pads to 4. A "no change" rebuild therefore came out 2 bytes short and failed the null-repack check. hugz202 patches the tool to pad to 4. **Always run a null repack of the stock file first** (rule A23). `[hw]` ([I40](../INCIDENTS.md#i40-a-no-change-rebuild-came-out-2-bytes-short))
- **Load (measured with a probe build on a MK1, OS 1.73):**
  - Stock audio alone is about **77 % of the CPU with nothing playing**.
  - One readout showed CPU 78.3 %, the audio interrupt at 61.2 % average and 74.0 % peak.
  - With a first chorus-plus-comb send on, the CPU reached **100 %**.
  - The CPU runs at roughly 120 MIPS. A one-to-one port of the A4's chorus (~8,000-9,000 instructions per block) would cost ~10 % of the unit and was rejected.
  - Same lesson as A34: replace work, and keep added effects idle when no track sends. `[hw]`
  - **Idle mods add up (Modwerk, 2026-11-06, OS 1.74, sequencer stopped, block timed on DTIM0):** in a 16-module set the idle block took **72.9 %**; making three modules return early when they have nothing to do (Ping Pong Loop's voice gates in stock's sample prefetch, Sample Playback Rate's block handler, QPERF) brought it to 70.6-71.1 %. Each module's idle path is part of the budget. `[hw]` {modwerk-rytm-idle} ([I49](../INCIDENTS.md#i49-idle-paths-of-sixteen-mods-cost-two-percent-of-a-rytm-block))
- **Cached vs uncached DRAM:** the chorus's delay line moved to a cached DRAM address (`0x428a0000`) in v2. The same rule applies as on the A4 MK1: don't touch uncached memory per sample. `[doc]`
- **RAM is not cleared at power-up** in the regions the mods use: clear your own buffers before use. `[hw]`
- **Dead code to reuse:**
  - The machine table (53 entries at `0x402543d0` on 1.73) holds **19 hidden machines** whose voice-mask byte is 0, so no list offers them. They look like earlier development versions of the shipped machines, and none has been played on hardware.
  - TEST machines (SD/RS/CY/CB) also exist.
  - hugz202 reuses their code space. Its only reference is its own table entry, which the mod repoints, and the build checks the stock bytes. A kit received over SysEx that names a hidden machine then plays the mod's machine or nothing. `[hw]` (the `full` image ran on a MK1)
- **Recovery:** FUNC at power-on, TRIG 4 (OS UPGRADE), stock `.syx` over **DIN MIDI** (Transfer's legacy mode). `[doc]`

## Mod machines in hidden slots (MKII OS 1.74, elekloader core-ar2 0.5; Modwerk's SDK guide, 2026-11-05) {modwerk-rytm-machines}
Read statically and checked in rytm-emu; the voice figures were measured on a unit.
- **Slots and claims:** a mod machine takes one of the hidden slots 34-43 through `core_machines` and claims it as `machine:<slot>` (rule D6c). Kits store the slot, so a kit naming it loads as DISABLE on a build without the mod. `[doc]`
- **From core-ar2 0.13 (2026-11-10) also slots 44-52**, the TEST machines. Their records carry no MIDI, so core copies each used knob's CC and NRPN from slot 35's record at the same sound index; the records' list-kind word (+0x24) stays 0, so a knob there is not offered as an LFO, velocity or aftertouch destination. Fewer knob records than 34-43 on several voices (e.g. SD TEST 9-12, 15, 16). `[doc]` {elekloader-core-ar2}
- **Per-voice trig and velocity (0.13):** core's trampoline per slot latches the owner track (`0x40291138[v]`), the trig state (`0x8000e508 + 4t`, 1 trig, 2 release) and the velocity word (`0x800067c4 + 2t`) before the engine runs; `core_voice_trigged(v)` and `core_voice_velocity(v)` read it. A knob on a record that is 14-bit in stock keeps a fraction in its engine word: read the high byte for the shown value. `[doc]` {elekloader-core-ar2}
- **Knob ids:** mods get their own parameter ids from 555 on; a mod declares `"knobs": n` and the linker hands out n ids in a row (`__knobs`). `[doc]` {elekloader-format}
- **Screen calls (0.13):** text, fonts, bitmaps, the level read-out field, progress boxes and keys go through stock's own routines (font objects at `0x417e381c + 8i`, text `0x4007154c`, progress window as COPYING SOUNDS uses it); no stock code or glyphs are copied. `[doc]` {elekloader-core-ar2}
- **Fixed knob positions per slot** (SYNTH page, sound indices): slot 40 A10 B13 C12 D11 / E14 F16 G15 H9; slot 41 A10 B13 C15 D11 / E16 F14 G12 H9; slot 42 A10 B12 C13 D11 / E16 F14 G15 H9. `knobs[k]` in `machines.h` is sound index 9 + k, not the panel order. Indices 9 (LEV), 10 (TUN) and 11 (DEC) keep stock's MIDI CCs. `[doc]`
- **Where it appears in the machine list:** a 34-byte section table at `0x40257d70` (read by `0x400df664`) files stock machines 0-33 under a section; slots 34+ have no entry and sort above every stock machine of their group. A machine with `home` -1 lands after DISABLE in slot order. Core 0.5 adds a 4-byte entry (slot, section, 0, 0) so a mod machine sits under its section's header. The SY comparators (`0x400bdc5e`, `0x400bde1c`) rank only SY DUAL VCO, SY CHIP and SY RAW, so a mod SY machine sorts after them. `[doc]`
- **Driving a dual-oscillator voice** (BD, SD, RS; control frame `0x800063c0`, TUNE1/TUNE2/LEVEL1/LEVEL2 at `+90`, `+98`, `+106`, as SY RAW `0x4011aa4c` writes them). Measured on a unit:
  - A tune word is 16 x Hz after stock's trim `0x401197f4`. Write it every block and force it on the trig; without that the oscillator crawls at a few Hz. Below about 40 Hz oscillator 1 runs sharp and oscillator 2 flat.
  - A LEVEL word acts within its block. Its loud end saturates mostly after AMP VOL, so it is not a drive control.
  - An amp record at -128 still passes about -45 dB: write the LEVELs to 0 when a note ends. `[hw]`
- **FUNC + turn drops its first detent** on the sound page (flag `0x417e32b8`); jumps come from a std::function in the parameter's RAM record (`0x419a4888 + 84 * id`, manager `+0x4c`, invoker `+0x50`). `[doc]`

## More from the MKII mod and research projects (rytm-mods-src OS 1.73, analog-rytm-mkii-research OS 1.72) {rytm-mods-src} {ar-mkii-research}
- **A zero run is not a free cave until it survives a hard run on the unit.** octatrack-mods had shipped code into a region that came from someone else's survey. The mod worked with the sequencer stopped and failed during playback, because the region was really `.bss` that the audio engine wrote. rytm-mods-src's check: fill the candidate with a known pattern, flash, run playback, sampling, Overbridge and +Drive access, then read it back. See rule A43. `[hw]`
- **Pick the narrowest assembler target that assembles.** The project went from `-mcpu=5407` (ISA_A) to `-mcpu=5475` (ISA_B + EMAC) only when a mod needed EMAC, and checked that the earlier mods rebuilt byte-identically. Too narrow a target fails at assembly time; too wide a one silently accepts instructions the chip lacks (rule A42). `[doc]`
- **Sections 5, 2, 1 and 8 must come back byte-identical**, and the bootstrap (section 2, 42,302 B at `0x07020000`) is checked by hash. Elektron's own bootstrap upgrade, which runs on the first restart after some OS updates, is the one moment the safety net is down: don't cut power then. `[doc]`
- **The master compressor is analog** (after the analog mix and the master distortion). The MKII firmware never reads its gain back (the MK1 did, through the on-chip ADC input AN1), so any gain-reduction display on the MKII is an estimate. A CC beyond an enumeration's last value makes the unit show ERR instead of clamping. `[doc]`
- **Sample bit reduction is not done on the ColdFire.**
  - The BR knob becomes a per-voice command word, `0xB31407FF + ceil(BR x 0x40000 / 127)`, sent over DSPI1/eDMA to the external audio hardware.
  - The main OS contains no mask or shift that would apply it to PCM.
  - So sample playback processing on the Rytm MKII likely sits in the FPGA/voice hardware: a lead for research map T12. Static and emulator work only.

  `[doc]`
- A third reading of the CPU: analog-rytm-mkii-research models the Rytm MKII as MCF5441x (conflict O14), with MAIN at `0x40000400` (2,903,032 B on 1.72) and the stack at `0x48000000`. `[doc]`
- **Porting MKII mods to the MK1: same code base, different data** (gdeo607/rytm1_mods, OS 1.73) {rytm1-mods}:
  - Most routines are byte-identical, but the parameter info record is 88 bytes on the MK1 and 84 on the MKII.
  - UI glyphs and the screen differ (122 px wide on the MK1, 128x64 on the MKII), so anything that draws its own pixels needs a redesign, not new addresses.
  - Every RAM address (`0x41xxxxxx`, `0x8000xxxx`) has to be found again.

  Each of these would have been a silent bug. `[doc]`

## Modwerk Rytm modules and stock behaviour (OS 1.74, 2026-11-10) {modwerk-rytm-modtests}
Read 2026-11-10 from Modwerk's Rytm guide, module manifests and test files. Unit runs are the module authors'.
- **Encoder events:** byte +20 of an encoder event is set while that knob's own push-button is held. It is not FUNC; read FUNC from the key table. `[hw]` (I55)
- **Machine list:** stock loads each machine as the list scrolls (UP, DOWN or any knob, with or without FUNC); YES only confirms, NO restores the machine the list opened with, and there is no undo for a machine change. rytm-emu does not pass emulated knob turns through stock's knob accumulator, so knob behaviour cannot be tested there. `[emu]` {modwerk-rytm-machines}
- **FX edit save:** stock maps live FX words 38-41 to stored slot 0, so a setter edit of those hidden words overwrites the delay's saved TIME (SB18). Modwerk's base redirects them to its own kit storage. `[emu]` {modwerk-rytm-machines}
- **Lock saves** keep bits 14-8 of a lock word; bits 7-1 survive only in a fine lane, one per track and word, which stock writes when the parameter row's fine flag (row word `+0x14`, read at `0x400071a6`, lane write `0x40009216`) is set: STA, END, LFO DEP and the machines' tunings have it, sample TUN and FIN do not. Bit 0 is always lost; test with odd values. (Corrects the earlier "bits 14-1", CONFLICTS S19.) `[emu]` {modwerk-rytm-machines} {modwerk-rytm-smpl}
- **Shared voices:** the amp-envelope record is at `0x40109c24`, 18 bytes per voice per block. A trig still takes a shared voice (CH/OH, RS/CP, MT/HT, CY/CB) even when its amp is held silent, so the partner is cut; dropping the trig in the audio-block trig loop (command byte `0x8000e508[track]`) keeps a track silent without that. A pad's light is a running mean of its own voice's level, so a dropped trig leaves the pad dark. `[doc]`, the silencing route `[hw]` (Silent Pad+Trig 0.8.0, run AT04)
- **CV input:** EXP/CV IN 1 in CV mode read raw `0x3fcc` at 0 V, `0x6048` at about 2.5 V and `0x7fff` at 5 V; with nothing plugged in it reads below CV ZERO. `[hw]` (run T221, driven from an A4 MKII CV out)
- **Stock mutes and MIDI:** on stock 1.74 a muted or soloed-out track still plays incoming MIDI notes (AUTO and its own channel, USB and DIN), and a held note keeps ringing after a CC 94 mute. By design, not a bug. `[hw]` (MIDI Mute's stock baseline)
- **Kit list:** on a unit the kit list draws a marker after kits 02-16 that rytm-emu's screen lacks (I56). `[hw]`
- **Load on Modwerk's base** (core-ar2 0.7 plus its health meter): about 74-75 % idle; 85 % with Compressor Preview open while playing; 92.9 % (DSP 86 %) with four Voice DAC voices beside LFO RND. `[hw]`
- **Stuck pad:** on one unit stock's key table once reported pad 1 held with no pad down; cause unknown. `[hw]`

## Room for +Drive mods (elekloader core-ar2 0.12, main after v0.10.0) {elekloader-core-ar2}
core-ar2 0.12 adds spare entries that a "Drive Loader" fills at boot: 256 per event table, 10 machines (hidden slots 34-43), 149 pages (the limit is 10 views x 16 pages), 256 parameters and 8 step owners in total, for about 20 KB of RAM. +Drive mods get no lock codes; codes 42-127 come from the flashed build. `[doc]`

Sidecar 0.4.3: every remote redraw the Sidecar's patched Rytm firmware receives redraws the whole Rytm screen; at 20-40 a second users saw screen and keys respond late, so redraws are now capped at 5/s (10/s for animations). `[hw]` (user reports) {sidecar-rn}

## +Drive mods loaded at boot (elekloader drive-loader-ar2 0.4, core-ar2 0.12, OS 1.74) {elekloader-drive}
- **A third Data route.** The loader adds a `/mods` route to stock's Data router (the one Transfer and Elektroid use for `/projects` and `/soundbanks`), registered at `0x400a005e` in the resolver's getter; uploads travel in stock's data container (31-byte header, 12-byte footer with CRC-32; a stock 1.74 project reads family 2, device 5). Folders go three deep; stock's rename moves a folder only within its parent, so a move elsewhere is mkdir plus one move per item, as SAMPLES' MOVE does. `[doc]`
- **Files on the +Drive need a 16-byte zero header.** The files share the sample filesystem, and stock's SAMPLES browser lists every folder, `/mods` too. LOAD TO PROJECT reads a file's first 16 bytes as a sample header: a raw `.elemod` there hangs stock, and a project that holds one stalls the next OS upgrade at PREPARING until CREATE NEW (SB19). The loader writes 16 zero bytes in front of every file, which stock loads as an empty sample. `[doc]`
- **The link runs at boot** from a site at `0x401009e0` in `main()`, after the +Drive is mounted and before audio and the UI task start; it skips when [NO] is held at power-on, when the eMMC or filesystem did not come up, or when a crash flag `/mods/.armed` from the last start is there (deleted about 10 s after the mods' inits ran). Its working memory (about 270 KB for the 4.3 MB area) comes from stock's heap and goes back after the link. The area runs from the flashed build's RAM end to `0x47FFF000`. `[doc]`
- **Keep UI-task work small.** Reading 13 files of 484 KB when a page opened held the key path and USB for over 5 s, and reading 257 small files for their sizes lost a key on a unit; the loader now reads 32 KB per tick, rests three times as long as it worked (timed with DTIM0) and waits 1 s after any key or encoder turn. Past 16 queued UI events, a remote key is refused as busy. `[hw]` (key loss) / `[doc]`
- **Stock's two-pane file view** (the one SAMPLES and PROJECTS use, `0x400734f2`) hangs the UI when it is first shown with no row at all; stock's own lists never are empty (`..`, or 128 RAM slots). `[doc]`

## Queued trigs: what a mod can see before a trig fires (Modwerk, OS 1.74, read from the code) {modwerk-rytm-queue}
- The sequencer queues a track's next trig one step ahead, its probability already rolled, in the lowest free of three event slots per track (state at `0x42ac5fb0 + 224*track + 56*slot`, fire time at `0x8000fd50 + 12*track + 4*slot` on the clock at `0x8000fe54`, which moves 2 x tempo per block). A trig queued while an earlier one still waits (swing, micro timing) lands in the second or third slot. Pads, MIDI notes and the first trig after PLAY take a fourth slot at once and cannot be seen ahead. `[doc]` (a trig that will not play is not queued: rytm-emu at 50 %, a unit for FILL and 2:2 `[hw]`)
- Stock fires one event per track per block, so two due in one block take that block and the next. Mutes and a track's held word apply when the trig fires, not when it is queued. Retrigs are not queued: they run on their own tick counter. A pattern change clears queued events from the change on. `[doc]`


## Modwerk Rytm findings (OS 1.74, 2026-11-11) {modwerk-rytm-smpl}
- **Keys:** `Brain::key` is at `0x400a0336`; calling it directly skips the `ev_key` handlers after it, so a mod plays actions through the base's `core_key`. `[emu]`
- **Parameter records** at `0x419a4888 + 84*id`: turn factors at +4/+8 and a 28-byte encoder profile at +16; every value turn is added at `0x400a88ea`. Sound parameters glide about 22 ms toward their targets (`0x8000e5b0 + 84*track`, routine `0x40120cfa`). `[emu]`
- **Screens:** a lock box is 27x7 over a label knob and 19x15 over a widget knob; the DEP formatter is `0x400fbbe8`; the SAMPLE view's vtable is `0x401e3420`, the FIN row's default and names at `0x401c03f8`/`0x401c0410`/`0x401c0418`, TUN's fine flag at `0x401c03c8`. `[emu]`
- **Adding the fine flag to TUN** makes a cents lock survive a pattern save: the pattern saves one more fine lane for that track (of stock's 72), stock loads it, and a pattern saved without the mod drops the cents. `[hw]` (Improved SMPL 0.4.0 on the author's unit, RAM boot)
- **Shared mod area (128 KiB):** Quick Mod Assign 0.2.0 takes 7,578 bytes plus 72 bytes of `.bss`. `[doc]`
- **SMPL WAVEFORM layout (OS 1.74):** SamplePageView's draw (`0x400d2004`) clears rows 12-52 and calls the view's knob-text routine (vtable +148, +152 with a trig held) for each knob at `0x400d20ee`; a lock adds a 27-wide XOR box. Holding a page key sets view byte +376 (stock's values view). The waveform widget at view + 400 keeps its area in RAM (x0 +28, y0 +32, width +36, height +40; stock 2, 16, 123, 32), read at every draw, so a mod can resize it without a code site. `[emu]` {modwerk-rytm-smpl05}
- **The waveform's slot follows parameter changes only:** the page callback `0x400d253a(view)` sets the widget's slot from SMP, STA and END when a parameter or the track changes, and sets it to 0 (centre line) while SMP's slot has no sample name (`0x400b8192`). A slot gets its name (`0x41942350`, written at `0x4009e39e`) only when the sample loader `0x4009df72` has read its file whole, and the project's pool loads slot by slot (`0x400b739c`) from background jobs a few seconds after boot. A page that shows the waveform from boot must call `0x400d253a` again while the slot reads 0; seen on a unit with Improved SMPL 0.5.0 (the waveform appeared by itself after a few seconds). `[hw]` {modwerk-rytm-smpl05}

## Where a MKII mod can keep its own data (rytm-mods-src `re/subsystems`, OS 1.73, checked in 1.74 by byte match; static plus rytm-emu, nothing on a unit) {rytm-mods-src}
- **Stored records are read only by their load serializers.** In a cold boot watched over the whole stored project image (`0x405c8f20`, 0x1f9f32 B), the only readers were each record's loader, the project-load code, and whole-image copies. Dumps are serialised from live objects. `[emu]`
- **37 stored kit bytes stock never reads or writes:** kit `+0x832..+0x841` (16 B) and `+0x902..+0x916` (21 B), on either side of the performance block (whose loader and saver start at `+0x842`). Mod 0018 keeps its scene mute masks there, behind a tag byte `0x53` at `+0x90c`. Whole-image copies carry them; kit copy/paste and SysEx kit transfer go through a live buffer and drop them. `[emu]`
- **A 140-byte gap in the power-fail image:** `0x405c8e84..0x405c8f0f`, between the end of the checksummed `COKI` global block and a saved random seed (`0x405c8f10`). The whole 2,096,059-byte image from `0x405c8e10` is written to eMMC (slots `0x7a000` / `0x7c000`) on power-fail and read back at boot. No code reference lands in the gap, and a marker survived a power-off and a cold boot in the emulator. Not yet checked: project and kit saves, OS upgrade, factory reset. Nothing initialises the gap, so give your data a tag (mod 0017 uses `CIPF`). `[emu]`
- **"Loosened" bytes have a cost on stock:** bytes that stock reads but always holds at one value (for example the 8 low bytes of the velocity and aftertouch route amounts, sound `+0x71/+0x74/+0x77/+0x7a` and `+0x8d/+0x90/+0x93/+0x96`) can carry mod data only if every stock reader is hooked. A project or dump using them is then not safe on unhooked firmware: a changed version long makes the record load at defaults, and a level LSB at 127 loads as 100. Bytes stock never reads are harmless there. See rule E3. `[doc]`
- **Performance macros are engine state, not kit data:** 12 words at `0x8000e57c + 2k` (0..`0x7f00`), glided each block (~22 ms) into `0x8000f774[0..11]`. Their setter `0x400b2bfe` raises no change notice, so the kit is not marked edited. CTRL IN 1/2 are ADC slots 0 and 1, smoothed and mapped each block by `adc_pedal_update` (`0x4013f1c8`). `[doc]`
- **Track mutes belong to the project**, scenes to the kit. Every UI and MIDI mute goes through `track_mute_set` (`0x400b786c`); Overbridge uses `track_mute_set_silent` (`0x400b6d6c`), which has no guard and bypasses hooks on the main setter. All scene engages (pads, CC 92, NRPN `0xE8`, Overbridge) go through `kit_scene_set_active` (`0x400a7d04`). `[doc]`

