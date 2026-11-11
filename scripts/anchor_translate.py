#!/usr/bin/env python3
"""Translate addresses between two versions of an OS image by byte-pattern anchors (research goal G5, tasks T6, T8).

Every mod pins one OS version, and its addresses move when Elektron relinks the main OS. Most of the code does not
change between two versions, it only shifts. This tool finds byte runs that occur exactly once in the old image and
exactly once in the new one (anchors), records how far each moved, and translates any address by the anchors around
it. The method is the one Overtone describes for carrying its 1.11 patch addresses to 1.12.

You supply both images yourself (the unpacked MAIN OS section of each version, e.g. from elektron-firmware-tool or
digikit). Nothing here contains firmware, and you must not commit the images or publish them.

  python3 scripts/anchor_translate.py OLD.bin NEW.bin --base 0x40000400 0x4002e464 0x400987a2
  python3 scripts/anchor_translate.py OLD.bin NEW.bin --base 0x40000400 --file addresses.txt --csv out.csv
  python3 scripts/anchor_translate.py OLD.bin NEW.bin --base 0x40000400 --map          # the shift map only

--base is the address the image's first byte is loaded at (old and new; --new-base if they differ).
Output per address: the new address, the shift, and how sure the tool is:
  exact       the bytes at the address itself are an anchor (found once in both images)
  bracketed   anchors before and after the address moved by the same amount
  one-sided   only an anchor on one side is near; the address is probably right, check it
  ambiguous   the anchors before and after moved by different amounts: the address lies where the code changed
  not-found   no anchor within reach
A translated address is a candidate, not a fact: disassemble at the new address and compare before you patch
(rules A41, A6). Data addresses (BSS, tables in RAM) are not in the image and cannot be translated this way; use the
code that references them.
"""
import argparse
import bisect
import csv
import sys


def is_plain(window):
    """Runs of padding or a repeated byte make useless anchors."""
    return len(set(window)) < max(4, len(window) // 6)


def unique_pos(hay, needle):
    i = hay.find(needle)
    if i < 0 or hay.find(needle, i + 1) >= 0:
        return None
    return i


def build_map(old, new, window=24, step=64):
    """[(old_offset, shift)] for byte runs that are unique in both images, in old-offset order."""
    anchors = []
    for i in range(0, len(old) - window, step):
        w = old[i:i + window]
        if is_plain(w):
            continue
        j = unique_pos(new, w)
        if j is None or unique_pos(old, w) != i:
            continue
        anchors.append((i, j - i))
    return anchors


def segments(anchors):
    """Merge neighbouring anchors with the same shift: [(first_old_offset, last_old_offset, shift, count)]."""
    out = []
    for off, d in anchors:
        if out and out[-1][2] == d:
            out[-1] = (out[-1][0], off, d, out[-1][3] + 1)
        else:
            out.append((off, off, d, 1))
    return out


def translate(off, old, new, anchors, window=24, reach=0x4000):
    """(new_offset or None, method) for one old offset."""
    if 0 <= off <= len(old) - window:
        w = old[off:off + window]
        if not is_plain(w) and unique_pos(old, w) == off:
            j = unique_pos(new, w)
            if j is not None:
                return j, "exact"
    keys = [a[0] for a in anchors]
    k = bisect.bisect_right(keys, off)
    before = anchors[k - 1] if k > 0 and off - anchors[k - 1][0] <= reach else None
    after = anchors[k] if k < len(anchors) and anchors[k][0] - off <= reach else None
    if before and after:
        if before[1] == after[1]:
            return off + before[1], "bracketed"
        return None, f"ambiguous (shift {before[1]:+d} before, {after[1]:+d} after)"
    if before or after:
        return off + (before or after)[1], "one-sided"
    return None, "not-found"


def parse_addr(s):
    return int(s, 16) if s.lower().startswith("0x") else int(s, 16)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("old"), ap.add_argument("new")
    ap.add_argument("addresses", nargs="*", help="addresses in the old image (hex)")
    ap.add_argument("--base", required=True, help="load address of the old image's first byte (hex)")
    ap.add_argument("--new-base", help="load address of the new image, if different")
    ap.add_argument("--file", help="text file with one hex address per line (text after it is kept as a label)")
    ap.add_argument("--window", type=int, default=24, help="anchor length in bytes (default 24)")
    ap.add_argument("--step", type=int, default=64, help="distance between anchor candidates (default 64)")
    ap.add_argument("--map", action="store_true", help="print the shift map (segments of equal shift)")
    ap.add_argument("--csv", help="also write the result as CSV")
    a = ap.parse_args(argv)
    old, new = open(a.old, "rb").read(), open(a.new, "rb").read()
    base = parse_addr(a.base)
    nbase = parse_addr(a.new_base) if a.new_base else base
    wanted = [(parse_addr(x), "") for x in a.addresses]
    if a.file:
        for line in open(a.file, encoding="utf-8"):
            parts = line.split(None, 1)
            if parts and not parts[0].startswith("#"):
                wanted.append((parse_addr(parts[0]), parts[1].strip() if len(parts) > 1 else ""))
    anchors = build_map(old, new, a.window, a.step)
    segs = segments(anchors)
    print(f"# {len(anchors)} anchors of {a.window} bytes, {len(segs)} segments of equal shift; "
          f"old {len(old):,} B, new {len(new):,} B", file=sys.stderr)
    if a.map or not wanted:
        print("old_from    old_to      shift     anchors")
        for f, t, d, n in segs:
            print(f"0x{base + f:08x}  0x{base + t:08x}  {d + nbase - base:+8d}  {n}")
    rows = []
    for addr, label in wanted:
        off = addr - base
        j, how = translate(off, old, new, anchors, a.window) if 0 <= off < len(old) else (None, "outside the image")
        rows.append({"old": f"0x{addr:08x}", "new": f"0x{nbase + j:08x}" if j is not None else "",
                     "shift": f"{nbase + j - addr:+d}" if j is not None else "", "method": how, "label": label})
    if rows:
        print(f"{'old':<12}{'new':<12}{'shift':<9}method")
        for r in rows:
            print(f"{r['old']:<12}{r['new'] or '-':<12}{r['shift'] or '-':<9}{r['method']}{'  ' + r['label'] if r['label'] else ''}")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=["old", "new", "shift", "method", "label"])
            wr.writeheader()
            wr.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
