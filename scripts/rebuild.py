#!/usr/bin/env python3
"""Run every generator in the right order after an edit to data/ or hardware/.

  python3 scripts/rebuild.py            local generators only (no network)
  python3 scripts/rebuild.py --online   first refresh GitHub numbers (scripts/repo_meta.py, needs gh)

Order: first_seen -> build (Markdown lists) -> research_snapshot -> export_db (database) -> agent_packs (context
packs, weak-evidence list, address map, llms.txt) -> find_duplicates -> feed. The change check
(scripts/check_updates.py) and the search for new repos (scripts/find_new.py) are separate: see docs/UPDATING.md.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["first_seen.py", "build.py", "research_snapshot.py", "export_db.py", "agent_packs.py", "find_duplicates.py", "feed.py"]


def main():
    steps = (["repo_meta.py"] if "--online" in sys.argv else []) + STEPS
    for s in steps:
        print(f"== {s}", flush=True)
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / s)], cwd=ROOT)
        if r.returncode:
            if s == "repo_meta.py":
                print("repo_meta failed; keeping the old numbers")
                continue
            sys.exit(f"{s} failed with exit code {r.returncode}")


if __name__ == "__main__":
    main()
