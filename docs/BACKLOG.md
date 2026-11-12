# Backlog (research as of 2026-10-31, project items as of 2026-11-11)

## Phase 1 - still to verify (small boxes + MKII versions)
- Find the community firmware index on GitHub launched 2026-10-11 (about 260 projects, 19 brands, per Dubspot; name/URL not given). Check overlap before duplicating work.
- Read the elekloader "mod shop" for the full mod list (digislicer, digihealth, ...) and find their repos.
- Elektronmods forum: read the per-device sections (Digitakt, Digitone, Syntakt, Analog Heat) and pages 2+ of long threads; the forum start page was not fetched.
- Thread 25: project file extraction/compaction scripts (Model:Samples, DN2, DT2, Model:Cycles). Repo link unknown.
- Thread 27: Elektron firmware download list.
- Analog Heat MKI / MKII / +FX: search Elektronauts-adjacent sources, Reddit, GitHub topics for any community work (none found so far).
- Syntakt: SY FM4 vs Syntakt MAX relationship, other Syntakt projects.
- Digitone II and Digitakt II: other patchers besides Overtone, DigiRust and digitakt-ii-research.
- ~~Real "last commit" dates~~ Done: `scripts/repo_meta.py` stores last push, stars and forks per repo in `state/repo_meta.json`; the check-updates workflow refreshes it.

## Phase 2 - other devices
Done 2026-11-01: catalogue of 45 projects for Octatrack, Analog Rytm, Analog Four/Keys, Model:Cycles/Samples, Machinedrum and Monomachine (from altstrument; facts only, our own notes). Next: read each repo's README like phase 1, then `hardware/` notes per platform (Octatrack: octabam/Modwerk DSP56300 + ColdFire; Model: Modded-Cycles; Rytm: rytm-fw-re, rytm-mods-src; Machinedrum: MDS/MDX, machinedrum-kit).

Done 2026-11-02: first `hardware/` profiles for Octatrack, Model:Cycles/Samples, Analog Rytm, Analog Four/Keys and Machinedrum (Monomachine thin); every older GitHub search hit triaged (42 added, the rest in `data/ignore.yml` with reasons). Next for phase 2: read the Rytm MK1 mods' HAZARDS (rule A38 likely applies), the Monomachine's board, and deeper octabam/Modwerk docs.

Original notes:
- Octatrack MKI/MKII: Modwerk/octabam (sambanks/octabam), "Octatrack Trifecta" (thread 6), Octamod hub (thread 36)
- Model:Cycles / Model:Samples: Modded-Cycles (18nelli18), Model-TG (TinyGregAudio), Model-Tweaks (thread 41)
- Analog Four / Rytm: ChopShop analog mods (thread 51), elekloader A4 MKII proof of concept
- Tonverk: research notes (thread 87), slicer request (thread 49)
- Machinedrum: Kitbasher (https://kitbasher.xyz/, source etcetc000/kitbasher, GPL-3.0): browser builder that adds machines to Machinedrum OS 1.63 / X.14 / beta md-26A09-132401 (UW and non-UW); X.20 not supported; no hardware test statement. Same project as the Kitbasher entry in the Lapin list.
- Non-Elektron: DOOM OS (SP-404MKII), Open500 (MPC500), Blackbox Mod (1010music), X0X and Groove OS (M-VAVE FM-1)

## Reference directories to re-read
- Lapin/awesome-music-gear-firmware (links only, CC0), philmillman/altstrument + altstrument.org (structured, CC-BY-4.0 data; Elektron brand page lists 13 devices, none is Analog Heat)

## Ground rules
- Metadata only: names, links, status. No firmware, no binaries, no scraped forum text beyond short notes.
- Every entry needs at least one source and a verification date.

## Project (from the review on 2026-11-11, after the elektronmods.com post)
- ~~Create the beginner issues~~ Done 2026-11-12 (label `good first test`); H5 and H24 held back on purpose, see `NOT_FOR_NEWCOMERS` in the script. Visitor tracking: decided against on 2026-11-12; GitHub's own traffic page is enough.
- Release assets instead of commits for the database: `export/aggregat.sqlite` (2 MB) has been committed about 70 times since 2026-10-31. Building it in the workflow and attaching it to a rolling release would keep the history small; the website and MCP server would need the new URL.
- Shorter entry for musicians: the README and the website lead with many links; a musician needs "pick your device, see its mods" first.
