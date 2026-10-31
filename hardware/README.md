# hardware/ - what we know about the boxes, written as rules for AI agents

Purpose: an agent that develops mods/tools for Elektron's small boxes should read **this folder** instead of
combing through dozens of repos. Everything here is distilled from public repos, READMEs and
manufacturer pages. It contains **no firmware, no binaries and no dumps** - only facts, addresses as
published by the authors, and rules.

## How to use

1. Read [`AGENT-RULES.md`](AGENT-RULES.md) first (safety and process rules, valid for every device).
2. Read [`common/firmware-container.md`](common/firmware-container.md), [`common/recovery.md`](common/recovery.md), [`common/flash-procedure.md`](common/flash-procedure.md) before any flash, and - if you only talk to a unit over MIDI/SysEx - [`common/sysex-and-midi.md`](common/sysex-and-midi.md).
3. Read the file for your device in [`devices/`](devices/).
4. Look up the project you build on in [`../INDEX.md`](../INDEX.md) (who maintains what, which OS, which state).

## Evidence levels (every fact carries one)

| Tag | Meaning |
|---|---|
| `[hw]` | The author reports it worked on a real unit. We did not test anything ourselves. |
| `[emu]` | Only checked in an emulator (digikit/digiemu). Not proof for real hardware, audio is not emulated. |
| `[doc]` | Stated in a README/doc/manufacturer page, no test result given. |
| `[?]` | Unclear, contradictory or inferred - treat as a question, not a fact. |

Every fact also names its source key in brackets, e.g. `{elekloader-adapting}`. Keys are resolved in
[`SOURCES.md`](SOURCES.md). All of it is **second-hand**: re-check against the source before you
rely on an address or a byte pattern.

## A finer evidence ladder to adopt when a source uses it
digitakt-ii-research grades its own statements as SOURCE/STATIC -> HOST -> SYNTHETIC UNICORN -> NATURAL EMULATED -> HARDWARE. Our `emu` tag lumps the middle three together; when a source draws that distinction, keep it in the note.

## Status of this folder (2026-10-31)

First pass, built from README-level reading of: elekloader (+ADAPTING.md), digikit, dn2-cfw,
dn2_firmware_explore, elektron-firmware-tool, digitakt-ii-research, Synthack-OS and Elektron's own
Analog Heat pages. Open reading list: [`MINING.md`](MINING.md).

Ecosystem, practices and legal context: [`common/ecosystem-lessons.md`](common/ecosystem-lessons.md); Overbridge USB: [`common/overbridge-usb.md`](common/overbridge-usb.md).

Deep dives: [`common/memory-maps.md`](common/memory-maps.md) (mod areas and flash budgets per device), [`devices/digitone-2-internals.md`](devices/digitone-2-internals.md), [`devices/digitone-2-machines-sampler-sharc.md`](devices/digitone-2-machines-sampler-sharc.md), [`devices/digitone-2-os111-reference.md`](devices/digitone-2-os111-reference.md) (Digitone II OS 1.11 engineering reference) and [`common/agent-workflow.md`](common/agent-workflow.md) (the loop an agent should follow).

Coverage per device: Digitakt mk1 **good**, Digitone mk1 **good** (via elekloader), Digitakt II **medium**,
Digitone II **medium**, Syntakt **thin**, Analog Heat **only official facts, no mod knowledge**.
