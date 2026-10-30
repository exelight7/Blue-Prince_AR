"""Build matched asset-only A/B Arabic runtime matrices; preserve the previous POC."""
import copy
import json
import re
import shutil
import sys
import UnityPy
import arabic_reshaper
from bidi.algorithm import get_display
from build_poc import encode
from project import ROOT, sha256, write_new
from schemas import Schemas

CASES = {
    3568: ('greeting', 'مرحبا بك في القصر'),
    3481: ('lamalef_punctuation', 'لا تفتح هذا الباب\nلا   لأ   لإ   لآ\nمرحبا، كيف حالك؟'),
    3534: ('number', 'الغرفة رقم 27'),
    3500: ('mixed_key', 'اضغط E لفتح الباب'),
    3411: ('latin_control', 'HP: 100'),
    3446: ('mixed_title', 'Blue Prince - الأمير الأزرق'),
    3456: ('wrapping', 'هذا اختبار طويل للتأكد من أن النص العربي يلتف داخل مساحة الواجهة بشكل صحيح ولا يخرج خارج حدود العنصر.'),
}


def main():
    if not __debug__:
        raise RuntimeError('Run Python without -O; integrity checks are mandatory')
    schema = Schemas()
    scripts = json.loads((ROOT / 'research/mono_scripts.json').read_text())
    source = ROOT / 'backups/source/BLUE PRINCE_Data/level1'
    env = UnityPy.load(str(source))
    originals = {o.path_id:o.get_raw_data() for o in env.objects}
    data_by_id, nodes = {}, {}
    for pid in CASES:
        obj = env.file.objects[pid]
        header = obj.read_typetree(check_read=False)
        script = scripts[str(header['m_Script']['m_PathID'])]
        node = schema.get(script['assembly'], f"TMPro.{script['name']}")
        data = obj.read_typetree(nodes=node)
        assert encode(data,node) == originals[pid]
        nodes[pid], data_by_id[pid] = node, data
    outputs = []
    for label, logical in [('a',True),('b',False)]:
        scene = UnityPy.load(str(source))
        changes, expected = [], {}
        for pid,(case,text) in CASES.items():
            data = copy.deepcopy(data_by_id[pid])
            data['m_text'] = text if logical else '\n'.join(
                get_display(arabic_reshaper.reshape(line),base_dir='R')
                if re.search(r'[\u0600-\u06ff]',line) else line for line in text.split('\n'))
            data['m_fontAsset'] = dict(m_FileID=2,m_PathID=244)
            data['m_sharedMaterial'] = dict(m_FileID=2,m_PathID=43)
            data['m_isRightToLeft'] = int(logical and bool(re.search(r'[\u0600-\u06ff]',text)))
            # Latin display-font tracking and old auto-size bounds are not Arabic controls.
            data['m_characterSpacing'] = 0.0
            data['m_wordSpacing'] = 0.0
            data['m_lineSpacing'] = 0.0
            data['m_fontStyle'] = 0
            data['m_enableAutoSizing'] = int(case in ('lamalef_punctuation','wrapping','mixed_title'))
            data['m_fontSizeMin'] = 1.0
            data['m_fontSizeMax'] = 2.5
            if case == 'wrapping':
                data['m_enableWordWrapping'] = 1
            expected[pid] = data
            scene.file.objects[pid].set_raw_data(encode(data,nodes[pid]))
            changes.append(dict(path_id=pid,case=case,logical_text=text,
                original_text=data_by_id[pid]['m_text'],
                fields={k:dict(before=data_by_id[pid].get(k),after=v) for k,v in data.items()
                        if data_by_id[pid].get(k)!=v}))
        path = ROOT / f'build/runtime_matrix_v2/{label}/BLUE PRINCE_Data/level1'
        path.parent.mkdir(parents=True,exist_ok=True)
        result = scene.file.save()
        if path.exists() and path.read_bytes()!=result:
            raise FileExistsError(path)
        if not path.exists():path.write_bytes(result)
        reload=UnityPy.load(str(path))
        for pid,raw in originals.items():
            if pid in CASES:
                assert reload.file.objects[pid].read_typetree(nodes=nodes[pid]) == expected[pid]
            else:
                assert reload.file.objects[pid].get_raw_data()==raw
        assert reload.file.save()==result
        outputs.append(dict(variant=label,method='logical TMP RTL' if logical else 'pre-shaped visual, TMP RTL disabled',
            path=str(path),sha256=sha256(path),source_sha256=sha256(source),
            changed_objects=list(CASES),untouched_objects=len(originals)-len(CASES),
            integrity='PASS',changes=changes))
    write_new(ROOT/'tests/runtime_matrix_v2_manifest.json',outputs)
    print('PASS: matched seven-case A/B runtime matrix, strict reparse and 4,253 unchanged objects')


if __name__=='__main__':
    main()
