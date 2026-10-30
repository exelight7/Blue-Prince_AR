#!/bin/sh
# kill, deploy latest plugin+translations, launch, start a new game and skip the intro (written to bpar/in_game.png when done)
cd "$(dirname "$0")"
python -I gamectl.py kill; sleep 2
sh deploy_plugin.sh ar.json | tail -1
rm -f ../runtime_test/BepInEx/bpar/*.png ../runtime_test/BepInEx/bpar/untranslated.tsv
python -I gamectl.py launch; sleep 38
python -I gamectl.py click 600 430; sleep 40
python -I gamectl.py keys ESC:4; sleep 8
python -I gamectl.py cmd "shot in_game"
