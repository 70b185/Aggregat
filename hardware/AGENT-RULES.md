# Rules for AI agents developing for Elektron small boxes

Rules are derived from what the community's own mod projects do and warn about. Each rule names its
evidence. If a rule conflicts with a device file, the device file is more specific.

## A. Safety - never skip

**A1. Do not touch the bootstrap/bootloader or the updater section.** Patch the main OS only.
Then the stock OS file can always restore the unit. `[doc]` {elekloader-adapting} {elekloader-readme}
{digikit} (ElekLabs README: patchkit refuses to change sections 2, 4 and 8) {dn2mk2-safety} (dn2mk2 gate: sections 2, 4, 5 and 8 byte-identical to stock; mods change only 3 = MAIN OS and 7 = DSP) {digikit-old} (earlier README: 2 = bootstrap and 4 = updater never modified; sections 3 and 7 were the
patch targets) {dn2-cfw} (brick checker refuses any bootstrap change).

**A2. Know the recovery path before anything is flashed.** Write it down in your output, with the exact
button combination for the device (see [`common/recovery.md`](common/recovery.md)). Keep the stock OS file and,
for Digitakt II / Digitone II, a physical DIN MIDI interface at hand. Note: digikit's README itself says recovery via the bootstrap menu is **"not tested on hardware"** - treat Digitakt II recovery as unproven, Digitone II recovery was exercised by dn2-cfw, Overtone and dn2mk2. `[doc]` {digikit} {digikit-old} {synthack-os}
{dn2-cfw}

**A3. Back up first.** Back up projects/sounds (+Drive) with Elektron Transfer before flashing. `[doc]` {dn2-cfw}

**A4. Never power off during an upgrade.** `[doc]` {elekloader-readme}

**A5. BOOTSTRAP UPGRADE is the only irreversible step** (DT2 startup menu; runs only if the incoming
bootstrap version is strictly higher). Never build or send an image with a higher bootstrap version. Elektron's own notes add that some official upgrades also upgrade the bootstrap right after the first restart - never cut the power then. `[doc]` {digikit-old} {elektron-dt2-notes}

**A6. Verify every candidate image before it is written** - re-read it, check all checksums, check
that only the intended section differs from stock, check it fits the flash budget, check the main OS unpacks to
exactly the patched image. elekloader does this per build; dn2-cfw additionally runs a 12-check brick checker. `[doc]`
{elekloader-readme} {dn2-cfw}

**A7. First run of a new DSP/audio build: volume down.** `[doc]` {dn2-cfw} {dn2mk2-firmware-md}

**A8. Gate what you ship.** Overtone and dn2mk2 only let the patcher save a file whose output hash matches a build
that passed the project's own checks (Overtone: ~160 emulator checks per build; dn2mk2: `scripts/ship_gate.py`
"CLEARED TO FLASH"). Do the same: no ungated output reaches a unit. `[doc]` {overtone} {dn2mk2}

**A9. Respect transfer limits.** Digitone II's USB upgrade receiver does not check the size limit of 2 MiB; oversized
images stall at the end (nothing is written, a power cycle clears it). The withdrawn dn2mk2 builds v0.4-v0.7 hit this.
Also keep the DSP image under 1,048,575 bytes. `[doc]` {dn2mk2-firmware-md}

**A10. Mods can be mutually exclusive by OS version.** On Digitone II, Overtone needs stock OS 1.12 and dn2mk2 needs
1.11; getting from 1.12 to dn2mk2 means going back to a 1.11 base, and projects saved under the newer OS may not open.
Always state the exact OS in the first line of a README. `[doc]` {overtone} {dn2mk2}

**A11. Rehearse recovery with a stock file before the first modified flash**, and prove the transfer link with stock firmware first.
Receivers have no error recovery (a dropped packet freezes the bar near 80 %), and recovery has so far been proven with stock images only.
Full procedure in [`common/flash-procedure.md`](common/flash-procedure.md). `[hw]` {dn2-flashing} {dn2mk2-safety}

**A12. One change per flash.** Never combine a new feature with a fix or a second patch in one image; keep the unmodified stock `.syx` untouched. `[doc]` {dn2-flashing}

