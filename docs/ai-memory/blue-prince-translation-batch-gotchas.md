---
name: blue-prince-translation-batch-gotchas
description: "Blue Prince Arabic batch tooling quirks (tr_prefix startswith, validator key/?? rules, keep.json, {ICON}, corpus tiers) learned finishing tiers 0/1/3"
metadata:
  node_type: memory
  type: project
  originSessionId: 054393d5-bbd6-4581-954f-d1c053fc45e2
  modified: 2026-10-29T07:48:03.167Z
---

State after 2026-10-29 translation session: `show_docs.py 0 {0,1,3}` all print `0 left`, merge `rejected 0`, ar.json ~5228 entries (112 with `{ICON}`), exceptions in `translation/work/b_exceptions.md`, overrides in `translation/arabic/batches/b901_quality.json` (sorts last, wins over every other batch).

**Why:** future sessions extend or polish these batches and hit the same traps.

**How to apply:**
- `tr_prefix.py` uses plain `startswith` and gives ALL hits the same Arabic, so a short key that prefixes a longer source silently clobbers it (once it wrongly marked a translatable sentence as kept). Prefer exact (strip-equal) match first and print every non-exact hit before trusting a batch.
- `merge_batches.check`: `[word]` (<=10 letters) and `{abc}` count as keys, so `[entrance]` cannot be translated (keep it); a literal `??` in Arabic is rejected (use ؟؟؟); `{ICON}` is stripped before the tag/key/number comparison; newline count mismatch is only a warning (55 old ones are baseline).
- `show_docs.py` hides a source when its tag-stripped lowercase text already exists in any batch or `keep.json`; deliberate English goes into `keep.json` (identity entry) and is documented in `b_exceptions.md`.
- Leading whitespace/newlines of a source are NOT added by merge; helpers must re-apply them. Tag-line strings keep their `   <size=4> </size>` padding (not `{ICON}`), like the older entries.
- Terms settled this session: draw floorplans = سحب, draft = اختيار, ALLOWANCE = الحصة/حصتك, Terminal = الطرفية/جهاز, keycard = بطاقة المفتاح, Contraption = الابتكار المرتجل, Drawing Room = غرفة الجلوس, Orindia = أورينديا, no tashkeel except fathatan.
