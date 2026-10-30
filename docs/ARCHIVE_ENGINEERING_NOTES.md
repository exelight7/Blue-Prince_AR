> **Historical.** Superseded by `HANDOFF.md` (2026-10-30), which has the current state, counts and next steps. The text below is kept as a record and may be out of date.

# Local engineering handoff

Project: `D:\Games\Blue Prince_AR`; inspected source: `D:\Games\Blue Prince`, always read-only. User requests are preserved in `reference/PROJECT_REQUEST.txt` and `reference/RUNTIME_PHASE_REQUEST.txt`. A disposable runtime copy has now been tested and the final small menu POC is staged there. No commit, push, publication, upload or original-installation modification has been performed.

Current instruction: continue offline without launching the game. Read `docs/RUNTIME_TESTING.md` and report_003.md for current artifacts, observed results and unresolved gates; the initial workflow below is historical context.

Use the existing Python 3.12 interpreter. Scripts are in English. Run commands from the project root:

```powershell
python tools/project.py inventory
python tools/project.py snapshot
python tools/project.py extract
python tools/extract_text.py
python tools/extract_playmaker.py
python tools/extract_arrays.py
python tools/validate.py translation/arabic/poc.json --source translation/source/strings.json
python tests/test_integrity.py
python tools/build_poc.py
python tools/project.py verify
```

`inventory` creates the immutable baseline and refuses to overwrite changed data; on updates use a new explicitly versioned baseline, never replace the old one. `snapshot` copies selected source containers/metadata into `backups/source` and checks their hashes. `extract` indexes containers and extracts TextAssets from copies. `extract_text` recovers selected managed schemas and writes normalized occurrences plus unresolved candidate/error ledgers. `verify` checks every original file hash plus added/removed paths against the baseline.

`build_poc` uses Python assertions as mandatory verification; run normal Python, never `python -O`. It changes seven text components in a copied main-menu scene, targets the existing Arabic font/material, and creates two separate experimental variants. It preserves all other object payloads and requires strict reparse and deterministic resave. It does not install or launch. Use one variant per controlled test; do not combine them.

Generated JSON files are immutable: a repeated identical run succeeds; different output raises a conflict. Do not silently delete evidence to force a rerun. Save revised datasets under a new version/run location if an intentional pipeline change produces different output.

`extract_playmaker` uses validated AssetStudio schemas for FSM/template string-value candidates and serialized typewriter actions. `extract_arrays` reads array string values. Both require byte-identical no-op serialization and preserve identifiers as context. Together they recovered every selected-class error from the first text pass. These candidate files contain many internal values and must not be mass translated. The source-backed validator additionally rejects changed IDs/source text/file metadata when `--source` is provided.

## Existing dependencies

UnityPy 1.25.3, fontTools 4.65.0, arabic-reshaper 3.0.1, python-bidi 0.6.11, pefile 2024.8.26 were already installed. Only TypeTreeGeneratorAPI 0.0.10 was added, project-locally, after confirming stripped schemas were unavailable from existing tools.

Wheel: `tools/packages/typetreegeneratorapi-0.0.10-cp36-abi3-win_amd64.whl`; SHA-256 `e96003e973c8d52d221b4ae50f377bcaf7538f2098e437d5383a1b7f13fa72ba`, checked against official PyPI. Local installation: `tools/vendor`; no global Python environment changed. Reinstall from saved wheel using `python -m pip install --no-index --no-deps --target tools/vendor <wheel>` only when vendor is absent. Source: [official repository](https://github.com/UnityPy-Org/TypeTreeGeneratorAPI), [PyPI checksum/provenance](https://pypi.org/project/TypeTreeGeneratorAPI/).

## Evidence

- `reference/source_inventory.json`: every original path, size, mtime and SHA-256.
- `reference/snapshot_manifest.json`: copied source file hash ledger. Stream sidecars are inventoried but not all copied; do not claim a full runnable backup.
- `research/asset_summary.json`, `research/asset_index/`: object counts, IDs, names, font/texture/video candidates. Script hints in this broad index are provisional for bundle-local script references; resolve exact externals before using a hint for patching.
- `research/build_identity.json`, `research/pe_identity.json`: local asset version/scenes plus executable identity/signature metadata. A valid UnityPlayer signature does not authenticate the entire installation. Only the disposable copy was launched during the completed runtime observations; the current workflow is offline.
- `research/metadata/`: parser, metadata offsets, declarations, subtitle/typewriter evidence and unconfirmed hardcoded candidates.
- `fonts/` and `rtl/`: original TTF references, exact TMP schema inventory, no-op checks and offline Arabic probes.
- `translation/source/strings.json`: occurrence-based normalized extraction, not a complete approved translation backlog.
- `translation/arabic/poc.json`, `tests/poc_results.json`, `build/poc/`: tiny experimental patch and data-level verification.

## Change control

Only work in this project. Preserve untouched source copies before experiments. Keep original `.resS`/`.resource`/bundle dependencies and external references intact. Do not modify unknown generic schemas, executable authentication, DRM, licensing or online systems. Stop and document any code-modification branch first. Do not ship copied game assets or fonts; local research permission is not distribution clearance.

For a future patch format, keep Arabic data independent of binary assets with original IDs/source/version, validate all placeholders/tags, enforce supported source hashes and require no-op/unchanged-object checks. Installer, update migration and complete gameplay QA are future phases, not completed features.
