# Agent workflow for firmware mods (distilled from the digitone-2-modding-skill)

An agent skill that was used to ship Overtone has a worked-out loop. The Digitone II specifics are in
[`../devices/digitone-2-os111-reference.md`](../devices/digitone-2-os111-reference.md); the loop below is device-independent in spirit. Each step "came from a costly hardware round trip" per the author. `[doc]` {dn2-skill-workflow}

## The loop
1. **Spec first, in one round.** Ask the user the spec questions together, each with 2-4 options and your recommendation first, because a wrong guess costs a full build and flash. Write the answers into the log before building.
2. **Find it in stock.** Read the routine you will hook from start to finish; note every register and flag that code after your hook reads. Use the project's tools, the manual and the upstream notes (`git pull` upstream first - its notes may already contain your plumbing).
3. **Write the test first**, with a stock control in the same run (a stock knob or key doing the same gesture, to confirm the gesture happened). For a bug: reproduce it as a failing test on the faulty build, fix it, confirm the test passes.
4. **Build and check:** build, run all static checks, run every test, run the container inspector, check the flash size.
5. **Flash one clearly named image** (e.g. `build/DN2_1.11_<NAME>_<N>.syx`), never overwrite an older image; keep your last hardware-good image and the stock image. Record the SHA-256, what changed and exactly what to try on the unit.
6. **Record the result** in a log entry per build (what to test, verdict) so the next session starts from facts.

## Rules (each from a hardware round trip)
- Run the emulator before every flash; the unit should only judge sound and feel.
- Test what the hardware actually consumes (the frames the CPU sends and the DSP's output). **Never test by reading back what your patch wrote.**
- Exercise the real path (sequencer, several tracks, a track other than 1) and the extremes: hard pan, 0 and 127, maximum feedback, every machine, unison.
- Check any stock state you read on every variant (every machine and filter type).
- If a gesture works on stock pages but not on yours, find the stock routine and its bound (Digitone II: `slot <= 100`).
- Keep levels honest: measure worst cases, report them, avoid unrequested gain compensation; send-FX returns are wet only; clamp every audio-writing build; never read memory you did not write.
- Profile L2/DDR accesses; if the unit's load disagrees with the emulator, measure on the unit before optimising. Keep per-block CPU work small, defer per-note work.
- Do not call a root cause certain until the hardware agrees.
- Never overwrite the stock image. Know the source of any third-party download.
- Ask the user before cloning or installing anything. Work only on the user's own copy of the stock file; never commit or share extracted sections, snapshots or built images; make every mod reversible by reflashing stock.

## Stopping rule
After **two failed flashes on one problem, stop**: restate the goal, what is proven, what is unknown, and the options.

## Triage: "silent unit" (UI works, no sound from power-on)
The DSP never ran a block. Compare builds for what the emulator cannot model: block lengths and alignment, instruction encodings, uninitialised DDR, sizes (section 7 under 1 MiB, L2 below the limit). **Split the images**: one build's ColdFire with the other's DSP section - one flash shows which side is at fault, then bisect that side. If sound drops after a certain gesture until restart, suspect a NaN in a feedback state (DDR garbage, a divide) or a register clobbered at a hook; diff registers at the callee. `[doc]` {dn2-skill-workflow}

## Spec questions to ask (one round, 2-4 options each, recommendation first)
1. Reference: which sound/behaviour is the target; 1:1 port or inspired-by?
2. Location: new machine, page insert, send/bus effect, global screen, key combo? Which keys?
3. Knobs: which parameters, order, names (4 characters max), ranges, defaults; what each encoder does on a menu page?
4. Level: unity gain without compensation, or matched to the reference?
5. Routing: per voice or per track; before the filter (mono) or after pan (stereo); do sends get dry or wet signal?
6. Modulation: restart per note or free-running; lockable per trig; LFO destination?
7. Storage: per sound, pattern, project or global; survive SAVE PROJECT and a power cycle?
8. CPU: acceptable worst case (all 16 voices or tracks); if it does not fit, accept fewer voices, half rate or a cheaper variant?
9. Done criteria: what will be tried on the unit and what counts as right (A/B against a reference, by ear, by measurement)?
`[doc]` {dn2-skill-workflow}

## Repo-level rules for agents (elekloader `AGENTS.md`, the only project we found that ships a formal agent file)
- **Read first:** README, `docs/README.md`; for mods `docs/ADAPTING.md` and the `examples/hello-marker/` starter; for core changes `docs/CORE-CONTRIBUTING.md`; for device facts `docs/DEVICES.md`; for the file format `docs/FORMAT.md`. `[doc]` {elekloader-agents}
- **Before adding a code site to a mod, check whether the core already has an event, table or export for it.** If another mod could want the same thing, build it in the core's shape in its own file so it can move into the core, tell the user and offer a pull request; use `lint`'s `core_candidates`, `sdk.coresites` and `sdk.bounties` to find hooks that belong in the core. `[doc]` {elekloader-agents}
- **Never commit firmware** - no `.syx`, extracted sections, `.bin` images, built `.elemod` files or anything derived from a stock OS; run `git status` to check. **Never weaken a check to make a test pass:** the checks in `syx.verify`, `elemod` and `link` protect users (bootloader stays stock, mods must not collide); if a check wrongly refuses something, narrow the fix and test both sides. Keep device facts in `devices/`, not in code paths; the writer must stay byte-exact (`test_writer_matches_c_tool`, `test_writer_no_change_is_stock`); keep the JS engine in sync with the Python one; keep the web kit site-agnostic; the web page loads nothing from other origins, sends user files nowhere, holds no firmware or builds, and pins catalog entries by SHA-256. `[doc]` {elekloader-agents}
- **Tests:** always `python tests/test_units.py` and `python tests/test_link_refusals.py`; others need firmware passed through environment variables (`ELEKLOADER_STOCK`, `ELEKLOADER_DN_SYX`, ...). **A test with missing files is skipped, not passed - report which tests ran** and never claim a skipped test passed. "Done" = all runnable tests pass, docs match the code, `git status` shows no firmware. `[doc]` {elekloader-agents}
- **Docs hygiene:** describe the current state once, in its home (a doc-hygiene skill with an audit exists in `.claude/skills/`). `[doc]` {elekloader-agents}
- **Format rules worth copying:** a mod stores a hash of stock bytes, never the bytes themselves; where its bytes repeat firmware it writes a `["stock", addr, len]` reference and the loader copies them from the user's own hash-checked image; a `code` site must cover whole instructions; the linker checks stock hashes, overlaps, memory regions within free areas, duplicates, unresolved imports and core versions, lays out the core first and then mods sorted by ID (output independent of input order), and **verifies that the built image differs from stock only inside declared sites and appended code**. `[doc]` {elekloader-format}

