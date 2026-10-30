> **Historical.** Superseded by `HANDOFF.md` (2026-10-30), which has the current state, counts and next steps. The text below is kept as a record and may be out of date.

# Runtime assessment and current offline workflow

Updated: 2026-10-28, Asia/Riyadh. The user now requires offline work: **do not launch the game** unless explicitly instructed later. A generic request to continue does not cancel that restriction.

## Preferred current artifact

`build/arabic_menu_poc/BLUE PRINCE_Data/level1`, built by `tools/build_arabic_menu.py`, contains eleven meaningful Main Menu/Settings labels. Canonical logical Arabic is `translation/arabic/menu_poc.json`; stored visual-order text is only a build representation.

This scene was rebuilt from the untouched source and is currently staged in `runtime_test`. It contains no diagnostic phrases or added typewriter FSMs. It has not been launched for a final visual review. All other 55 runtime files match the original file hashes. The original installation remains untouched.

The font route is deliberately narrow: each selected TMP component points to sharedassets1 TMP244/material43. No global font replacement or fallback change was made. Font211 is the embedded Noto Naskh Arabic source. Original UI layout structures remain intact.

## Offline commands

Run from the project root using normal Python, never `python -O`:

```powershell
python tools/build_arabic_menu.py
python tools/validate.py translation/arabic/menu_poc.json --source translation/source/strings.json
python tests/test_arabic_plain.py
python tests/test_integrity.py
python tools/stage_runtime.py arabic_menu
python tools/verify_runtime.py
python tools/project.py verify
```

None of these commands launches the game. Staging refuses to run while a Blue Prince process exists, rejects unknown input/output hashes, validates the source backup, and replaces only the disposable scene after verifying a pending copy. Each successful staging operation has a numbered hash record under `tests/runtime_staging/`.

Immutable JSON evidence is preserved. Re-running an identical build succeeds; differing output refuses to overwrite old evidence. `prepare_runtime.py` refuses to recreate an existing runtime folder. Do not delete manifests just to force a command through.

## Static preprocessing limits

`tools/arabic_plain.py` handles plain, resolved static strings only. It measures words with the embedded font, wraps in logical order, then shapes and applies BiDi independently to each line. Using TMP autowrap on a whole visual-order paragraph reversed the logical line order in actual screenshots.

The helper preserves diacritics in data, explicit paragraph breaks and Latin/numeric runs. It rejects rich tags, unresolved variables/format placeholders/escape tokens and words wider than the chosen bound. These boundaries prevent accidental use as a universal runtime processor. Diacritic placement was not visually tested after the offline change.

Measured advances do not reproduce all TMP kerning, autosize, hover animation, scale or viewport behavior. The sampled 17-em paragraph and 1.5 font cap are calibration evidence for that test label, not global settings. The eleven short menu labels use the original non-auto-size baseline with Latin tracking removed.

Settings source: [arabic-reshaper's documented configuration](https://github.com/mpcabd/python-arabic-reshaper#settings). Mark retention and placement are separate questions; codepoint tests do not establish runtime appearance.

## Preserved experiments

- `build/poc/`: the first offline seven-string POC; not the current deliverable.
- `build/runtime_matrix_v2/a` and `/b`: matched diagnostic strings. A used logical Arabic/TMP RTL; B used pre-shaped visual text/TMP RTL disabled. Neither is a semantically localized menu.
- `build/runtime_layout_typewriter`, `_v4`, `_v5`: isolated logical-wrap/lam-alef and injected typewriter probes. Their binary integrity passed, but the reveal control was inconclusive. These are not approved menu builds.
- `build/rejected/level1_float_0_3`: rejected pre-launch experiment retained for audit. It is not whitelisted for staging. A float equality check failed; later probes use an exactly representable interval.

The typewriter source is game FSM314189, with input -> typing_text -> TMP297408.text. Injections use the game's existing FSM serialization type, not executable modification. The English control did not provide a reliable visible progressive baseline, so no Arabic reveal direction conclusion is justified. Continue analysis offline instead of repeating the same injection blindly.

## Evidence and user state

`tests/runtime_results_003.json` separates A/B observations, static success and unresolved progressive behavior. `tests/screenshot_evidence_003.json` hashes 18 screenshots. Final integrity is in `tests/runtime_integrity_003.json` and `tests/original_integrity_after_runtime_003.json`.

Known LocalLow/registry paths were checked before first launch. Previously absent game storage/settings files were created by testing and backed up under `backups/runtime_user_state_after_003`. A copied installation shares user-state paths unless explicitly redirected. Nothing was deleted or restored automatically.

Future runtime checks, only if explicitly allowed later: meaningful menu labels including hover states, an existing game progressive path with a valid English control, subtitle timing, dynamic substitutions, rich text, diacritics and multiple layout sizes. Full translation and installer work remain gated.
