# Runtime font and POC evidence

28 October 2026. Scope: read-only inspection; writes confined to `research/runtime_fontmap`. No assets, original files, save data or runtime state changed by this role. No game launch or screenshots performed by this role. All conclusions below are static evidence unless explicitly marked unknown.

## Two preserved variants

| Field | A — logical | B — preshaped_visual |
|---|---|---|
| Asset | `build/poc/logical/BLUE PRINCE_Data/level1` | `build/poc/preshaped_visual/BLUE PRINCE_Data/level1` |
| Changed object IDs | 3357,3404,3411,3481,3500,3534,3535 | Same seven |
| Components | TextMeshPro/TextMeshProUGUI as recorded individually in JSON | Same components |
| Font/material | Scene external file2 = sharedassets1.assets, TMP244/material43 | Same |
| Text | Logical Unicode Arabic | Plain-line arabic-reshaper + python-bidi visual-order output |
| RTL field | `m_isRightToLeft=1` | `m_isRightToLeft=0` to avoid reversing visual data again |
| Shaping method | No explicit pre-shaping; native behavior unproved | Offline contextual forms |
| Fallback | Direct Arabic font assignment; no new fallback entries | Same |
| Other A/B differences | None beyond text/RTL | None beyond text/RTL |
| Expected result | Tests whether this game/TMP natively handles logical Arabic | Tests whether plain visual preprocessing improves joining and mixed order |

Neither expectation is a runtime result. A should be tested first because it preserves logical text and leaves shaping/BiDi to the game; B is a comparison only if A fails. Preprocessing is not established as a solution to dynamic wrapping, tags, substitutions or progressive reveal.

Strict schema parsing plus byte-identical in-memory no-op serialization passed for all 21 inspected component records (original + A + B). Full settings, ancestor activity and transforms: `poc_component_font_evidence.json`.

## Important deficiencies in the preserved seven

- **3357 is not the main NEW GAME label.** It is `NEW GAME TEXT 4 > SAVE SLOT 4 > SAVE FILES` and is initially inactive. The accessible main-menu NEW GAME label is **3568**.
- **3404** is under initially inactive `CALIBRATION`.
- **3535** is under `SAVE FOUND > BEQUEST MODE > MODES > NEW GAME SELECTION`, initially inactive. It should not require save selection/overwriting merely to test Arabic.
- **3481 Continue,3500 Quit,3534 Settings** are in active `MAINMENU LAYOUT > MAIN MENU`.
- **3411 Volume** is in `SETTINGS LAYOUT`, initially off but normally accessible through Settings.
- The preserved POC enables auto-size on3534, but inherited limits are **min18,max72** while original fontSize is **2.5**. This may enlarge the label over seven-fold. For a clean renderer baseline leave auto-size off, or set a deliberate suitable range such as1–2.5 for a separate sizing test.
- Inherited Latin display tracking is substantial: characterSpacing19.4 for Settings,33.1 for Volume,18.6 for Continue,9.9 for Quit; lineSpacing-55 for those labels. Large tracking can produce gaps and fit problems separately from Arabic shaping. Record it and change only the isolated POC when needed.

## Safer reachable matrix locations

`menu_settings_labels.json` maps all main-menu/settings labels and ancestors, including transforms, active states and actual serialized properties.

| Scene object ID | Original label | Reachability |
|---:|---|---|
|3568|NEW GAME|Main menu; inspect text without clicking|
|3481|CONTINUE|Main menu; inspect without continuing save|
|3534|SETTINGS|Main menu; safe navigation to Settings|
|3500|QUIT GAME|Main menu; inspect without quitting until finished|
|3380|CONTROLS|Settings layout|
|3411|VOLUME|Settings layout|
|3446|GRAPHICS|Settings layout|
|3527|CREDITS|Settings layout|
|3456|RETURN|Settings layout; safe return navigation|
|3429|SAVE DATA|Settings layout; do not click for the POC|

