# Dr. Mario 64 — clean room web build

Play: **https://andrewnakas.github.io/drmario64-cleanroom/**

Dr. Mario 64 built from the [AngheloAlf/drmario64](https://github.com/AngheloAlf/drmario64) decompilation and played in the browser
(EmulatorJS + mupen64plus-next). **Every asset the decomp extracts from a ROM is regenerated**: textures, palettes,
fonts, sound samples. No ROM is needed to play.

Keys: **Arrows** move / drop · **X** A (rotate) · **Z** B (rotate back) · **Enter** Start · **Space** Z · **Q / W** L / R ·
**I J K L** C buttons. Gamepads work too.

## What is kept, what is generated

| Asset | Kept fact | Generated |
|---|---|---|
| Textures (1205) and palettes (393) | format, size, a 4×4 colour grid (16×16 for ≥128 px), a 2-bit alpha outline | colour from the grid plus our own detail; CI textures that share a palette are quantised together into our own palette |
| Fonts (ASCII, kana/kanji, debug) | which character sits in which slot (the decomp's own tables in `font.c`) | drawn with Rubik, M PLUS Rounded 1c, Press Start 2P (OFL) |
| Samples (190, libmus bank) | length, loop points, codebook shape, a coarse spectral outline, one median pitch | resynthesised, our own VADPCM codebooks (same predictor count, so the bank keeps its size) |
| Music and sound-effect scripts | the note data (melodies) | played by the resynthesised instruments |
| Code, display lists, vertices, tables | the decomp | — |

`games/drmario64/taint_report.py` compares every generated texture, palette and sample with the retail data, and also
looks for any 32-byte retail asset run anywhere in the clean image: **0 failing**.

## How the ROM is built

- `extract_spec.py` (dirty room, reads the ROM once): coarse facts into `games/drmario64/spec/`, plus a local
  *skeleton* (the uncompressed image with every asset byte zeroed; never published).
- `generate.py` (clean room): skeleton + spec + our drawings → clean image → ROM (`romfile.py`).
  - Segments after `main_segment` are packed and the boot tables rewritten, so regenerated segments can change size.
  - Every compressed segment is checked with the game's own inflate code (`tools/gzcheck`, built from the decomp).
    Its Huffman tables live in a fixed 16 KB arena, and many valid deflate streams overflow it.
- `ports/ejs/`: the web page, the site builder, and a core patch that points the emulator's Dr. Mario 64 settings
  (EEPROM save type) at our ROM's MD5.

The decomp's code is built with KMC GCC 2.7.2 (Linux/macOS only). Because the decomp matches, its compiled code is
identical to the retail code, so the skeleton keeps the code bytes.

Status and decisions: [STATUS.md](STATUS.md).

## Licences

Our code: MIT. Fonts: see `games/drmario64/fonts/`. EmulatorJS (GPL-3.0) and the mupen64plus-next core (GPL-2.0)
are only in the site (`THIRD_PARTY.md` there). Dr. Mario is a trademark of Nintendo; this project is not affiliated
with Nintendo.
