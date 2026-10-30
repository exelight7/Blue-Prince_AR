# Font and Arabic rendering research

Date: 2026-10-28 (Asia/Riyadh). Risk: 🟩 LOW inspection; proposed font/asset changes would be 🟨 MEDIUM. No original game files were changed. No game process was launched.

## Confirmed findings

- Unity serialized files report **2021.3.45f1**. TextMeshPro is present. The native font inventory covers resources.assets, sharedassets0–2.assets, globalgamemanagers.assets and Unity default resources: **12 embedded Font objects** and one unembedded Arial reference. Native Font objects were not found in sharedassets2.assets. Bundle/scene coverage must be reconciled with the main project inventory.
- **sharedassets1.assets:211**, `NotoNaskhArabic-Medium`, contains a 192,416-byte TTF. SHA-256: `04730ab4b326c5acbfb03d74533f352adfdfc4310c1758d21ee552968c0cc50e`. It contains 1,438 Unicode cmap entries: 253 in U+0600–06FF, 611 in Arabic Presentation Forms A and 141 in Presentation Forms B. Western digits, Arabic-Indic digits, printable ASCII Latin and all requested Arabic/lam-alef test characters are present. GSUB and GPOS tables exist. That does **not** prove the game invokes shaping or positioning.
- **sharedassets1.assets:244**, `NotoNaskhArabic-Medium SDF`, is an actual TMP_FontAsset, version 1.1.0. It references native Font **211**, material **43**, and atlas Texture2D **104** in the same file. Atlas population mode is **1 (Dynamic)**; dimensions 1024×1024, padding 9, render mode 4165. Multiatlas and clear-dynamic-data-on-build are disabled. The serialized character and glyph tables each contain **12 characters**, all Latin/symbols; there are **zero pre-baked Arabic characters**. Arabic glyph rasterization must therefore be demonstrated at runtime.
- Atlas **104** is a readable 1024×1024 Texture2D with format 1. Material **43**, `NotoNaskhArabic-Medium Atlas Material`, references fileID 5/pathID31. sharedassets1's fifth external is sharedassets0.assets; its Shader **31** parses as **TextMeshPro/Distance Field**. Preserve this material/atlas/shader relationship.
- **56 TMP_FontAsset objects and one TMP_Settings object** were found in loose resources/sharedassets0–2 copies. All **57 passed strict full-object parsing and byte-identical no-op serialization in memory**. No serialized asset file was written by the inspector. Full records, names, references, modes, atlas details and character sets are in `fonts/tmp_inventory.json`.
- Global TMP settings are **resources.assets:1168**. Their general fallback list is **empty**, and default font is fileID3/pathID428, LiberationSans SDF in sharedassets0.assets. Missing-glyph warnings are disabled (`m_warningsDisabled=1`), so absence of warnings is not a success criterion.
- **sharedassets1.assets:241**, `CharcuterieBlock SDF Gamertag`, lists Arabic font244 as its first fallback, followed by the other language fonts. Normal `CharcuterieBlock SDF` **242** has no fallback. Most other static styled fonts have no fallback. Arabic font presence does not imply ordinary menus/documents can reach it.
- Original game typography includes Charcuterie Block, Damned Architect, several serif/typewriter styles and many distinct handwritten document fonts. The full TMP inventory preserves these names and IDs. A global font replacement would lose meaningful stylistic distinctions; prefer the existing language font mechanism or targeted fallback/primary-font changes.
- Metadata research records `LocalizedText.TargetText`, `ChangeFontOnly`, `AlternativeFont`, `_originalFont` and `LocalizationLanguageAsset.AlternativeFont`. Their existence is confirmed; whether each UI path uses these fields correctly remains a runtime question. Metadata also contains `TMP_Text.isRightToLeftText` and `m_maxVisibleCharacters`; neither proves Arabic support or actual typewriter use.

## Parsing method and reproducibility

Run `python fonts/inspect_fonts.py` from the project with installed UnityPy/fontTools. It reads native fonts, writes only `fonts/original` references and `fonts/font_inventory.json`, and refuses to overwrite a reference containing different bytes.

