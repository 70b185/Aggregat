# Release checklist for mod authors

A short list to run before you publish a build for an Elektron device, distilled from the incidents on real units
([INCIDENTS.md](../hardware/INCIDENTS.md)) and the rules they taught
([AGENT-RULES.md](../hardware/AGENT-RULES.md)). Each line names the rule, which says why and gives the evidence.

**Copy the block below into your README** (it is CC0, no credit needed) and fill in the parts in angle brackets; the recovery path per device is in [recovery.md](../hardware/common/recovery.md). It tells your users what you checked, and it
lets Aggregat show your mod with the right test status on its [mods page](https://70b185.github.io/Aggregat/?t=mods).

```markdown
## Safety and test status

- **Tested on:** <device and OS version>, <unit / emulator only / not yet> (<date>). Builds for other OS versions: <tested / untested>.
- **Recovery:** <the path for your device; on the Digitakt and Digitone families: hold FUNC while powering on, choose
  OS UPGRADE and send the stock OS file over **DIN MIDI** (USB does not work in that mode)>. Keep the stock OS file
  for your exact version and a DIN MIDI interface at hand before you flash.
- **Back up** projects, sounds and the +Drive with Elektron Transfer first. Never cut the power during an update or
  the restart right after it. First start of a new audio build: volume down.
- **What this build changes:** <sections, e.g. only section 3 (MAIN OS); bootstrap, updater and FPGA untouched>.
- **RAM it uses:** <ranges>, declared in Aggregat's [RAM tenancy register](https://github.com/70b185/Aggregat/blob/master/hardware/RAM-TENANCY.md).
- **Combines with:** <mods it was tested together with / not tested with others>.
- Unofficial, not affiliated with Elektron. Custom firmware can brick a unit and may affect warranty.
```

## Before you build

- [ ] Patch the main OS only. Never the bootstrap, the updater, the panel MCU blob or an FPGA bitstream (A1, A15, A22).
- [ ] Never ship an image with a higher bootstrap version: BOOTSTRAP UPGRADE is the only irreversible step (A5).
- [ ] Pick RAM that nobody else claims for your OS version, and declare it ([RAM-TENANCY.md](../hardware/RAM-TENANCY.md), G8).
  A "free" cave is free only after a hard run on the unit (A43).
- [ ] Check [STOCK-BUGS.md](../hardware/STOCK-BUGS.md) for your device, so you do not ship a fix for a bug you caused,
  or blame yourself for one Elektron's OS has anyway.

## Before you flash your own unit

- [ ] Know the recovery path and write it down, with the button combination for the device (A2, A36: DIN MIDI only).
- [ ] Rehearse recovery once with the stock file before the first modified flash (A11).
- [ ] Back up (A3). One change per flash (A12). Volume down on the first run of new audio code (A7).

## Try these on the unit before you call it working

Failures of these kinds passed the author's earlier checks.

- [ ] Edit and play on a pattern, bank and project far from the defaults, not only on A01 (A79).
- [ ] Build and run the smallest legal composition (no machines, one module), not only the full one (A83).
- [ ] If you patched a routine for audio tracks, find its MIDI-track twin and test that too (A84).
- [ ] Sound you start without a trig obeys mute (A81).
- [ ] Save, change, reload, switch pattern and Part, copy and paste, power-cycle: data a saved pattern points to must not
  have changed under it (A95).
- [ ] Screen code draws only from the task that owns the screen (A98).
- [ ] An input stock ignored and you now act on also posts every event stock pairs with it (A104).
- [ ] If you reboot into another image (RAM boot, self-boot): check every precondition before the upload and count the
  restart against a pending update (A96); on the Octatrack, reset the USB controller first (A101).

## When you move to a new OS version

- [ ] Re-locate, do not re-apply: re-find every patch and pin the build by hash (C7).
- [ ] Re-locate your own RAM chunks too, and check them against the new OS's stock claims with `check_ram`
  ([RAM-TENANCY.md](../hardware/RAM-TENANCY.md), D11). A full emulator gate has passed a build that crashed a unit at
  start-up ([I215](../hardware/INCIDENTS.md#i215-a-dn2mk2-build-ported-to-os-112-crashed-at-start-up-digitone-ii-v073-t1)).

## Before you publish

- [ ] Verify the image: checksums, only the intended sections differ from stock, size under the transfer limit
  (2 MiB on the Digitone II, A9), the main OS unpacks to exactly what you patched (A6).
- [ ] Gate what you ship: your patcher saves only a build whose hash matches one that passed your checks (A8), and you
  have tried to fool your own gate once (A19).
- [ ] Test after a long power-off, not only quick restarts or the emulator (A40), and install once on a unit in stock
  condition, not only on your development unit (A49).
- [ ] The progress bar and "Success! Rebooting" are not proof; play the unit (A20, A23).
- [ ] Say "not hardware-tested" in the file name or release notes wherever it is true, and keep saying it (A18).
- [ ] Name the exact OS version the build needs; mods for different OS versions cannot be combined (A10).

## After you publish

- [ ] A build that loses sound or hangs: withdraw it, say so in the release notes (A16).
- [ ] Every failure on a unit teaches something. Write it down in your repo, or report it to Aggregat with the
  [test-result form](https://github.com/70b185/Aggregat/issues/new?template=test-result.yml), so the next author does
  not repeat it (C11).
