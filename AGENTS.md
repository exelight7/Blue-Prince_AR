# Agent instructions - Blue Prince Arabic localization

Read `HANDOFF.md` first: it has the current state, the repo map, the workflows, the open items and the rules. `README.md` is the user-facing install guide (Arabic). The author's earlier AI memory notes are in `docs/ai-memory/`.

Hard rules:
- The user writes Arabic: answer in Arabic.
- Never modify the original game folder. The only write to it is `release/BluePrince_Arabic/install.ps1` (reversible with `uninstall.ps1`), and only when the user asks.
- Do not launch the game without the user's clear permission, and never delete saves or profiles.
- Do not commit game files (`runtime_test/`, `backups/`, `extracted/`, `fonts/original/` are git-ignored).
- Write JSON, regex, C# and PowerShell files with file-write tools, not shell heredocs (backslashes get halved). Use `python -X utf8` for Arabic output.
- After changing translations: `python tools/merge_batches.py` (0 rejects), `sh tools/deploy_plugin.sh ar.json`, `python -X utf8 tools/build_release.py`, and update `HANDOFF.md` if the state changed.
