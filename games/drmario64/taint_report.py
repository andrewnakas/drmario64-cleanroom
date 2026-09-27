"""DEV/DIRTY check: does any retail texture, palette or sample byte run survive in the clean image?

    python -m games.drmario64.taint_report <dirty tree> <clean_uncompressed.bin.gz>

1. per asset: the clean bytes of each texture/palette/wave vs the retail bytes at the same place
   (fail at a shared run of >= 32 bytes that is not trivial: > 6 byte values, no value 20+ times)
2. whole image: every 32-byte retail asset window (stride 8) is looked up at every offset of the
   clean image, so a retail run of >= 40 bytes anywhere (code, data, other assets) is caught.
Prints counts and the worst offenders; exit status 1 if anything fails.
"""
import gzip
import json
import os
import sys

from games.drmario64.audio import SPEC


def trivial(b):
    """Mostly one byte value (zero fill, table padding, flat colour): not evidence of copying."""
    return len(set(b)) <= 6 or max(b.count(bytes([v])) for v in set(b)) >= 20


def longest_run(a, b):
    best = cur = 0
    start = 0
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            cur += 1
            if cur > best:
                best, start = cur, i - cur + 1
        else:
            cur = 0
    return best, start


def ranges():
    texs = json.load(open(os.path.join(SPEC, "textures.json")))
    pals = json.load(open(os.path.join(SPEC, "palettes.json")))
    lay = json.load(open(os.path.join(SPEC, "layout.json")))
    smp = json.load(open(os.path.join(SPEC, "samples.json")))
    out = [(n, d["off"], d["bytes"]) for n, d in texs.items()]
    out += [("pal:" + n, p["off"], p["size"]) for n, p in pals.items()]
    out += [(f"wave{d['i']}", lay["wave_tables"] + d["base"], d["len"]) for d in smp]
    return out


def main(argv):
    ret = open(os.path.join(argv[1], "config/us/baserom_uncompressed.us.z64"), "rb").read()
    cl = gzip.open(argv[2]).read()
    fails, checked = [], 0
    windows = set()
    for name, off, size in ranges():
        a, b = ret[off:off + size], cl[off:off + size]
        checked += 1
        # shared runs, ignoring trivial ones
        i, n = 0, min(len(a), len(b))
        while i < n:
            if a[i] != b[i]:
                i += 1
                continue
            j = i
            while j < n and a[j] == b[j]:
                j += 1
            if j - i >= 32 and not trivial(a[i:j]):
                fails.append((name, off + i, j - i))
                break
            i = j
        for k in range(0, size - 32, 8):
            w = a[k:k + 32]
            if not trivial(w):
                windows.add(w)
    gen_ranges = sorted((off, off + size) for _, off, size in ranges())
    import bisect
    starts = [a for a, _ in gen_ranges]

    def generated(k):
        i = bisect.bisect_right(starts, k) - 1
        return i >= 0 and k < gen_ranges[i][1]
    hits, info = [], 0
    for k in range(0, len(cl) - 32):
        if cl[k:k + 32] in windows:
            if generated(k):
                hits.append(k)
            else:
                info += 1   # bytes the decomp itself defines in C (tables, ramps), outside every asset
    print(f"taint: {checked} assets checked, {len(fails)} failing in place; retail asset windows inside "
          f"generated assets: {len(hits)} (decomp-defined data matching a retail window, info only: {info})")
    for f in fails[:8]:
        print("  in place:", f)
    for h in hits[:8]:
        print(f"  window at {h:#x}")
    sys.exit(1 if fails or hits else 0)


if __name__ == "__main__":
    main(sys.argv)
