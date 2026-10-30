# PlayMaker text flow and asset-only typewriter test

Date: 2026-10-28, Asia/Riyadh. Scope: read copied assets and write research evidence only in `research/runtime_textflow`. No game launch, runtime input, asset file modification, executable modification, dependency installation or publication was performed by this branch.

## Confirmed text mutation paths

All 164 PlayMaker FSMs in the copied Main Menu scene (`level1`) were strictly parsed with AssetStudio-generated schemas and checked by exact byte-identical no-op serialization. `level1_textflow.json` records action counts, 364 relevant text-related states and 52 states referencing the seven original POC objects or their owner GameObjects.

| Serialized action | Main Menu count | Meaning of the evidence |
|---|---:|---|
| `setTextmeshProText` | 194 | Direct text assignment is referenced in the scene |
| `setTextmeshProTextColor` | 369 | Text colors are changed by gameplay/UI state |
| `BuildString` | 25 | Runtime string construction is referenced |
| `SetStringValue` | 11 | String values can be changed before display |
| `StringCompare` | 80 | Many strings are control values, not translations |
| `StringContains` | 2 | String-dependent control logic is referenced |
| `AnyKeyStoreString` | 8 | Key/input strings may be generated dynamically |

No action-name match for Substring, string Replace, string Length, StringJoin, FormatString or StringTypewriter was found in this bounded `level1` scan. That does not prove those features are absent from the whole game, or establish the method bodies of custom actions. The prior full asset ledger contains **535 enabled serialized StringTypewriter references in 191 level2 FSMs**.

Thus PlayMaker **does affect displayed text**. Transforming every raw string at extraction time is insufficient as a general solution: string construction and later assignment must be considered. This branch did not patch any PlayMaker state.

## Original POC labels

| TMP object | Owner GameObject | Context |
|---:|---:|---|
| 3357 | 7 | NEW GAME TEXT 4 |
| 3404 | 139 | screen calibration (1) |
| 3411 | 170 | VOLUME TEXT |
| 3481 | 403 | CONTINUE TEXT |
| 3500 | 462 | QUIT TEXT |
| 3534 | 586 | SETTINGS TEXT |
| 3535 | 587 | Description |

These seven owner component lists do not already include a PlayMakerFSM component. Their visibility depends on UI state. GameObject 7 is one of several save-slot/new-game labels; its initial visibility must not be assumed.

The observed PlayMaker references mainly control activation, color and font size. Direct SetProperty references change `fontSize` on Continue (FSM3788 -> TMP3481), Quit (3815 -> 3500), Settings (3821 -> 3534), and Volume (3852 -> 3411). Values include 2.5, approximately 2.8, and 3.0 for different interaction states. Clipping should therefore be checked both idle and hovered/selected.

The text-setting actions in POC-related settings/layout states target decorative GameObject89, rather than the seven POC text values. This bounded mapping found no direct text setter overwriting those seven labels. It does not rule out custom runtime component resolution or other scripts.

## Concrete progressive-text chain

Three existing level2 FSMs were strictly parsed and byte-identical no-op checked. Their original serialized data are saved in `typewriter_samples.json`.

The smallest source is **level2 PlayMakerFSM314189**, owner GO1123, context `description Spread done`:

```text
fsm.states[0], name "State 4"
  StringTypewriter
    baseString: constant English message
    resultString: FSM string variable "typing_text"
  SetProperty (every frame)
    TargetObject: TMP TextMeshPro297408
    PropertyName: "text"
    StringParameter: variable "typing_text"
```

This proves an asset-data chain from a typewriter result variable to a visible-text property. It does not prove that a particular gameplay route executes the state or that Arabic reveals correctly. The FSM initially starts `Clear Em All`, which only clears that same property. A dedicated test must deliberately start `State 4` or trigger the correct event; otherwise a blank result is expected.

Other bounded samples: FSM314212 `SECURITY 1` targets TMP310125 in one typewriter state and a second text target in another; FSM314251 `Email Content` targets TMP297463 and contains rich-text email content. The latter demonstrates tags in a typewriter input but was not altered.

No compiled method body was inspected. Therefore exact `Substring(0,n)` semantics, UTF-16/grapheme indexing, reveal direction, and reshape timing remain UNKNOWN until runtime observation. Typewriter must not be marked N/A.

