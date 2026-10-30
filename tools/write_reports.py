"""Write the local forensic milestone reports from saved evidence."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from project import ROOT, write_new


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))


def save(relative, body):
    path = ROOT / relative
    if path.exists():
        if path.read_text(encoding='utf-8') != body:
            raise FileExistsError(f'Refusing to overwrite report/state: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(body)


def main():
    inventory = load('reference/source_inventory.json')
    summary = load('research/asset_summary.json')
    text = load('research/text_extraction_summary.json')
    fsm = load('research/playmaker_extraction_summary.json')
    arrays = load('research/array_extraction_summary.json')
    original = load('tests/original_integrity.json')
    stamp = datetime.now(timezone(timedelta(hours=3))).isoformat(timespec='seconds')
    version = dict(application='1.0.5.0', engine='2021.3.45f1', platform='Windows AMD64',
        original_root=str(ROOT.with_name('Blue Prince')), baseline='reference/source_inventory.json',
        containers={r['path']:r['sha256'] for r in inventory if Path(r['path']).suffix in ('.assets', '.bundle') or Path(r['path']).name in ('level0','level1','level2')})
    write_new(ROOT / 'translation/source/SOURCE_VERSION.json', version)
    lines = ['# Original file map', '', f'Inspected: {stamp}. Paths relative to `D:\\Games\\Blue Prince`.', '',
        'All 56 files are hashed in the immutable machine-readable baseline. Status means inspection, not permission to modify. Risk refers to a future modification.', '',
        '| Path | Type / purpose | Bytes | SHA-256 | Extraction / repacking | Risk / status |',
        '|---|---|---:|---|---|---|']
    for row in inventory:
        p = Path(row['path']); ext = p.suffix.lower()
        if ext == '.bundle':
            purpose = 'UnityFS Addressables container; mesh data or end-of-day VideoClip'
            method = 'UnityPy parse PASS; bundle save/catalog CRC not tested'
            risk = 'MEDIUM; indexed'
        elif ext == '.assets' or p.name in ('level0','level1','level2','globalgamemanagers'):
            purpose = 'Unity serialized objects: UI, text, scripts, fonts, textures, audio/video refs'
            method = 'UnityPy + generated schemas; level1 asset POC roundtrip PASS'
            risk = 'MEDIUM; indexed, field-specific schemas required'
        elif ext in ('.ress','.resource'):
            purpose = 'External texture/mesh/audio/video stream; exact owner references required'
            method = 'Preserve raw bytes; no blind edits or repacking yet'
            risk = 'MEDIUM; inventoried'
        elif p.name == 'global-metadata.dat':
            purpose = 'IL2CPP v31 declarations and managed string literals'
            method = 'Read-only parser PASS; no modification planned'
            risk = 'HIGH if patched; inspected read-only'
        elif ext in ('.exe','.dll'):
            purpose = 'Native runtime/plugin/installer code; not an asset modification target'
            method = 'PE headers/identity only as needed; no patching/execution'
            risk = 'HIGH if modified; preserved'
        elif ext in ('.json','.xml','.config','.info'):
            purpose = 'Build/assembly/Addressables metadata and configuration'
            method = 'UTF-8/JSON/XML reads; preserve keys; no current patch'
            risk = 'LOW read; inventoried'
        else:
            purpose = 'Ancillary, builtin resource or unknown file; no localization assumption'
            method = 'Inventory/hash; inspect only if relevant'
            risk = 'UNKNOWN modification; preserved'
        lines.append(f"| `{row['path']}` | {purpose} | {row['size']} | `{row['sha256']}` | {method} | {risk} |")
    lines += ['', '## Internal-object inventory', '',
        f"{len(summary)} game containers indexed; {sum(x['objects'] for x in summary):,} objects. Builtin Font inspection is separately recorded by the font branch.", '',
        '1,043 Texture2D records, 25 VideoClip records and 631 AudioClip records are indexed. These counts include atlases, decorative and unused content; none is a count of translatable images or lines.', '',
        'Source-level localization categories are mapped in LOCALIZATION_MAP.md. Internal records include container, asset name, object path ID, type, size and available name/dimensions. Broad script hints are provisional for bundle-local references; resolve actual external files before patching.', '',
        'Important font/text IDs: sharedassets1:237 key list,238 English,239 Italian,240 locale database,211 native Arabic font,244 Arabic TMP font,43 Arabic material; resources:1168 TMP settings. POC changes only level1 objects3357,3404,3411,3481,3500,3534,3535.']
    save('state/FILE_MAP.md', '\n'.join(lines)+'\n')
    lm = f'''# Localization map

Updated: {stamp}. CONFIRMED means parsed evidence; visibility is still subject to gameplay validation.

## Normalized direct text

`translation/source/strings.json`: {text['occurrences']:,} nonempty occurrences / {text['unique_sources']:,} distinct source values. Includes repeated objects, single letters, punctuation, debug UI and possibly unused content. Not an approved translatable count. All {text['counts']['TextMeshPro']:,} TextMeshPro and {text['counts']['TextMeshProUGUI']:,} TextMeshProUGUI instances in the scanned loose scene/asset files parsed. Empty component values are not included as strings.

ID format: `container:path_id:field_path`. Context is GameObject name or asset name. Each row preserves Source, blank Arabic, File, Category, Notes and Status. `SOURCE_VERSION.json` records application version and source-container hashes. Do not deduplicate contextual occurrences.

Example: `level1:3357:m_text` -> `NEW GAME` -> Main Menu scene -> GameObject-resolved component; POC Arabic `لعبة جديدة`. `level1:3404:m_text` contains a multiline calibration message and `[ENTER]`; token and line-break counts are preserved in the POC.

## Key database and bindings

`sharedassets1.assets:238` (en-us, tag en) has74 English entries. `:239` has Italian data; `:237` defines74 keys; `:240` references key/language assets. All are exported in `extracted/original/structured/sharedassets1.assets/`.

164 LocalizedText components are mapped in `research/localized_text_bindings.json`. Relation: `LocalizationKey -> locale Entries.Key/Value -> LocalizedText -> TargetText or runtime component -> scene GameObject`. Some TargetText references are null; a runtime resolution must be observed, not invented. One binding key `UI.SETTINGS.CONTROLS.STROLL_SUB` is present even though the small table is not demonstrably complete. Missing-key behavior is UNKNOWN.

## PlayMaker

Alternate AssetStudio schemas read all {fsm['counts']['PlayMakerFSM']:,} FSMs and {fsm['counts']['FsmTemplate']:,} templates with strict full reads and byte-identical no-op serialization: {fsm['strict_byte_noop_pass']:,} PASS, {fsm['errors']} errors. The first AssetsTools pass logged11,815 errors; those records remain as historical evidence, not the current FSM failure count. The key-list failure was also recovered.

`translation/source/playmaker_candidates.json` contains {fsm['candidate_occurrences']:,} candidate occurrences / {fsm['unique_candidate_values']:,} distinct values from string variable defaults and constant FsmString action parameters. Many are save keys, filenames, identifiers, puzzle controls or invisible values: **do not translate this file automatically**. Variable names, state names and action identifiers are context only, not patch targets. Enabled serialized typewriter/video action references are in `research/serialized_text_actions.json`; this proves asset references, not execution during gameplay.

All {arrays['strict_byte_noop_pass']} array proxies also passed strict parsing and exact no-op equality using AssetStudio, recovering the remaining172 first-pass errors. Their {arrays['candidate_occurrences']:,} string occurrences remain candidates in `translation/source/array_candidates.json`, not approved visible strings. Historical schema errors are fully recovered for this selected set of classes. Nested BluePrince.Language data, subtitle arrays, custom game classes and managed constant callsites still need additional mapping.

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
'''
    save('state/LOCALIZATION_MAP.md', lm)
    qa = ['# Gameplay / rendering QA matrix','',f'Updated: {stamp}. No game launch or actual rendering capture performed.','',
        '| Area | Result | Evidence |','|---|---|---|']
    for area in ['Main Menu','Settings','New Game','Load Game','Gameplay HUD','Dialogue','Subtitles','Items','Rooms','Puzzle UI','Tutorials','Notes/Documents','Pause Menu','Game Over','Save/Load','Credits']:
        qa.append(f'| {area} | BLOCKED | Awaiting controlled in-game visual test; source inspection is not gameplay evidence |')
    qa += ['','## POC checks','','| Check | Result | Evidence |','|---|---|---|',
        '| Extraction | PASS for seven targeted fields | Strict schemas; original object no-op serialization identical |',
        '| Repacking | PASS offline / runtime UNKNOWN | Seven changed objects;4,253 unchanged payloads; deterministic save and reparse |']
    for check in ['Arabic glyphs','Arabic shaping','RTL','BiDi','Font runtime generation','Wrapping','UI clipping','Alignment','Progressive text']:
        qa.append(f'| {check} | BLOCKED / NOT TESTED IN GAME | Offline font/sample data does not establish rendering correctness |')
    qa += ['','Progressive text is not marked N/A: serialized typewriter references exist and need a dedicated test. No confirmed dialogue/subtitle line was patched in the first POC. No test was marked PASS from a screenshot that does not exist.']
    save('tests/GAMEPLAY_QA.md','\n'.join(qa)+'\n')
    first = f'''# Report001 — source preservation and forensic baseline

Recorded: {stamp} (Asia/Riyadh). Project `D:\\Games\\Blue Prince_AR`; source `D:\\Games\\Blue Prince` read-only.

CONFIRMED engine Unity2021.3.45f1, IL2CPP metadata31, PE AMD64. PlayerSettings: Dogubomb, BLUE PRINCE,1.0.5.0. Main Menu is level1 and Mount Holly Estate level2.56 source files totaling4,162,841,374 bytes inventoried with SHA-256; selected source containers and metadata were copied and verified. Five Addressables UnityFS bundles parsed; settings specify Addressables1.19.19. No game binary executed or modified. Nothing uploaded, committed, pushed or published.

Custom key localization, TMP components, PlayMaker, timed subtitle declarations and embedded Arabic font found. These are static findings, not a working Arabic localization. Evidence: reference/source_inventory.json, research/build_identity.json, research/asset_summary.json, research/metadata/, fonts/ and rtl/.

Existing installed libraries were preferred. Only the official TypeTreeGeneratorAPI0.0.10 wheel was added project-locally to recover stripped schemas; SHA-256e96003e973c8d52d221b4ae50f377bcaf7538f2098e437d5383a1b7f13fa72ba matches PyPI. Scripts read copied GameAssembly/metadata as data. Generated schemas require backend-specific handling and complete-byte checks.

Risk: 🟩 LOW for inspection/copying/parsing; later copied-asset/font POC is 🟨 MEDIUM. 🟥 HIGH executable/DRM work is outside automatic scope. Next: map text schemas, verify a tiny asset roundtrip and identify rendering gates. Full translation must wait for a genuine rendering test.
'''
    save('reports/report_001.md',first)
    second = f'''# Report002 — extraction and offline Arabic asset POC

Recorded: {stamp} (Asia/Riyadh). This is a continuation handoff, independent of chat history.

## Outcome

ENGINE: CONFIRMED Unity2021.3.45f1 / Windows AMD64 / IL2CPP metadata31.
ENGINE VERSION:2021.3.45f1; local application1.0.5.0, Dogubomb BLUE PRINCE.
LOCALIZATION SYSTEM: custom SummertimeMadness.Localization plus BluePrince.Language declarations; direct TMP and PlayMaker sources. Not proven to be Unity Localization package.
TEXT FORMAT: binary serialized fields,74 English key/value entries, FSM string parameters/defaults, timed subtitle declarations, managed literals, texture/video text.
FONT SYSTEM:12 embedded Font objects,56 TMP font assets; existing NotoNaskhArabic-Medium Font211 / TMP244 / material43 in sharedassets1.
RTL SUPPORT: TMP RTL property exists; game correctness UNKNOWN. Global fallback list is empty.
ARABIC SHAPING: native TTF GSUB/GPOS present; runtime shaping UNKNOWN. Plain offline logical/presentation glyph probes PASS11 samples.
EXTRACTION: {text['occurrences']:,} direct occurrences / {text['unique_sources']:,} distinct values; {fsm['candidate_occurrences']:,} FSM candidates / {fsm['unique_candidate_values']:,} distinct candidate values. Do not add these counts as unique translations. All12,010 FSM/template objects strict/no-op PASS; all748 array proxies also strict/no-op PASS; other sources remain context work.
REPACKING: copied level1 offline POC PASS; runtime loading and bundle repacking UNKNOWN.
POC STATUS: two seven-string asset variants built, not installed/launched or visually approved.
MAIN BLOCKERS: actual Arabic rendering/BiDi/wrap/reveal tests; complete context/source coverage; subtitle and image/puzzle adaptation.
RISK LEVEL: 🟩 LOW completed inspection; 🟨 MEDIUM offline asset POC; no 🟥 HIGH operation.
NEXT ACTION: resolve remaining source/schema ledgers and visually test the tiny POC in a separate complete runnable copy with actual save/settings preservation.

## Safety and reproducibility

Original preservation verification: **{original['status']} across {original['files']} files**, no added/removed or changed hashes. No original file was written, renamed, moved, patched or deleted. No game executable was launched; no DRM/authentication/license branch was changed. All work remains local. Backups are selected verified research files, not a claim of a full playable backup.

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
'''
    save('reports/report_002.md',second)
    print('Created file/localization maps, gameplay matrix, source version and two immutable milestone reports')


if __name__ == '__main__':
    main()
