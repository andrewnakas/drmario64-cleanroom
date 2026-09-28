#!/bin/sh
# Rebuild the site from the clean ROM and push it to gh-pages. Refuses the retail ROM (make_site.py).
set -e
W=${W:-D:/n64work/drmario64}
cd "$(dirname "$0")/.."
python ports/ejs/make_site.py $W/build/drmario64.clean.z64 $W/emu/ejs $W/site
python ports/ejs/patch_core.py $W/site/drmario64.z64 $W/site/data/cores $W/site/data/cores
cd $W/site
git init -q -b gh-pages 2>/dev/null || true
git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/andrewnakas/drmario64-cleanroom.git
git add -A
git -c user.name=andre -c user.email=treesixtyweather@gmail.com commit -qm "Site update: $(date +%F\ %H:%M)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" || true
git push -q -f origin gh-pages