Run `python fonts/inspect_tmp.py` after project-local `tools/vendor` and `backups/source` exist. This uses TypeTreeGeneratorAPI 0.0.10's **AssetsTools** backend. Call `get_nodes` with assembly **Unity.TextMeshPro without .dll**. Construct the UnityPy TypeTreeNode from its flat fields. The generated MonoBehaviour root's `m_Enabled` requires `m_MetaFlag |= 0x4000` to match the native three padding bytes before `m_Script`; only the depth-1 field is corrected. Every complete object must pass strict consumption and its no-op byte comparison. AssetRipper-generated font schemas failed strict parsing and are not accepted evidence.

`fonts/tmp_arabic_fontasset.json` preserves the complete strict Arabic TMP record. `fonts/tmp_candidates.json` is the earlier partial header-only survey of resources/sharedassets0–1; the later `tmp_inventory.json` supersedes it for conclusions.

## Offline probe results

Run `python rtl/probe_plain_arabic.py`. It verifies the extracted font hash and tests eleven plain-string samples, including all required examples, lam-alef forms, a diacritic sample and `مرحبا بك`. Arabic-reshaper plus python-bidi produce a reference presentation-form/visual-order variant. The test asserts zero missing logical and shaped glyphs and preserves sampled Latin/numeric runs.

| Check | Result | Meaning |
|---|---|---|
| Native TTF extraction | PASS | Reference font bytes and hashes recorded |
| Full TMP parsing | PASS | 57/57 full records consumed |
| TMP no-op serializer | PASS | 57/57 objects byte-identical in memory |
| Plain logical glyph coverage | PASS | Eleven samples covered by the TTF cmap |
| Plain shaped glyph coverage | PASS | Eleven offline reference samples covered |
| Unity glyph generation | NOT TESTED | Dynamic Arabic atlas must populate in game |
| Unity Arabic shaping / BiDi | NOT TESTED | Font tables or TMP direction flags do not establish this |
| Alignment / wrapping / clipping | NOT TESTED | Requires representative game screens |
| Arabic typewriter direction | NOT TESTED | Requires actual reveal path and runtime evidence |

This is a static/offline probe, **not a passed in-game Arabic rendering POC**. No screenshot is offered as game evidence. Pillow on this machine lacks RAQM; no substitute renderer image was generated.

## Least invasive next experiment

1. On a disposable playable copy only, target one known visible menu label through its verified text resource. Prefer the game's language `AlternativeFont` path if the parent investigation confirms the reference; otherwise explicitly use existing Arabic TMP asset244 on that one label. No new font dependency is necessary for this first test.
2. Test logical Unicode Arabic with existing native processing first. Verify joining, RTL, punctuation, Western numbers and an English key prompt separately. Record exact asset IDs/field changes and a real screenshot.
3. If native joining/BiDi fails, evaluate the smallest supported runtime solution before choosing preprocessing. The offline reference strings must **not** be blindly injected: TMP/game RTL processing could apply direction twice.
4. A preprocessing fallback would need markup-safe segments, placeholder preservation, measured per-line wrapping and a mapping from logical graphemes to visual glyphs. Never reverse a whole mixed string, and never reveal it by taking an LTR substring of visual-order text. Reveal must be tested separately; a full-line display can be considered only when the gameplay design permits it.
5. Keep original Latin text/materials and document style where possible. Check large Noto Naskh ascent/descent, diacritics, clipping, line spacing, autosizing, italic simulation and dynamic-atlas exhaustion. Multiatlas is currently disabled; do not change it without a targeted test.

## Official documentation consulted

TextMeshPro exposes `isRightToLeftText`, visible-character controls and overflow/layout properties. This API evidence establishes that these controls exist, not that the game correctly combines them for Arabic. [Unity TMP_Text 3.0 API](https://docs.unity3d.com/Packages/com.unity.textmeshpro@3.0/api/TMPro.TMP_Text.html).

Unity documents separate primary/local/global font fallback chains. That supports testing reference reachability rather than assuming a bundled Arabic font will be used. [Unity TMP fallback font assets](https://docs.unity.cn/Packages/com.unity.textmeshpro%402.2/manual/FontAssetsFallback.html).

Dynamic font assets retain a source-font link and generate atlas content as characters are used. The game's source/atlas linkage and actual runtime generation remain separate checks. [Unity dynamic font assets](https://docs.unity.cn/Packages/com.unity.textmeshpro%404.0/manual/FontAssetsDynamicFonts.html).

The embedded TTF's name-table license states SIL Open Font License 1.1. This is provenance metadata, not a complete redistribution package; no font was published or redistributed.
