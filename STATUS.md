# Dr. Mario 64 clean room: status

## For the morning
- **Not published yet.** The first clean ROM (default fonts, retail audio) booted to the title natively and in the browser. The current clean ROM (drawn fonts + resynthesised audio + relocated segments) hangs or crashes before the first frame, natively (mupen64plus) and in EmulatorJS.
  - Ruled out: the ROM relocation (retail content shifted by 0x21e0 boots), the game's inflater (gzcheck, built from the decomp's own inflate.c, decodes every stream), the checksum, and single-byte changes.
  - Fixed on the way: boot_data's `_romDataTbl` holds pairs *inside* the uncompressed audio/data region, which are now shifted too (94 pairs).
  - Open: retail main_segment + retail audio + clean textures + shifted layout fails, while clean textures without a shift boot. The next step is a per-segment-group bisect (`devR_*` ROMs are already built in D:/n64work/drmario64/build).
- **Stopped by the system (low memory), not restarted:** the local web server (port 8631) and the background bisect run (`devR_title/anime/menu/game/story`). Rerun the bisect when memory allows: `for g in title anime menu game story; do python tools/m64p_test.py D:/n64work/drmario64/build/devR_$g.z64 D:/n64work/drmario64/shots/devR_$g --frames 300; done`
- **C: is full (0 bytes free)**; set TEMP/TMP to D:/n64work/drmario64/tmp for this work. Other sessions' `cdprun_*` browser profiles in the Temp folder use ~0.35 GB each (54 of them); I did not delete them because they are not mine.

## Pipeline (commands)
- Dirty: `python -m games.drmario64.extract_spec D:/n64work/drmario64/dirty games/drmario64/spec D:/n64work/drmario64/spec_local`
- Clean: `python -m games.drmario64.generate D:/n64work/drmario64/spec_local D:/n64work/drmario64/build` -> `drmario64.clean.z64`
- Taint: `python -m games.drmario64.taint_report D:/n64work/drmario64/dirty D:/n64work/drmario64/build/clean_uncompressed.bin.gz`
- Native check: `python tools/m64p_test.py <rom> <out> --frames 300,900` (mupen64plus copy in D:/n64work/drmario64/m64p)
- Site: `ports/ejs/make_site.py` + `ports/ejs/patch_core.py`; headless: `ports/ejs/cdp_shot.py --gpu`

## What works
- ROM unpacked (`D:/n64work/drmario64/rom`), SHA1 a130d362… = decomp's US baserom (md5 1a793636…).
- Decomp AngheloAlf/drmario64 @ b552609 cloned LF-only to `D:/n64work/drmario64/pristine`; dirty copy extracted with the decomp's own tools (rom_decompressor + splat 0.37): 1205 textures (657 i4, 202 ci8, 191 ci4, 111 rgba16, 44 i8), 393 palettes, 31 databins (audio banks/sequences, ipl3). Only 32 KB of asm is left: the code is essentially all C.

## Decisions (log)
- 2026-09-26 23:30 **Web route = 3 (clean N64 ROM + EmulatorJS/mupen64plus_next)**, same runtime as MK64 (EmulatorJS 4.2.3 GPL-3, local copy in `C:/Users/andre/n64work/mk64/emu/ejs`).
  - No Dr. Mario 64 PC port exists; the game is 2D, so emulation cost is low.
- **Code bytes**: the decomp is built with KMC GCC 2.7.2, which only ships Linux/mac binaries (no WSL on this PC). Since the decomp matches (CI checks the md5), its compiled code is byte-identical to the retail code, so the clean ROM keeps the code and structural data (headers, pointer tables, display lists, vertices, metadata) of each segment as a *skeleton* and replaces every texture, palette and sample byte range listed by splat. A whole-ROM taint scan checks that no retail texture/palette/sample run survives anywhere (not only in generated files).
  - Later improvement: build KMC gcc for Windows (or cross-compile the asset C with mips64-elf-gcc) so the skeleton comes from compiling the decomp instead of from the dirty image.
- **ROM layout**: compressed segments (raw deflate + crc + size, `tools/compressor`) are rebuilt with our own zlib at level 9. Slots are kept (padded) when a clean segment fits; otherwise ROM_START/END references are patched (to do if needed).
- **ROM relayout** (`romfile.py`): every segment after main_segment is referenced only via the `{start,end}` tables in boot_data.c (uncompressed boot segment), so later segments are packed and those pairs rewritten (67 pairs). main_segment keeps its start; its end is one lui/addiu pair in boot_main (ROM 0x1134) that is patched, so it can grow. Retail round-trip through this assembler is byte-identical apart from alignment garbage.
- Textures: CI textures sharing a palette (anime frames use frame 0's TLUT, per char_anime.c) are quantised together into one palette computed from our images. Intensity textures (masks) are our softened rendering of the 2-bit outline. main_segment textures get no detail noise (compressibility).
- Fonts: slot -> character from the decomp's tables in font.c (font_e_tbl/font_e2_tbl ASCII, char_code_tbl Shift-JIS; 322 kana/kanji slots). Drawn with Rubik (ASCII), M PLUS Rounded 1c ExtraBold (kana/kanji), Press Start 2P (debug font), 4 ink levels; the second half of font_e2/font_2 cells is a 1 px outline of the glyph (two-pass draw).
- Audio: libmus "N64 PtrTablesV2" bank, 190 waves. Facts: length, type, loop, book shape, spectral outline, median pitch. Clean: resynthesis + our own VADPCM books with the same predictor count (bank keeps its size) + loop states. Songs (`segment_17xxxx`) and fxbank kept as note data.
- Taint: per-asset in-place runs plus a whole-image scan of every 32-byte retail asset window. Hits outside generated assets are data the decomp defines in C (a grey ramp TLUT, tables) and reported as info only.
- Emulator save type: mupen64plus keys settings by ROM MD5, so the core's Dr. Mario 64 entry is pointed at our ROM's MD5 (same-length patch, as MK64).
