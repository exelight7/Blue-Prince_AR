"""Collect every string leaf from the game's own MonoBehaviour/ScriptableObject classes (Room, BookCheckoutEntry,
LanguageText, ...). Read-only on backups/source. Output: translation/source/custom_candidates.json"""
import json, re, sys
import UnityPy
from collections import Counter
from project import ROOT
from schemas import Schemas

SKIP = {'PlayMakerArrayListProxy', 'LocalizedText', 'MJCornerButtonHandler', 'ControllerSelectable', 'CullableEntity',
        'MJBoxButtonHandler', 'UIScreen', 'ControllerSelector', 'StepSurface', 'HighlightObject', 'BPPathController',
        'BPSetChildrenInvisible', 'BirdAnimator', 'BirdPather', 'BirdController', 'AddressablesMeshReferences',
        'HeadNode', 'PathwayPoint', 'MorajaiController', 'TrackGroup_Simple', 'UISelectableGraphics', 'Beautify'}
HAS_LETTERS = re.compile(r'[A-Za-z]{3}')


def walk(v, path, out):
    if isinstance(v, str):
        if HAS_LETTERS.search(v):
            out.append((path, v))
    elif isinstance(v, dict):
        for k, x in v.items():
            walk(x, f'{path}.{k}' if path else k, out)
    elif isinstance(v, (list, tuple)):
        for i, x in enumerate(v):
            walk(x, f'{path}[{i}]', out)


def main():
    schemas = Schemas('AssetStudio')
    rows, errors, stats = [], Counter(), Counter()
    envs = {}
    for index in sorted((ROOT / 'research/asset_index').glob('*.json')):
        records = [r for r in json.loads(index.read_text())
                   if r.get('script_hint', {}).get('assembly') == 'Assembly-CSharp.dll'
                   and r['script_hint']['name'] not in SKIP]
        if not records:
            continue
        file = records[0]['container']
        if '/' in file:
            continue
        env = envs.setdefault(file, UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data' / file)))
        for r in records:
            name = r['script_hint']['name']
            try:
                obj = env.file.objects[r['path_id']]
                data = obj.read_typetree(nodes=schemas.get('Assembly-CSharp.dll', name))
            except Exception as e:
                errors[f'{name}: {str(e)[:60]}'] += 1
                continue
            hits = []
            walk(data, '', hits)
            stats[name] += 1
            for path, text in hits:
                if path.startswith(('m_Name', 'm_GameObject', 'm_Script')):
                    continue
                rows.append(dict(ID=f"{file}:{r['path_id']}:{path}", Type=name, Context=data.get('m_Name') or r.get('name', ''),
                                 Source=text, File=file))
        print(file, len(rows), flush=True)
    out = ROOT / 'translation/source/custom_candidates.json'
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('rows', len(rows), 'distinct', len({r['Source'] for r in rows}))
    print('by type', Counter(r['Type'] for r in rows).most_common(25))
    print('errors', errors.most_common(80))


if __name__ == '__main__':
    main()
