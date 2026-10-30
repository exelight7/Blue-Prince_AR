# HANDOFF - Blue Prince Arabic localization

Rewritten 2026-10-30 from the files and logs (the older handoff was stale). If anything here disagrees with the files, trust the files and fix this document.

The user writes Arabic: reply in Arabic. Keep token use low: do not print huge logs or whole big files; summarize.

## 1. What this is
Full Arabic (RTL, shaped) localization of **Blue Prince** (Steam, Unity 2021.3.45f1 IL2CPP, game 1.0.5.0) as a **BepInEx 6.0.0-be.791 IL2CPP plugin**. It patches TextMeshPro at runtime and never edits the original game files. An earlier attempt that repacked game assets was abandoned (fragile, 2.5 GB, no dynamic text).

## 2. State (2026-10-30)
- `translation/arabic/ar.json`: 5,228 entries (737 identity = deliberately English, 112 with `{ICON}`), 211 regex patterns, `keep.json` 812, `dropcap.json` 128, 101 batch files. `merge_batches.py`: 0 rejects. `python tools/show_docs.py 0` and `show_docs.py 0 3`: 0 left (tiers 0-3 done; tier 9 = internal FSM names, only translate what the runtime log shows).
- Installed in the author's real game and the release package matches it: `release/BluePrince_Arabic/` (246 files, ~79 MB, manifest.json with SHA256 of every file).
- Verified by the user in the real game: letter joining after the lam-alef fix, the intro (zoomed video, Arabic over the picture), menus and the Settings title. Everything else was verified in the disposable copy `runtime_test/` by screenshots, or not yet seen in the real game (see section 6).

## 3. Rules (do not break)
- Never modify the original game folder. The only write to it is `release/BluePrince_Arabic/install.ps1` (reversible with `uninstall.ps1`).
- Do not launch the game unless the user clearly allows it: the user watches the window and takes their own screenshots. Say so before killing or relaunching `runtime_test`. Never delete saves or profiles.
- No git push, install of software or deletion of data unless asked.
- Puzzle words and keys stay English (`keep.json`, reasons in `translation/work/b_exceptions.md`): Erajan words, gem-box logic puzzles (`<size=N>` ALL-CAPS BOX/GEMS/STATEMENT lines), riddle poems, admin keys like `[JoneS]`, the network password SWANSONG.
- Glossary (keep consistent): هربرت س. سنكلير, ماونت هولي, سايمون ب. جونز, ريدينغتون, فين أريس, آرتش أريس, إيراجا/إيراجي, أورينديا, Manor = قصر, Entrance Hall = ردهة المدخل, Solarium = غرفة الشمس, Drawing Room = غرفة الجلوس, draft = اختيار, draw floorplans = سحب, ALLOWANCE = الحصة, Terminal = الطرفية/جهاز, keycard = بطاقة المفتاح, Contraption = الابتكار المرتجل. No tashkeel except fathatan.
- Tooling quirks: the Bash tool halves backslashes in heredocs, so write JSON/regex/C#/ps1 with Write/Edit. Use `python -X utf8` for Arabic output. Keep tool calls under ~1 minute.

## 4. Repo map (paths relative to the repo root)
| Path | Content |
|---|---|
| `plugin/BluePrinceArabic/` | C# plugin. `Plugin.cs` (Runner: hotkeys, `cmd.txt` debug commands), `Patches.cs` (`Patch_ParseInputText`, `Patch_Typewriter`, `TextOps`: alignment flip, spacing zeroing, shrink-to-fit, render cache), `Shaper.cs`, `Translator.cs`, `ArabicFont.cs`, `IntroSubs.cs`, `DropCaps.cs`, `IconGaps.cs`, `Layout.cs`, `DocFont.cs` |
| `translation/arabic/` | `batches/bNNN.json` (source -> Arabic), `ar.json` (merged output), `keep.json`, `ar_patterns.json`, `dropcap.json`, `tagwords.json`, `intro_subs.tsv`, `intro_cards.tsv`, `layout.tsv` |
| `translation/work/` | `corpus.json` (visible game text, tiers 0-3 and 9), `prefix_bNNN.json`, `b_exceptions.md`, `rejects.json`, `warnings.json` |
| `tools/` | `show_docs.py`, `t3list.py`, `next_batch.py`, `tr_prefix.py`, `merge_batches.py`, `make_patterns.py`, `build_corpus.py`, `deploy_plugin.sh`, `build_release.py`, `gamectl.py`, `enter_game.sh`, `release_src/` (install.ps1, uninstall.ps1, README_AR.txt) and older extraction tools |
| `release/BluePrince_Arabic/` | install package: `payload/` (BepInEx + plugin + fonts + data), `manifest.json`, `install.ps1`, `uninstall.ps1`, `README_AR.txt` |
| `fonts/arabic/` | Arabic fonts (`pf/` = presentation-form versions made by `tools/make_pf_font.py`) |
| `tests/ShaperCheck/` | `dotnet run` compiles `Shaper.cs` alone and asserts exact codepoints; add a word when joins look wrong |
| `state/`, `docs/`, `rtl/`, `reference/`, `research/` | status notes, older engineering notes (`docs/ARCHIVE_ENGINEERING_NOTES.md`), RTL research, the original user requests, small research data |
| `docs/ai-memory/` | the author's AI memory notes (workflow and batch gotchas), saved before a PC reformat |

