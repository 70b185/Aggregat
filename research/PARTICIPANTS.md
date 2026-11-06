# Projects that take part in the research

Projects that keep an `AGGREGAT_RESEARCH.md` in their repo are listed here, each with tasks suggested for what that
project already does and the devices it can test. Taking part is voluntary; nobody needs to, and anyone can stop.

## How it works

1. **Join:** copy [AGGREGAT_RESEARCH.md](AGGREGAT_RESEARCH.md) to the root of your repo and fill in your project,
   your devices and what you can test. The file carries a full copy of the current goals, tasks, hypotheses and open
   conflicts, so your results stay tied to the state you started from.
2. **We notice:** Aggregat's update runs find the file (GitHub code search for the file name) and watch it in every
   catalogued repo. A new project with the file gets a section below.
3. **Suggested tasks:** in your section we list tasks that fit your project. You read them here; we do not open issues
   or pull requests in your repo, and we do not mention you.
4. **Results:** fill in the results table in your file. When we update, a maintainer reads new rows, checks them and
   merges them into the device pages with credit to your project. One unit report makes a fact 🟢 (shown once), a
   second unit or project makes it ✅. A result that contradicts others goes to the conflict list.
5. **No repo?** Report single results with the **Test result** issue template in the Aggregat repo.

Results are merged by hand only, by the repo maintainer, during manual updates.

## Participants

None yet.

## Contributions by pull request

Pull requests are welcome too: correct a fact about your own project, add evidence, fix the tooling. A maintainer
reviews and merges them by hand, as with results.

| Date | From | What | PR |
|---|---|---|---|
| 2026-11-04 | armio (dn2-dt2-firmware-research) | R012 listing; SHARC cache ranges and diagnostic-word losses corrected against digikit findings 101 and 103 (H12) | [#1](https://github.com/70b185/Aggregat/pull/1) |
| 2026-11-04 | angellinares (dn2_firmware_explore) | four facts about dn2_firmware_explore corrected from its own records; O17 settled as S17; unit evidence for O19 | [#2](https://github.com/70b185/Aggregat/pull/2) |
| 2026-11-04 | angellinares | relation graph in the README (`scripts/relation_graph.py`) and the `license` field | [#3](https://github.com/70b185/Aggregat/pull/3) |
| 2026-11-06 | armio (dn2-dt2-firmware-research) | Digiwerk 0.3.0 availability (spring builds still withdrawn) and the scope of two USB research figures, pinned to the source commit | [#4](https://github.com/70b185/Aggregat/pull/4) |

<!-- Section template for a participant:
## <project> (<repo link>)
Joined: <date>; snapshot they copied: `<hash>`; devices: <...>; can do: <stock / probe / build>.

| Suggested | Why this project | Status | Result merged |
|---|---|---|---|
| H12 | has DSP hooks on the DN2 already | open | - |
-->
