# Blue Prince Arabic localization architecture

Date: 2026-10-28, Asia/Riyadh. Original installation is read-only. Confidence labels describe evidence, not expectations.

Current runtime update: report_003.md supersedes earlier untested status for sampled static text. The current user instruction is to continue offline without launching the game.

## Confirmed build

- Unity **2021.3.45f1**: serialized-file headers and `globalgamemanagers` BuildSettings.
- Application version **1.0.5.0**, company **Dogubomb**, product **BLUE PRINCE**: PlayerSettings. This is the inspected local build, not a claim about the newest release.
- Windows AMD64 / PE machine `0x8664`: game executable, UnityPlayer and GameAssembly.
- IL2CPP: GameAssembly.dll plus `il2cpp_data/Metadata/global-metadata.dat`, metadata format **31**. The metadata format number differs from the engine version.
- Scenes: `level0` = FurySDK Initialize; `level1` = Main Menu; `level2` = Mount Holly Estate (BuildSettings scene order).
- Loose Unity serialized files and `.resS` / `.resource` streams; five Addressables UnityFS bundles. All five bundle containers parse with installed UnityPy. Header format 8, flags `0x243`, block-info compression code 3. No encryption key was required for these containers; this does not prove every embedded payload is unencrypted.
- Addressables version **1.19.19** from `StreamingAssets/aa/settings.json`.

## Text and localization

CONFIRMED: TextMeshPro components, Unity UGUI/Canvas, and extensive PlayMaker FSMs. Custom namespace `SummertimeMadness.Localization` defines a key database, language database, manager and LocalizedText components. `sharedassets1.assets` has `Key_test:237`, `en-us:238`, `it-it:239`, `Locale:240`. The English table has **74** key/value entries, including action prompts. It is not the whole game's text.

CONFIRMED: a second `BluePrince.Language` family defines language arrays, upgrades and video text. Presence is established by metadata; active serialized instances and complete coverage need correlation. The EN/NL enum does not prove a working language-selection feature. English and Italian assets do not prove complete Italian localization.

CONFIRMED: timed subtitle declarations connect `VideoText.text`, `VideoTextData.startTime/endTime`, `VideoTextWriter`, a VideoPlayer/VideoClip and TMP text. Native VideoClip assets occur in sharedassets1/2 and the video bundle. Native AudioClip assets exist; no separate FMOD/Wwise bank files were found in the complete file inventory. UNKNOWN: audio/subtitle coverage, timing units, video-embedded English, dialogue triggers and fallback behavior.

CONFIRMED: localized components can change font, upper-case strings and use params. Ordinary UI also stores text directly in TMP components; FSMs and array proxies contain additional data. Managed literals include possible hardcoded text, but their visibility and callsites are unresolved. No compiled code was changed.

## Fonts and Arabic

CONFIRMED: 12 embedded Font objects, 56 TMP font assets, one TMP settings object, and an unembedded Arial reference. Style fonts include Charcuterie and other display/handwriting faces; see `fonts/tmp_inventory.json` for every asset/reference/material/atlas.

CONFIRMED: sharedassets1 Font **211**, `NotoNaskhArabic-Medium`; TMP font **244**, `NotoNaskhArabic-Medium SDF`; material **43**, referencing the TMP Distance Field shader. Native TTF covers required logical and presentation-shaped samples, Latin, Western digits and Arabic-Indic digits. GSUB/GPOS exist.

CONFIRMED: Arabic TMP font is dynamic, uses its embedded source Font, has a 1024x1024 atlas with only 12 initial Latin/symbol characters and no Arabic/presentation glyphs, and has multiatlas disabled. Global TMP fallback list is empty. Only the Gamertag Charcuterie variant includes Arabic as its first fallback. Normal UI is not automatically connected to Arabic.

CONFIRMED by sampled runtime screenshots: logical Arabic with TMP RTL did not shape correctly and reversed27 to72. Pre-shaped visual Arabic with TMP RTL disabled rendered joined forms,27/100, English E/Blue Prince, lam-alef forms and punctuation correctly in the sampled static cases. Full Unicode/rich-text/dynamic coverage, diacritic placement and progressive reveal remain UNKNOWN. No recognizable RTLTMPro/ArabicSupport/HarfBuzz names were found in the metadata name table; absence is not proof of absence of all support.

## Extraction and repacking decision

Use local **UnityPy 1.25.3** for containers/native objects and the official **TypeTreeGeneratorAPI 0.0.10** for stripped managed schemas. The dependency was introduced only after installed tools lacked schemas; its wheel SHA-256 was checked against PyPI, and installed only under `tools/vendor`. It reads copied GameAssembly and metadata as data; it does not execute the game assembly.

Important integration findings:

1. Call the native backend with extensionless assembly names. UnityPy's convenience wrapper adds `.dll`, which fails for the tested AssetsTools path.
2. Correct the generated native MonoBehaviour enabled-byte alignment before building the node tree. Validate original script references against the common header.
3. Require strict complete-byte reads and no-op byte equality for any object to be changed. Generated schemas are not automatically trustworthy. Generic-array/schema failures remain explicitly tracked.
4. Preserve each ID, file, object path ID, field path, source and context. Do not merge identical strings across objects or treat identifiers as visible text.
5. Modify only schema-decoded fields in copied assets. The seven-object level1 POC passes reload, unchanged-object bytes and deterministic second-save checks. This is **offline repacking evidence**, not proof that Unity will load or render it correctly.

No loader is installed; no EXE/DLL is patched; no original file is replaced. Addressables repacking/CRC/catalog updates are not yet validated. Any future need for executable modification stops that branch for documentation first.

## Reveal and layout gate

CONFIRMED: 535 enabled StringTypewriter references across191 FSMs exist in level2. The source chain314189 maps a base string through typing_text to TMP297408.text. Menu injection using existing serialization types was valid at the asset level but did not yield a reliable progressive control at runtime, even with English. Reveal direction/grapheme indexing remain UNKNOWN.

CONFIRMED: TMP automatic wrapping of a whole visual-order paragraph reordered its logical lines. The tested remedy is logical word wrapping first, then shaping/BiDi per explicit line with TMP autowrap disabled. A17-em measured paragraph with a1.5 font cap fit the recorded menu area. This is a calibrated static probe, not a general layout guarantee. tools/arabic_plain.py preserves diacritics in data and rejects tags/variables/escapes and overwide tokens; placement of diacritics and richer runtime inputs remains unverified.

The preferred current build is build/arabic_menu_poc: eleven meaningful labels rebuilt from untouched level1. Diagnostic phrases and added FSMs are absent. Only eleven existing TMP objects differ;4,249 other object payloads match original. It is staged in runtime_test and was not launched after the user's offline-only instruction. Static strategy E is supported; overall dynamic/game-wide strategy remains G pending valid evidence. Never reverse whole strings or globally mirror the interface.

Primary implementation references consulted: [UnityPy README](https://github.com/K0lb3/UnityPy), [TypeTreeGeneratorAPI source](https://github.com/UnityPy-Org/TypeTreeGeneratorAPI), [verified wheel metadata](https://pypi.org/project/TypeTreeGeneratorAPI/), [IL2CPP metadata declarations](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/MetadataClass.cs). Local evidence takes precedence over generic engine assumptions.