**A13. Gate DSP code against hardware rules the emulators cannot see.** dn2mk2 runs `gate_hwrules.py` (complex-ping's `hwrules.py`) because DSP code that
runs in the emulator can fail on silicon with DSP silence until power cycle. Use a comparable static check and keep to instruction encodings found in stock. `[doc]` {dn2mk2-safety}

**A14. Check the size margin at every loader stage, not just the file size.** On the Digitone II the in-place loader of section 4 has a stock margin of +31,182 bytes and the default compressor setting turns that into -39,318, corrupting the image; the receive buffer is 2 MiB and the stock container is `0x1CC740` bytes. Use a packer that respects Elektron's stream limits (1 MiB window, 2,048-byte matches) and verify the margin of both stages. `[hw]` {dn2-cfw-handoff} {dn2-ele3}

**A15. Leave the panel-MCU blob, its updater and section 8 (Outbox 8 firmware) stock**, together with the bootstrap and updater. `[doc]` {dn2-cfw-handoff} {dn2-ele3}

**A16. Withdraw builds that lose sound.** Digiwerk withdrew its six spring-reverb builds after finding that two of them stop the sound on a Digitone II; dn2mk2 withdrew v0.4-v0.7 for oversized images. Keep a visible list of withdrawn builds with the reason. `[hw]` {alt-digitone-ii} {dn2mk2-firmware-md}

## B. Legal / distribution

**B1. Never include, commit or publish Elektron firmware** (original or modified), dumps or decompressed code.
Ship patches that carry only the author's bytes plus hashes of the expected stock bytes. The **user supplies the
stock OS file.** `[doc]` {elekloader-readme} {elektron-firmware-tool} {digitakt-ii-research} {dn2-cfw}

**B2. Identify the stock file by hash (SHA-256) and refuse anything else** - modified files and other OS
versions are rejected, not "adapted". `[doc]` {digitakt-ii-research} {synthack-os} {syntakt-workbench}

**B3. Say what you are.** Mods are unofficial, unsupported, not affiliated with Elektron, and used at the
user's own risk (may brick; Elektron's wording: modifications "may affect warranty coverage" and may prevent future
updates - it does not explicitly say the warranty is void, so do not claim more than that). Put that in every README. `[doc]` all mod READMEs {elektronauts-policy}

**B4. Respect the manufacturer's forum policy.** Elektron's post of 2026-09-16 (updated 09-17) forbids, on Elektronauts and
Elektron's official social platforms, sharing, requesting or linking to files, tools, repositories or instructions for modifying
firmware, and developing or distributing firmware/hardware that makes unauthorized use of Elektron's IP; such posts are removed.
General discussion stays allowed. It applies to legacy machines as well. Do not post mod links there. This aggregator lives on
GitHub and links only to metadata. `[doc]` {elektronauts-policy}

**B5. Respect each project's contribution policy - for AI agents too.** elk-herd's README says issues, comments and pull requests
generated by AI will be summarily rejected. Before opening an issue or PR in someone else's repo, read the README/CONTRIBUTING
and disclose AI help where the project expects it. `[doc]` {elk-herd}

## C. Process


**C1. One mod = one OS version.** Addresses and stock bytes are version-specific (hash-pinned). A mod for
Digitakt mk1 1.53 is refused on 1.54; Digitakt II 1.17 addresses do not carry to 1.18+. Porting = find every
address again. Keep a separate build per OS version. `[doc]` {elekloader-adapting} {digitakt2-perform}

**C2. Test ladder, in order:** build -> lint -> emulator cold boot compared against stock -> a unit you can
recover. A verifying build is well-formed, **not** proven to work. `[doc]` {elekloader-adapting}

**C3. Record the test state of every build** as `hw` / `emu` / `untested` in the project metadata. Several
projects ship builds that are lint-clean but "not yet run on a unit". `[doc]` {digislicer} {digichroma} {digitakt2-perform}

**C4. Emulators do not prove real-time DSP behaviour.** The earlier digikit README said "no audio"; the current ElekLabs
README has ColdFire + SHARC+ running together with audio, but the DSP "does not run in real time yet", and dn2mk2
reports the emulators do not model the two chips' timing. DSP overruns show up only on a unit. `[doc]` {digikit-old}

**C5. Windows:** the DN2 tooling needs an m68k objdump; use WSL. `[doc]` {dn2-firmware-explore}

**C6. Report honestly.** "Nothing counts as working until it has run on my unit" is the standard the more careful
authors apply. `[doc]` {dn2-cfw}

## D. Writing mods (format-2 / linkable, Digitakt mk1 and Digitone mk1)

**D1. Prefer events over raw patch sites.** The core mod owns the shared hook sites; subscribe via its event
bus, do not patch core-owned sites. `[doc]` {elekloader-adapting}

**D2. Patch whole instructions only.** A site that ends mid-instruction is refused. `[doc]` {elekloader-adapting}

