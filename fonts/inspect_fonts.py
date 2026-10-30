"""Read-only inventory of embedded Unity fonts and Arabic cmap coverage."""
import hashlib
import io
import json
import re
from pathlib import Path

import UnityPy
from fontTools.ttLib import TTFont

GAME = Path(r"D:\Games\Blue Prince\BLUE PRINCE_Data")
OUT = Path(__file__).resolve().parent
TESTS = ["ابتسم، فكل شيء ممكن.", "الغرفة رقم 27", "HP: 100", "اضغط E لفتح الباب", "Blue Prince - الأمير الأزرق", "لا لأ لإ لآ ة ى ئ ؤ ء أ إ آ", "اضغط E للمتابعة", "Room 46 - الغرفة", "HP 75%"]


def inspect():
    records = []
    for filename in ["resources.assets", "sharedassets0.assets", "sharedassets1.assets", "sharedassets2.assets", "globalgamemanagers.assets", "Resources/unity default resources"]:
        asset_path = GAME / filename
        if not asset_path.exists():
            continue
        env = UnityPy.load(str(asset_path))
        for obj in env.objects:
            if obj.type.name != "Font":
                continue
            tree = obj.read_typetree()
            data = bytes(x % 256 for x in tree["m_FontData"])
            name = tree["m_Name"]
            record = {"file": filename, "path_id": obj.path_id, "name": name, "font_names": tree["m_FontNames"], "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "fallback_fonts": tree["m_FallbackFonts"], "serialized_character_rect_count": len(tree["m_CharacterRects"]), "rendering_mode": tree["m_FontRenderingMode"]}
            if data:
                destination = OUT / "original" / (filename.replace("/", "_") + "__" + str(obj.path_id) + "__" + re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".ttf")
                destination.parent.mkdir(exist_ok=True)
                if destination.exists():
                    assert destination.read_bytes() == data, "Refusing to overwrite different reference font"
                else:
                    destination.write_bytes(data)
                font = TTFont(io.BytesIO(data))
                cmap = font.getBestCmap() or {}
                record.update({"reference": str(destination), "cmap_count": len(cmap), "arabic_block_count": sum(0x600 <= c <= 0x6ff for c in cmap), "arabic_presentation_forms_a_count": sum(0xfb50 <= c <= 0xfdff for c in cmap), "arabic_presentation_forms_b_count": sum(0xfe70 <= c <= 0xfeff for c in cmap), "gsub": "GSUB" in font, "gpos": "GPOS" in font, "test_missing": [{"text": text, "missing": sorted(set(ch for ch in text if not ch.isspace() and ord(ch) not in cmap))} for text in TESTS]})
                record["license"] = [{"name_id": n.nameID, "text": n.toUnicode()} for n in font["name"].names if n.nameID in [13, 14] and n.platformID == 3]
                record["western_digits"] = all(ord(ch) in cmap for ch in "0123456789")
                record["arabic_indic_digits"] = all(ord(ch) in cmap for ch in "٠١٢٣٤٥٦٧٨٩")
                record["latin_ascii"] = all(c in cmap for c in range(32, 127))
                font.close()
            records.append(record)
        del env
    output = {"scope": "Native Font objects in all loose serialized assets and Unity default resources. Bundle counts supplied separately by parent extraction. TMP assets require recovered schemas.", "tests": TESTS, "fonts": records}
    (OUT / "font_inventory.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{"name": r["name"], "file": r["file"], "path_id": r["path_id"], "bytes": r["bytes"], "arabic": r.get("arabic_block_count"), "forms_b": r.get("arabic_presentation_forms_b_count"), "missing_counts": [len(t["missing"]) for t in r.get("test_missing", [])]} for r in records], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    inspect()
