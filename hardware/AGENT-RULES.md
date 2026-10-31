# Rules for AI agents developing for Elektron small boxes

Rules are derived from what the community's own mod projects do and warn about. Each rule names its
evidence. If a rule conflicts with a device file, the device file is more specific.

## A. Safety - never skip

**A1. Do not touch the bootstrap/bootloader or the updater section.** Patch the main OS only.
Then the stock OS file can always restore the unit. `[doc]` {elekloader-adapting} {elekloader-readme}
{digikit} (DT2: sections 2 = bootstrap and 4 = updater must never be modified; sections 3 and 7 are the
patch targets) {dn2-cfw} (brick checker refuses any bootstrap change).

**A2. Know the recovery path before anything is flashed.** Write it down in your output, with the exact
button combination for the device (see [`common/recovery.md`](common/recovery.md)). Keep the stock OS file and,
for Digitakt II / Digitone II, a physical DIN MIDI interface at hand. `[doc]` {digikit} {synthack-os}
{dn2-cfw}

**A3. Back up first.** Back up projects/sounds (+Drive) with Elektron Transfer before flashing. `[doc]` {dn2-cfw}

**A4. Never power off during an upgrade.** `[doc]` {elekloader-readme}

**A5. BOOTSTRAP UPGRADE is the only irreversible step** (DT2 startup menu; runs only if the incoming
bootstrap version is strictly higher). Never build or send an image with a higher bootstrap version. `[doc]` {digikit}

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

## B. Legal / distribution

**B1. Never include, commit or publish Elektron firmware** (original or modified), dumps or decompressed code.
Ship patches that carry only the author's bytes plus hashes of the expected stock bytes. The **user supplies the
stock OS file.** `[doc]` {elekloader-readme} {elektron-firmware-tool} {digitakt-ii-research} {dn2-cfw}

**B2. Identify the stock file by hash (SHA-256) and refuse anything else** - modified files and other OS
versions are rejected, not "adapted". `[doc]` {digitakt-ii-research} {synthack-os} {syntakt-workbench}

**B3. Say what you are.** Mods are unofficial, unsupported, not affiliated with Elektron, and used at the
user's own risk (voids warranty, may brick). Put that in every README. `[doc]` all mod READMEs

**B4. Respect the manufacturer's forum policy** (Elektron removes mod links/files/instructions from
Elektronauts; discussion lives on GitHub/Discord/elektronmods.com). `[doc]` {letsdatascience}

## C. Process

**C1. One mod = one OS version.** Addresses and stock bytes are version-specific (hash-pinned). A mod for
Digitakt mk1 1.53 is refused on 1.54; Digitakt II 1.17 addresses do not carry to 1.18+. Porting = find every
address again. Keep a separate build per OS version. `[doc]` {elekloader-adapting} {digitakt2-perform}

**C2. Test ladder, in order:** build -> lint -> emulator cold boot compared against stock -> a unit you can
recover. A verifying build is well-formed, **not** proven to work. `[doc]` {elekloader-adapting}

**C3. Record the test state of every build** as `hw` / `emu` / `untested` in the project metadata. Several
projects ship builds that are lint-clean but "not yet run on a unit". `[doc]` {digislicer} {digichroma} {digitakt2-perform}

**C4. Emulators do not emulate audio.** digikit has no DSP emulation (Digitakt II: "no audio, no input,
storage not supported"). Changes to audio code or DSP cannot be validated there. `[doc]` {digikit}

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

**E1. Projects store values by slot, not by table row.** Moving the OS parameter table does not by itself change
the saved format. New rows are only safe if they follow the author's growth rules
(`docs/parameter-table-growth.md` in dn2-cfw - not yet read by us). `[doc]` {dn2-cfw}
