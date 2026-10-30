# Problems and gates

Updated: 2026-10-28, Asia/Riyadh.

| ID | Status | Evidence / effect | Next resolution |
|---|---|---|---|
| P01 | PARTIAL | Runtime A/B screenshots now exist. B passes sampled static cases; the final eleven-label menu is prepared offline and not visually retested. | Keep full-game claims gated. User currently prohibits new launches. |
| P02 | RESOLVED for sampled direct routing | Font244/material43 rendered sampled Arabic and presentation forms. Ordinary/global fallback still does not route most UI to Arabic. | Use targeted routing; automatic fallback behavior remains unverified. |
| P03 | PARTIAL | A failed shaping and reversed27. B passed sampled static shaping/BiDi. Native wrap reversed lines; logical prewrap fixed order and a size adjustment removed sample overlap. | Validate other layouts, dynamic/rich text and widths later; no blanket preprocessing. |
| P04 | RESOLVED for selected classes | All11,815 first-pass failures recovered:11,605 FSMs,37 templates,172 arrays and one key list. All12,010 FSM/template and748 array objects now pass strict/no-op checks. | Use AssetStudio for these generic types. Other custom classes still require their own validation. |
| P05 | OPEN / INCONCLUSIVE | 535 enabled typewriter references found. Injected menu probes did not produce a valid progressive control, including English. | Resolve the genuine initialization/action path offline; do not label Arabic reveal PASS, FAIL or N/A from an invalid control. |
| P06 | OPEN |Six texture samples visually reviewed; English map labels, Latin glyph atlas and puzzle typography confirmed. Remaining texture/video review is incomplete. | Continue selective contextual review; preserve letter-dependent puzzle behavior. |
| P07 | OPEN | Only 74 English keyed entries; most text is outside the small table. Hardcoded candidates lack callsite evidence. | Extend structured mapping across TMP, PlayMaker, language arrays, subtitles and image text. |
| P08 | OPEN | Static menu matrix was observed, including lam-alef and punctuation, but no confirmed live dialogue/subtitle or valid progressive reveal. Continue label was hidden without a save. | Keep these cases explicitly unverified; final meaningful labels need later visual review. |
| P09 | OPEN | Existing runtime language selection, Italian completeness, absent-key fallback and AlternativeFont behavior unknown. | Controlled observation from copied assets; preserve original English fallback until proven. |
| P10 | OPEN | Content/puzzle-specific Arabic wording and visual identity require contextual review. | Build room/item/character/pun glossary from actual contexts; do not mass translate yet. |

Resolved engineering findings: AssetsTools schema calls require extensionless assembly names; native enabled-byte alignment corrected before tree creation. AssetRipper-generated arrays were unsuitable for the tested objects. These fixes do not justify accepting other incomplete parses.

Risk policy: 🟩 LOW inspection/extraction; 🟨 MEDIUM copied-asset repacking/fonts/experiments; 🟥 HIGH executable/DRM/destructive branches are not performed automatically. None performed.

Current constraint: the user asked to continue offline without launching the game. No new launches until that instruction is explicitly changed. Remaining issues are not an authorization to patch executable code.
