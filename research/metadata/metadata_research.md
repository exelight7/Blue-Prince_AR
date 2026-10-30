# IL2CPP localization and subtitle metadata research

Date: 2026-10-28 (Asia/Riyadh). Risk: 🟩 LOW, read-only parsing. No executable code was loaded, run, patched or disassembled. Original game files were only read. Project ownership for this research: `research/metadata/`.

## Method and reproducibility

Input: `D:\Games\Blue Prince\BLUE PRINCE_Data\il2cpp_data\Metadata\global-metadata.dat` (13,695,464 bytes).

Run with the existing local Python installation:

```powershell
python research/metadata/inspect_metadata.py "D:\Games\Blue Prince\BLUE PRINCE_Data\il2cpp_data\Metadata\global-metadata.dat"
python research/metadata/inspect_video.py
```

The parser validates the magic, exact supported version, section bounds, record divisibility, UTF-8 names/literals, image-to-type ranges, method declaring types and field ranges. It stops on inconsistent data. These are metadata declarations and constant strings, not method bodies, control flow or usage references.

Format source: [Il2CppDumper MetadataClass.cs](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/MetadataClass.cs) and [Metadata.cs](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/Metadata.cs), primary project source, consulted 2026-10-28. No program or dependency was downloaded. Field ordering and version gates were used to implement a narrow local reader; it is not a general-purpose IL2CPP dumper.

## Confirmed results

- IL2CPP magic `0xFAB11BAF`, metadata version **31**, first section at byte 256. This metadata format number is not the Unity engine version.
- 14,164 type definitions, 99,268 method definitions, 78,415 field definitions and 15,088 managed string literals decoded successfully.
- `ScriptingAssemblies.json` lists `Unity.TextMeshPro.dll`, `UnityEngine.UI.dll`, `Unity.Addressables.dll`, `Unity.ResourceManager.dll`, and `PlayMaker.dll`.
- The assembly list does not include a named `Unity.Localization.dll` package assembly. `UnityEngine.LocalizationModule.dll` is present; that engine module alone does not establish use of the Unity Localization package.

Full evidence, source hash and byte offsets: `metadata_evidence.json`. A complete literal dump is `string_literals.json`. These 15,088 literals include framework errors, diagnostics, internal keys and identifiers; **the count must not be presented as the game's translatable string count**.

## Localization definitions

Two distinct sets of game-owned localization definitions are present in `Assembly-CSharp.dll`. Their active use and coverage must be correlated with serialized instances; definitions can include unused code.

| Namespace / class | Type index | Metadata byte offset | Relevant evidence |
|---|---:|---:|---|
| `SummertimeMadness.Localization.LocalizationDatabaseAsset` | 2320 | 10901820 | `Keys`, `Languages`, `GenerateDictionaries` |
| `LocalizationKeyDatabaseAsset` in same namespace | 2321 | 10901908 | `IsEnabled`, `Keys`, `AddKey`, `RemoveDuplicates` |
| `LocalizationKeyValue` | 2322 | 10901996 | `Key`, `Value` |
| `LocalizationLanguageAsset` | 2323 | 10902084 | `IsEnabled`, `AlternativeFont`, `LocalizedName`, `LanguageTag`, `Entries`, `_tempDictionary` |
| `LocalizationManager` | 2324 | 10902172 | `LanguageIndex`, `SelectNextLanguage`, `GetLanguage`, `TranslateKey`, two `Translate` overloads |
| `LocalizedText` | 2327 | 10902436 | `TargetText`, `ChangeFontOnly`, `ConvertToUpper`, `LocalizationKey`, `AlternativeFont`, `_params` |
| `BluePrince.Language.Languages` | 2462 | 10914316 | `languages`, `dirigiblocksTextRef`; `GetText`, `GetGroupText`, `SetNewVideoTextData` |
| `BluePrince.Language.LanguageText` | 2463 | 10914404 | `dirigiblocksText`, upgrade names/descriptions, `videoTextList` |
| `BluePrince.LanguageOptions` | 2453 | 10913524 | Enum member names `EN`, `NL` only |
| `BluePrince.LanguageGroup` | 2454 | 10913612 | Enum member names `Dirigiblocks`, `MainMenu`, `MainGame` |

LIKELY: localization databases, localized components, params and language-specific fonts offer a safer asset-level route than executable modification. UNKNOWN: whether these are the primary active paths, whether NL is a working language, how absent keys fall back, how language tags are exposed, or whether alternative fonts are selected at runtime. The enum is not a reliable list of installed/working language packs.

