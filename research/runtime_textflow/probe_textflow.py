"""Read copied assets; map text mutations and bounded typewriter samples."""
from pathlib import Path
import collections
import hashlib
import json
import sys

ROOT = Path(r'D:\Games\Blue Prince_AR')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import UnityPy
from schemas import Schemas
from build_poc import encode


def refs(value, path=''):
    if isinstance(value, dict):
        if set(('m_FileID', 'm_PathID')) <= set(value):
            yield dict(field=path, **value)
        for key, child in value.items():
            yield from refs(child, f'{path}.{key}' if path else key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from refs(child, f'{path}[{i}]')


def main():
    fsm_schema = Schemas('AssetStudio').get('PlayMaker', 'PlayMakerFSM')
    tmp_schemas = Schemas('AssetsTools')
    scripts = json.loads((ROOT / 'research/mono_scripts.json').read_text())
    wanted = {3357, 3404, 3411, 3481, 3500, 3534, 3535}
    level1 = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data/level1'))
    targets = []
    for pid in wanted:
        obj = level1.file.objects[pid]
        base = obj.read_typetree(check_read=False)
        script = scripts[str(base['m_Script']['m_PathID'])]
        node = tmp_schemas.get(script['assembly'], 'TMPro.' + script['name'])
        data = obj.read_typetree(nodes=node)
        assert encode(data, node) == obj.get_raw_data()
        go = level1.file.objects[data['m_GameObject']['m_PathID']].read_typetree()
        targets.append(dict(path_id=pid, gameobject_id=data['m_GameObject']['m_PathID'],
                            gameobject_name=go['m_Name'], text=data['m_text'],
                            components=go['m_Component']))
    target_ids = wanted | {x['gameobject_id'] for x in targets}
    records, counter, direct = [], collections.Counter(), []
    needles = ('setstring', 'buildstring', 'formatstring', 'substring', 'stringreplace',
               'stringlength', 'getstringlength', 'stringjoin', 'textmesh', 'guitext',
               'localiz', 'typewriter', 'settext', 'concat')
    for obj in level1.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        base = obj.read_typetree(check_read=False)
        script = scripts.get(str(base['m_Script']['m_PathID']), {})
        if script.get('name') != 'PlayMakerFSM':
            continue
        data = obj.read_typetree(nodes=fsm_schema)
        assert encode(data, fsm_schema) == obj.get_raw_data()
        go = level1.file.objects[data['m_GameObject']['m_PathID']].read_typetree()
        for state_index, state in enumerate(data['fsm']['states']):
            ad = state['actionData']
            for index, action in enumerate(ad['actionNames']):
                counter[action] += 1
            hits = [dict(index=i, action=x, enabled=ad['actionEnabled'][i])
                    for i, x in enumerate(ad['actionNames']) if any(n in x.lower() for n in needles)]
            matched_refs = [x for x in refs(ad) if x['m_FileID'] == 0 and x['m_PathID'] in target_ids]
            rec = dict(file='level1', path_id=obj.path_id, context=go['m_Name'],
                       owner_gameobject=data['m_GameObject']['m_PathID'],
                       fsm_name=data['fsm']['name'], state_index=state_index,
                       state=state['name'], actions=hits, poc_target_refs=matched_refs,
                       string_variables=data['fsm']['variables']['stringVariables'],
                       fsmStringParams=ad['fsmStringParams'],
                       stringParams=ad['stringParams'], paramName=ad['paramName'],
                       paramDataType=ad['paramDataType'], paramDataPos=ad['paramDataPos'],
                       actionNames=ad['actionNames'], actionEnabled=ad['actionEnabled'],
                       fsmOwnerDefaultParams=ad['fsmOwnerDefaultParams'],
                       fsmPropertyParams=ad['fsmPropertyParams'],
                       actionStartIndex=ad['actionStartIndex'], unityObjectParams=ad['unityObjectParams'],
                       fsmGameObjectParams=ad['fsmGameObjectParams'])
            if hits:
                records.append(rec)
            if matched_refs or data['m_GameObject']['m_PathID'] in target_ids:
                direct.append(rec)
    (OUT / 'level1_textflow.json').write_text(json.dumps(dict(poc_targets=targets,
        action_counts=dict(counter), relevant_states=records, poc_related_states=direct), indent=2))
    print('level1', len(records), 'text states;', len(direct), 'POC-related states', flush=True)
    level2 = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data/level2'))
    samples = []
    for pid in [314189, 314212, 314251]:
        obj = level2.file.objects[pid]
        data = obj.read_typetree(nodes=fsm_schema)
        assert encode(data, fsm_schema) == obj.get_raw_data()
        goid = data['m_GameObject']['m_PathID']
        go = level2.file.objects[goid].read_typetree()
        sample = dict(file='level2', path_id=pid, context=go['m_Name'], gameobject_id=goid,
                      raw_sha256=hashlib.sha256(obj.get_raw_data()).hexdigest(),
                      strict_parse='PASS', exact_byte_noop='PASS', data=data,
                      owner_components=go['m_Component'])
        samples.append(sample)
    (OUT / 'typewriter_samples.json').write_text(json.dumps(samples, indent=2))
    print('level2 typewriter samples saved', len(samples), flush=True)


if __name__ == '__main__':
    main()
