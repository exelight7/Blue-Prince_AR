> **Historical.** Superseded by `HANDOFF.md` (2026-10-30), which has the current state, counts and next steps. The text below is kept as a record and may be out of date.

# Current project status

Updated: 2026-10-28. This file supersedes the earlier asset-repacking status (reports 001-003 stay as history).

## Approach (changed)
Asset repacking was abandoned. The localization now runs as a **BepInEx 6 IL2CPP plugin** (`plugin/BluePrinceArabic`) inside the disposable copy `runtime_test/`. Nothing in `D:\Games\Blue Prince` was modified.

- `TMP_Text.ParseInputText` is patched: the English `m_text` is swapped for pre-shaped Arabic (presentation forms, logical order, TMP `m_isRightToLeft = true`, LTR runs reversed) and restored afterwards, so game logic that reads `.text` is unaffected. TMP's own word wrap works (screenshot verified).
- `StringTypewriter.OnEnter` is patched to translate the base string before typing starts (reveal itself still unverified).
- Fonts: Arabic styles (Amiri regular/bold/italic, IBM Plex Sans Arabic medium/bold, Mirza, Katibeh, Rakkas, Lalezar unused; menu/display fonts use Plex Bold because Lalezar looked too heavy). All loaded fallbacks are patched up front every 2 s. `style <latin font substring>=<style>` and `gallery` commands allow live comparison. Aref Ruqaa/Jomhuria/Scheherazade/Harmattan cannot be used (decomposed glyphs, `tools/make_pf_font_hb.py` could not resolve single glyphs), generated with `tools/make_pf_font.py` so the presentation-form codepoints exist, registered as the first fallback of each game font asset according to the Latin font's style (`ArabicFont.StyleFor`).
- Translation data: `translation/arabic/batches/bNNN.json` -> `tools/merge_batches.py` -> `translation/arabic/ar.json`; `ar_patterns.json` (from `tools/make_patterns.py`) handles dates/counters; `keep.json` lists strings intentionally kept in English.

## Verified in the running game (screenshots in runtime_test/BepInEx/bpar)
Arabic shaping, lam-alef, mixed Arabic/English/digits/punctuation, multi-line wrapping, alignment flip, rich-text tags, case-insensitive matching, fonts loading from TTF files at runtime.

## Translation progress (2026-10-28, measured)
ar.json: 1,384 entries (196 kept as English on purpose: puzzle words/poems, element tables, fictional-language text) + 208 regex patterns (dates, counters, terminal account cards, e-mail headers, secret-floorplan prompt with {T1} room-name lookup).
Visible corpus (tiers 0-3) = 5,575 entries / ~78,900 words; translated so far ~1,370 entries / ~12,900 words (about 16% by words). All short UI/room/item strings are done; most of the remaining words are long documents (letters, books, memos: ~700 entries / ~40k words) plus tier 3 FSM texts.
Not in the static data: intro video subtitles (VideoText) - they never show up in untranslated.tsv; the hook probably misses how VideoTextWriter sets the text (see NEXT_STEPS).