## Exact dedicated-test adaptation

Preferred approach: add one new FSM component in the **copied** level1 asset, retaining existing menu FSMs and behavior. Source data314189 has only four nonzero references: owner GO1123, script global file1/path4508, and target TMP297408 in states0 and1. No nonzero audio or other asset reference needs carrying into the test.

The target level1 already contains the compatible PlayMakerFSM serialization type: example object3741, `type_id=26`, script file1/path4508. A shallow copy of that target-file ObjectReader wrapper can hold a new ID and the adapted source payload, avoiding cross-file serialization-type transplantation. The original wrapper object must remain byte-identical.

Exact payload changes:

| Field | Test value |
|---|---|
| `m_GameObject` | Target label's actual owner GO |
| `fsm.name` | Unique test-only name |
| `fsm.startState` | `State 4` |
| `fsm.states[0].actionData.fsmStringParams[0].value` | Test sentence |
| `fsm.states[0].actionData.fsmFloatParams[0].value` | 0.25 for a slower reveal experiment |
| `fsm.states[0/1].actionData.fsmPropertyParams[0].TargetObject.value` | Target TMP component reference |
| Both property `TargetTypeName` values | Preserve `TMPro.TextMeshPro` for a same-class target; change only if target actually is `TMPro.TextMeshProUGUI` |

The parameter table explicitly maps the following fields; these are not guessed offsets:

| Parameter | `paramDataType` | `paramDataPos` | Serialized location |
|---|---:|---:|---|
| baseString | 18 | 0 | fsmStringParams[0] |
| resultString | 18 | 1 | fsmStringParams[1], variable typing_text |
| pause | 15 | 0 | fsmFloatParams[0] |
| punctuationMultiplier | 15 | 1 | fsmFloatParams[1], preserve1 |
| speedMultiplier | 15 | 2 | fsmFloatParams[2], preserve1 |
| realtime | 17 | 0 | fsmBoolParams[0], preserve false |
| richText | 1 | 0 | byteData[0] |
| useSounds | 1 | 1 | byteData[1], already0 |
| noSoundOnSpaces | 1 | 2 | byteData[2], already1 |
| SetProperty.everyFrame | 1 | 3 | byteData[3], must stay1 |

Original byteData is `[1,0,1,1]`. The plain-string experiment disables richText only, yielding `[0,0,1,1]`. `stringParams[1]` is an optional-sounds section label; do not interpret it as a direction mode. `d1` maps to that label and should remain unchanged. `finishEvent` is empty in the original; no additional transition is required to keep final text visible.

The owner GameObject's `m_Component` list must gain the new FSM reference. Do not replace an existing navigation/save FSM. Pick an unoccupied path ID, check for collision, and validate all original object payloads except the explicitly changed owner GO. Keep target font/material and text-mode settings consistent with the A/B experiment being tested.

## Addition feasibility check

`probe_typewriter_addition.py` verifies the proposed addition entirely **in memory**. It writes only JSON evidence, not a modified asset file.

- Target example: GO170 / TMP3411 (Volume), new ID1000000001.
- Original scene objects:4260; new scene objects:4261.
- Strict reparse of the added FSM: PASS.
- Exact owner component list after reload: PASS.
- All4259 other existing object payloads, including source wrapper3741: byte-identical PASS.
- Deterministic second save: PASS.
- Adapted payload: `adapted_typewriter_data.json`.
- Test sentence: `مرحبا بك في القصر، الغرفة رقم 27.`
- Runtime execution: NOT TESTED by this research branch.

The parent may choose a more visible label/overlay target; the example Volume label requires navigating to its screen. Capture multiple reveal frames and the final frame for both logical and pre-shaped strategies. Correct final text alone cannot validate progressive reveal. Pre-shaped visual text may reveal from an inappropriate side or expose intermediate joining forms, but that is a risk to test, not an observed failure in this report.

## Reproduction

```powershell
python research/runtime_textflow/probe_textflow.py
python research/runtime_textflow/probe_typewriter_addition.py
```

Both scripts read `backups/source` and existing JSON evidence; all their writes stay in this owned research directory. Runtime screenshot results belong to the parent's separate test workflow.
