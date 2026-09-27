"""Uncompressed image <-> N64 ROM for Dr. Mario 64 (layout kept: every segment stays in its slot).

    python -m games.drmario64.romfile roundtrip <dirty tree>     (dev check: rebuild retail from its own image)
"""
import json
import os
import sys

import crunch64
import ipl3checksum

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec")


def layout():
    return json.load(open(os.path.join(SPEC, "layout.json")))


def build(unc, lay=None, level=None, fill=0xFF):
    """unc: uncompressed image bytes. Returns (rom bytes, report list of (segment, used, slot)).

    Everything up to and including main_segment keeps its place (boot code refers to it
    with hi/lo pairs). Every later segment is referenced only through the {start, end}
    tables in boot_data.c (uncompressed), so later segments are packed one after another
    and those pairs are rewritten."""
    lay = lay or layout()
    segs = lay["segments"]
    main = next(s for s in segs if s["name"] == "main_segment")
    blobs, report = [], []
    for s in segs:
        data = bytes(unc[s["ustart"]:s["ustart"] + s["ulen"]])
        if s["compressed"]:
            lv = s["level"] if level is None else level
            data = crunch64.gzip.compress(data, lv, small_mem=s["tool"] == "gzip_smallmem")
            data += bytes(-len(data) % 16)
            report.append((s["name"], len(data), s["cend"] - s["cstart"]))
        blobs.append(data)
    out = bytearray()
    moved = {}
    for s, data in zip(segs, blobs):
        if s["cstart"] <= main["cstart"]:
            slot = s["cend"] - s["cstart"]
            if len(data) > slot:
                raise ValueError(f"fixed segment {s['name'] or hex(s['cstart'])} is {len(data):#x} > slot {slot:#x}")
            out += data + bytes(slot - len(data))
            continue
        start = len(out)
        out += data
        moved[(s["cstart"], s["cend"])] = (start, start + len(data))
    size = max(lay["crom_len"], (len(out) + 0xFFFFF) & ~0xFFFFF)
    out += bytes([fill]) * (size - len(out))
    patched = 0
    fixed = bytes(out[:main["cstart"]])
    for (a, b), (na, nb) in moved.items():
        pat = a.to_bytes(4, "big") + b.to_bytes(4, "big")
        pos = fixed.find(pat)
        while pos >= 0:
            out[pos:pos + 8] = na.to_bytes(4, "big") + nb.to_bytes(4, "big")
            patched += 1
            pos = fixed.find(pat, pos + 4)
    report.append(("pairs patched", patched, len(moved)))
    return fix_crc(out), report


def fix_crc(rom):
    rom = bytearray(rom)
    cic = ipl3checksum.detectCIC(rom) or ipl3checksum.CICKind.CIC_6102_7101
    c1, c2 = ipl3checksum.calculateChecksum(rom, cic)
    rom[0x10:0x14] = c1.to_bytes(4, "big")
    rom[0x14:0x18] = c2.to_bytes(4, "big")
    return bytes(rom)


def main(argv):
    if argv[1] == "roundtrip":
        tree = argv[2]
        unc = open(os.path.join(tree, "config/us/baserom_uncompressed.us.z64"), "rb").read()
        ret = open(os.path.join(tree, "config/us/baserom.us.z64"), "rb").read()
        rom, rep = build(unc)
        diff = [i for i in range(0, len(rom), 0x1000) if rom[i:i + 0x1000] != ret[i:i + 0x1000]]
        print(f"roundtrip: {'OK identical' if rom == ret else f'{len(diff)} differing 4K blocks (alignment garbage expected), first {diff[:5]}'}; {rep[-1]}")


if __name__ == "__main__":
    main(sys.argv)
