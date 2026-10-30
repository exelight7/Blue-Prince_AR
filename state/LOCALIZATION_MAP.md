# Localization map

Updated: 2026-10-28T10:33:16+03:00. CONFIRMED means parsed evidence; visibility is still subject to gameplay validation.

## Normalized direct text

`translation/source/strings.json`: 20,815 nonempty occurrences / 4,850 distinct source values. Includes repeated objects, single letters, punctuation, debug UI and possibly unused content. Not an approved translatable count. All 20,730 TextMeshPro and 147 TextMeshProUGUI instances in the scanned loose scene/asset files parsed. Empty component values are not included as strings.

ID format: `container:path_id:field_path`. Context is GameObject name or asset name. Each row preserves Source, blank Arabic, File, Category, Notes and Status. `SOURCE_VERSION.json` records application version and source-container hashes. Do not deduplicate contextual occurrences.

Example: `level1:3357:m_text` -> `NEW GAME` -> Main Menu scene -> GameObject-resolved component; POC Arabic `لعبة جديدة`. `level1:3404:m_text` contains a multiline calibration message and `[ENTER]`; token and line-break counts are preserved in the POC.

## Key database and bindings

`sharedassets1.assets:238` (en-us, tag en) has74 English entries. `:239` has Italian data; `:237` defines74 keys; `:240` references key/language assets. All are exported in `extracted/original/structured/sharedassets1.assets/`.

164 LocalizedText components are mapped in `research/localized_text_bindings.json`. Relation: `LocalizationKey -> locale Entries.Key/Value -> LocalizedText -> TargetText or runtime component -> scene GameObject`. Some TargetText references are null; a runtime resolution must be observed, not invented. One binding key `UI.SETTINGS.CONTROLS.STROLL_SUB` is present even though the small table is not demonstrably complete. Missing-key behavior is UNKNOWN.

## PlayMaker

Alternate AssetStudio schemas read all 11,973 FSMs and 37 templates with strict full reads and byte-identical no-op serialization: 12,010 PASS, 0 errors. The first AssetsTools pass logged11,815 errors; those records remain as historical evidence, not the current FSM failure count. The key-list failure was also recovered.

`translation/source/playmaker_candidates.json` contains 141,161 candidate occurrences / 4,251 distinct values from string variable defaults and constant FsmString action parameters. Many are save keys, filenames, identifiers, puzzle controls or invisible values: **do not translate this file automatically**. Variable names, state names and action identifiers are context only, not patch targets. Enabled serialized typewriter/video action references are in `research/serialized_text_actions.json`; this proves asset references, not execution during gameplay.

All 748 array proxies also passed strict parsing and exact no-op equality using AssetStudio, recovering the remaining172 first-pass errors. Their 2,686 string occurrences remain candidates in `translation/source/array_candidates.json`, not approved visible strings. Historical schema errors are fully recovered for this selected set of classes. Nested BluePrince.Language data, subtitle arrays, custom game classes and managed constant callsites still need additional mapping.

## Coverage by category

| Category | Evidence / current source | Coverage |
|---|---|---|
| menus, settings, button prompts, system messages | level1 TMP, locale ACTIONS/UI keys, FSM candidates | Confirmed source candidates; active screen review pending |
| gameplay UI, tooltips, tutorials, objectives, item/room names and descriptions | level2/sharedassets2 TMP and FSM string values | Contextual classification incomplete |
| dialogue / subtitles | VideoText/VideoTextData/VideoTextWriter declarations plus video asset refs and serialized actions | Text/timing data-to-screen mapping incomplete |
| lore, books, notes/documents | Many TMP components and FSM values; some texture art | Context/gameplay review pending |
| map labels / puzzle text | TMP plus image samples worldmap1, LETTERSatlas, 8letter, 5letter | Text-bearing images confirmed; puzzle adaptation required |
| achievements | No locally visible text resource identified | UNKNOWN; do not change platform services |
| credits | Not conclusively mapped to a live screen | UNKNOWN |
| image text | 1,043 textures indexed, six sampled | Partial; see texture_review.json |
| video-embedded text | 25 clips indexed | Frame review not performed |
| fonts | 12 embedded native fonts,56 TMP fonts,1 settings | Complete identified-font static inventory; runtime coverage unknown |
| hardcoded strings |15,088 managed literals with offsets; selected visibility-unresolved candidates | Not a translation count; no executable changes |

The total final translatable count is **UNKNOWN**. The current estimate is several thousand distinct text values, with additional dynamic/image/subtitle content and substantial contextual duplication. This estimate must not be treated as complete coverage.
