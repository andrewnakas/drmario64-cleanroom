"""CLEAN ROOM: spec + skeleton -> clean uncompressed image -> clean ROM.

    python -m games.drmario64.generate <spec_local dir> <out dir> [--only regex]

Textures come from `texture_image()` (defaults: colour grid + our own detail + the kept
alpha outline; overrides: drawn fonts, labels, briefs). CI textures sharing a palette
are quantised together into one palette we compute from our own images.
"""
import gzip
import json
import os
import re
import sys

import numpy as np

from cleanroom.decomp import gen
from cleanroom.gfx import png, texfmt as tf
from games.drmario64 import romfile
from games.drmario64.extract_spec import FMT

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "spec")

HOOKS = []   # callables (name, d) -> rgba or None, tried in order before the default


def texture_image(name, d):
    for hook in HOOKS:
        im = hook(name, d)
        if im is not None:
            return np.asarray(im, np.uint8)
    im = gen.from_digest(name, d)
    if d["disp"] in ("i4", "i8"):
        # intensity textures: the shape is the kept 2-bit outline, softened by the grid level
        a = gen.unpack_alpha2(d["alpha2"], d["w"], d["h"]) if "alpha2" in d else np.full((d["h"], d["w"]), 255.0)
        im = np.repeat(a[..., None], 4, -1).astype(np.uint8)
    return im


def rgb5551(p):
    p = np.asarray(p, np.int64)
    return ((p[:, 0] >> 3) << 11) | ((p[:, 1] >> 3) << 6) | ((p[:, 2] >> 3) << 1) | (p[:, 3] >= 128)


def kmeans(px, k, seed=1, iters=8):
    rng = np.random.default_rng(seed)
    if len(px) > 12000:
        px = px[rng.choice(len(px), 12000, replace=False)]
    uniq = np.unique(px, axis=0)
    if len(uniq) <= k:
        return uniq
    c = uniq[rng.choice(len(uniq), k, replace=False)].astype(np.float32)
    x = px.astype(np.float32)
    for _ in range(iters):
        lab = ((x[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            m = lab == j
            if m.any():
                c[j] = x[m].mean(0)
    return np.clip(np.round(c), 0, 255).astype(np.uint8)


def make_palette(images, n):
    """n entries; entry 0 transparent if any image has alpha < 128."""
    px = np.concatenate([im.reshape(-1, 4) for im in images])
    trans = (px[:, 3] < 128).any()
    opaque = px[px[:, 3] >= 128][:, :3]
    k = n - 1 if trans else n
    cols = kmeans(opaque, k) if len(opaque) else np.zeros((1, 3), np.uint8)
    pal = np.zeros((n, 4), np.uint8)
    off = 1 if trans else 0
    pal[off:off + len(cols), :3] = cols
    pal[off:off + len(cols), 3] = 255
    if len(cols) < k:
        pal[off + len(cols):] = pal[off]
    return pal


def quantise(im, pal):
    flat = im.reshape(-1, 4).astype(np.int32)
    opaque = pal[:, 3] >= 128
    idx = np.zeros(len(flat), np.int64)
    oi = np.nonzero(opaque)[0]
    d = ((flat[:, None, :3] - pal[None, oi, :3].astype(np.int32)) ** 2).sum(-1)
    idx[:] = oi[d.argmin(1)]
    if (~opaque).any():
        idx[flat[:, 3] < 128] = np.nonzero(~opaque)[0][0]
    return idx.reshape(im.shape[:2])


def build_image(skeleton, only=None, log=print):
    texs = json.load(open(os.path.join(SPEC, "textures.json")))
    pals = json.load(open(os.path.join(SPEC, "palettes.json")))
    img = bytearray(skeleton)
    images = {n: texture_image(n, d) for n, d in texs.items() if not only or only.search(n)}
    groups = {}
    for n in images:
        if "pal" in texs[n]:
            groups.setdefault(texs[n]["pal"], []).append(n)
    for pname, users in groups.items():
        p = pals[pname]
        n = 16 if all(texs[u]["disp"] == "ci4" for u in users) else 256
        pal = make_palette([images[u] for u in users], n)
        words = rgb5551(pal).astype(">u2").tobytes()
        region = (words * (p["size"] // len(words) + 1))[:p["size"]]
        img[p["off"]:p["off"] + p["size"]] = region
        for u in users:
            d = texs[u]
            siz = FMT[d["fmt"]][1]
            ncol = 16 if siz == tf.B4 else 256
            q = quantise(images[u], pal[:ncol] if len(pal) >= ncol else pal)
            idx = np.zeros(q.shape + (4,), np.uint8)
            idx[..., 0] = q
            img[d["off"]:d["off"] + d["bytes"]] = tf.encode(idx, tf.CI, siz)
    for n, im in images.items():
        d = texs[n]
        if "pal" in d:
            continue
        fmt, siz = FMT[d["fmt"]]
        if fmt == tf.CI:   # CI data drawn as intensity
            fmt = tf.I
        img[d["off"]:d["off"] + d["bytes"]] = tf.encode(im, fmt, siz)[:d["bytes"]]
    log(f"textures {len(images)} ({len(groups)} palettes)")
    return img


def main(argv):
    local, out = argv[1], argv[2]
    only = re.compile(argv[argv.index("--only") + 1]) if "--only" in argv else None
    os.makedirs(out, exist_ok=True)
    skel = gzip.open(os.path.join(local, "skeleton.bin.gz")).read()
    from games.drmario64 import hooks  # noqa: F401  (registers drawn assets)
    img = build_image(skel, only)
    with gzip.open(os.path.join(out, "clean_uncompressed.bin.gz"), "wb") as f:
        f.write(img)
    rom, rep = romfile.build(img, level=9)
    open(os.path.join(out, "drmario64.clean.z64"), "wb").write(rom)
    tight = sorted(rep, key=lambda r: r[2] - r[1])[:3]
    print(f"rom {len(rom) // 1024} KB; tightest slots: " + ", ".join(f"{n} {u:#x}/{s:#x}" for n, u, s in tight))


if __name__ == "__main__":
    main(sys.argv)
