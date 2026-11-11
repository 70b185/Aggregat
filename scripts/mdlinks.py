"""Rewrite relative Markdown links when text moves from one file to a page in another folder.

Generated pages (hardware/DUPLICATES.md, hardware/WEAK-EVIDENCE.md, ...) quote facts from files in other folders. A
link like ../common/recovery.md is relative to the fact's own file; relink() makes it relative to the page that quotes
it, so the link keeps working.
"""
import posixpath
import re

LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


# where the root-level pages went when the root was tidied (2026-11-11); text written with root-relative links to
# these names is pointed at their new place
MOVED = {"INDEX.md": "catalog/README.md", "MODS.md": "catalog/MODS.md", "DEV-TOOLS.md": "catalog/DEV-TOOLS.md",
         "MUSICIAN-TOOLS.md": "catalog/MUSICIAN-TOOLS.md", "PROJECT-FAMILIES.md": "catalog/PROJECT-FAMILIES.md",
         "RESEARCH-MAP.md": "research/RESEARCH-MAP.md", "FEATURE-OVERLAP.md": "research/FEATURE-OVERLAP.md",
         "CONTRIBUTING.md": ".github/CONTRIBUTING.md"}


def relink(text, src_file, dst_file, moves=MOVED):
    """src_file, dst_file: repository-relative paths (e.g. hardware/devices/dn2.md, hardware/WEAK-EVIDENCE.md)."""
    src_dir, dst_dir = posixpath.dirname(src_file), posixpath.dirname(dst_file)

    def fix(m):
        href = m.group(2)
        if re.match(r"^(https?:|mailto:|#|\?)", href):
            return m.group(0)
        path, sep, anchor = href.partition("#")
        full = posixpath.normpath(posixpath.join(src_dir, path))
        full = moves.get(full, full)
        new = posixpath.relpath(full, dst_dir or ".")
        return f"[{m.group(1)}]({new}{sep}{anchor})"
    return LINK.sub(fix, text or "")