Recommended first seven IDs:3568,3481,3534,3500,3411,3446,3456. Place the required natural Arabic, lam-alef, numeric and mixed examples among these temporary labels. A long wrapping probe needs a designated measured text rectangle or a reachable helper panel; a tiny menu label is a poor wrapping benchmark. Available helper3563 is under old `MOUSE SETTINGS(new)` with RectTransform10.2484×1.5725 and y-1002.14;3539 is under the newer controls layout with similar bounds and y-1003.96. Their actual visibility needs runtime observation; coordinates alone do not establish screen location.

Menu label RectTransforms have sizeDelta0 and anchors0, but nonzero TMP margins (left13.1496,top4.4845,right-20.0307,bottom-15.2609). Do not claim zero displayed width or clipping from sizeDelta alone: TMP/world transforms and negative margins affect the available region.

## Actual TMP settings

All seven preserved POC objects use actual serialized names `m_fontAsset`, `m_fontSize`, `m_HorizontalAlignment`, `m_VerticalAlignment`, `m_isRightToLeft`, `m_enableWordWrapping`, `m_overflowMode`, `m_isRichText`, `m_characterSpacing`, `m_wordSpacing`, `m_lineSpacing`, `m_text`. Raw alignment values are retained in JSON rather than guessed from screenshots. `m_maxVisibleCharacters` is not serialized in these component schemas, so its runtime value is **UNKNOWN**, not zero or unlimited by inference.

The ordinary main/settings labels have fontSize2.5, horizontalAlignment2, verticalAlignment512, wrapping1, overflowMode0, richText1; values are raw serialization enums. Original calibration3404 instead has fontSize3, horizontal2/vertical256, spacing-2/0/33. Original mode description3535 has fontSize2.6, horizontal1/vertical256, spacing-5.97/7.39/29.83. The POC changes font/material/text/RTL and the one auto-size flag; it does not normalize these different layouts.

## Font dependency graph

- Main menu labels3568/3481/3534/3500 and settings labels3411/3446/3456 -> sharedassets1 **242 CharcuterieBlock SDF** -> empty fallback table -> no automatic Arabic route.
- Preserved hidden NEW GAME3357 -> sharedassets1 **256 VersicaSerif SDF**, empty Arabic route; description3535 uses font258; calibration3404 uses sharedassets0 **430 Rank Font**.
- Gamertag3399 -> sharedassets1 **241 CharcuterieBlock SDF Gamertag** -> first fallback **244 NotoNaskhArabic-Medium SDF** (plus other script fonts).
- Global TMP_Settings resources1168 -> default sharedassets0 **428 LiberationSans SDF**; global fallback list empty.
- Both POC variants bypass that gap: each targeted UI component -> sharedassets1 **244** -> source native Font **211**, material **43**, atlas Texture2D **104**. Arabic244 has no own fallback entries.

Exact reference graph: `font_dependency_graph.json`.

## Noto Naskh Arabic details

CONFIRMED TMP asset244, version1.1.0, dynamic populationMode1, atlas1024×1024, padding9, renderMode4165, multiatlas disabled. Initial glyph and character tables each contain12 entries, with zero Arabic or presentation-form entries. Material43 is `NotoNaskhArabic-Medium Atlas Material`, references shader sharedassets0:31 (TMP Distance Field); atlas104 is readable format1.

CONFIRMED source Font211: NotoNaskhArabic-Medium,192,416 bytes;1438 cmap code points;253 Arabic block entries;611 presentation-A and141 presentation-B entries; GSUB and GPOS; Latin ASCII,Western digits,Arabic-Indic digits and required sample punctuation covered. Its data is recorded in `fonts/font_inventory.json` and `fonts/tmp_arabic_fontasset.json`.

UNKNOWN until observed: runtime dynamic generation for logical/presentation glyphs, atlas capacity behavior, native joining, actual BiDi, punctuation layout, wrapping, clipping and reveal. Font GSUB/GPOS presence does not prove TMP invokes Arabic shaping.
