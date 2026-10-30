"""Build a seven-string asset-only POC; never install or launch the game."""
import copy
import hashlib
import json
import UnityPy
from UnityPy.helpers.TypeTreeHelper import write_typetree
from UnityPy.streams import EndianBinaryWriter
from bidi.algorithm import get_display
import arabic_reshaper
from project import ROOT, sha256, write_new
from schemas import Schemas
from validate import validate


TRANSLATIONS = {
    3357: 'لعبة جديدة',
    3481: 'متابعة',
    3500: 'إنهاء اللعبة',
    3534: 'الإعدادات',
    3411: 'مستوى الصوت',
    3535: 'هذا هو مستوى الصعوبة\nالأصلي والاعتيادي للعبة. تبدأ\nكل يوم ولديك 50 خطوة.',
    3404: 'اضبط إعدادات الشاشة أو التلفاز حتى يكاد يظهر رمز Mt. Holly أعلاه، وتختفي الصور في الزوايا.\n\nاضغط [ENTER] عندما تنتهي.',
}


def encode(data, node):
    writer = EndianBinaryWriter(endian='<')
    write_typetree(data, node, writer)
    return writer.bytes


def main():
    if not __debug__:
        raise RuntimeError('POC integrity checks require Python without -O')
    source = ROOT / 'backups/source/BLUE PRINCE_Data/level1'
    baseline_rows = json.loads((ROOT / 'reference/source_inventory.json').read_text())
    required_inputs = {'BLUE PRINCE_Data/level1', 'BLUE PRINCE_Data/sharedassets1.assets',
        'BLUE PRINCE_Data/globalgamemanagers.assets', 'GameAssembly.dll',
        'BLUE PRINCE_Data/il2cpp_data/Metadata/global-metadata.dat'}
    for row in baseline_rows:
        if row['path'] in required_inputs:
            if sha256(ROOT / 'backups/source' / row['path']) != row['sha256']:
                raise ValueError(f"Copied source hash differs: {row['path']}")
    schemas = Schemas()
    scripts = json.loads((ROOT / 'research/mono_scripts.json').read_text())
    baseline = UnityPy.load(str(source))
    source_objects = {o.path_id: o.get_raw_data() for o in baseline.objects}
    source_types = {o.path_id: o.type for o in baseline.objects}
    assert baseline.file.externals[1].path == 'sharedassets1.assets'
    entries, nodes, original = [], {}, {}
    for pid, arabic in TRANSLATIONS.items():
        obj = baseline.file.objects[pid]
        common = obj.read_typetree(check_read=False)
        script = scripts[str(common['m_Script']['m_PathID'])]
        assert script['name'] in ('TextMeshPro', 'TextMeshProUGUI')
        node = schemas.get(script['assembly'], 'TMPro.' + script['name'])
        data = obj.read_typetree(nodes=node)
        assert encode(data, node) == obj.get_raw_data(), f'No-op differs: {pid}'
        nodes[pid], original[pid] = node, data
        entries.append(dict(ID=f'level1:{pid}:m_text', Context=script['name'],
            Source=data['m_text'], Arabic=arabic, File='level1', Category='POC',
            Notes='Temporary draft; requires visual gameplay review', Status='POC_ONLY'))
    errors = validate(entries, json.loads((ROOT / 'translation/source/strings.json').read_text()))
    if errors:
        raise ValueError(errors)
    write_new(ROOT / 'translation/arabic/poc.json', entries)
    results, changes = [], []
    for variant in ('logical', 'preshaped_visual'):
        env = UnityPy.load(str(source))
        expected = {}
        for pid, arabic in TRANSLATIONS.items():
            data = copy.deepcopy(original[pid])
            text = arabic
            if variant == 'preshaped_visual':
                text = '\n'.join(get_display(arabic_reshaper.reshape(line), base_dir='R')
                                 if line else '' for line in arabic.split('\n'))
            data['m_text'] = text
            data['m_fontAsset'] = {'m_FileID': 2, 'm_PathID': 244}
            data['m_sharedMaterial'] = {'m_FileID': 2, 'm_PathID': 43}
            # Visual-order preprocessed text must not be reversed again by TMP.
            data['m_isRightToLeft'] = 1 if variant == 'logical' else 0
            if pid == 3534:
                data['m_enableAutoSizing'] = 1
            changes.append(dict(variant=variant, path_id=pid,
                fields={key: dict(before=original[pid].get(key), after=value)
                        for key, value in data.items() if original[pid].get(key) != value}))
            expected[pid] = data
            env.file.objects[pid].set_raw_data(encode(data, nodes[pid]))
        output = env.file.save()
        dest = ROOT / f'build/poc/{variant}/BLUE PRINCE_Data/level1'
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != output:
            raise FileExistsError(f'Refusing to overwrite different POC: {dest}')
        if not dest.exists():
            dest.write_bytes(output)
        reload = UnityPy.load(str(dest))
        assert set(reload.file.objects) == set(source_objects)
        changed = []
        for pid, raw in source_objects.items():
            obj = reload.file.objects[pid]
            assert obj.type == source_types[pid]
            if pid in expected:
                assert obj.read_typetree(nodes=nodes[pid]) == expected[pid]
                assert encode(expected[pid], nodes[pid]) == obj.get_raw_data()
                changed.append(pid)
            else:
                assert obj.get_raw_data() == raw, f'Unexpected object change: {pid}'
        assert reload.file.save() == output, 'Second save is not byte-idempotent'
        results.append(dict(variant=variant, sha256=sha256(dest), bytes=len(output),
            changed_object_ids=changed, unchanged_objects=len(source_objects)-len(changed),
            strict_reparse='PASS', unchanged_object_bytes='PASS', idempotent_save='PASS',
            in_game_rendering='NOT_TESTED'))
    write_new(ROOT / 'tests/poc_results.json', results)
    write_new(ROOT / 'tests/poc_change_manifest.json', dict(source_sha256=sha256(source),
        application_version='1.0.5.0', engine='2021.3.45f1', changes=changes))
    print(json.dumps(results, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
