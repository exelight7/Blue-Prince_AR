"""Recover PlayMaker string-value candidates; never treat action/variable IDs as translations."""
import collections
import json
import UnityPy
from project import ROOT, write_new
from schemas import Schemas
from build_poc import encode


def values(fsm):
    for i, item in enumerate(fsm.get('variables', {}).get('stringVariables', [])):
        if item.get('value'):
            yield f'fsm.variables.stringVariables[{i}].value', item['value'], item.get('name', ''), 'variable_default'
    for i, state in enumerate(fsm.get('states', [])):
        action = state.get('actionData', {})
        for j, item in enumerate(action.get('fsmStringParams', [])):
            if item.get('value') and not item.get('useVariable'):
                yield f'fsm.states[{i}].actionData.fsmStringParams[{j}].value', item['value'], state.get('name', ''), 'constant_action_parameter'


def main():
    schemas = Schemas('AssetStudio')
    # Include every FSM, including those read by the first backend, to keep one consistent ledger.
    sources = []
    for file in sorted((ROOT / 'research/asset_index').glob('*.json')):
        for record in json.loads(file.read_text()):
            if record.get('script_hint', {}).get('name') in ('PlayMakerFSM', 'FsmTemplate'):
                sources.append(record)
    rows, errors, actions = [], [], []
    counts = collections.Counter()
    for filename in sorted({r['container'] for r in sources if '/' not in r['container']}):
        env = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data' / filename))
        targets = [r for r in sources if r['container'] == filename]
        for record in targets:
            pid = record['path_id']
            obj = env.file.objects[pid]
            script = record['script_hint']
            fullname = '.'.join(filter(None, [script['namespace'], script['name']]))
            try:
                node = schemas.get(script['assembly'], fullname)
                data = obj.read_typetree(nodes=node)
                if encode(data, node) != obj.get_raw_data():
                    raise ValueError('No-op serialization differs')
                if data['m_Script'] != obj.read_typetree(check_read=False)['m_Script']:
                    raise ValueError('Script reference differs')
                fsm = data.get('fsm', {})
                go = env.file.objects.get(data.get('m_GameObject', {}).get('m_PathID'))
                context = go.read().m_Name if go and go.type.name == 'GameObject' else data['m_Name']
                counts[script['name']] += 1
                for field, value, subcontext, kind in values(fsm):
                    rows.append(dict(ID=f'{filename}:{pid}:{field}', Context=context,
                        Source=value, Arabic='', File=filename, Category='playmaker_candidate',
                        Notes=f'{kind}; state/variable={subcontext}; visibility unresolved',
                        Status='NEEDS_CONTEXT', PathID=pid, Field=field))
                for state_index, state in enumerate(fsm.get('states', [])):
                    ad = state.get('actionData', {})
                    for index, name in enumerate(ad.get('actionNames', [])):
                        if any(term in name for term in ('StringTypewriter', 'VideoTextWriter', 'Localized', 'LanguageText')):
                            enabled = ad.get('actionEnabled', [])
                            actions.append(dict(file=filename, path_id=pid, context=context,
                                state_index=state_index, state=state.get('name'),
                                action_index=index, action=name,
                                enabled=enabled[index] if index < len(enabled) else None,
                                status='SERIALIZED_REFERENCE_NOT_RUNTIME_EXECUTION'))
            except Exception as error:
                errors.append(dict(file=filename,path_id=pid,script=fullname,error=str(error)))
        print(filename, dict(counts), 'candidates', len(rows), 'errors', len(errors), flush=True)
    # Recover the small key list using the same validated backend.
    env = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data/sharedassets1.assets'))
    obj = env.file.objects[237]
    node = schemas.get('Assembly-CSharp', 'SummertimeMadness.Localization.LocalizationKeyDatabaseAsset')
    keys = obj.read_typetree(nodes=node)
    if encode(keys, node) != obj.get_raw_data():
        raise ValueError('Key list no-op serialization differs')
    write_new(ROOT / 'extracted/original/structured/sharedassets1.assets/237.json', keys)
    write_new(ROOT / 'translation/source/playmaker_candidates.json', rows)
    write_new(ROOT / 'research/playmaker_extraction_errors.json', errors)
    write_new(ROOT / 'research/serialized_text_actions.json', actions)
    write_new(ROOT / 'research/playmaker_extraction_summary.json', dict(counts=counts,
        candidate_occurrences=len(rows), unique_candidate_values=len({r['Source'] for r in rows}),
        strict_byte_noop_pass=sum(counts.values()), errors=len(errors), recovered_keys=len(keys['Keys'])))


if __name__ == '__main__':
    main()
