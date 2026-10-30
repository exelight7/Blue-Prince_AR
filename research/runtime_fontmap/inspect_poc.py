"""Read-only POC component/font evidence. Writes only this research directory."""
import json
import sys
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import UnityPy
from schemas import Schemas
from build_poc import encode

PIDS = [3357, 3404, 3411, 3481, 3500, 3534, 3535]


def hierarchy(env, gameobject_id):
    result, seen = [], set()
    while gameobject_id and gameobject_id not in seen:
        seen.add(gameobject_id)
        obj = env.file.objects.get(gameobject_id)
        if not obj:
            break
        data = obj.read_typetree()
        item = dict(path_id=gameobject_id, name=data['m_Name'], active=data.get('m_IsActive'))
        transform = None
        for comp in data.get('m_Component', []):
            compid = comp['component']['m_PathID']
            c = env.file.objects.get(compid)
            if c and c.type.name in ('RectTransform', 'Transform'):
                transform = c.read_typetree()
                item['transform_id'] = compid
                item['transform_type'] = c.type.name
                item['transform'] = {k:v for k,v in transform.items() if k not in ('m_GameObject','m_Children')}
                break
        result.append(item)
        if not transform:
            break
        father_id = transform.get('m_Father', {}).get('m_PathID')
        father = env.file.objects.get(father_id)
        gameobject_id = father.read_typetree()['m_GameObject']['m_PathID'] if father else 0
    return result


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    schemas = Schemas('AssetsTools')
    scripts = json.loads((ROOT/'research/mono_scripts.json').read_text())
    variants = dict(original=ROOT/'backups/source/BLUE PRINCE_Data/level1',
        A_logical=ROOT/'build/poc/logical/BLUE PRINCE_Data/level1',
        B_preshaped_visual=ROOT/'build/poc/preshaped_visual/BLUE PRINCE_Data/level1')
    out = {}
    for name,path in variants.items():
        env = UnityPy.load(str(path))
        components = []
        for pid in PIDS:
            obj = env.file.objects[pid]
            common = obj.read_typetree(check_read=False)
            script = scripts[str(common['m_Script']['m_PathID'])]
            node = schemas.get(script['assembly'], '.'.join([script['namespace'],script['name']]))
            data = obj.read_typetree(nodes=node)
            if encode(data,node) != obj.get_raw_data():
                raise ValueError(f'No-op mismatch {name}:{pid}')
            keys = [k for k in data if any(term in k.lower() for term in
                ('font','align','righttoleft','wrapp','overflow','richtext','spacing',
                 'maxvisible','text','margin','autosiz'))]
            chain = hierarchy(env,data['m_GameObject']['m_PathID'])
            components.append(dict(path_id=pid,component=script['name'],
                strict_parse='PASS',noop='PASS',settings={k:data[k] for k in keys},
                hierarchy=chain,active_in_serialized_hierarchy=all(bool(x['active']) for x in chain)))
        out[name]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            externals=[dict(file_id=i+1,path=x.path) for i,x in enumerate(env.file.externals)],
            components=components)
    assets=json.loads((ROOT/'fonts/tmp_inventory.json').read_text())['assets']
    important=[x for x in assets if (x['file']=='sharedassets1.assets' and x['path_id'] in [241,242,244,256]) or
               (x['file']=='sharedassets0.assets' and x['path_id'] in [428,429,430]) or x['class']=='TMP_Settings']
    out['font_assets']=important
    out['status']='STATIC_EVIDENCE_ONLY; runtime UNKNOWN'
    HERE.mkdir(parents=True,exist_ok=True)
    (HERE/'poc_component_font_evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    for comp in out['original']['components']:
        print(comp['path_id'],comp['settings'].get('m_text'),
            ' > '.join(x['name']+(' [OFF]' if not x['active'] else '') for x in comp['hierarchy']))


if __name__ == '__main__':
    main()
