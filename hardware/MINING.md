# Reading list - what still has to be mined for hardware/

Ordered by expected value for an agent that builds mods. Tick off and fold the result into the matching device file.

## Digitone II (highest value)
- [ ] complex-ping/digitone-2-modding-skill: `skills/.../references/*` - addresses, hook sites, ColdFire-to-DSP frame format, free memory, and the **hardware rules the emulators cannot check** (each "once silenced a real unit")
- [ ] angellinares/dn2_firmware_explore: `docs/flashing.md`, `docs/mainos-image.md`
- [ ] naturarum/dn2-cfw: `docs/parameter-table-growth.md`, T1.4/T1.5 notes (flash-write audit, STARTUP independence), `tools/brickcheck` (the 12 checks)
- [ ] De-Pattern/dn2mk2-firmware: `docs/SAFETY.md`, `docs/emulator.md`, `docs/user-reports.md`, FIRMWARE.md v0.20 and older
- [ ] complex-ping/overtone: `docs/` and the patcher's ~160 checks
- [ ] nzimas/digirust: `docs/FEATURES.md` (Digitone II OS 1.12)

## Digitakt mk1 / Digitone mk1
- [ ] elekloader `docs/DEVICES.md` (maturity per device), `mods/core/mod.json` (all core-owned sites), `mods/core-dn1`
- [ ] machine-ID usage of digisophie, DT-FM, digigrain, digidrum, digistring (fill the registry in `devices/digitakt.md`)
- [ ] Digitone mk1 recovery buttons (not stated in anything we read)

## Digitakt II
- [ ] lalzart/digitakt-ii-firmware-research-public (architecture notes), lalzart/dt2-machine-lab
- [ ] karigardarsson/digitakt-ii-research: install and recovery docs

## Syntakt
- [ ] karigardarsson/Synthack-OS: `RECOVERY.md`, `patch.json` examples, protected-section list
- [ ] Syntakt container: signed or not? sections?

## Analog Heat
- [ ] Anything at all. Candidate first steps: check whether the elektron-firmware-tool README/issues mention Heat results; search Elektronauts-adjacent communities and GitHub topics for "analog heat" firmware; ask the user whether they own Heat OS files to inspect.

## Cross-checks
- [ ] altstrument.org device pages (Digitakt 12, Digitakt II 3, Digitone 5, Digitone II 3, Syntakt 4 firmwares listed) against `data/projects.yml`
- [ ] Lapin list: re-read weekly for new Elektron entries
- [ ] Hardware facts above were extracted from READMEs by summarising tools; spot-check numbers (addresses, sizes) against the original files before depending on them.
