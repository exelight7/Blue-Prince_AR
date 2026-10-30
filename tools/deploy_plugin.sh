#!/bin/sh
# build the plugin and copy it (plus translations) into the disposable runtime copy
set -e
R="/d/Games/Blue Prince_AR"
cd "$R/plugin/BluePrinceArabic"
OUT=$(dotnet build -c Release -o out 2>&1) || true
echo "$OUT" | grep -E "error" | sort -u | head -5
echo "$OUT" | grep -q " 0 Error(s)" || { echo "BUILD FAILED"; exit 1; }
P="$R/runtime_test/BepInEx/plugins/BluePrinceArabic"
mkdir -p "$P"
cp -f out/BluePrinceArabic.dll "$P/"
mkdir -p "$P/fonts"
for f in Amiri-Regular.ttf Amiri-Bold.ttf Amiri-Italic.ttf IBMPlexSansArabic-Medium.ttf IBMPlexSansArabic-Bold.ttf; do cp -f "$R/fonts/arabic/$f" "$P/fonts/"; done
for f in Lalezar-Regular Mirza-Bold Katibeh-Regular Rakkas-Regular; do cp -f "$R/fonts/arabic/pf/$f-PF.ttf" "$P/fonts/"; done
cp -f "$R/translation/arabic/${1:-ar_testpack.json}" "$P/ar.json"
[ -f "$R/translation/arabic/ar_patterns.json" ] && cp -f "$R/translation/arabic/ar_patterns.json" "$P/" || true
[ -f "$R/translation/arabic/intro_subs.tsv" ] && cp -f "$R/translation/arabic/intro_subs.tsv" "$P/" || true
[ -f "$R/translation/arabic/intro_cards.tsv" ] && cp -f "$R/translation/arabic/intro_cards.tsv" "$P/" || true
[ -f "$R/translation/arabic/tagwords.json" ] && cp -f "$R/translation/arabic/tagwords.json" "$P/" || true
[ -f "$R/translation/arabic/layout.tsv" ] && cp -f "$R/translation/arabic/layout.tsv" "$P/" || true
[ -f "$R/translation/arabic/dropcap.json" ] && cp -f "$R/translation/arabic/dropcap.json" "$P/" || true
echo deployed
