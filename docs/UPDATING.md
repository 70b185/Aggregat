# Updating Aggregat cheaply (procedure for agents and humans)

Goal: find out **what changed** without reading every repo again. Most runs should end with "Nothing to do".

## How it works
- `scripts/check_updates.py` keeps one compact fingerprint per watched repo in `state/fingerprints.json`:
  default-branch HEAD, tag set, and the blob hashes of the *watched* files (README and other `*.md`, `mod.json`, `*.toml`, licences; per-project overrides in `data/watch.yml`).
- **Stage 1** (every repo, ~one `git ls-remote`, no content): HEAD and tags unchanged -> `unchanged`, nothing else happens.
- **Stage 2** (only if HEAD moved): blobless depth-1 clone, `git ls-tree`, compare hashes -> lists added `+`, changed `~`, removed `-` watched files and new tags.
- `--diff` additionally prints the text diff of exactly those files (old HEAD fetched blobless).
- Directories (altstrument data folder, Lapin list) are watched the same way to **discover new projects**.
- A daily GitHub Action (`.github/workflows/check-updates.yml`) runs the check with `--report` and commits `state/CHANGES.md`. It does **not** move the baselines, so the report lists every change since the last update run read it, however many days ago; and lists repos not in the catalogue yet in `state/NEW.md` (see "Finding new projects").

## Agent procedure (token-cheap)
1. `git pull`, then read **only** `state/CHANGES.md` and `state/NEW.md` (a few lines each). Do not open `state/fingerprints.json` - it is for the script.
2. If it says "Nothing to do" -> stop.
3. For each `changed` entry: `python3 scripts/check_updates.py --only <id> --diff` and read just that diff.
   - new tag -> update `version` / `last_activity` in `data/projects.yml`
   - changed README/docs -> fold only the changed facts into `data/` and `hardware/` (with source key and date)
   - `code-only` entries -> usually nothing to do; look only if the project is one you depend on
   - `ERROR` -> repo deleted, renamed or private: set `status: unreachable` or fix the URL
   - directory changes (`dir-altstrument`, `dir-lapin`) -> new paths = candidate projects for `data/candidates.yml`
4. `python3 scripts/check_updates.py --only <ids you read> --update` (stores the new baseline for those only; a plain `--update` would drop changes nobody has read), `python3 scripts/repo_meta.py` (GitHub numbers for the network map and community page; needs `gh`), `python3 scripts/first_seen.py` (date each entry first appeared, from git history; drives the "new" markers), `python3 scripts/build.py` (also rebuilds MODS.md, DEV-TOOLS.md, MUSICIAN-TOOLS.md), `python3 scripts/export_db.py` and `python3 scripts/find_duplicates.py` (database in `export/`, duplicate report in `hardware/DUPLICATES.md`), commit. A new entry lands in a list by its `kind`; give a `tool` entry `list: musician` (or `mods`) when it is not a developer tool. An entry that also ships usable mods (a research repo, a hardware mod) gets `also_lists: [mods]`, so MODS.md and the website's Mods tab show it too; a loader or platform lists the mods it ships itself (no repo or entry of their own) in `own_mods`, so they show together as one mod entry "<loader> mods" (one entry per repo, as for any collection), installed via that loader, and picking the loader on the website shows it; a mod a loader takes from a repo we list gets `mod_for` on that entry instead (Modwerk's `modwerk.module.json` and elekloader's `mods/` name their source repos); fill `tested` for every mod and `contains` for collections. Scope: every Elektron device that custom firmware or mods are written for; a loader's `devices` lists every device its README supports, and a project for an Elektron device not yet in `data/devices.yml` adds that device there (with a section in `index.html`'s `--c-<device>` colours). Check the elekloader shop catalogue (`web/catalog.json` in elekloader/elekloader) for repos we do not list yet.

## What it cannot see
Forum threads, vendor pages (elektron.se release notes), PDFs and non-git sites. Those stay on the manual list in `hardware/MINING.md`; check them occasionally, e.g. when a new OS appears in a repo's diff.

## Adding a repo
Add the project to `data/projects.yml` with a `repo:` URL - it is watched automatically. For a narrower or wider watch list add an entry under `overrides` in `data/watch.yml`.

## Finding new projects (daily, automatic)
The daily Action runs `python3 scripts/find_new.py --since <30 days ago> --authors --code --report state/NEW.md`. The
report lists only repos that are in neither `data/projects.yml` / `data/candidates.yml` nor `data/ignore.yml`, from
three sources:
- **keyword search** of repo names, descriptions and topics (digitakt, elekloader, octatrack, ...);
- **new repos of catalogued authors** whose name or description points at Elektron gear, even when it names no
  device (e.g. "Digi2Core"); forks only when their description differs from every catalogued repo's;
- **code search** for stock OS file names, the DT2 flash-cave address and `elemod`, which finds projects whose name and
  description never mention Elektron (generic hits: read before adding).

Triage every entry of `state/NEW.md` in each update run: read the README start (a blobless
`git clone --depth 1 --filter=blob:none --no-checkout` plus `git show HEAD:README.md` costs almost nothing), then
- add an entry (own words, facts only) when it is firmware, a mod, a loader or a tool for an Elektron device in scope,
  or a fork with changes of its own;
- add it to `data/ignore.yml` with a one-line reason when it is out of scope, or a copy or fork without changes of its
  own (compare with the original: only notices, links or a mirror do not count);
- put it in `data/candidates.yml` when the README does not settle it.
An entry leaves the report once it is in one of the three files. New entries get a fingerprint baseline on the next
`check_updates.py --only <ids> --update`. Without `--report` the script prints the same lists for a manual run.

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
