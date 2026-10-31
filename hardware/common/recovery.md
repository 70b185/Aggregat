# Recovery and flashing

Know this **before** flashing a test unit. Sources are second-hand; check Elektron's own pages for your device.

## Entering the startup menu
| Device | How | Source |
|---|---|---|
| Digitakt mk1 | Hold FUNC while powering on -> startup menu -> TRIG 4 = OS UPGRADE -> send stock `.syx` (Transfer's legacy OS upgrade mode) | `[doc]` {elekloader-readme} |
| Digitakt II | Hold FUNC at power-on -> startup menu. SysEx accepted **over MIDI DIN only, not USB** (digikit's reading of the bootstrap) | `[doc]` {digikit} |
| Digitone II | Hold FUNC at power-on -> TRIG 4 (OS UPGRADE) -> send stock OS over DIN MIDI. Tested on dn2-cfw's author's unit | `[hw]` {dn2-cfw} |
| Digitone (mk1) | Not stated by the sources we read. Assume same pattern as Digitakt mk1, **verify** | `[?]` |
| Syntakt | Synthack-OS: flash over USB with Elektron Transfer ("Drop" page); revert by flashing the stock OS the same way. Exact startup-menu recovery not stated | `[doc]` {synthack-os} |
| Analog Heat MKI/MKII | Hold ACTIVE (MKI) or ON (MKII) while powering on -> STARTUP menu -> press [LFO] = OS UPGRADE -> send the SysEx file via MIDI In. Official Elektron instructions | `[doc]` {elektron-heat-notes} |
| Analog Heat +FX | Own OS and own release notes; do not use the MKII file ("Incompatible OS" error seen on Elektronauts) | `[doc]` {elektron-heat-fx-notes} {elektronauts-heatfx} |

## Rules of thumb (all from the sources above)
- The stock OS file can always recover the unit **if** the bootstrap/bootloader was never modified (rule A1).
- Keep a physical MIDI interface for DIN-only recovery (Digitakt II / Digitone II). {digitakt-ii-research}
- Do not power off during an upgrade.
- Known recovery-path problem: dn2_firmware_explore's *own* (rebuilt) images stall at ~80% when sent via the recovery path; a fix is built, untested. Stock files are fine. `[doc]` {dn2-firmware-explore}
- Digitakt II OS 1.16 is no longer on Elektron's download page (author suggests asking Elektron support). Keep stock files you may need. `[doc]` {digitakt-ii-research}
