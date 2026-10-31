# Analog Heat (MKI, MKII, +FX)

Coverage: **official facts only. We found no community firmware mod and no reverse-engineering notes.**
Projects/tools: [../../devices/analog-heat.md](../../devices/analog-heat.md)

## Official facts (elektron.se, read 2026-10-31)
- Analog Heat MKI and MKII: latest OS **1.22** (2024-10-16, "added support for Overbridge 2.13"). `[doc]` {elektron-heat-mkii-page}
- The **+FX** has its own OS and release notes (last updated 2024-10-16). **The MKII file is rejected on +FX** ("Incompatible OS" in Transfer). `[doc]` {elektron-heat-fx-notes} {elektronauts-heatfx}
- Minimum OS for updating via Transfer: 1.20. Product IDs from Elektron's FAQ: Analog Heat 000A, Analog Heat MKII 0016 (meaning of the field not shown). `[doc]`/`[?]` {elektron-support} {elektron-faq}
- Update/recovery: hold ACTIVE (MKI) or ON (MKII) while powering on -> STARTUP menu -> [LFO] = OS UPGRADE -> send the SysEx file via MIDI In (or USB MIDI In from within the OS). `[doc]` {elektron-heat-notes}
- Elektron Transfer 1.10.4 (2026-06-23) covers Heat +FX; Overbridge integration since OS 1.2 (USB audio streaming, MKII Overbridge). `[doc]` {elektron-heat-mkii-page} {synthanatomy-heat}

## Tooling that already lists the Heat
- elektron-firmware-tool names Analog Heat MKI, MKII and +FX among supported devices (container tool, not a mod). {elektron-firmware-tool}
- Elektroid (sample/SysEx manager) lists Analog Heat MKI, MKII and +FX. Overwitch (Overbridge audio on Linux) lists Analog Heat, MKII and +FX. {elektroid} {overwitch}
- screendump lists Analog Heat as known but **not implemented**. {screendump}
- Neither the Lapin list nor altstrument.org carries a firmware entry for any Analog Heat.

## Unknown / to do
CPU/DSP architecture, container format specifics, signing, memory map, whether Heat firmware can be unpacked by the same tools beyond the container level, any community interest: nothing verified. First step would be running elektron-firmware-tool on the user's own Heat OS files (not by an agent without the user's files).
