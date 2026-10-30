> **Historical.** Superseded by `HANDOFF.md` (2026-10-30), which has the current state, counts and next steps. The text below is kept as a record and may be out of date.

# Next steps

Updated: 2026-10-28.

1. **Fonts**: review each style in game (use `scan` which now prints font asset + style per text object) and adjust `ArabicFont.StyleFor`; consider Amiri-Italic for the italic serif (Versica) subtitles; tune glyph scale if Arabic looks smaller than Latin.
2. **Intro subtitles** (finding: burned into the `_INTRO` video; no VideoTextWriter/TMP exists). Built `IntroSubs.cs` overlay: black bar over the bottom 12.8% + Arabic line timed by the clip clock, data in `translation/arabic/intro_subs.tsv` (20 lines, 45-153s) with Arabic in `batches/b029.json`. Deployed to runtime_test but NOT yet verified in game: relaunch, profiles menu, empty slot (slots 1-3 now used: delete one via the delete-save button), watch 45-153s, check bar covers English, font/size, timing margins (-0.3/+0.3s). Bar must NOT show outside subtitle windows (picture fills frame after 153s). Tools: `gamectl.py cmd trace` (frame sampler), `trace_strips.py`, `group_strips.py`.
3. **Drop-cap names**: many item/headline strings are split into a big first letter TMP + remainder TMP (e.g. `ODE    ELECTION`, `ROPHY`). Plan: `dropcap` dictionary in the plugin that puts the whole Arabic name into the remainder object and disables its single-letter siblings. Currently these remainders are in `keep.json`/identity.
4. **Fragments**: Spiral of Stars rule sentences, `A SMALL DATA` item descriptions and similar are built from several TMPs; they need context-specific word order (see `translation/arabic/keep.json` TODO group).
5. **Translate the rest**: `python tools/next_batch.py 150` (tier 2/3 long texts), validate with `python tools/merge_batches.py`, deploy with `sh tools/deploy_plugin.sh ar.json`.
6. **Typewriter / reveal**: verify on a real typewriter text (Antechamber note, entrance tip) now that the Harmony patch exists.
7. **Textures with text** (map, signs) and video-embedded text (intro will, credits) cannot go through TMP; decide per item.
8. **Release**: write `install.ps1` / `uninstall.ps1` for the real game folder (BepInEx + plugin + fonts + ar.json); only after the user approves installing into `D:\Games\Blue Prince`.

Test loop: `sh tools/enter_game.sh` (kill, deploy, launch, new game, skip intro) then `python tools/gamectl.py cmd "scan" "shot name"`.

## Long-document workflow (works well)
`python tools/show_docs.py 12` prints the next long documents -> write `translation/work/prefix_bNNN.json` ({source prefix: arabic}) -> `python tools/tr_prefix.py <that file> bNNN` -> `python tools/merge_batches.py` (reports rejects) -> `sh tools/deploy_plugin.sh ar.json`. Variants that differ only in tags/numbers need their own longer prefix. Staged terminal texts use chained '*' patterns in tools/make_patterns.py. Open rejects: indicator-light notes (b028) and a 'Most historians ... Ajera' variant.

## Checkpoint (session 2026-10-28, plan approved: finish translation then install; do NOT run the game before install)
- ar.json 1,576 entries; batches b029-b039 done; tier-2 docs left: 509 (33.4k words), tier 3: 827, tier 9: 1,990 (check with `python tools/show_docs.py 0 <tier>`).
- Offline intro preview: `python -X utf8 tools/preview_intro.py` (all 20 lines fit, all English frames covered). IntroSubs hardened (aspect-based bar, fade, hides on skip). Diag.cs removed.
- tr_prefix.py now keeps a variant's own trailing whitespace. Substitution builders for icon-gap texts live in the session scratchpad pattern (see realm.py/camp.py approach: replace pieces on the exact corpus source).
- Python heredocs through the Bash tool halve backslashes: write JSON/C#/py with the Write/Edit tools when they contain `
` or regex.
- Still TODO per plan: fix playtime pattern, b028 rejects, dropcap map, fragments, textures, release package + install.ps1/uninstall.ps1, install into the real game (user asked for it after the work is finished).

## Checkpoint 2 (later the same day)
- ar.json 2,369 entries (225+148 kept as English). Tier 2 long documents: 0 left. Tier 3 sentence-like left: ~230 (room-description cards, upgrade effect clauses). Tools: `python -X utf8 tools/t3list.py N` lists them; write `translation/work/prefix_bNNN.json` (sorted shortest key first) -> `tr_prefix.py` -> `merge_batches.py`.
- Gem-box logic puzzles (`<size=N>` ALL-CAPS BOX/GEMS/STATEMENT lines) are kept English (letter-based clues); do NOT regenerate prefix_b039/b041/b076/b077 batches (they still hold old translations of some) - they are overridden by keep.json at merge time.
- Room-type header lines ("Drafting, Blueprint, Dead End") are translated by `TagLine` in Translator.cs from `translation/arabic/tagwords.json`.
- Release: `python tools/build_release.py` -> `release/BluePrince_Arabic` (payload 243 files, 79 MB, manifest, install.ps1, uninstall.ps1, README_AR.txt). Installer/uninstaller tested on a fake game folder (restores backed-up files, removes everything it added). NOT yet run against `D:\Games\Blue Prince`.

## Checkpoint 3 - INSTALLED into the real game (2026-10-28)
- Installed with release/BluePrince_Arabic/install.ps1 (243 files; manifest BluePrinceArabic_installed.json in the game folder). 56 original files verified unchanged (size + mtime); all installed files match payload SHA256. Uninstall: release/BluePrince_Arabic/uninstall.ps1.
- ar.json 2,864 entries (503 kept English: puzzle keys, riddles, gem-box logic). Tier 2 long documents: 0 left. Tier 3 sentence-like: done (the rest are internal FSM names). Tier 1: about 116 internal left. Tier 0 fragments (item description openers such as "A SMALL DATA") and tier 9 internal names remain.
- NOT yet seen in the real game (the user asked not to run it before install): intro subtitle overlay, TagLine headers, and every text added today. First launch = BepInEx interop generation, 1-2 minutes.
- After the first run: read BepInEx/bpar/untranslated.tsv, translate what is visible via the prefix_bNNN workflow, `sh tools/deploy_plugin.sh ar.json`, `python tools/build_release.py`, then rerun install.ps1 (or copy ar.json into the game plugin folder).
- Still open: drop-cap names (ODE ELECTION, ROPHY), item-description fragments (tier 0), typewriter reveal check, textures with text (map, signs), playtime pattern "0h 3m" visual order.
