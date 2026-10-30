"""Inspect TMP assets on forensic copies, with strict parsing and no-op checks."""
import hashlib
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools/vendor"))
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.helpers.TypeTreeNode import TypeTreeNode


def schema(generator, classname):
    raw = generator.get_nodes("Unity.TextMeshPro", "TMPro." + classname)
    for field in raw:
        if field.m_Level == 1 and field.m_Name == "m_Enabled":
            field.m_MetaFlag |= 0x4000  # Match native MonoBehaviour's three padding bytes.
    return TypeTreeNode.from_list([TypeTreeNode(f.m_Level, f.m_Type, f.m_Name, 0, 0, m_MetaFlag=f.m_MetaFlag) for f in raw])


def inspect():
    source = PROJECT / "backups/source"
    generator = TypeTreeGenerator("2021.3.45f1", generator="AssetsTools")
    generator.load_local_game(str(source))
    scripts = json.loads((PROJECT / "research/mono_scripts.json").read_text(encoding="utf-8"))
    classes = {int(k): v["name"] for k, v in scripts.items() if v["assembly"] == "Unity.TextMeshPro.dll" and v["name"] in ["TMP_FontAsset", "TMP_Settings"]}
    nodes = {c: schema(generator, c) for c in set(classes.values())}
    evidence = []
    for filename in ["resources.assets", "sharedassets0.assets", "sharedassets1.assets", "sharedassets2.assets"]:
        env = UnityPy.load(str(source / "BLUE PRINCE_Data" / filename))
        objects = {o.path_id: o for o in env.objects}
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            base = obj.read_typetree(check_read=False)
            classname = classes.get(base.get("m_Script", {}).get("m_PathID"))
            if classname is None:
                continue
            tree = obj.read_typetree(nodes=nodes[classname])
            before = obj.get_raw_data()
            obj.save_typetree(tree, nodes=nodes[classname])
            after = obj.get_raw_data()
            assert after == before, (filename, obj.path_id, "No-op serializer changed bytes")
            row = {"file": filename, "path_id": obj.path_id, "class": classname, "name": tree["m_Name"], "raw_sha256": hashlib.sha256(before).hexdigest(), "strict_parse": "PASS", "byte_identical_noop": "PASS"}
            if classname == "TMP_FontAsset":
                chars = [c["m_Unicode"] for c in tree["m_CharacterTable"]]
                row.update({k: v for k, v in tree.items() if k in ["m_Version", "m_SourceFontFile", "m_AtlasPopulationMode", "material", "m_AtlasTextures", "m_AtlasWidth", "m_AtlasHeight", "m_AtlasPadding", "m_AtlasRenderMode", "m_IsMultiAtlasTexturesEnabled", "m_ClearDynamicDataOnBuild", "fallbackFontAssets", "m_FallbackFontAssetTable", "m_FontWeightTable", "normalStyle", "boldStyle", "italicStyle"]})
                row.update({"glyph_count": len(tree["m_GlyphTable"]), "character_count": len(chars), "arabic_character_count": sum(0x600 <= c <= 0x6ff for c in chars), "presentation_character_count": sum(0xfb50 <= c <= 0xfeff for c in chars), "characters": chars, "face": tree["m_FaceInfo"]})
                material_ref = tree["material"]
                if material_ref["m_FileID"] == 0 and material_ref["m_PathID"] in objects:
                    material = objects[material_ref["m_PathID"]].read_typetree()
                    row["material_details"] = {k: v for k, v in material.items() if k in ["m_Name", "m_Shader", "m_CustomRenderQueue", "m_ValidKeywords", "m_InvalidKeywords"]}
                row["atlas_details"] = []
                for ref in tree["m_AtlasTextures"]:
                    if ref["m_FileID"] == 0 and ref["m_PathID"] in objects:
                        texture = objects[ref["m_PathID"]].read_typetree()
                        row["atlas_details"].append({"path_id": ref["m_PathID"], **{k: v for k, v in texture.items() if k in ["m_Name", "m_Width", "m_Height", "m_TextureFormat", "m_IsReadable"]}})
            else:
                row["settings"] = tree
            evidence.append(row)
        del env
    output = {"schema_backend": "TypeTreeGeneratorAPI 0.0.10 / AssetsTools / assembly without .dll; native MonoBehaviour enabled alignment corrected", "scope": "TMP_FontAsset and TMP_Settings in loose resources/sharedassets0-2 copies. Every matching object strictly parsed and serialized to identical bytes in memory; files not modified.", "assets": evidence}
    (PROJECT / "fonts/tmp_inventory.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k in ["file", "path_id", "class", "name", "m_AtlasPopulationMode", "m_FallbackFontAssetTable", "character_count", "arabic_character_count", "byte_identical_noop"]} for r in evidence], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    inspect()
