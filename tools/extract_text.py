"""Extract proven text fields and keep unresolved strings as review candidates."""
import collections
import json
from pathlib import Path
import UnityPy
from project import ROOT, write_new
from schemas import Schemas


def strings(value, path=''):
    if isinstance(value, str):
        if value:
            yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f'{path}.{key}' if path else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f'{path}[{index}]')


def extract():
    schemas = Schemas('AssetsTools')
    scripts = json.loads((ROOT / 'research/mono_scripts.json').read_text())
    target_names = {'TextMeshPro', 'TextMeshProUGUI', 'LocalizedText',
                    'LocalizationLanguageAsset', 'LocalizationDatabaseAsset',
                    'LocalizationKeyDatabaseAsset', 'PlayMakerFSM', 'PlayMakerArrayListProxy',
                    'VideoTextWriter', 'Languages', 'LanguageText', 'FsmTemplate'}
    rows, candidates, errors, bindings = [], [], [], []
    counts = collections.Counter()
    base = ROOT / 'backups/source/BLUE PRINCE_Data'
    for file in sorted(base.iterdir()):
        if not (file.suffix == '.assets' or file.name in ('level0', 'level1', 'level2')):
            continue
        env = UnityPy.load(str(file))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            common = obj.read_typetree(check_read=False)
            script = scripts.get(str(common['m_Script']['m_PathID']), {})
            name = script.get('name')
            if name not in target_names:
                continue
            fullname = '.'.join(filter(None, [script['namespace'], name]))
            try:
                node = schemas.get(script['assembly'], fullname)
                data = obj.read_typetree(nodes=node)
                if data['m_Script'] != common['m_Script']:
                    raise ValueError('Schema changed the script reference')
                counts[name] += 1
                go_id = data.get('m_GameObject', {}).get('m_PathID')
                go = obj.assets_file.objects.get(go_id)
                context = go.read().m_Name if go and go.type.name == 'GameObject' else data['m_Name']
                if name == 'LocalizedText':
                    bindings.append(dict(file=file.name,path_id=obj.path_id,context=context,data=data))
                if name.startswith('Localization'):
                    write_new(ROOT / f'extracted/original/structured/{file.name}/{obj.path_id}.json', data)
                for field, value in strings(data):
                    if field == 'm_Name':
                        continue
                    record = dict(ID=f'{file.name}:{obj.path_id}:{field}', Context=context,
                                  Source=value, Arabic='', File=file.name, Category='UNKNOWN',
                                  Notes=f'{fullname}; field={field}', Status='NEEDS_CONTEXT',
                                  PathID=obj.path_id, Field=field)
                    if name in ('TextMeshPro', 'TextMeshProUGUI') and field == 'm_text':
                        record['Category'] = 'serialized_ui_text'
                        rows.append(record)
                    elif name == 'LocalizationLanguageAsset' and field.endswith('.Value'):
                        index = int(field.split('[')[1].split(']')[0])
                        record['SourceKey'] = data['Entries'][index]['Key']
                        record['Language'] = data['LanguageTag']
                        record['Category'] = 'localization_database'
                        (rows if data['LanguageTag'] == 'en' else candidates).append(record)
                    else:
                        candidates.append(record)
            except Exception as error:
                errors.append(dict(file=file.name,path_id=obj.path_id,script=fullname,error=str(error)))
        print(file.name, dict(counts), 'errors', len(errors), flush=True)
    write_new(ROOT / 'translation/source/strings.json', rows)
    write_new(ROOT / 'research/text_candidates.json', candidates)
    write_new(ROOT / 'research/localized_text_bindings.json', bindings)
    write_new(ROOT / 'research/text_extraction_errors.json', errors)
    write_new(ROOT / 'research/text_extraction_summary.json', dict(counts=counts,
        occurrences=len(rows), unique_sources=len({r['Source'] for r in rows}),
        candidates=len(candidates), errors=len(errors)))


if __name__ == '__main__':
    extract()
