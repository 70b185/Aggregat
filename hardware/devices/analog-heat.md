# Analog Heat (MKI, MKII, +FX)

Coverage: **official facts only. We found no community firmware mod and no reverse-engineering notes.**
Projects/tools: [../../devices/analog-heat.md](../../devices/analog-heat.md)

## Official facts (elektron.se, read 2026-10-31)
- Analog Heat MKI and MKII: latest OS **1.22** (2024-10-16, "added support for Overbridge 2.13"). `[doc]` {elektron-heat-mkii-page}
- The **+FX** has its own OS and release notes (last updated 2024-10-16). **The MKII file is rejected on +FX** ("Incompatible OS" in Transfer). `[doc]` {elektron-heat-fx-notes} {elektronauts-heatfx}
- Minimum OS for updating via Transfer: 1.20. Product IDs from Elektron's FAQ: Analog Heat 000A, Analog Heat MKII 0016 (meaning of the field not shown). `[doc]`/`[?]` {elektron-support} {elektron-faq}
- Update/recovery MKI/MKII: hold ACTIVE (MKI) or ON (MKII) while powering on -> STARTUP menu -> [LFO] = OS UPGRADE -> send the SysEx file via MIDI In (or USB MIDI In from within the OS). `[doc]` {elektron-heat-notes}
- Update/recovery +FX differs: hold ACTIVE, then **MOD** = OS UPGRADE (see below). `[doc]` {elektron-heat-fx-notes}
- Elektron Transfer 1.10.4 (2026-06-23) covers Heat +FX; Overbridge integration since OS 1.2 (USB audio streaming, MKII Overbridge). `[doc]` {elektron-heat-mkii-page} {synthanatomy-heat}

## Analog Heat +FX (official, elektron.se release notes, page updated 2024-10-16)
- OS **1.02** is the newest listed (adds Overbridge 2.13 support); **1.01** added a momentary mode for ACTIVE (SETTINGS > OPTIONS), OUTPUT GAIN (PRESET SETUP), FX TO USB (AUDIO ROUTING), randomize/reset on parameter pages, LFO RND slew, and fixed MIDI input on further channels, modulation matrix DEPTH resolution, BANK/SBANK MIDI support, LFO trigger timing and VU/clip display. 1.00 is only the baseline. No release dates are given per version. `[doc]` {elektron-heat-fx-notes}
- 1.01 was announced as exclusive to the +FX: not compatible with Analog Heat MKI/MKII. `[doc]` {gearnews-heatfx}
- Product facts from reviews/shops (not firmware): released 2023-05 (Superbooth), $999 / EUR 999; the analog "heat block" keeps 8 stereo distortion circuits, a 7-mode analog filter and a 2-band EQ, adds a noise gate and a chain of digital effects (reverb, delay, chorus, warble, bits, compressor, bass focus) with reorderable routing; 128x64 OLED; MIDI In/Out/Thru; two CV/expression/footswitch inputs; class-compliant USB audio and Overbridge. `[doc]` {synthtopia-heatfx} {sos-heatfx} {musicradar-heatfx}
- A forum post says the +FX is "just an iterative upgrade to the MKII" (opinion, no hardware evidence). `[?]`
- **No teardown, PCB photo, chip list or reverse-engineering note for any Analog Heat was found** in two search rounds (2026-10-31).

## More Heat facts from listings and forum posts (marketing/forum level, not firmware evidence)
- **+FX modulation and storage** (CDM listing): 1 assignable envelope generator/follower with two destinations, **3 assignable LFOs** (two destinations each), **512 user preset slots**, 128x64 OLED, MIDI In/Out/Thru with DIN Sync out, 24-bit/48 kHz converters, 215 x 184 x 63 mm, ~1.5 kg. The MKII has 1 assignable LFO, 1 envelope/follower and **128 user presets** (listings); the +FX ships with PSU-3c, the MKII with PSU-3b. Headphone out peak +19 dBu (+FX listing). Two CV/expression/footswitch input jacks. `[?]` {heat-fx-specs}
- **MIDI behaviour (forum users citing the manual):** the Heat can send MIDI clock and program change (manual p.18 of the MKI-era manual); forwarding notes received over USB to MIDI Out is reported as not possible; the MKI-era manual recommended a TM-1 TurboMIDI interface for sending OS upgrades to the MIDI In port (the current +FX notes recommend the C6 - SysEx Tool). `[?]` {elektronauts-heat-midi}
- **Signal path (+FX):** forum users quoting the manual: the digital effects form an "FX block"; an **analog-only mode turns off all digital effects and gives a pure analog path with no AD/DA**. So the +FX digitises the signal only when digital effects are in use - relevant for anyone modelling its processing chain. Headphone peak level is given as +19 dBu (one listing) and +22 dBu (Equipboard) - unresolved. `[?]` {kvr-heatfx} {equipboard-heatfx}
- **Third-generation naming:** a merchant calls the +FX "the third generation"; Elektronauts users joke about an "Analog Heat III+FX". Not a hardware statement. `[?]`
- 2026-10-31, second attempt: the elektron.se +FX support page and the explorer page returned a site error (client_error); still unread.
- Needed but not read (the first fetch was not approved): the elektron.se support pages for Analog Heat +FX, the explorer/spec page and the manuals (MIDI implementation, modulation matrix, OS upgrade steps). See [`../MINING.md`](../MINING.md).

## Tooling that already lists the Heat
- elektron-firmware-tool names Analog Heat MKI, MKII and +FX among supported devices (container tool, not a mod). {elektron-firmware-tool}
- Elektroid (sample/SysEx manager) lists Analog Heat MKI, MKII and +FX. Overwitch (Overbridge audio on Linux) lists Analog Heat, MKII and +FX. {elektroid} {overwitch}
- screendump lists Analog Heat as known but **not implemented**. {screendump}
- Neither the Lapin list nor altstrument.org carries a firmware entry for any Analog Heat.

## Unknown / to do
CPU/DSP architecture, container format specifics, signing, memory map, whether Heat firmware can be unpacked by the same tools beyond the container level, any community interest: nothing verified. First step would be running elektron-firmware-tool on the user's own Heat OS files (not by an agent without the user's files).
