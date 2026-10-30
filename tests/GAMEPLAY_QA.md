> **Historical.** Superseded by `HANDOFF.md` (2026-10-30), which has the current state, counts and next steps. The text below is kept as a record and may be out of date.

# Gameplay and rendering QA

Updated: 2026-10-28, Asia/Riyadh. Runtime observations preceded the user's current offline-only instruction. No new launch is authorized by this matrix.

| Area | Result | Evidence / scope |
|---|---|---|
| Main Menu | PARTIAL | A/B diagnostic labels observed; final eleven-label menu only checked offline |
| Settings | PARTIAL | Mixed text, numbers and paragraph samples observed; final labels not visually retested |
| New Game / Load Game | BLOCKED | Entry labels are not proof that game/save loading works |
| Gameplay HUD / Dialogue / Subtitles | BLOCKED | No representative gameplay rendering test completed |
| Items / Rooms / Puzzle UI / Tutorials | BLOCKED | Source inspection only |
| Notes/Documents / Pause / Game Over | BLOCKED | Source inspection only |
| Save/Load | BLOCKED | No save compatibility or restore test; no save deletion |
| Credits | BLOCKED | Menu heading prepared; body/screen not reviewed |

## Rendering cases

| Case | A | B / follow-up |
|---|---|---|
| Arabic glyph availability | PASS sampled | PASS sampled |
| Joining / shaping | FAIL | PASS sampled |
| Number27 | FAIL:72 | PASS:27 |
| HP:100 / Latin control | Not assessed | PASS static sample |
| Arabic + E / Blue Prince | PARTIAL | PASS static samples |
| Lam-alef / punctuation | Not assessed | PASS captured lam-alef probe |
| Automatic wrap of visual-order paragraph | Not assessed | FAIL: logical line order reversed |
| Logical wrap before shaping/BiDi | Not assessed | PASS for recorded17-em paragraph |
| Paragraph overlap | Not assessed | FAIL initially; corrected with1.5 font cap in v4 |
| Alignment | Limited | Centered sampled UI fits after adjustment |
| Progressive/typewriter | Not tested | INCONCLUSIVE: injected menu control not validated, including English |
| Dynamic substitutions / tags | Not tested | Not supported by current plain helper |
| Diacritic placement | Not tested | Data retention passes offline; placement not tested |
| Automatic font fallback | Not tested | Direct Arabic asset routing tested; fallback remains unverified |
| Final meaningful eleven-label menu | Not applicable | OFFLINE PASS; visual check deferred by user instruction |

Eighteen screenshots are listed and hashed in screenshot_evidence_003.json. Runtime result details are in runtime_results_003.json. Typewriter is never N/A: game-owned action references exist. A valid progressive control is required before a language-direction conclusion.