**D3. No overlapping claims.** No two mods may patch or claim overlapping bytes, memory or named resources. Declare
resources (`sysex:`, `settings:`, `drive:`, `ui:`, `machine:` names; other memory as regions). `[doc]` {elekloader-adapting}

**D4. Prefix every global symbol with the mod id, make internals `static`.** `[doc]` {elekloader-adapting}

**D5. Let the linker place code and data, never hard-code addresses.** Sections allowed: `.run`, `.fast`, `.bss`.
`[doc]` {elekloader-adapting}

**D6. Custom machine IDs are permanent once kits store them.** Range 4-127. Claim `machine:<id>`. Known claims
(Digitakt mk1, core 2.1): 4 = NEIGHBOR, 5 = DIGISLICER. Pick a free ID, then register it in
[`devices/digitakt.md`](devices/digitakt.md). `[doc]` {elekloader-adapting}

**D7. Do not mix format 1 (whole build) with format 2 (linkable) mods** - whole builds cannot be combined. `[doc]` {elekloader-adapting}

**D8. Keep the audio interrupt handlers (`ev_render_in/out`) short.** `[doc]` {elekloader-adapting}

**D9. Licence everything with an SPDX identifier and matching file headers.** The ecosystem is mostly GPL-2.0-or-later
(elekloader family); MIT and AGPL-3.0 also occur. `[doc]` {elekloader-adapting}

**D10. Disclose AI-generated code** the way DT-FM does ("largely AI-generated, not proofread"). Not a technical rule,
but readers decide on risk from it. `[doc]` {dt-fm}

## E. Changing parameter tables / saved data (Digitone II)

**E1. Projects store values by slot, not by table row.** Details and the P-lock trap in [`devices/digitone-2.md`](devices/digitone-2.md). Moving the OS parameter table does not by itself change
the saved format. New rows are only safe if they follow the author's growth rules
(`docs/parameter-table-growth.md` in dn2-cfw - not yet read by us). `[doc]` {dn2-cfw}

## F. Writing to a unit over SysEx (control-side tools)
**F1.** Back up first, via Elektron Transfer and by re-reading the destination pattern; abort if the backup fails. `[hw]` {digi-roll-studio}
**F2.** Allowlist the exact OS builds you have tested; refuse others. `[hw]` {digi-roll-studio}
**F3.** Change only the bytes that must change, then read back and byte-compare. `[hw]` {digi-roll-studio}
**F4.** Work on throwaway projects while a format is still being decoded; trust only mappings with a hardware-confirmed level (SYXGRID level A). `[doc]` {syxgrid}
**F5.** Never run parsers across device generations (Digitone mk1 device ID 0x0D vs Digitone II, Analog Four gen-1 vs gen-2). `[doc]` {syxgrid} {digi-roll-studio}
**F6.** Treat file-write / delete commands of the +Drive API as dangerous: only single-chunk writes were hardware-verified; move/copy/delete are not implemented anywhere we know. `[hw]` {digi-roll-studio}

## G. Working method (from the digitone-2-modding-skill - the one public agent skill that shipped a firmware mod)
Full loop, spec questions and triage in [`common/agent-workflow.md`](common/agent-workflow.md). Short form:
**G1.** Ask the spec questions in one round before building. **G2.** Reproduce every bug as a failing test with a stock control before fixing it.
**G3.** Test what the hardware consumes, never by reading back what your own patch wrote. **G4.** Run emulator and static checks before every flash;
the unit should only judge sound and feel. **G5.** Flash one clearly named image with its SHA-256 and a list of what to try; never overwrite older images.
**G6.** After two failed flashes on the same problem stop and restate goal, proven facts, unknowns and options. **G7.** Ask the user before cloning or installing anything.
**G8.** Keep levels honest: measure worst cases, add no unrequested gain compensation, clamp audio output, never read memory you did not write.
`[doc]` {dn2-skill-md} {dn2-skill-workflow}

**G9. DSP rules the emulators cannot check** (Digitone II, each reportedly silenced or crashed a real unit): whole 32-byte boot blocks, stock instruction encodings only
(incl. sign bits of negative shift immediates), PRM loop/DAG/branch rules, no L2 above `0x200B0000`, never read unwritten DDR (power-on NaN), preserve registers at hooks
(clobbered R8 at the FX-bus mixer hook lost all audio), count memory accesses not instructions. Details and addresses in
[`devices/digitone-2-os111-reference.md`](devices/digitone-2-os111-reference.md). `[hw]` {dn2-skill-sharc}

