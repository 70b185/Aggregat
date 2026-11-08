# Updating Aggregat cheaply (procedure for agents and humans)

Goal: find out **what changed** without reading every repo again. Most runs should end with "Nothing to do".

## How it works
- `scripts/check_updates.py` keeps one compact fingerprint per watched repo in `state/fingerprints.json`:
  default-branch HEAD, tag set, and the blob hashes of the *watched* files (README and other `*.md`, `mod.json`, `*.toml`, licences; per-project overrides in `data/watch.yml`).
- **Stage 1** (every repo, ~one `git ls-remote`, no content): HEAD and tags unchanged -> `unchanged`, nothing else happens.
- **Stage 2** (only if HEAD moved): blobless depth-1 clone, `git ls-tree`, compare hashes -> lists added `+`, changed `~`, removed `-` watched files and new tags.
- `--diff` additionally prints the text diff of exactly those files (old HEAD fetched blobless).
- Directories (altstrument data folder, Lapin list) are watched the same way to **discover new projects**.
- A daily GitHub Action (`.github/workflows/check-updates.yml`) runs the check and commits `state/CHANGES.md`. A full run over ~60 repos takes about 15 s.

## Agent procedure (token-cheap)
1. `git pull`, then read **only** `state/CHANGES.md` (a few lines). Do not open `state/fingerprints.json` - it is for the script.
2. If it says "Nothing to do" -> stop.
3. For each `changed` entry: `python3 scripts/check_updates.py --only <id> --diff` and read just that diff.
   - new tag -> update `version` / `last_activity` in `data/projects.yml`
   - changed README/docs -> fold only the changed facts into `data/` and `hardware/` (with source key and date)
   - `code-only` entries -> usually nothing to do; look only if the project is one you depend on
   - `ERROR` -> repo deleted, renamed or private: set `status: unreachable` or fix the URL
   - directory changes (`dir-altstrument`, `dir-lapin`) -> new paths = candidate projects for `data/candidates.yml`
4. `python3 scripts/check_updates.py --update` (stores the new baseline), `python3 scripts/repo_meta.py` (GitHub numbers for the network map and community page; needs `gh`), `python3 scripts/first_seen.py` (date each entry first appeared, from git history; drives the "new" markers), `python3 scripts/build.py` (also rebuilds MODS.md, DEV-TOOLS.md, MUSICIAN-TOOLS.md), `python3 scripts/export_db.py` and `python3 scripts/find_duplicates.py` (database in `export/`, duplicate report in `hardware/DUPLICATES.md`), commit. A new entry lands in a list by its `kind`; give a `tool` entry `list: musician` (or `mods`) when it is not a developer tool. An entry that also ships usable mods (a research repo, a hardware mod) gets `also_lists: [mods]`, so MODS.md and the website's Mods tab show it too; fill `tested` for every mod and `contains` for collections. Check the elekloader shop catalogue (`web/catalog.json` in elekloader/elekloader) for repos we do not list yet.

## What it cannot see
Forum threads, vendor pages (elektron.se release notes), PDFs and non-git sites. Those stay on the manual list in `hardware/MINING.md`; check them occasionally, e.g. when a new OS appears in a repo's diff.

## Adding a repo
Add the project to `data/projects.yml` with a `repo:` URL - it is watched automatically. For a narrower or wider watch list add an entry under `overrides` in `data/watch.yml`.

## Finding new projects (cheap, run weekly or when asked)
`python3 scripts/find_new.py --since <last run date>` searches GitHub for Elektron terms and prints only repos that are
neither in `data/projects.yml` / `data/candidates.yml` nor in `data/ignore.yml`. Read each README start (a blobless
`git clone --depth 1 --filter=blob:none --no-checkout` plus `git show HEAD:README.md` costs almost nothing), then either add
an entry (own words, facts only) or add the repo to `data/ignore.yml` so it is not shown again. New entries get a
fingerprint baseline on the next `check_updates.py --update`.

Add `--code` once a month: it searches file contents (stock OS file names, the DT2 flash-cave address, `elemod`) and finds projects whose repo name and description never mention Elektron. On 2026-11-03 it found x0x, Motor:Cycles, RytmRandomizer and Synfact's new repo, none of which the keyword search had listed. Its generic hits include unrelated repos, so read each README before adding.

## Research results from other projects (manual, maintainer only)
Results come in two ways: **Test result** issues in this repo, and the results tables of `AGGREGAT_RESEARCH.md` files
in participating repos (a change report lists the file when it changed; `find_new.py --code` finds new ones).
For now a maintainer merges them by hand during manual updates; nothing is taken over automatically.
1. Read the new rows: test id, unit and OS, what happened, evidence tag, link to details.
2. Check them against what is already known (device page, HYPOTHESES.md, CONFLICTS.md).
3. Confirmed: move the fact into the device page with `[hw]` and a source key for the project or issue, update the
   status mark in RESEARCH-MAP.md, remove or close the hypothesis or task. Contradicted: add a conflict.
   A failure or a test on a unit (a hang, crash, silence, stall, wrong behaviour, a recovery) also becomes an incident
   in `hardware/INCIDENTS.md` (rule C11): next free I-number, cause and how it was found, fix, status, evidence. Then
   add a rule to AGENT-RULES.md or add the incident to the rule it confirms, and tag the device-page fact `(I<n>)`.
   A bug in Elektron's own OS (a project writes "stock bug", or it reproduces on the unmodified OS) also goes into
   `hardware/STOCK-BUGS.md` with the next free SB-number (rule C12); stock-bug issues come in with the label
   `stock bug`. To find new ones, search the catalogued repos for "stock bug", "firmware bug" and "on stock too".
4. A new participant gets a section in `research/PARTICIPANTS.md` with suggested tasks that fit the project.
5. `python3 scripts/research_snapshot.py`, then build and export as usual.
