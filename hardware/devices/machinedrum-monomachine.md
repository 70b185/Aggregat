# Machinedrum (SPS-1 UW) and Monomachine (SFX-6/60)

Coverage: **first profile** (phase 2). The Machinedrum part is detailed; the Monomachine part is thin, because its internals are not written up publicly.

Sources read 2026-11-02:
- janne808/machinedrum-kit `docs/` (system overview, SysEx updates, firmware image, DSP2 voice ABI, DSP programming, emulation and verification, open questions). Key {mdkit-docs}. The kit's custom machines ran on units, and it says where emulator and hardware differ.
- emuyia's em's Machinedrum and Monomachine firmware READMEs and CHANGELOG. Key {ems-fw}.
- shnolk/monomodule README. Key {monomodule}.
- joelanders/gearmulator-md-mm source (`source/elektron/md/mdLib`: memory map, types, board scheduler comments). Key {gearmulator-md-mm}.

Projects: [../../catalog/machinedrum.md](../../catalog/machinedrum.md), [../../catalog/monomachine.md](../../catalog/monomachine.md).

**The short version:** an early-2000s three-chip design (an old ColdFire plus two Motorola DSP56303s). It is nothing like the DT2/DN2: no SHARC, no FreeRTOS budget model, and no USB. Its flash updater lives in a boot sector that the OS itself can rewrite.

## Machinedrum silicon {mdkit-docs}
- **CPU: ColdFire MCF5206E.** It runs the OS (UI, sequencer, MIDI, kits, parameter conversion, flash, DSP control). Older notes say MCF5307; the board model and the MAME driver both identify an MCF5206E. `[doc]`
- **DSP2 ("producer"), a DSP56303:** renders the 16 machine voices, one 32-sample mono block per track per audio block. It holds the machine code, the stock sample data and the sample RAM. **Custom machines run here.**
- **DSP1 ("mixer"), a DSP56303:** track effects, mix, master delay/reverb/EQ/dynamics, and the six-output codec. Custom-machine work leaves it untouched.
- **Links:**
  - ColdFire to each DSP over the **HI08 host port**. The DSP-side handler takes an address and a count and DMAs the words into Y memory; this is how parameters reach a voice.
  - DSP2 to DSP1 over ESSI0 (one block per track); codec on ESSI1.
  - MIDI on ColdFire UART1; front panel on UART2.
  - The old idea that the ColdFire plays voices through a DSP SCI port is wrong. `[doc]`
- **Timing:** 44.1 kHz, 32-sample blocks.
  - DSP1 at 101.6064 MHz = **73,728 cycles per block**.
  - DSP2 at 98.784 MHz = **71,680 cycles per block**. Its program never sets the PLL, so the boot stub's setting stays. The emulator clocks it at DSP1's rate and so overstates the budget.
  - **The two budgets cannot be pooled.** `[hw]`

## Machinedrum budget facts (DSP2) {mdkit-docs}
- The whole producer pass (16 renders plus dispatch, updates, interrupts and DMA waits) must fit in 71,680 cycles. **A severe overrun on hardware first crackled, then lit every LED and left the engine silent.** `[hw]`
- **Per-track floor of ~3,290 cycles** (measured on hardware): each track's 32-word block travels to DSP1 over ESSI0 at ~100 cycles a word, double-buffered.
  - Track k's transfer runs during track k+1's render, so a track costs `max(render + ~40, ~3,290)`.
  - **Time saved below the floor is lost, not banked.** Making a cheap machine cheaper gains nothing. `[hw]`
- Planning numbers (emulator): an idle track 3,438 cycles; stock TRX/EFM/E12/P-I voices ~2,000-3,200. `[emu]`
- External-memory wait states (the emulator ignores them; measured on hardware): ~1 wait state in areas 0-2, ~5 in area 3 (`0x1C0000+`). A machine with many external accesses costs several thousand cycles more on hardware than in the emulator. `[hw]`