`LocalizedText.ConvertToUpper` is an extra behavior to verify against Arabic and mixed text. It does not itself prevent Arabic, but a pipeline must not assume text is displayed verbatim or that string lengths remain unchanged.

## Video/subtitle relationship

Confirmed game-owned declarations, all in `Assembly-CSharp.dll`:

| Class | Type index | Metadata offset | Relevant fields/methods |
|---|---:|---:|---|
| `BluePrince.VideoText` | 2455 | 10913700 | `videoName`, `text`, `data` |
| `BluePrince.VideoTextData` | 2456 | 10913788 | `startTime`, `endTime` |
| `BluePrince.VideoTextWriter` | 2459 | 10914052 | `videoPlayer`, `videoClip`, `subTitles`, `currentLine`, `videoTextIndex`, `textMeshPro`; `StartVideo`, `LineSetter`, `StopVideoTextWriter` |
| `HutongGames.PlayMaker.Actions.BP_VideoTextWriterPlay` | 2299 | 10899972 | `videoClip`, `videoIndex`, `textMeshComponent`, `videoTextWriter` |
| `HutongGames.PlayMaker.Actions.BP_VideoTextWriterStop` | 2300 | 10900060 | `videoTextWriter` |

LIKELY: subtitles can be synchronized as separate timed text against video clips, and language data supplies video text. UNKNOWN: exact timing units, whether every clip uses this path, line wrapping, rich tags, progressive reveal, and whether video frames also contain embedded English. Do not edit start/end times while testing translation.

Evidence with methods, fields and offsets: `video_settings_evidence.json`.

## Progressive reveal and Arabic risks

CONFIRMED: `HutongGames.PlayMaker.Actions.StringTypewriter` exists (type 1155, offset 10799300), with `DoTyping`, `DoRichText`, `DoFinish`, `OnUpdate`, plus `baseString`, `resultString`, `message`, `index`, `lastChar`, `nextChar`, `_charCount`, rich-text flags and typing sound fields. This proves a typing action is compiled in; it does **not** prove a visible game screen uses it, or how it indexes text.

CONFIRMED: `TMPro.TMP_Text` metadata includes `get_isRightToLeftText` (method 83042, byte 6136348), `set_isRightToLeftText` (83043, 6136384), `m_isRightToLeft` (field 68784, 9350324), and `m_maxVisibleCharacters` (field 68885, 9351536). Those options do not prove contextual Arabic shaping or complete Unicode BiDi.

No exact `ArabicSupport`, `RTLTMPro`, `HarfBuzz`, or `BiDi` name was found in the metadata name table. Generic `Arabic`/Arabic keyboard names and .NET regex block names exist; they are not evidence of a game Arabic rendering implementation. Absence of recognizable plugin names does not prove that no custom or native implementation exists.

Arabic glyph coverage, joining, mixed-direction layout, punctuation, wrapping, clipping and animation remain **UNKNOWN / NOT TESTED** from this branch. Never reverse the entire string. Before expanding translation, correlate serialized PlayMaker actions and video writer instances, then capture a genuine game rendering test from a safe isolated copy.

## Hardcoded text candidates

`hardcoded_text_candidates.json` records six selected managed literal candidates with byte offsets and unresolved visibility/context status. Examples include a controller reconnect message, a location label, a dynamic prompt fragment and a room-label fragment. Another room ID literal may be debug-only. These must not be translated blindly or counted as confirmed player-facing strings. No callsite ownership was inferred from the literal table; the literal pool is shared across assemblies.

Most broad keyword matches were diagnostics or framework text, so a broad literal scan is unsuitable as a translation backlog. Local extraction should prioritize structured asset data and serialized fields, with managed constants tracked separately when actual visible usage is established.

## Next safe actions

1. Correlate the listed class names with MonoScript/MonoBehaviour object references and typetrees in the asset inventory.
2. Export localization entries, BluePrince language arrays, timed video text and serialized PlayMaker strings with resource/object/field IDs intact.
3. Verify an unchanged asset roundtrip, then one copied asset target with a reversible Arabic probe.
4. Prove glyph rendering, shaping, mixed-direction layout and progressive reveal independently in a game copy. Keep original installation and code files untouched.

No executable modification is currently justified. Fallback semantics or a missing serializer may require further read-only research; do not jump from a missing asset link to code patching.
