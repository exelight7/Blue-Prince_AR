# Report001 — source preservation and forensic baseline

Recorded: 2026-10-28T10:33:16+03:00 (Asia/Riyadh). Project `D:\Games\Blue Prince_AR`; source `D:\Games\Blue Prince` read-only.

CONFIRMED engine Unity2021.3.45f1, IL2CPP metadata31, PE AMD64. PlayerSettings: Dogubomb, BLUE PRINCE,1.0.5.0. Main Menu is level1 and Mount Holly Estate level2.56 source files totaling4,162,841,374 bytes inventoried with SHA-256; selected source containers and metadata were copied and verified. Five Addressables UnityFS bundles parsed; settings specify Addressables1.19.19. No game binary executed or modified. Nothing uploaded, committed, pushed or published.

Custom key localization, TMP components, PlayMaker, timed subtitle declarations and embedded Arabic font found. These are static findings, not a working Arabic localization. Evidence: reference/source_inventory.json, research/build_identity.json, research/asset_summary.json, research/metadata/, fonts/ and rtl/.

Existing installed libraries were preferred. Only the official TypeTreeGeneratorAPI0.0.10 wheel was added project-locally to recover stripped schemas; SHA-256e96003e973c8d52d221b4ae50f377bcaf7538f2098e437d5383a1b7f13fa72ba matches PyPI. Scripts read copied GameAssembly/metadata as data. Generated schemas require backend-specific handling and complete-byte checks.

Risk: 🟩 LOW for inspection/copying/parsing; later copied-asset/font POC is 🟨 MEDIUM. 🟥 HIGH executable/DRM work is outside automatic scope. Next: map text schemas, verify a tiny asset roundtrip and identify rendering gates. Full translation must wait for a genuine rendering test.
