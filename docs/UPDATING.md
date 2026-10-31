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
4. `python3 scripts/check_updates.py --update` (stores the new baseline), `python3 scripts/build.py`, commit.

## What it cannot see
Forum threads, vendor pages (elektron.se release notes), PDFs and non-git sites. Those stay on the manual list in `hardware/MINING.md`; check them occasionally, e.g. when a new OS appears in a repo's diff.

## Adding a repo
Add the project to `data/projects.yml` with a `repo:` URL - it is watched automatically. For a narrower or wider watch list add an entry under `overrides` in `data/watch.yml`.
