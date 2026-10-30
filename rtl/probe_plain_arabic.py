"""Offline plain-text reference probe; this does not prove Unity rendering."""
import hashlib
import json
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from fontTools.ttLib import TTFont


def main():
    project = Path(__file__).resolve().parent.parent
    inventory = json.loads((project / "fonts/font_inventory.json").read_text(encoding="utf-8"))
    record = next(f for f in inventory["fonts"] if f["name"] == "NotoNaskhArabic-Medium")
    font_path = Path(record["reference"])
    assert hashlib.sha256(font_path.read_bytes()).hexdigest() == record["sha256"]
    cmap = TTFont(font_path).getBestCmap()
    samples = inventory["tests"] + ["اللُّغَةُ العَرَبِيَّةُ", "مرحبا بك"]
    reshaper = arabic_reshaper.ArabicReshaper(configuration={"delete_harakat": False, "shift_harakat_position": True})
    rows = []
    for source in samples:
        shaped = reshaper.reshape(source)
        visual = get_display(shaped)
        logical_missing = sorted(set(c for c in source if not c.isspace() and ord(c) not in cmap))
        visual_missing = sorted(set(c for c in visual if not c.isspace() and ord(c) not in cmap))
        assert not logical_missing, (source, logical_missing)
        assert not visual_missing, (source, visual_missing)
        for latin_run in ["27", "HP: 100", "Blue Prince", "46", "HP 75%"]:
            if latin_run in source:
                assert latin_run in visual, (source, visual, latin_run)
        rows.append({"logical": source, "plain_shaped_visual_order": visual, "visual_codepoints": [f"U+{ord(c):04X}" for c in visual], "logical_missing": logical_missing, "visual_missing": visual_missing})
    output = {"status": "PASS: offline plain-string glyph coverage and preserved Latin/numeric runs only", "game_rendering": "NOT TESTED", "limitations": ["No rich text, substitutions, line wrapping or typewriter integration is implemented by this probe.", "Do not inject visual-order strings until game native processing and double reversal are tested.", "Font GSUB/GPOS existence does not prove that Unity invokes it."], "font_sha256": record["sha256"], "samples": rows}
    (project / "rtl/plain_arabic_probe.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(rows)} plain reference samples have zero missing logical/shaped glyphs; Unity rendering NOT TESTED")


if __name__ == "__main__":
    main()
