# Recovery and flashing

Know this **before** flashing a test unit. Sources are second-hand; check Elektron's own pages for your device.

## Entering the startup menu
| Device | How | Source |
|---|---|---|
| Digitakt mk1 | Hold FUNC while powering on -> startup menu -> TRIG 4 = OS UPGRADE -> send stock `.syx` (Transfer's legacy OS upgrade mode) | `[doc]` {elekloader-readme} |
| Digitakt II | Hold FUNC at power-on -> startup menu. SysEx accepted **over MIDI DIN only, not USB** (earlier digikit README's reading of the bootstrap). The current digikit README says bootstrap-menu recovery is **not tested on hardware** | `[doc]` {digikit-old} {digikit} |
| Digitone II | Hold FUNC at power-on -> TRIG 4 (OS UPGRADE) -> send stock OS over DIN MIDI. Tested on dn2-cfw's author's unit | `[hw]` {dn2-cfw} |
| Digitone (mk1) | Not stated by the sources we read. Assume same pattern as Digitakt mk1, **verify** | `[?]` |
| Syntakt | Synthack-OS: flash over USB with Elektron Transfer ("Drop" page); revert by flashing the stock OS the same way. Exact startup-menu recovery not stated | `[doc]` {synthack-os} |
| Analog Heat MKI/MKII | Hold ACTIVE (MKI) or ON (MKII) while powering on -> STARTUP menu -> press [LFO] = OS UPGRADE -> send the SysEx file via MIDI In. Official Elektron instructions | `[doc]` {elektron-heat-notes} |
| Analog Heat +FX | Hold ACTIVE while powering on -> STARTUP menu -> press **MOD** (not LFO) = OS UPGRADE -> send the SysEx file via MIDI In. Elektron recommends the C6 - SysEx Tool for sending. Own OS: the MKII file is rejected ("Incompatible OS" on Elektronauts) | `[doc]` {elektron-heat-fx-notes} {elektronauts-heatfx} |

## Rules of thumb (all from the sources above)
- The stock OS file can always recover the unit **if** the bootstrap/bootloader was never modified (rule A1).
- Keep a physical MIDI interface for DIN-only recovery (Digitakt II / Digitone II). {digitakt-ii-research}
- Do not power off during an upgrade.
- Known recovery-path problem: dn2_firmware_explore's *own* (rebuilt) images stall at ~80% when sent via the recovery path; a fix is built, untested. Stock files are fine. `[doc]` {dn2-firmware-explore}
- Digitakt II OS 1.16 is no longer on Elektron's download page (author suggests asking Elektron support). Keep stock files you may need. `[doc]` {digitakt-ii-research}

## What Elektron's own release notes say (elektron.se, pages updated 2026-10-01 for Digitakt II / Digitone II; 2024-10-16 for Heat +FX)
- Two upgrade paths: from within the OS (Transfer, DROP page, confirm with YES on the device; devices whose OS does not fully support Transfer are sent to the LEGACY OS UPGRADE page) and from the **Startup Menu** (device's **MIDI port, not USB**; hold FUNC while powering on; TRIG 4 = OS UPGRADE; Transfer in LEGACY OS UPGRADE mode). `[doc]` {elektron-dt2-notes} {elektron-dn2-notes}
- "Some upgrades also upgrade the bootstrap" right after the first restart; do not turn the power off then. `[doc]` {elektron-dt2-notes} {elektron-dn2-notes} {elektron-heat-fx-notes}
- Downgrading is **not supported** and is at the user's own risk; user content may be lost. `[doc]` {elektron-dt2-notes} {elektron-dn2-notes}
- Digitakt II, first reboot after upgrading to OS 1.15: a file-system integrity check (up to a minute). On errors: back up all projects and samples with Transfer, SETTINGS > SYSTEM > FORMAT +DRIVE (tick SAMPLES), re-import. `[doc]` {elektron-dt2-notes}
- Heat +FX: in-OS path is SETTINGS > SYSTEM > OS UPGRADE with the file sent through MIDI In **or USB MIDI In**; the startup path takes MIDI In only. `[doc]` {elektron-heat-fx-notes}

## Additions from the "read everything" pass (2026-10-31)
- **Digitakt II (digitakt-ii-research `RECOVERY.md`):** keep an official stock `.syx`, a physical MIDI interface and cable ready; MIDI OUT of the interface to the Digitakt II's MIDI IN (**USB MIDI cannot be used**); hold FUNC at power-on, TRIG 4 = OS UPGRADE; in Elektron Transfer open the SYSEX TRANSFER page and choose **"OS upgrade via device startup menu"**; select the stock file and keep power on until the unit reboots. No durations are given and the author states recovery is not guaranteed if the startup menu or bootloader cannot run, power is lost during a critical write, or storage/hardware is damaged; the page reports no hardware test of the procedure. `[doc]` {dt2-recovery}
- **Syntakt (SyntHack OS `RECOVERY.md`):** if the OS still boots, flash the stock `.syx` via Transfer's Drop page (works even if a mod misbehaved); if not, MIDI interface with a 5-pin OUT to the Syntakt's MIDI IN (**"USB doesn't work from the startup menu"**), FUNC at power-on, TRIG 4, Transfer SYSEX TRANSFER "OS Upgrade via device startup menu", **tens of minutes at 31.25 kbit/s**, the unit restarts itself. **Avoid TRIG 2 (empty reset) and TRIG 3 (factory reset) in the startup menu - both erase data.** Do a dry run of the DIN procedure with the stock OS before the first flash; flash only files for which `tools/unpack/eft.py info <file>` reports `checksums : ok`; no hardware results are reported on the page. `[doc]` {synthack-recovery}
- **Other Elektron devices, from elekloader's BUILDING.md (for reference):** Analog Rytm MKII and Analog Four MKII - FUNC at power-on (STARTUP menu), TRIG 4, stock `.syx` over 5-pin DIN MIDI, USB does not work. Octatrack - hold FUNC at power-on, **TRIG 3 = MIDI UPGRADE**, DIN MIDI; normal flashing from the card (PROJECT > SYSTEM > USB DISK MODE, copy the `.bin`, then PROJECT > SYSTEM > OS UPGRADE, power-cycle once more before judging). Digitakt mk1 / Digitone mk1: FUNC, TRIG 4, legacy mode; the connection is not stated for these two. `[doc]` {elekloader-building}
- **Transfer "PREPARING" stalls:** Overtone 1.0 could stall on "Receiving"/"PREPARING..." when an OS was sent while Overtone ran; the earlier Plaits builds in digitakt-ii-research's All-in-One line "failed normal Transfer updates at 0%/PREPARING" and the author says not to assume the route is reliable on every installation. Recovery from such a stall is a power cycle and the startup menu. `[hw]` {overtone} {dt2-install}

## Why recovery survives a bad OS, and what would break it (Digitone II 1.12; Digiwerk notes T1.4, T1.5) {dn2-cfw-t14} {dn2-cfw-t15}
**Result:** no content of flash at `0x80000` and above can stop the STARTUP menu when FUNC is held. This was checked statically and in 15 emulated boots with stock, corrupt, truncated, all-`0xFF` and hostile containers. The menu, the FUNC decision, the font and the OS UPGRADE receive all live in the bootstrap and read **no flash** until a transfer commits. `[emu]`

**NOR flash map (16 MiB, DSPI0 `0xFC05C000`):**
| Range | Content | Written by |
|---|---|---|
| `0x000000-0x040000` | NXP serial-boot image | no firmware path (factory only) |
| `0x040000-0x080000` | **bootstrap** (section 2, version word `0x0201`), DYB-protected | only the bootstrap self-upgrade and the factory console `#FULL_UPGRADE` |
| `0x080000-0x380000` | OS container (3 MB window; stock about 1.1 MB packed) | in-OS upgrade, console `#UPGRADE`, STARTUP-menu upgrade |
| `0x380000` / `0x3c0000` | test/flag record / serial record (same on DT2) | factory console only |
| `0x400000`, `0x800000`, `0xc00000` | legacy "COKi" persistence copies | boot migration to eMMC |
The main OS has no chip-erase command, and no main-OS path writes below `0x40000`. `[doc]`

**What a mod must never change** (keep all of these, and recovery stays intact):
1. **Section 2 byte-identical, and its table entry version `0x0201`.** A higher version there plus a new section-2 image is the one way the boot-time self-upgrade rewrites the bootstrap. It runs on *every* boot, before the menu.
2. **The container at most `0x200000` bytes.** The in-OS writer has no length clamp and wraps 24-bit addresses. An over-long container could erase `0x380000`/`0x3c0000` and, past `0xF80000`, wrap onto the bootstrap.
3. **Section 4 (the factory board-test program and in-place loader) stock, and a non-negative depack margin** at both stages. If the panel read times out, the bootstrap boots through section 4. An underflowing build then hangs with no menu, a soft brick.
4. **The panel-MCU firmware blob, its version word and its updater stock.** The main OS reflashes the panel when it reports a version below `0x15`, and FUNC and the menu keys depend on the panel.
5. **The serial and test records intact.**
6. **No new soft-reset paths** (`0xB0B0DADA` at `0x48000000`, 5-key, panel timeout): they set maintenance/section-4 flags.

## Factory reset (official FAQ on the support pages, 2026-10-31) - not a recovery, it overwrites data
- **Digitakt II:** hold FUNC while powering on, press the key the startup menu shows; project slot 001 is overwritten with the factory project and the loaded project is cleared; sound/preset bank A is overwritten; other slots/banks untouched; **samples on the +Drive are kept**. `[doc]` {elektron-dt2-support}
- **Digitone II:** same procedure; project slot 001 overwritten, loaded project cleared, **sound banks A and B** overwritten; other slots/banks untouched. Save the active project above slot 001 first. `[doc]` {elektron-dn2-support}

