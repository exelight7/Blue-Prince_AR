"""Bounded, read-only PlayMaker schema comparison on workspace backup copies."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(r'D:\Games\Blue Prince_AR')
sys.path.insert(0, str(ROOT / 'tools'))
from schemas import Schemas
import UnityPy

OUTPUT = Path(__file__).resolve().parent
SCRIPTS = json.loads((ROOT / 'research/mono_scripts.json').read_text(encoding='utf-8'))


def strings(value, prefix=''):
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, f'{prefix}.{key}' if prefix else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f'{prefix}[{index}]')


def run():
    report_path = OUTPUT / 'playmaker_backend_comparison.json'
    if report_path.exists():
        raise FileExistsError(report_path)
    print('Initializing trusted project schema adapters', flush=True)
    generators = {name: Schemas(name) for name in ('AssetsTools', 'AssetStudio')}
    result = []
    for filename in ('level0', 'level1'):
        env = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data' / filename))
        sampled = 0
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            header = obj.read_typetree(check_read=False)
            script = SCRIPTS.get(str(header['m_Script']['m_PathID']), {})
            if script.get('name') != 'PlayMakerFSM':
                continue
            sampled += 1
            raw = obj.get_raw_data()
            item = {'file': filename, 'path_id': obj.path_id, 'raw_sha256': hashlib.sha256(raw).hexdigest(),
                    'size': len(raw), 'backends': {}}
            fullname = '.'.join(filter(None, [script['namespace'], script['name']]))
            for backend, generator in generators.items():
                attempt = {}
                try:
                    node = generator.get(script['assembly'], fullname)
                    tree = obj.read_typetree(nodes=node)
                    assert tree['m_Script'] == header['m_Script']
                    attempt['strict_parse'] = 'PASS'
                    go = obj.assets_file.objects.get(tree.get('m_GameObject', {}).get('m_PathID'))
                    attempt['context'] = go.read().m_Name if go and go.type.name == 'GameObject' else tree.get('m_Name')
                    attempt['top_keys'] = list(tree)
                    found = list(strings(tree))
                    attempt['string_count'] = len(found)
                    attempt['action_and_text_fields'] = [dict(field=k, text=v) for k, v in found
                        if any(x in (k + ' ' + v).lower() for x in ('actionname', 'typewriter', 'videotext', 'subtitle'))]
                    obj.save_typetree(tree, nodes=node)
                    attempt['exact_byte_noop'] = 'PASS' if obj.get_raw_data() == raw else 'FAIL'
                    attempt['reserialized_size'] = len(obj.get_raw_data())
                    obj.set_raw_data(raw)
                except Exception as error:
                    attempt['strict_parse'] = 'FAIL'
                    attempt['error'] = str(error)
                    obj.set_raw_data(raw)
                item['backends'][backend] = attempt
            result.append(item)
            print(filename, obj.path_id, {k: (v.get('strict_parse'), v.get('exact_byte_noop'), v.get('error'))
                                         for k, v in item['backends'].items()}, flush=True)
            if sampled >= 8:
                break
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    run()
