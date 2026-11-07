# Aggregat

**An index and agent knowledge base for community firmware, mods and tools on Elektron devices.** In depth for
Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt and Analog Heat MKI/MKII/+FX; as a catalogue for Octatrack, Analog
Rytm/Four/Keys, Model:Cycles/Samples, Machinedrum and Monomachine.

**[Website](https://70b185.github.io/Aggregat/)** (search everything) ·
[Network map](https://70b185.github.io/Aggregat/?t=network) ·
[Community](https://70b185.github.io/Aggregat/?t=community) ·
[Stock bugs](hardware/STOCK-BUGS.md) ·
[Incidents](hardware/INCIDENTS.md) ·
[Research map](RESEARCH-MAP.md)

## Start here

| You are | Read |
|---|---|
| **Musician** looking for a mod or a tool | [MODS.md](MODS.md) (mods, custom firmware, loaders) · [MUSICIAN-TOOLS.md](MUSICIAN-TOOLS.md) (editors, sample and project managers, nothing that changes firmware) · [INDEX.md](INDEX.md) and [devices/](devices/) (everything per device) |
| **Developer** writing a mod | [hardware/](hardware/README.md) (how the hardware works) · [AGENT-RULES.md](hardware/AGENT-RULES.md) (rules, grown from tests) · [INCIDENTS.md](hardware/INCIDENTS.md) (what went wrong on real units) · [STOCK-BUGS.md](hardware/STOCK-BUGS.md) (bugs in Elektron's own OS, check before you blame your mod) · [DEV-TOOLS.md](DEV-TOOLS.md) (toolchains, emulators, unpackers) · [FEATURE-OVERLAP.md](FEATURE-OVERLAP.md) (features already built elsewhere) |
| **Researcher**, or want to help | [RESEARCH-MAP.md](RESEARCH-MAP.md) (what is known and open per device, shared goals, tests that take minutes on a stock unit) · [research/PARTICIPANTS.md](research/PARTICIPANTS.md) (take part with your project) |
| **Agent or script** | [export/](export/README.md): one SQLite/JSON database with projects, relations, rules, incidents, stock bugs, sources, conflicts and about 1,000 hardware facts, with full-text search |

The lists are generated from [`data/projects.yml`](data/projects.yml); [PROJECT-FAMILIES.md](PROJECT-FAMILIES.md)
shows which entries are forks, ports or copies of each other, so nothing is counted twice.

## Using it with an AI agent

Point the agent at this repo. For open-ended research, start with the prompt in [RESEARCH-MAP.md](RESEARCH-MAP.md);
otherwise have it read, in this order:

1. [`hardware/README.md`](hardware/README.md): the ten things to know first
2. [`hardware/AGENT-RULES.md`](hardware/AGENT-RULES.md), [`hardware/INCIDENTS.md`](hardware/INCIDENTS.md) and [`hardware/STOCK-BUGS.md`](hardware/STOCK-BUGS.md)
3. [`hardware/common/recovery.md`](hardware/common/recovery.md) and [`hardware/common/flash-procedure.md`](hardware/common/flash-procedure.md)
4. the device file under [`hardware/devices/`](hardware/devices/), then [`INDEX.md`](INDEX.md) for the project it builds on

Evidence tags: `[hw]` seen on a real unit, `[emu]` emulator only, `[doc]` stated without a test result, `[?]` unclear
or inferred. Everything is second-hand: check addresses and byte patterns against the original source. Source keys
like `{dn2-ele3}` resolve in [`hardware/SOURCES.md`](hardware/SOURCES.md).

**Starting a new project?** Copy [`research/AGGREGAT_RESEARCH.md`](research/AGGREGAT_RESEARCH.md) into its root on
day one and let your agent keep its results table. It holds the shared goals, tasks and tests as of that day; we merge
results back by hand, with credit.

## Contributing

- **Pull requests** are welcome: correct a fact about your project, add evidence, fix the tooling. A maintainer
  reviews and merges by hand ([credits](research/PARTICIPANTS.md)).
- **Issue forms:** [test result](https://github.com/70b185/Aggregat/issues/new?template=test-result.yml) for a test
  from the research map, [stock bug](https://github.com/70b185/Aggregat/issues/new?template=stock-bug.yml) for a bug in
  Elektron's OS.
- **Ground rules:** metadata only (names, links, status, short notes in our own words); never firmware, extracted
  sections, built images or copied code. Every entry has a source and a date. Do not post firmware-mod links on
  Elektronauts (Elektron's policy since 2026-09-16), and read each project's contribution rules before opening issues
  there.
- **Not affiliated with Elektron.** Custom firmware can brick a unit and may affect warranty. This repo points to
  projects; it does not endorse or test them.

## Keeping it current

A daily GitHub Action checks every catalogued repo for changes and writes [`state/CHANGES.md`](state/CHANGES.md).
To update by hand: edit [`data/projects.yml`](data/projects.yml) (fields are documented at its top) and run
`python3 scripts/build.py`; generated Markdown carries a marker, so edit the YAML, not the Markdown. The full
procedure, including finding new projects and merging research results, is in [`docs/UPDATING.md`](docs/UPDATING.md).

## Scope

- **Phase 1, in depth:** Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX: catalogue plus the
  knowledge base in [`hardware/`](hardware/).
- **Phase 2, catalogue:** Octatrack, Analog Rytm, Analog Four/Keys, Model:Cycles/Samples, Machinedrum, Monomachine,
  with device profiles in `hardware/devices/` where projects have published research.
- Not covered: Tonverk and other brands ([`docs/BACKLOG.md`](docs/BACKLOG.md)).

Related directories: [Awesome Music Gear Firmware](https://github.com/Lapin/awesome-music-gear-firmware) (19 brands),
[altstrument](https://altstrument.org) (structured directory of alternative firmware),
[elektronmods.com](https://elektronmods.com) (community forum). Aggregat goes deeper on fewer devices: the current
version and OS per project, and a hardware knowledge base for agents.

## How the projects relate

The [network map](https://70b185.github.io/Aggregat/?t=network) shows all relations, including mods for a loader,
tools a project uses and projects it cites. The graph below, drawn by GitHub, shows lineage only: forks, copies,
ports, variants, and projects that build on, bundle, describe or vendor code from another. Arrows point to the entry
named, boxes group device families, colours show the licence. Each relation names its evidence in
[`data/projects.yml`](data/projects.yml); [PROJECT-FAMILIES.md](PROJECT-FAMILIES.md) lists them.

<!-- relation-graph:start - generated by scripts/build.py from data/projects.yml, do not edit by hand -->

106 entries with 110 relations. Colour: licence family (green permissive, blue copyleft, yellow public domain, grey none stated or not recorded).

```mermaid
flowchart LR
  subgraph n_group_Digitakt["Digitakt"]
    n_digi1_mods["digi1_mods<br/>not recorded"]:::none
    n_digifilter["DigiFilter<br/>GPL-2.0-or-later"]:::copyleft
    n_digimod["digimod<br/>MIT (own code); mods derived from digikit and the All-in-One AGPL-3.0-or-later"]:::copyleft
    n_digiseq_digitakt["DIGISEQ (Digitakt)<br/>GPL"]:::copyleft
    n_digisnake_digitakt["DIGISNAKE (Digitakt)<br/>GPL"]:::copyleft
    n_digisophie["Digisophie / Sophie for Digitakt<br/>not recorded"]:::none
    n_digitakt_sidecar_pi["Digitakt integrated sidecar<br/>not stated"]:::none
    n_digitakt_pattern_editor_juce["Digitakt Pattern Editor (JUCE)<br/>BSD-2-Clause"]:::permissive
    n_digitakt_ii_research["digitakt-ii-research<br/>MIT (repo root); the Sample Editing Pack AGPL-3.0-or-later (derived from digikit)"]:::copyleft
    n_digitakt_midi_mcp["digitakt-midi-mcp<br/>not recorded"]:::none
    n_digitakt_reorder["digitakt-reorder<br/>MIT"]:::permissive
    n_directjump_digitakt["DIRECT JUMP (Digitakt)<br/>GPL"]:::copyleft
    n_dt_fm["DT-FM<br/>MIT, part GPL-2.0-or-later"]:::copyleft
    n_dt2_capicola["dt2-capicola<br/>not recorded"]:::none
    n_dt2_machine_lab["dt2-machine-lab<br/>not stated"]:::none
    n_dtdump["dtdump<br/>not recorded"]:::none
    n_elk_herd["elk-herd<br/>BSD-2-Clause (per other projects)"]:::permissive
    n_keyframer_lab["Frame Lab (keyframer-lab)<br/>AGPL"]:::copyleft
    n_mezclando["Mezclando<br/>GPL-3.0-or-later"]:::copyleft
    n_pump_digitakt["PUMP (Digitakt)<br/>GPL"]:::copyleft
    n_screendump["screendump<br/>MIT"]:::permissive
    n_sidecar_digitakt["Sidecar (Digitakt mod)<br/>GPL"]:::copyleft
  end
  subgraph n_group_Digitone["Digitone"]
    n_digiseq_digitone["DIGISEQ (Digitone)<br/>GPL"]:::copyleft
    n_digisnake_digitone["DIGISNAKE (Digitone)<br/>GPL"]:::copyleft
    n_elektron_mods_rumorismo["Digitone MK1 Modding Project<br/>not recorded"]:::none
    n_directjump_digitone["DIRECT JUMP (Digitone)<br/>GPL"]:::copyleft
    n_dn2mk2["DN2 mk2 Mod (dn2mk2-firmware)<br/>AGPL-3.0-or-later"]:::copyleft
    n_dn2_cfw["dn2-cfw<br/>not recorded"]:::none
    n_dn2_firmware_explore["dn2_firmware_explore<br/>AGPL-3.0-or-later"]:::copyleft
    n_overtone["Overtone<br/>not recorded"]:::none
    n_pump_digitone["PUMP (Digitone)<br/>GPL"]:::copyleft
    n_ringtone["RingTone<br/>not recorded"]:::none
    n_syxgrid["SYXGRID v2<br/>not recorded"]:::none
    n_tone_fx["Tone+FX<br/>GPL-2.0"]:::copyleft
  end
  subgraph n_group_Syntakt["Syntakt"]
    n_synfact["Synfact<br/>GPL-2.0 (old release repo MIT)"]:::copyleft
    n_synthack_os_upstream["SyntHack OS (upstream)<br/>MIT"]:::permissive
    n_synthack_os["Synthack-OS<br/>not recorded"]:::none
  end
  subgraph n_group_Octatrack["Octatrack"]
    n_acidtrack_modules["aCiDtRacK modules<br/>MIT"]:::permissive
    n_ems_octakit["ems-octakit<br/>not recorded"]:::none
    n_midisc["midisc<br/>MIT"]:::permissive
    n_midisc_patcher["midisc-patcher<br/>not stated"]:::none
    n_octa_bt_pt["octa-bt-pt<br/>not recorded"]:::none
    n_octa_panel["octa-panel<br/>MIT"]:::permissive
    n_octabam["octabam<br/>MIT"]:::permissive
    n_octamax["OCTAMAX<br/>not recorded"]:::none
    n_octatrack_manager["Octatrack Manager<br/>not recorded"]:::none
    n_octatrack_modules_radiohagen["Octatrack modules<br/>not recorded"]:::none
    n_octatrick["Octatrick<br/>not recorded"]:::none
    n_octemu["octemu<br/>not recorded"]:::none
    n_ot_tools_io["ot-tools-io<br/>not recorded"]:::none
    n_passos["PassOS<br/>MIT"]:::permissive
    n_rebirth2octatrack["ReBirth to Octatrack<br/>not recorded"]:::none
    n_trackpatterns["TrackPatterns<br/>MIT"]:::permissive
  end
  subgraph n_group_Analog_Rytm["Analog Rytm"]
    n_rytm_mk1_mods_hugz202["Analog Rytm MK1 OS 1.74 mods<br/>not recorded"]:::none
    n_libanalogrytm["libanalogrytm<br/>MIT"]:::permissive
    n_rytm_mods_src["rytm-mods-src<br/>GPL-2.0-only"]:::copyleft
    n_rytm_rs["rytm-rs / rytm-sys<br/>MIT"]:::permissive
    n_rytm1_mods["rytm1_mods<br/>not stated"]:::none
    n_rytm2_mods["rytm2_mods<br/>GPL"]:::copyleft
  end
  subgraph n_group_Model["Model"]
    n_bias["BIAS<br/>MIT"]:::permissive
    n_chord_keys["Chord Keys<br/>not stated"]:::none
    n_cycles_control_all_config["Control All Config<br/>not recorded"]:::none
    n_cycles_engines["Cycles Engines<br/>not recorded"]:::none
    n_cycles_mod_standard["Cycles Mod Standard<br/>MIT"]:::permissive
    n_cycles_one_shot["Cycles One-Shot<br/>not recorded"]:::none
    n_elektron_model_tweaks["elektron-model-tweaks<br/>not recorded"]:::none
    n_modded_cycles["Modded Cycles<br/>MIT"]:::permissive
    n_modded_cycles_techno["Modded Cycles Techno Edition<br/>MIT (firmware side); plug-in AGPL-3.0 (JUCE)"]:::copyleft
    n_model_tg["Model-TG<br/>not recorded"]:::none
    n_model27["model27<br/>MIT"]:::permissive
    n_model909["model909<br/>MIT"]:::permissive
    n_motorcycles["Motor:Cycles<br/>not recorded"]:::none
    n_ms_multi_output["ms-multi-output<br/>not recorded"]:::none
    n_plaits_on_models["plaits-on-models<br/>not recorded"]:::none
    n_spokes["SPOKES<br/>MIT"]:::permissive
    n_supermodel_edition["Supermodel Edition<br/>not stated"]:::none
    n_vladiktron_spoke["Vladiktron Spoke<br/>not recorded"]:::none
  end
  subgraph n_group_Machinedrum["Machinedrum"]
    n_machinemodule_desktop["MachineModule (desktop)<br/>AGPL-3.0"]:::copyleft
    n_machinemodule_mpc["Machinemodule for MPC OS<br/>AGPL-3.0"]:::copyleft
    n_mds["MDS (Machine Dump Standard)<br/>not stated"]:::none
    n_mds_tools["mds-tools<br/>GPL"]:::copyleft
    n_mmodule["MoDule (MD Drums)<br/>GPL"]:::copyleft
    n_moduledrum["ModuleDrum<br/>AGPL-3.0"]:::copyleft
  end
  subgraph n_group_Monomachine["Monomachine"]
    n_monomodule["Monomodule<br/>AGPL-3.0-only"]:::copyleft
    n_schwung_monomodule["Monomodule for Schwung<br/>GPL-3.0 per README (repo metadata: AGPL-3.0)"]:::copyleft
  end
  subgraph n_group_Several_device_families["Several device families"]
    n_analoghealth["analoghealth<br/>not recorded"]:::none
    n_chopshop["Chopshop<br/>not recorded"]:::none
    n_digi_roll_studio["digi-roll-studio<br/>not recorded"]:::none
    n_digiemu["digiemu<br/>not recorded"]:::none
    n_digihealth["digihealth<br/>not recorded"]:::none
    n_digikit["digikit<br/>AGPL-3.0-or-later with extra terms"]:::copyleft
    n_digitakt_digitone_mcp["digitakt-digitone-mcp<br/>not recorded"]:::none
    n_dn2_dt2_firmware_research["DN2 DT2 firmware research<br/>not recorded"]:::none
    n_elek_view["Elek View<br/>GPL-3.0"]:::copyleft
    n_elekloader["elekloader<br/>GPL-2.0-or-later"]:::copyleft
    n_elekloader_simonjohansson["elekloader<br/>GPL-2.0-or-later"]:::copyleft
    n_elektron_firmware_tool["elektron-firmware-tool<br/>not recorded"]:::none
    n_elektron_screen_tool["Elektron-Screen-Tool<br/>MIT"]:::permissive
    n_filter_plus["Filter+ (13 filter types)<br/>GPL-2.0-or-later"]:::copyleft
    n_gearmulator_md_mm["Gearmulator MD/MM<br/>GPL-3.0-only"]:::copyleft
    n_maschine_md_mm["Maschine MD-MM<br/>GPL-3.0"]:::copyleft
    n_mdmm["MDMM<br/>not recorded"]:::none
    n_modwerk["Modwerk (formerly Octamod)<br/>not recorded"]:::none
    n_overwitch["Overwitch<br/>not recorded"]:::none
    n_sidecar_expander["Sidecar | Expander<br/>GPL-2.0"]:::copyleft
    n_taktone["taktone<br/>not recorded"]:::none
  end
  n_digiemu -- "builds on" --> n_digikit
  %% evidence: README: digiemu is derived from m-dwyer/digikit at an upstream commit
  n_digitakt_ii_research -- "builds on" --> n_digikit
  %% evidence: all-in-one/README.md: modified firmware derived from digikit; uses its patchkit
  n_digitakt_ii_research -- "vendors code from" --> n_elektron_firmware_tool
  %% evidence: catalogue notes: elektron-firmware-tool (vendored)
  n_overtone -- "vendors code from" --> n_dn2_firmware_explore
  %% evidence: README: patcher/_dnfw is dnfw's code, unchanged
  n_motorcycles -- "bundles" --> n_modded_cycles
  %% evidence: README: mods included from Modded-Cycles are part of Motor:Cycles
  n_syxgrid -- "vendors code from" --> n_elk_herd
  %% evidence: README credits under Code: elk-herd, BSD-2-Clause
  n_dn2_dt2_firmware_research -- "builds on" --> n_dn2_firmware_explore
  %% evidence: catalogue notes: builds on dnfw (pinned commit)
  n_dn2_dt2_firmware_research -- "builds on" --> n_digikit
  %% evidence: catalogue notes: builds on digikit (pinned commit)
  n_dn2_dt2_firmware_research -- "builds on" --> n_elektron_firmware_tool
  %% evidence: catalogue notes: builds on elektron-firmware-tool (pinned commit)
  n_synthack_os -- "fork of" --> n_synthack_os_upstream
  %% evidence: GitHub fork flag
  n_filter_plus -- "builds on" --> n_digifilter
  %% evidence: same author; BP/BP2/COMB/TRASH are DigiFilter modes; LICENSE names the DigiFilter authors
  n_digi1_mods -- "bundles" --> n_tone_fx
  %% evidence: README: Tone+FX, Digital Alchemy DSP's master effects suite, ported
  n_dt_fm -- "builds on" --> n_digisophie
  %% evidence: notes
  n_elek_view -- "port of" --> n_screendump
  %% evidence: README: a .html implementation of jakobbak/screendump
  n_dt2_machine_lab -- "bundles" --> n_dt2_capicola
  %% evidence: machines/capicola-reddit/upstream keeps its 66 files byte-exact
  n_dn2_firmware_explore -- "builds on" --> n_elektron_firmware_tool
  %% evidence: README credit: container, transport, codec and integrity work stands on it
  n_dn2_cfw -- "vendors code from" --> n_digikit
  %% evidence: catalogue notes: upstream cloned into vendor/ (author's fork, branch dn2-1.12)
  n_dn2_cfw -- "vendors code from" --> n_elekloader
  %% evidence: catalogue notes: upstream cloned into vendor/ (author's fork, branch dn2-1.12)
  n_dn2_cfw -- "vendors code from" --> n_digitakt_ii_research
  %% evidence: README: Kari Gardarsson's Deja vu LFO from the Digitakt II, brought to the Digitone II
  n_overwitch -- "builds on" --> n_dtdump
  %% evidence: README: based on the Overbridge USB reverse engineering in dtdump
  n_dn2mk2 -- "builds on" --> n_dn2_firmware_explore
  %% evidence: docs/CHANGES-FROM-UPSTREAM: forked dnfw at 8c40698
  n_elekloader_simonjohansson -- "fork of" --> n_elekloader
  %% evidence: GitHub fork flag
  n_elekloader_simonjohansson -- "vendors code from" --> n_digikit
  %% evidence: catalogue notes: NOTICE covers digikit code
  n_digi_roll_studio -- "vendors code from" --> n_elk_herd
  %% evidence: catalogue notes: protocol code ported from elk-herd
  n_chopshop -- "vendors code from" --> n_elektron_firmware_tool
  %% evidence: README: built on elektron-firmware-tool compiled to WebAssembly
  n_chopshop -- "builds on" --> n_rytm1_mods
  %% evidence: README: built on gdeo607's rytm1_mods
  n_rytm1_mods -- "port of" --> n_rytm_mods_src
  %% evidence: README: port of the MKII project to the MK1
  n_mdmm -- "builds on" --> n_gearmulator_md_mm
  %% evidence: README: grew out of joelanders' Machinedrum and Monomachine emulation
  n_mds_tools -- "builds on" --> n_mds
  %% evidence: README: tools for the MDS specification
  n_chord_keys -- "fork of" --> n_modded_cycles
  %% evidence: GitHub fork flag
  n_modded_cycles -- "bundles" --> n_model_tg
  %% evidence: README: Model-TG's Sampler as the 7th machine
  n_modded_cycles -- "bundles" --> n_elektron_model_tweaks
  %% evidence: README: includes drumkilla's tweaks (latching mute, trig preview)
  n_modded_cycles -- "bundles" --> n_ms_multi_output
  %% evidence: README: 6-channel audio after scottmetoyer/ms-multi-output
  n_model_tg -- "bundles" --> n_elektron_model_tweaks
  %% evidence: README: includes drumkilla's tweaks (latching mute, trig preview)
  n_model27 -- "fork of" --> n_modded_cycles
  %% evidence: own README: beta fork of Modded Cycles 1.55
  n_model27 -- "bundles" --> n_elektron_model_tweaks
  %% evidence: README: includes drumkilla's tweaks (latching mute, trig preview)
  n_model27 -- "bundles" --> n_cycles_control_all_config
  %% evidence: README: Modded-Cycles 1.55 plus the Control All Config mod
  n_model27 -- "bundles" --> n_cycles_one_shot
  %% evidence: README: the SAMPLE machine of Cycles One-Shot
  n_plaits_on_models -- "builds on" --> n_digi1_mods
  %% evidence: README: the base is MACRO from gdeo607/digi1_mods
  n_plaits_on_models -- "builds on" --> n_modded_cycles
  %% evidence: README: clone the Modded-Cycles fork with the PLAITS files
  n_spokes -- "bundles" --> n_modded_cycles
  %% evidence: README table
  n_spokes -- "bundles" --> n_model27
  %% evidence: README table
  n_spokes -- "bundles" --> n_supermodel_edition
  %% evidence: README table
  n_supermodel_edition -- "fork of" --> n_modded_cycles
  %% evidence: GitHub fork flag
  n_supermodel_edition -- "vendors code from" --> n_model27
  %% evidence: README: release 2.61 adds durchgemacht/model27 POTS delay (MIT)
  n_vladiktron_spoke -- "builds on" --> n_modded_cycles
  %% evidence: README: this project builds on Modded-Cycles
  n_elektron_model_tweaks -- "vendors code from" --> n_elekloader
  %% evidence: README: linked by elekloader's linker, an unchanged copy in elekloader/
  n_elektron_model_tweaks -- "builds on" --> n_elektron_firmware_tool
  %% evidence: README: building scripts are based on elektron-firmware-tool
  n_elektron_model_tweaks -- "builds on" --> n_ms_multi_output
  %% evidence: README: based on ms-multi-output by Scott Metoyer
  n_midisc_patcher -- "builds on" --> n_midisc
  %% evidence: README: patcher for the 1.40MIDISC build
  n_octa_panel -- "copy of" --> n_octabam
  %% evidence: repo content is octabam (README, modules) as of 2026-10-13
  n_octa_panel -- "bundles" --> n_ems_octakit
  %% evidence: README: module table lists OCTAKIT from emuyia/ems-octakit
  n_octa_panel -- "bundles" --> n_midisc
  %% evidence: README: module table lists MIDI SCENES from bkkbrls-del/midisc
  n_octa_panel -- "bundles" --> n_octa_bt_pt
  %% evidence: README: module table lists LOFI AMF FIX from bryantysinger/octa-bt-pt
  n_octabam -- "bundles" --> n_ems_octakit
  %% evidence: README: module table lists OCTAKIT from emuyia/ems-octakit
  n_octabam -- "bundles" --> n_midisc
  %% evidence: README: module table lists MIDI SCENES from bkkbrls-del/midisc
  n_octabam -- "bundles" --> n_octa_bt_pt
  %% evidence: README: module table lists LOFI AMF FIX from bryantysinger/octa-bt-pt
  n_octabam -- "bundles" --> n_octatrick
  %% evidence: README: module table lists DIRECT JUMP from timhastie/octatrick-modules
  n_octabam -- "bundles" --> n_octemu
  %% evidence: README: module table lists USB from markandrus/octemu
  n_octabam -- "fork of" --> n_octamax
  %% evidence: README: began as a fork of mxldyn/octamax
  n_octatrack_manager -- "builds on" --> n_ot_tools_io
  %% evidence: README: built with ot-tools-io
  n_passos -- "builds on" --> n_octabam
  %% evidence: README
  n_synfact -- "builds on" --> n_elekloader
  %% evidence: README of synfact-dev: built on elekloader, its engine, file format and checks
  n_synfact -- "vendors code from" --> n_digikit
  %% evidence: README: NOTICE covers the code that comes from elekloader and digikit
  n_digitakt_digitone_mcp -- "builds on" --> n_digitakt_midi_mcp
  %% evidence: README: the project this one grew out of
  n_digiseq_digitakt -- "bundles" --> n_digisnake_digitakt
  %% evidence: README: DIGISNAKE for Digitakt, unchanged, as its SNAKE type
  n_digiseq_digitone -- "variant of" --> n_digiseq_digitakt
  %% evidence: same author, Digitone build
  n_digiseq_digitone -- "bundles" --> n_digisnake_digitone
  %% evidence: README: DIGISNAKE carries on in DIGISEQ for Digitone, unchanged
  n_pump_digitone -- "variant of" --> n_pump_digitakt
  %% evidence: same author, Digitone build
  n_pump_digitone -- "vendors code from" --> n_ringtone
  %% evidence: README: adapted from Tone+FX's digictl (DigiAlchemydsp/RingTone), GPL-2.0-or-later
  n_directjump_digitone -- "variant of" --> n_directjump_digitakt
  %% evidence: same author, Digitone build
  n_directjump_digitone -- "vendors code from" --> n_digihealth
  %% evidence: README: SETTINGS row callbacks adapted from digihealth's SYSTEM INFO row (GPL-2.0-or-later)
  n_digisnake_digitone -- "variant of" --> n_digisnake_digitakt
  %% evidence: same author, Digitone build
  n_sidecar_digitakt -- "variant of" --> n_sidecar_expander
  %% evidence: same author, Digitakt side of Sidecar
  n_digitakt_sidecar_pi -- "builds on" --> n_sidecar_expander
  %% evidence: README: based on Sidecar by Trig Condition
  n_elektron_screen_tool -- "fork of" --> n_screendump
  %% evidence: README
  n_dt2_capicola -- "builds on" --> n_keyframer_lab
  %% evidence: same Capicola keyframe engine by Heavylight Industries
  n_taktone -- "vendors code from" --> n_digiemu
  %% evidence: README: the ColdFire instruction decoder comes from irpina/digiemu (GPL retained)
  n_taktone -- "bundles" --> n_digisophie
  %% evidence: README: Digisophie machines running on the second DSP
  n_elektron_mods_rumorismo -- "vendors code from" --> n_elekloader
  %% evidence: README: repo tree includes elekloader
  n_analoghealth -- "port of" --> n_digihealth
  %% evidence: README: irpina's digihealth for the Digitakt mk1, ported to the Rytm MKII and Analog Four MKII
  n_rytm2_mods -- "port of" --> n_rytm_mods_src
  %% evidence: README: ported to elemod
  n_mmodule -- "builds on" --> n_gearmulator_md_mm
  %% evidence: README: MD Drums came from gearmulator-md-mm
  n_mmodule -- "builds on" --> n_machinemodule_mpc
  %% evidence: README: Machinemodule by sd88me, the Machinedrum engine without its OS
  n_cycles_engines -- "builds on" --> n_modded_cycles
  %% evidence: README credits
  n_cycles_engines -- "builds on" --> n_model27
  %% evidence: README credits
  n_cycles_mod_standard -- "describes" --> n_model27
  %% evidence: README: implemented in model27
  n_model909 -- "builds on" --> n_modded_cycles
  %% evidence: README: built on Modded-Cycles and Model-TG
  n_model909 -- "builds on" --> n_model_tg
  %% evidence: README: Model-TG is ticked with model909
  n_octatrack_modules_radiohagen -- "builds on" --> n_octabam
  %% evidence: README
  n_rebirth2octatrack -- "builds on" --> n_octabam
  %% evidence: README: targets the GARDEN engines
  n_moduledrum -- "fork of" --> n_monomodule
  %% evidence: README
  n_machinemodule_mpc -- "vendors code from" --> n_moduledrum
  %% evidence: README: ideas and code adapted from ModuleDrum (AGPL-3.0)
  n_machinemodule_desktop -- "port of" --> n_machinemodule_mpc
  %% evidence: README
  n_schwung_monomodule -- "port of" --> n_monomodule
  %% evidence: README
  n_rytm_mk1_mods_hugz202 -- "builds on" --> n_rytm1_mods
  %% evidence: README: based on rytm1_mods and keeps its pipeline
  n_trackpatterns -- "builds on" --> n_octabam
  %% evidence: README: also submitted as octabam PR 846
  n_acidtrack_modules -- "builds on" --> n_octabam
  %% evidence: README
  n_maschine_md_mm -- "fork of" --> n_gearmulator_md_mm
  %% evidence: README
  n_rytm_rs -- "builds on" --> n_libanalogrytm
  %% evidence: README
  n_digitakt_pattern_editor_juce -- "port of" --> n_elk_herd
  %% evidence: README: format layer ported to C++ from elk-herd
  n_digitakt_reorder -- "builds on" --> n_elk_herd
  %% evidence: README: works on .syx dumps fetched and sent with elk-herd
  n_bias -- "builds on" --> n_model27
  %% evidence: altstrument: a machine package for model27; its scripts clone model27 at a pinned commit
  n_mezclando -- "builds on" --> n_modwerk
  %% evidence: README: build needs a Modwerk checkout with core-dt2 1.0
  n_digimod -- "vendors code from" --> n_digikit
  %% evidence: README credits: Plaits and other mods are ports of digikit work (AGPL-3.0-or-later)
  n_digimod -- "vendors code from" --> n_digitakt_ii_research
  %% evidence: README credits: Musical WAVE / Deja Vu and One-Shot Zoom from Kari Gardarsson's All-in-One
  n_modded_cycles_techno -- "builds on" --> n_modded_cycles
  %% evidence: README credits: build toolchain, per-track filter, machine list, MACRO and ACID ports
  n_modded_cycles_techno -- "bundles" --> n_model909
  %% evidence: README credits: the 909 kick, toms, rim and clap from DMDaudio/model909
  n_modded_cycles_techno -- "bundles" --> n_elektron_model_tweaks
  %% evidence: README credits: scrolling names and the mtlib toolkit
  n_modded_cycles_techno -- "builds on" --> n_ms_multi_output
  %% evidence: README credits: the original 6-channel USB audio mod
  classDef permissive fill:#d9f2e3,stroke:#2b7a4b,color:#10301e
  classDef copyleft fill:#dde7fb,stroke:#3460b0,color:#13254a
  classDef public-domain fill:#f9ecc8,stroke:#a07410,color:#3d2c05
  classDef none fill:#ececec,stroke:#7a7a7a,color:#2a2a2a
```

<!-- relation-graph:end -->

## Licence

Everything in this repository (texts, data and scripts) is dedicated to the public domain under
[CC0 1.0 Universal](LICENSE). The linked projects keep their own licences.
