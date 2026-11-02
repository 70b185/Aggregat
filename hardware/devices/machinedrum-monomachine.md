# Machinedrum (SPS-1 UW) and Monomachine (SFX-6/60)

Coverage: **first profile** (phase 2). The Machinedrum part is detailed; the Monomachine part is thin, because its internals are not written up publicly.

Sources read 2026-11-02:
- janne808/machinedrum-kit `docs/` (system overview, SysEx updates, firmware image, DSP2 voice ABI, DSP programming, emulation and verification, open questions). Key {mdkit-docs}. The kit's custom machines ran on units, and it says where emulator and hardware differ.
- emuyia's em's Machinedrum and Monomachine firmware READMEs and CHANGELOG. Key {ems-fw}.
- shnolk/monomodule README. Key {monomodule}.
- joelanders/gearmulator-md-mm source (`source/elektron/md/mdLib`: memory map, types, board scheduler comments). Key {gearmulator-md-mm}.

Projects: [../../devices/machinedrum.md](../../devices/machinedrum.md), [../../devices/monomachine.md](../../devices/monomachine.md).

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

## Emulator vs unit (Gearmulator's Machinedrum board model) {mdkit-docs}
Things that pass in the emulator and fail on a unit:
- **Flash appears at both `0x0` and `0x10000000` in the emulator.** On hardware, after the OS remaps CS0 nothing decodes the low window: images with low-window flash pointers **boot in the emulator and hang on the unit.** Link and point through `0x10000000`, and scan images for low pointers. `[hw]`
- **`P:0x400-0x4FF` on DSP2 is not internal memory** on hardware (the cache is on, so internal P ends at `0x3FF`). Early prototypes put code there. `[hw]`
- No pipeline interlocks, no wait states and no instruction-cache timing in the emulator. Bit-exact tests can't see any of them.
- A coarse CPU/DSP time slice (125 µs) produced false "missed blocks" that look exactly like overruns. Use a 30 µs quantum before blaming your code. `[emu]`

Rule A23 ("success is no proof") applies with force here.

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

## Open
- The Monomachine's clocks and DSP budgets on a unit (only the emulator's board model exists).
- The Machinedrum's hardware wait states per area (only two areas measured).
- Why arithmetic stalls cost so little on hardware while AGU interlocks cost about their estimate (the kit lists this as open).
