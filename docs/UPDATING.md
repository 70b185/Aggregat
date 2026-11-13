# Updating Aggregat cheaply (procedure for agents and humans)

Goal: find out **what changed** without reading every repo again. Most runs should end with "Nothing to do".

## Scope (what goes into the catalogue)

- **Phase 1, in depth:** Digitakt MKI/II, Digitone MKI/Keys/II, Syntakt, Analog Heat MKI/MKII/+FX: catalogue plus the
  knowledge base in [`hardware/`](../hardware/).
- **Phase 2, catalogue:** Octatrack, Analog Rytm, Analog Four/Keys, Model:Cycles/Samples, Machinedrum, Monomachine,
  with device profiles in `hardware/devices/` where projects have published research.
- **Every Elektron device that custom firmware or mods are written for belongs in the catalogue.** A device gets an
  entry in [`data/devices.yml`](../data/devices.yml) as soon as the first such project appears, and a loader lists every
  device it supports. Tonverk is not listed yet: so far there are research notes and requests, no mod.
- Not covered: other brands ([`BACKLOG.md`](BACKLOG.md)).

## How it works
- `scripts/check_updates.py` keeps one compact fingerprint per watched repo in `state/fingerprints.json`:
  default-branch HEAD, tag set, and the blob hashes of the *watched* files (README and other `*.md`, `mod.json`, `*.toml`, licences; per-project overrides in `data/watch.yml`).
- **Stage 1** (every repo, ~one `git ls-remote`, no content): HEAD and tags unchanged -> `unchanged`, nothing else happens.
- **Stage 2** (only if HEAD moved): blobless depth-1 clone, `git ls-tree`, compare hashes -> lists added `+`, changed `~`, removed `-` watched files and new tags.
- `--diff` additionally prints the text diff of exactly those files (old HEAD fetched blobless).
- Directories (altstrument data folder, Lapin list) are watched the same way to **discover new projects**.
- A GitHub Action (`.github/workflows/check-updates.yml`, twice a day; GitHub starts it hours late) runs the check with `--report` and commits `state/CHANGES.md`. It does **not** move the baselines, so the report lists every change since the last update run read it, however many days ago; and lists repos not in the catalogue yet in `state/NEW.md` (see "Finding new projects").

## Agent procedure (token-cheap)
1. `git pull`, then read **only** `state/CHANGES.md` and `state/NEW.md` (a few lines each). Do not open `state/fingerprints.json` - it is for the script.
2. If it says "Nothing to do" -> stop.
3. For each `changed` entry: `python3 scripts/check_updates.py --only <id> --diff` and read just that diff.
   - new tag -> update `version` / `last_activity` in `data/projects.yml`
   - changed README/docs -> fold only the changed facts into `data/` and `hardware/` (with source key and date)
   - changed README of a mod -> also check its `features` list (the main things it does, a few short points in our own words) and update it, with `README (YYYY-MM-DD)` in `sources`
   - `code-only` entries -> usually nothing to do; look only if the project is one you depend on
   - `ERROR` -> repo deleted, renamed or private: set `status: unreachable` or fix the URL
   - `BACK ONLINE` -> a repo catalogued as `unreachable` answers again (the script checks every such repo once per run with one `git ls-remote`): reread its README, set `status` and the other fields from it (version, last_activity, tested, features), note in `notes` that it was offline and is public again, then store its baseline with `--only <id> --update`. The entry is listed normally again.
   - directory changes (`dir-altstrument`, `dir-lapin`) -> new paths = candidate projects for `data/candidates.yml`