## How full DSP2 is with stock kits (MModule research 04, OS 1.63, emulator) {mmodule-research}
- In emulated cycles, a busy kit costs 38,789 per block (54 % of 71,680), and the most expensive stock kit, 16 ROM machines, up to 67,309 (94 %). `[emu]`
- Kitbasher measured that pipeline interlocks alone add a median 26 % on hardware, so the dearest stock kits sit close to the limit. **Treat these numbers as a floor.**
- MModule found `$020000-$0FFFFF` of the emulated DSP's shared P/X/Y never written by the 1.63 program (found by poisoning memory and playing all 104 machines). That is emulator memory: check what a real unit decodes there before relying on it (compare the `P:0x400` lesson below). `[emu]`

## Emulator vs unit (Gearmulator's Machinedrum board model) {mdkit-docs}
Things that pass in the emulator and fail on a unit:
- **Flash appears at both `0x0` and `0x10000000` in the emulator.** On hardware, after the OS remaps CS0 nothing decodes the low window: images with low-window flash pointers **boot in the emulator and hang on the unit.** Link and point through `0x10000000`, and scan images for low pointers. `[hw]` ([I38](../INCIDENTS.md#i38-low-window-flash-pointers-boot-in-the-emulator-and-hang-on-the-unit))
- **`P:0x400-0x4FF` on DSP2 is not internal memory** on hardware (the cache is on, so internal P ends at `0x3FF`). Early prototypes put code there. `[hw]`
- No pipeline interlocks, no wait states and no instruction-cache timing in the emulator. Bit-exact tests can't see any of them.
- A coarse CPU/DSP time slice (125 µs) produced false "missed blocks" that look exactly like overruns. Use a 30 µs quantum before blaming your code. `[emu]`

Rule A23 ("success is no proof") applies with force here.

## What crashed, froze or corrupted real Machinedrums (Kitbasher's FIRMWARE-SAFETY, mostly a MKII +Drive UW) {kitbasher-safety}
Each item failed on a unit and passed in the emulator. `[hw]`
- **ColdFire ISA:** `movem.l d0-d1,-(sp)` is a 68000/68020 form ColdFire lacks. Emulators run a 68020 core, and the first trigger of every new machine froze the unit. Kitbasher allows only ISA_A for the MCF5206e (no MAC in added code) and decodes the final image from every entry point (rule A42).
- **Boot-time memory:**
  - Ordinary stores to flash relocation sites hung the unit at the boot screen; the emulator ignored them.
  - Boot writes from `0x2bd000` up froze a MKII +Drive UW at the logo, while the same image without them booted. Use only hardware-proven RAM ranges.
  - Boot code must not push registers before the OS has set up a stack.
- **The host port to the DSPs holds about two words; the emulator buffers thousands.**
  - A sender whose poll timed out left DSP1's handler armed, so the next stock send was shifted by two words.
  - A loader interleaving its writes with the OS's put a thousand words at a wrong address.
  - Send exactly as stock does (interrupts masked) and own the port for the whole transfer.
- **The per-step trigger loop is hot:** a hook doing a table lookup and register save on every call froze the audio with 12-16 tracks triggering (CPU! lit). It was found only by a hardware bisect. Cache, then exit early.
- **Never remove stock DSP pacing.** Replacing a 480-cycle DSP1 pad contributed to that freeze. Letting DSP2 skip ahead on silent tracks starved the ColdFire's stream and lost triggers.
- **No long `rep` on a DSP path:** `rep #$600` (clearing 1,536 words) overran the CPU on the first P-I bass-drum trigger. Changing it to `rep #1` proved the cause; two stores per `do` pass fixed it. This is the same rule as on the Octatrack.
- **The stock DSP1 watchdog:** DSP1 counts blocks that DSP2 delivered late. **On the third in a row it stops the output DMA and spins, silent until a power cycle.** Half a percent over budget for three blocks is enough.
- **DSP correctness traps:**
  - Nested `do` loops sharing an end address left state on the real hardware stack, and DSP2 hung.
  - An inherited modulo register wrapped a 384-word clear into 32 words.
  - DSP2 external RAM holds **power-on garbage** (the emulator reads zero), so init must clear everything it reads, and every block must write all 32 samples.
- **Machine ids 124-127** fall inside the OS's "control machine" range tests.
- **Pin data assumptions:** after a firmware update, wavetable models went silent because older UW sample sets were shorter than the new build expected. Declare minimum lengths.
- **What the emulator does not show, in numbers:**
  - DSP56300 pipeline interlocks add a median ~26 % (12-47 % per model).
  - Instruction-cache misses and wait states: 16 copies of one model fit in the emulator and stalled on the unit.
  - The emulator's default 441-sample slicing invents host-port spins of ~13,000 cycles. Use 64- or 8-sample slices, and don't "fix" spins it invents.

## DSP56300 pitfalls (from building custom machines) {mdkit-docs}
- `move #16,a` loads a **fraction** (`a1 = $100000`), not 16. Write integers into data-ALU registers in the long form `#>16`. Address registers and the ALU immediates (`cmp`, `add`, `sub`) take integers.
- Moving an accumulator to memory **saturates**: `move b,a` limits, `tfr b,a` doesn't. After `and #mask,a` take `a1` explicitly.
- The reference assembler (mborgerson/dsp56300) accepts overlapping `ORG`s silently, so validate its output before packing: one contiguous segment, inside its bank, no warnings, entry points inside. A DO loop's end label goes on the instruction after the last loop instruction. `[doc]`

## OS update and recovery (Machinedrum) {mdkit-docs}
- The OS `.syx` carries flash from `0x4000` up (stock 1.63: 939,744 bytes), in 2+7+7-packed 64-byte packets with a checksum and two terminators. **It never carries the 16 KiB boot sector.**
- The boot-ROM updater **stages the whole image in RAM and checks it before the first erase**, so an interrupted or corrupt transfer changes nothing. `[doc]` (code reading)
- It refuses a version not newer than "140", and halts on one flash part ID.
- An exporter must include everything up to the last non-`0xFF` byte below `0x100000`. Custom code near `0xFE000-0xFFFFF` sits after the blob chain, and stopping at the last blob boots with pointers into erased flash. `[doc]`
- **The trap: the OS rewrites the boot sector.** On every boot, MainOS checks the magic word at flash `0x3FFE`. If it isn't `0x224B`, MainOS erases the boot sector and rewrites it from a copy embedded in MainOS. A modified OS that alters that check or that copy can **destroy the updater on its first boot**; after that only an external flash programmer helps. Same pattern as the A4 MK1, so **rule A38 applies**. `[doc]`
- Recovery otherwise: enter the boot ROM's upgrade mode and send the stock `.syx` over DIN MIDI (the unit has no USB). Rule A36. `[doc]`

## Monomachine (thin)
- Monomodule runs the Monomachine's own sound engine in an emulated DSP56300 and matches the hardware sample for sample. So the sound engine is DSP56300 code taken from the OS file (OS 1.32B, `Elektron_SFX6-60_OS1.32B.syx`). `[doc]` {monomodule}
- **Board, as Gearmulator models it** (joelanders' gearmulator-md-mm, which boots the unmodified MnM OS 1.32B on the same board model as the Machinedrum, `[emu]` {gearmulator-md-mm}):
  - the same ColdFire MCF5206E (modelled at 40 MHz) and two DSP56300-family DSPs;
  - the same address map: flash at `0x10000000` (8 MiB OS images for both machines), main RAM `0x200000-0x2fffff`, each DSP's HI08 host port at `0x500000` / `0x600000`, internal SRAM at `0x1000000`;
  - the SFX-60 MKII keeps user DigiPRO waveforms in a 2 MiB flash window at `0x10200000`.
- **What differs from the MD** in that model:
  - the ColdFire services the DSP host port through the hardware receive latch rather than the MD's HREQ-to-IRQ4 wire;
  - the two DSPs are coupled by their own link handshake.

  These are emulator-level facts. Nothing in our sources has measured a unit's clocks. `[emu]`
- **Custom OS saved-data hazard:** em's firmware reclaims song slots for extended data (MnM: slots 13-24; MD: 13-32). Songs left in those slots are **corrupted on boot**, so back them up first. The same can happen with any mod that changes saved-data layouts (compare section E of AGENT-RULES). `[doc]` {ems-fw}
- em's firmware carries features from jmamma's MDX (new machines, tunings, LFO shapes, MIDI fixes) with credit. `[doc]` {ems-fw}

- **Screen dump (ems-monomachine-firmware 26B09):** the request `F0 00 20 3C 03 00 64 F7` returns 16 SysEx chunks of 7-bit-packed data, 64 bytes each once decoded: the native LCD bitmap, 128x64, 1 bit, column-major, bottom to top, MSB first. Whether stock 1.32B answers it is not stated. The firmware is now compressed, so boot is slower. `[doc]` {ems-mnm-changelog}

- **MIDI Stop is a pause on the MM (OS 1.32B):** after MIDI Stop (`0xFC`) the step is held and Continue resumes; while paused, LOAD SONG (SysEx `0x6C`) is silently ignored, while load pattern (`0x57`) and set status (`0x71`) still work. One press of the panel's STOP clears it. The factory global has TRANSPORT IN = IGNORE, so SPP, Continue and Start do nothing until it is set to ACCEPT. `[emu]` {mdmm-091}
- **MM factory data:** the factory kits, patterns and songs are stored packed inside the OS image and unpacked when the OS starts with empty patch RAM: two fresh boots gave identical data, 128 kits, 128 patterns and 24 songs. The stock FACTORY RESET (early startup menu, item 3) also resets the globals and the DigiPRO user waveforms and cannot be undone. `[emu]` / `[doc]` {mdmm-091}
- **Dump sets:** the MD answers as product id 2 (64 kits, 128 patterns, 32 songs), the MM as product id 3 (128 kits, 128 patterns, 24 songs); a freshly booted emulated MM needs about 9 s after MIDI is ready before it takes dumps, and a real MM accepts dumps only on its SYSEX RECV screen. `[emu]` / `[doc]` {mdmm-091}
- **Machinedrum 1.63: live recording dead after an SDS sample arrives** (SB24): the RECEIVING SAMPLE screen unlinks the main screen's objects and puts them back without restoring the list head (head cell at RAM `0x28092c`); a restart clears it. `[emu]` {mdmm-091}

## Open
- The Monomachine's clocks and DSP budgets on a unit (only the emulator's board model exists).
- The Machinedrum's hardware wait states per area (only two areas measured).
- Why arithmetic stalls cost so little on hardware while AGU interlocks cost about their estimate (the kit lists this as open).

## Gearmulator alpha.15: the DSP-to-DSP link and emulator timing (MD OS 1.63, MM 1.32B, 2026-11-18) {gearmulator-1118}
- **Inter-DSP link protocol (MD OS 1.63):** per 32-frame block the producer (DSP2) sends each of its 16 tracks as 32 words through DMA 0 and ESSI0, one after the other, and waits for DMA 0 to finish before the next send. The mixer (DSP1) takes all 512 words through DMA 4 into `Y:$600` and reads DDR4 to see how far the transfer has come before it mixes a track. Once per block the mixer hands 64 words back through DMA 2 and ESSI0, toggles Port C bit 1 and re-arms DMA 4; the producer waits for that toggle before it sends track 1. `[emu]` (read from the programs' behaviour in the emulator)
- **What the two programs watch of the link:** DDR4 on the mixer, the enable bit of DCR0 and the Port C pin on the producer, and the buffers. Neither reads an ESSI0 or DMA status register for it and neither uses a link interrupt. A custom DSP2 program that keeps this handshake keeps the link working. `[emu]`
- **ESSI0 word slot = 96 DSP cycles.** The DMA request is already pending when a channel is armed, so the first word leaves on the slot already under way (modelled as arm time - 96 cycles; with that, every DDR4 read of 110 traced blocks fell on the same cycle as on the serial model). This refines "~100 cycles a word" in the budget section. `[emu]`
- **Emulator quantum and latency:** with the MD's 125 µs background quantum a DSP could answer the ColdFire up to 5.5 frames ahead, the ColdFire busy-waited and its update loop slowed by a tenth: trigger to sound 5.5 ms instead of 5.1 ms. 30 µs (the MM's quantum) gave 4.95 ms. Over 185 onsets the block link measured 5.22 ms, the serial model 5.46 ms. A unit's own figure is not published. `[emu]`
- **Block link output is not bit-identical:** it is the serial model's waveform moved by whole 32-sample blocks, because the serial model showed the producer the mixer's toggle 4,000-12,000 DSP cycles late, a different amount each block. With the link off, output stays bit-identical on 79 machines. On by default for MD OS 1.63 only, and only when the loaded DSP programs match at the instructions it relies on; `GEARMULATOR_MDMM_BLOCK_LINK=0` keeps the serial model. MM and other MD OS versions are untouched. `[emu]`
- **GND-IMP's first trigger after a machine assignment** gives an extra low thump in the emulator; the serial model drops it when a short host message to the producer lands just before the trigger (seen at 1.5 s after the assignment, not from 1.6 to 8 s). Skip the first trigger when comparing renders. `[emu]`
- **MD first launch with empty storage:** the OS runs its factory setup and reboots in process, then boots normally in about 11 s; a 20 s render capture can miss its only note. Start captures from a set-up state or run them 40 s. `[emu]`
- **ColdFire idle loop:** the MD/MM OS spends long stretches in two-cycle idle instructions, 13-16 million per second of audio in the emulator's idle skip; polling host input once per 64 skipped instructions delays it by at most 128 ColdFire cycles. The plain RAM windows have no side effects on access; flash, patch RAM and the peripheral windows do. `[emu]`
- **Emulator CPU cost (host, not unit):** 24 machines rendered in 707 ms of CPU per 2 s of audio with the block link, 1,021 ms on the serial model (M2 Pro); the MD standalone idles at 40 % of one arm64 core (alpha.14: 51 %). `[emu]`
- **MM firmware sometimes drops a status request:** a pattern status request sent right after a kit dump was read and never answered; the next identical request was answered. alpha.15 resends a read request up to twice after a 3 s timeout (never a kit save). Not checked on a unit (H44). `[emu]`
- **Kit-save race over SysEx:** a "save current kit" that asks the status for the slot and then saves can store the wrong kit when the machine switches kit in between (a chained pattern or program change). alpha.15 asks again after the save and fails if the kit changed. Applies to any editor that saves this way. `[emu]`
- **Front-panel keys driven over MIDI** are sent with each key's press and release at least 30 ms apart so that a short pad tap is seen by the firmware. The 30 ms is the project's choice; the firmware's real minimum is not stated. `[?]`

## MDX X.20 C user-machine slots over SysEx (WebLoader 0.1, MKI UW+, 2026-11-19) {md-webloader-1120}
- **Empty slot answer:** on a MKI UW+ with MDX X.20 C, a dump request for an empty user-machine slot came back as NAK 12, detail 0; WebLoader reads that as empty for this profile only, and a timeout or any other error never as empty. A capability NAK 15, detail 0 gives no free-memory figure. `[hw]` (reads with the author's Python/RtMidi tool; the web page's own write is not yet tested on a unit)
- **Slots and banks:** only U01-U16 of the bank selected on the unit were read; a read of U17 timed out on hardware. The bank number and a bank change over MIDI are not confirmed. The identity reply `X20` does not tell models or sub-revisions apart. `[hw]` / `[?]`
- **Loading:** the loader needs Enhanced GUI and sends four NO key presses to leave an open MACHINE MGR; it refuses a target slot the current kit uses; a load counts as done on the final commit ACK, with no readback. `[doc]`

## MDX X.20 C effect user machines by minimal (CROSSFIELD, NFX-OT, NFX-DC; 2026-11-20) {md-webloader-1121}
From the setup notes WebLoader ships with three development machine packages (MDS 1.1). None was run on a unit.
- **The Neighbor input** reads the preceding track's signal before that track's effects, LEVEL and PAN: lowering the source's LEVEL does not stop the feed, and the global reverb return cannot feed it. An effect machine on T+1 processes continuously after its first trig, and a retrig keeps its state. `[doc]`
- **UW RAM slots:** the CROSSFIELD reverb pair (two programs on consecutive tracks, not the firmware's STEREO PAIR) uses UW RAM slots R1 and R2, 96 KiB each; missing RAM or a missing partner silences both returns. The pair takes almost all of the MD's DSP capacity, so one pair per kit with an external input. `[doc]`
- **Cross-track memory reads are outside the MDS specification:** CROSSFIELD's second half reads the first's memory, and MDS's Quick certifier rejects that access; the pair passed 39 DSP-fixture checks and 21 checks in a full X.20-C UW MKII firmware emulator. NFX-OT (23 checks) and NFX-DC (35) are Quick-checked development builds with provisional cycle declarations. `[emu]`
