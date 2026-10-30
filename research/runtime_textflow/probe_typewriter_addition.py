"""Verify an asset-only typewriter addition IN MEMORY; save only JSON evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(r'D:\Games\Blue Prince_AR')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import UnityPy
from schemas import Schemas
from build_poc import encode


def main():
    path = ROOT / 'backups/source/BLUE PRINCE_Data/level1'
    env = UnityPy.load(str(path))
    baseline = {o.path_id: o.get_raw_data() for o in env.objects}
    source = json.loads((OUT / 'typewriter_samples.json').read_text())[0]['data']
    data = copy.deepcopy(source)
    target_go, target_tmp, new_id = 170, 3411, 1000000001
    if new_id in env.file.objects:
        raise ValueError('Experimental object ID collision')
    node = Schemas('AssetStudio').get('PlayMaker', 'PlayMakerFSM')
    data['m_GameObject'] = dict(m_FileID=0, m_PathID=target_go)
    data['fsm']['name'] = 'Arabic typewriter POC only'
    data['fsm']['startState'] = 'State 4'
    for state in data['fsm']['states']:
        state['actionData']['fsmPropertyParams'][0]['TargetObject']['value'] = dict(m_FileID=0,m_PathID=target_tmp)
    action = data['fsm']['states'][0]['actionData']
    action['fsmStringParams'][0]['value'] = 'مرحبا بك في القصر، الغرفة رقم 27.'
    action['fsmFloatParams'][0]['value'] = 0.25
    action['byteData'][0] = 0  # richText false for the plain-string probe.
    assert action['byteData'] == [0, 0, 1, 1]
    # Copy a wrapper already using the same file-local serialization type and script.
    wrapper = env.file.objects[3741]
    assert wrapper.read_typetree(check_read=False)['m_Script'] == data['m_Script']
    added = copy.copy(wrapper)
    added.path_id = new_id
    added.set_raw_data(encode(data, node))
    env.file.objects[new_id] = added
    go_obj = env.file.objects[target_go]
    go = go_obj.read_typetree()
    go_obj.save_typetree(go)
    assert go_obj.get_raw_data() == baseline[target_go]
    go['m_Component'].append(dict(component=dict(m_FileID=0,m_PathID=new_id)))
    go_obj.save_typetree(go)
    result = env.file.save()
    reopened = UnityPy.load(result)
    assert len(reopened.file.objects) == len(baseline)+1
    assert reopened.file.objects[new_id].read_typetree(nodes=node) == data
    assert reopened.file.objects[target_go].read_typetree() == go
    for pid, raw in baseline.items():
        if pid != target_go:
            assert reopened.file.objects[pid].get_raw_data() == raw, pid
    assert reopened.file.save() == result
    evidence = dict(status='PASS_IN_MEMORY_ONLY', game_launched=False, asset_file_written=False,
        source_scene=str(path), original_scene_objects=len(baseline), new_scene_objects=len(reopened.file.objects),
        reused_wrapper_id=3741, wrapper_type_id=wrapper.type_id, new_object_id=new_id,
        target_gameobject=target_go, target_tmp=target_tmp,
        unchanged_existing_objects=len(baseline)-1, modified_existing_objects=[target_go],
        strict_added_fsm_parse='PASS', exact_existing_object_payloads='PASS',
        deterministic_second_save='PASS', serialized_bytes=len(result),
        serialized_sha256=hashlib.sha256(result).hexdigest(), runtime_execution='NOT_TESTED')
    (OUT / 'typewriter_addition_probe.json').write_text(json.dumps(evidence,indent=2))
    (OUT / 'adapted_typewriter_data.json').write_text(json.dumps(data,indent=2))
    print(json.dumps(evidence,indent=2))


if __name__ == '__main__':
    main()