Not in the repo (too big or game data): `runtime_test/` (copy of the game), `backups/`, `extracted/`, `build/`, `fonts/original/`, `translation/source/`, `research/asset_index/`, `tools/vendor/`. See section 8 to recreate what you need.

## 5. How it works
- `Patch_ParseInputText` swaps the English `m_text` for shaped Arabic (presentation forms in logical order, TMP `m_isRightToLeft = true`, Latin/digit runs stored reversed, brackets mirrored, tags kept atomic, diacritics stripped) and restores it afterwards, so game logic never sees Arabic. `Patch_Typewriter` translates `StringTypewriter.OnEnter` base strings.
- `Translator.Resolve` order: exact -> wrapper (outer tags/whitespace kept) -> lowercase -> regex patterns (`$1`, `{T1}`) -> chained `*` patterns -> `TagLine` (comma-separated room-type headers via `tagwords.json`). An identity entry means intentionally English. Misses are logged to `BepInEx/bpar/untranslated.tsv` (flushed every 2 s).
- Fonts: TMP does no GSUB shaping, so fonts need presentation-form cmap entries. Fallbacks are patched on ALL loaded font assets up front (every 2 s); patching lazily showed boxes. Styles in `ArabicFont.StyleFor`: serif = Amiri, sans/display = IBM Plex Sans Arabic Medium/Bold, hand = Mirza (85% size), script = Katibeh, quirky = Rakkas.
- Layout lessons: Latin letter spacing/negative leading breaks joins, so spacing is zeroed for Arabic; only Left flips to Right (menus anchored right stay put); single-line boxes keep alignment and shrink to fit (min 55%); lookups keep leading/trailing `\n`; Arabic wraps to fewer lines, so pages with separate TMPs under a paragraph need extra blank lines. `layout.tsv` holds per-plate size factors.
- `DropCaps.cs`: "You Found/Bought/Dug Up" titles are split over several TMP pieces; `dropcap.json` has one full Arabic title per group and the biggest piece shows it while the others are hidden. `IconGaps.cs`: sentences with a gap for an icon use `{ICON}` in the translation and the icon objects are moved into the slots after layout.
- `IntroSubs.cs` (intro video `_INTRO`, 194.9 s, `VIDEO CAM/Cinematic Player`, MaterialOverride): the English subtitles are burned into the video's letterbox bar, so while the clip plays the video quad is scaled x1.36 (local X and Z only, restored whenever the intro is not playing) so the bar leaves the screen, and the Arabic line (from `intro_subs.tsv`, 20 lines, 45-153 s, Arabic in batch b029) is drawn over the picture with an outline. `intro_cards.tsv` covers one big caption inside the picture with a soft plate and draws Arabic on it. If the user dislikes the crop, the agreed fallback is Arabic at the top of the screen with the English left at the bottom, no zoom.
- Shaper bug fixed 2026-10-29: after a لا/لأ/لإ/لآ ligature the swallowed alef must keep `Src` (only `S` is blanked), otherwise the next letter takes a medial/final form. `tools/preview_intro.py` renders with arabic_reshaper, so it cannot catch Shaper.cs bugs; use `tests/ShaperCheck`.

## 6. Open items
1. Drop-cap / item-description fragments and icon-gap sentences: implemented (`DropCaps`, `IconGaps`), only partly seen in the real game. Check after play.
2. Typewriter reveal (`Patch_Typewriter`): patched, never verified on a real typewriter text (Antechamber note, entrance tip).
3. Textures with English text (map, signs): not done. `research/texture_review.json` lists candidates; plan was a texture swap by name at load time. Letter atlases stay English. Document risky ones instead of forcing them.
4. Clock-face roman numerals and a few fixed strings in `untranslated.tsv`: probably leave.
5. Behaviour at non-16:9 resolutions is unverified.
6. Playtime pattern `^(\d+)h (\d+)m$` now maps to `$1س $2د` in `ar_patterns.json` (was reported in the wrong visual order); not yet confirmed on screen.
7. After the user plays: read `D:\Games\Blue Prince\BepInEx\bpar\untranslated.tsv` and `LogOutput.log` (grep error|exception) and translate what is visible.

