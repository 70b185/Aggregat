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
