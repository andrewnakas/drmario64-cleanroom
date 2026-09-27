# Dr. Mario 64 clean room: status

## For the morning
- (in progress, see below)

## What works
- ROM unpacked (`D:/n64work/drmario64/rom`), SHA1 a130d362… = decomp's US baserom (md5 1a793636…).
- Decomp AngheloAlf/drmario64 @ b552609 cloned LF-only to `D:/n64work/drmario64/pristine`; dirty copy extracted with the decomp's own tools (rom_decompressor + splat 0.37): 1205 textures (657 i4, 202 ci8, 191 ci4, 111 rgba16, 44 i8), 393 palettes, 31 databins (audio banks/sequences, ipl3). Only 32 KB of asm is left: the code is essentially all C.

## Decisions (log)
- 2026-09-26 23:30 **Web route = 3 (clean N64 ROM + EmulatorJS/mupen64plus_next)**, same runtime as MK64 (EmulatorJS 4.2.3 GPL-3, local copy in `C:/Users/andre/n64work/mk64/emu/ejs`).
  - No Dr. Mario 64 PC port exists; the game is 2D, so emulation cost is low.
- **Code bytes**: the decomp is built with KMC GCC 2.7.2, which only ships Linux/mac binaries (no WSL on this PC). Since the decomp matches (CI checks the md5), its compiled code is byte-identical to the retail code, so the clean ROM keeps the code and structural data (headers, pointer tables, display lists, vertices, metadata) of each segment as a *skeleton* and replaces every texture, palette and sample byte range listed by splat. A whole-ROM taint scan checks that no retail texture/palette/sample run survives anywhere (not only in generated files).
  - Later improvement: build KMC gcc for Windows (or cross-compile the asset C with mips64-elf-gcc) so the skeleton comes from compiling the decomp instead of from the dirty image.
- **ROM layout**: compressed segments (raw deflate + crc + size, `tools/compressor`) are rebuilt with our own zlib at level 9. Slots are kept (padded) when a clean segment fits; otherwise ROM_START/END references are patched (to do if needed).
- Emulator save type: mupen64plus keys settings by ROM MD5, so the core's Dr. Mario 64 entry is pointed at our ROM's MD5 (same-length patch, as MK64).