## 7. Workflows
Translate (long texts):
1. `python tools/show_docs.py 12 [tier]` prints the next untranslated documents (run from `tools/`; it reads `../translation/work/corpus.json`).
2. Write `translation/work/prefix_bNNN.json` as `{source prefix: arabic}`, shorter keys first.
3. `python tools/tr_prefix.py translation/work/prefix_bNNN.json bNNN` writes `translation/arabic/batches/bNNN.json`.
4. `python tools/merge_batches.py` validates and rebuilds `ar.json`; zero rejects required.
Validator rejects: tag multiset mismatch, digit mismatch (use digits when the source has digits), `??` or control characters (use ؟), lost `[KEY]`/`{abc}`. `tr_prefix.py` uses plain `startswith` and gives every hit the same Arabic, so very short keys (item names, glossary terms) belong in an exact-key batch to avoid clobbering longer sources. `show_docs.py` hides a source already present in any batch or `keep.json`. `b901_quality.json` and `b999_fixes.json` sort last and override everything else.

Build and deploy to the test copy: `sh tools/deploy_plugin.sh ar.json` (aborts with BUILD FAILED on compile errors). Then `python -X utf8 tools/build_release.py` rebuilds `release/BluePrince_Arabic`, and `install.ps1` (game closed) installs it into the real game.

Test copy (only with the user's permission): `sh tools/enter_game.sh`, then `python tools/gamectl.py cmd "scan" "shot name" "video" "trace" "dump" "reload"`. In game: F10 toggle, F11 reload, F12 screenshot. `tools/gamectl.py` and some tools hard-code `D:\Games\Blue Prince_AR\runtime_test`; edit `ROOT` if the project lives elsewhere.

## 8. Recreating the environment on a new machine
1. Install the Steam game, .NET SDK 6+ (build uses net6.0), Python 3.12 with `arabic-reshaper`, `python-bidi`, `Pillow`, `numpy`, `fontTools` (and `UnityPy` only for the old extraction tools).
2. Copy the game folder to `<repo>/runtime_test` (or use `tools/prepare_runtime.py`), then run `powershell -ExecutionPolicy Bypass -File release/BluePrince_Arabic/install.ps1 -GameDir <repo>\runtime_test`.
3. Launch `runtime_test` once so BepInEx generates `BepInEx/interop` (1-2 minutes). The plugin csproj references those DLLs through `GameRoot` (default `..\..\runtime_test`; override with `dotnet build -p:GameRoot=<game dir>`).
4. `sh tools/deploy_plugin.sh ar.json` should now build and stage the plugin.
5. Data that was left out can be regenerated from the game: `python tools/project.py inventory|snapshot|extract`, `tools/extract_text.py`, `tools/extract_playmaker.py`, `tools/extract_arrays.py`, then `tools/build_corpus.py` (TypeTreeGeneratorAPI 0.0.10 from PyPI is needed by the extraction tools). You normally do not need this: `translation/work/corpus.json` is already in the repo.

## 9. Failed approaches (do not retry)
Static asset repacking with UnityPy; searching bundles or hooking SetText for the intro subtitles (they are video pixels); HarfBuzz presentation-form fonts for Aref Ruqaa, Jomhuria, Scheherazade and Harmattan (decomposed, unusable); Lalezar for display (too heavy, Plex Bold used); lazy fallback patching (boxes); Latin spacing on Arabic; flipping alignment on single-line labels; Katibeh for dArchitect (overlapping lines); a black overlay bar on the intro (replaced by the zoom).

## 10. Next session prompt
```
اقرأ HANDOFF.md أولًا ثم تابع من قسم Open items.
- افحص فقط الملفات الضرورية ولا تعد اكتشاف ما أُثبت في الـHandoff.
- إن خالف الـHandoff حالة الملفات فثق بالملفات وحدّث HANDOFF.md.
- لا تشغّل اللعبة دون إذني الصريح ولا تعدّل ملفات اللعبة الأصلية.
- اجعل استهلاك tokens منخفضًا وردّ عليّ بالعربية.
```