4. `python3 scripts/check_updates.py --only <ids you read> --update` (stores the new baseline for those only; a plain `--update` would drop changes nobody has read), `python3 scripts/repo_meta.py` (GitHub numbers for the network map and community page; needs `gh`), set `checked:` at the top of `data/projects.yml` to today's date (the website shows it as "checked daily (last ...)"), `python3 scripts/validate.py` (schema and cross-references; fix what it reports), then `python3 scripts/rebuild.py`, which runs every local generator in order: `first_seen.py` (date each entry first appeared, from git history; drives the "new" markers), `build.py` (the project lists in `catalog/`: README.md as the index, MODS.md, DEV-TOOLS.md, MUSICIAN-TOOLS.md, PROJECT-FAMILIES.md and one page per device), `research_snapshot.py`, `export_db.py` (database in `export/`), `agent_packs.py` (context packs in `export/context/`, `hardware/WEAK-EVIDENCE.md`, `hardware/ADDRESS-MAP.md`, `llms.txt`), `find_duplicates.py` (`hardware/DUPLICATES.md`), `feed.py` (`feed.xml`, the website's New tab) and `site_pages.py` (share pages in `p/`, sitemap); commit. A project that names RAM ranges it uses gets rows in `hardware/RAM-TENANCY.md`; a device whose recovery status changed gets it in `data/devices.yml` (`recovery`), in step with goal G1 in RESEARCH-MAP.md. A new entry lands in a list by its `kind`; give a `tool` entry `list: musician` (or `mods`) when it is not a developer tool. An entry that also ships usable mods (a research repo, a hardware mod) gets `also_lists: [mods]`, so MODS.md and the website's Mods tab show it too; a loader or platform lists the mods it ships itself (no repo or entry of their own) in `own_mods`, so they show together as one mod entry "<loader> mods" (one entry per repo, as for any collection), installed via that loader, and picking the loader on the website shows it; a mod a loader takes from a repo we list gets `mod_for` on that entry instead (Modwerk's `modwerk.module.json` and elekloader's `mods/` name their source repos); fill `tested` and `features` (what it does, 1-7 short points from its README, in our words) for every mod and `contains` for collections. Scope: every Elektron device that custom firmware or mods are written for; a loader's `devices` lists every device its README supports, but an entry in the mods list (a mod, or a repo with `also_lists: [mods]`) lists only the devices it ships mods for: tools, notes or file support for other devices go into its `notes` (example: dn2-firmware-explore, whose container tools also read Digitone MKI files, lists only the Digitone II), and a project for an Elektron device not yet in `data/devices.yml` adds that device there (with a section in `index.html`'s `--c-<device>` colours). Check the elekloader shop catalogue (`web/catalog.json` in elekloader/elekloader) for repos we do not list yet.

## What it cannot see
Forum threads, vendor pages (elektron.se release notes), PDFs and non-git sites. Those stay on the manual list in `hardware/MINING.md`; check them occasionally, e.g. when a new OS appears in a repo's diff.

## Adding a repo
Add the project to `data/projects.yml` with a `repo:` URL - it is watched automatically. For a narrower or wider watch list add an entry under `overrides` in `data/watch.yml`.

## Finding new projects (daily, automatic)
The daily update run (a scheduled agent session at 07:00 Vienna) runs the search itself and triages the result; the Action also runs `python3 scripts/find_new.py --since <30 days ago> --authors --code --report state/NEW.md`. The
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
   status mark in research/RESEARCH-MAP.md, remove or close the hypothesis or task. Contradicted: add a conflict.
   A failure or a test on a unit (a hang, crash, silence, stall, wrong behaviour, a recovery) also becomes an incident
   in `hardware/INCIDENTS.md` (rule C11): next free I-number, cause and how it was found, fix, status, evidence. Then
   add a rule to AGENT-RULES.md or add the incident to the rule it confirms, and tag the device-page fact `(I<n>)`.
   A bug in Elektron's own OS (a project writes "stock bug", or it reproduces on the unmodified OS) also goes into
   `hardware/STOCK-BUGS.md` with the next free SB-number (rule C12); stock-bug issues come in with the label
   `stock bug`. To find new ones, search the catalogued repos for "stock bug", "firmware bug" and "on stock too".
4. A new participant gets a section in `research/PARTICIPANTS.md` with suggested tasks that fit the project.
5. `python3 scripts/research_snapshot.py`, then build and export as usual.
