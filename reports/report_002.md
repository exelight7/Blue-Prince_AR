# Report002 — extraction and offline Arabic asset POC

Recorded: 2026-10-28T10:33:16+03:00 (Asia/Riyadh). This is a continuation handoff, independent of chat history.

## Outcome

ENGINE: CONFIRMED Unity2021.3.45f1 / Windows AMD64 / IL2CPP metadata31.
ENGINE VERSION:2021.3.45f1; local application1.0.5.0, Dogubomb BLUE PRINCE.
LOCALIZATION SYSTEM: custom SummertimeMadness.Localization plus BluePrince.Language declarations; direct TMP and PlayMaker sources. Not proven to be Unity Localization package.
TEXT FORMAT: binary serialized fields,74 English key/value entries, FSM string parameters/defaults, timed subtitle declarations, managed literals, texture/video text.
FONT SYSTEM:12 embedded Font objects,56 TMP font assets; existing NotoNaskhArabic-Medium Font211 / TMP244 / material43 in sharedassets1.
RTL SUPPORT: TMP RTL property exists; game correctness UNKNOWN. Global fallback list is empty.
ARABIC SHAPING: native TTF GSUB/GPOS present; runtime shaping UNKNOWN. Plain offline logical/presentation glyph probes PASS11 samples.
EXTRACTION: 20,815 direct occurrences / 4,850 distinct values; 141,161 FSM candidates / 4,251 distinct candidate values. Do not add these counts as unique translations. All12,010 FSM/template objects strict/no-op PASS; all748 array proxies also strict/no-op PASS; other sources remain context work.
REPACKING: copied level1 offline POC PASS; runtime loading and bundle repacking UNKNOWN.
POC STATUS: two seven-string asset variants built, not installed/launched or visually approved.
MAIN BLOCKERS: actual Arabic rendering/BiDi/wrap/reveal tests; complete context/source coverage; subtitle and image/puzzle adaptation.
RISK LEVEL: 🟩 LOW completed inspection; 🟨 MEDIUM offline asset POC; no 🟥 HIGH operation.
NEXT ACTION: resolve remaining source/schema ledgers and visually test the tiny POC in a separate complete runnable copy with actual save/settings preservation.

## Safety and reproducibility

Original preservation verification: **PASS across 56 files**, no added/removed or changed hashes. No original file was written, renamed, moved, patched or deleted. No game executable was launched; no DRM/authentication/license branch was changed. All work remains local. Backups are selected verified research files, not a claim of a full playable backup.

Run tools/project.py verify against the original installation before/after any further work. Immutable baseline, snapshot hashes and source-version mapping are in reference/ and translation/source/SOURCE_VERSION.json. Do not replace old reports or silently overwrite conflicts. All scripts reside inside this project and are English; docs/README.md has exact commands and dependencies.

## POC details and checks

Scene: level1 (Main Menu). Changes: objects3357 New Game,3481 Continue,3500 Quit Game,3534 Settings,3411 Volume,3535 multiline difficulty text with50,3404 mixed calibration text with Mt.Holly/[ENTER]. Seven temporary natural-Arabic strings only; no mass translation.

Both variants target existing sharedassets1 TMP244/material43. Logical variant uses TMP RTL flag; pre-shaped variant uses arabic-reshaper/python-bidi plain-line visual ordering with TMP RTL disabled. Settings label enables auto-size solely for that experiment. These are comparison hypotheses, not a final renderer solution. No actual dialogue/subtitle or reveal case was patched.

PASS: original seven object byte-identical no-op serialization, strict changed-object reparse, all4,253 other object payloads byte-identical, object IDs/types unchanged, second serialization byte-identical, repeated builds identical, placeholder/tag/line-break validator for seven rows, validation boundary self-checks,57/57 TMP font/settings no-op equality,11 offline font/sample probes. Exact changed fields and before/after values are in tests/poc_change_manifest.json; output hashes in tests/poc_results.json.

NOT TESTED: Unity runtime loading, glyph atlas generation, Arabic joining, true Unicode BiDi, layout/wrapping/clipping/alignment, animation/typewriter, actual dialogue and subtitle synchronization. Full matrix: tests/GAMEPLAY_QA.md. Never mark the entire POC PASS from these offline checks.

## Extraction decisions

UnityPy1.25.3 uses project-local TypeTreeGeneratorAPI0.0.10. Call native get_nodes with extensionless assembly names; correct root m_Enabled padding before creating tree nodes. AssetsTools works for TMP/localization; AssetStudio works for PlayMaker/generic lists. The initial11,815 failures are retained as historical evidence. Alternate extraction recovered all11,973 FSMs,37 templates and the74-key list with strict parse plus exact byte no-op checks. Constant string parameter/variable values stay NEEDS_CONTEXT, since save keys/filenames/events can resemble visible text.

Text locations use container+pathID+field, context GameObject name, unchanged source text and separate Arabic.164 LocalizedText bindings link keys to components where statically possible; null TargetText references stay unresolved.15,088 managed literals are mostly framework/internal strings and are not a localization backlog. Serialized action references reveal actual typewriter use in asset data; execution and Arabic direction still require observation.

## Font, image and puzzle risks

Arabic font244 is dynamic, initially lacks Arabic atlas characters, and multiatlas is disabled. Ordinary UI/global fallback does not automatically select it. Test targeted references and runtime generation; do not replace every display font globally.

1,043 textures/25 video clips/631 AudioClips indexed. Six original texture samples were extracted with verified matching resource sidecar and visually reviewed: worldmap1 has embedded map labels; LETTERSatlas is Latin glyph art;8letter and5letter contain English/puzzle typography. Museum map is primarily diagrammatic; treasure map contains compass/puzzle markings. Details: research/texture_review.json and texture_contact_sheet.png. No image was translated or replaced. English-letter-dependent clues need puzzle adaptation rather than blind art substitution; video frames remain unreviewed.

## Continuation

Read state/ARCHITECTURE.md, FILE_MAP.md, LOCALIZATION_MAP.md, PROBLEMS.md, NEXT_STEPS.md and docs/README.md. Resolve array-proxy visibility and custom nested language/subtitle sources, then run a single controlled variant in an isolated full copy and capture screens. Use logical text or a designed RTL solution only after results justify it; pre-shaped strings alone do not solve dynamic substitutions/wrap/reveal. Keep the full-translation gate closed until the complete minimum rendering matrix passes. Glossary remains draft. Final installer and migration tools await a stable pipeline as requested.
