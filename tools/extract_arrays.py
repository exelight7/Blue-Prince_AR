"""Extract exact-schema PlayMaker string array candidates without translating identifiers."""
import json
import UnityPy
from project import ROOT, write_new
from schemas import Schemas
from build_poc import encode


def main():
    schema = Schemas('AssetStudio').get('Assembly-CSharp', 'PlayMakerArrayListProxy')
    rows, errors, count = [], [], 0
    for index in sorted((ROOT / 'research/asset_index').glob('*.json')):
        records = [r for r in json.loads(index.read_text())
                   if r.get('script_hint', {}).get('name') == 'PlayMakerArrayListProxy']
        if not records:
            continue
        file = records[0]['container']
        if '/' in file:
            continue
        env = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data' / file))
        for record in records:
            pid = record['path_id']
            obj = env.file.objects[pid]
            try:
                data = obj.read_typetree(nodes=schema)
                if encode(data, schema) != obj.get_raw_data():
                    raise ValueError('No-op serialization differs')
                count += 1
                for i, value in enumerate(data.get('preFillStringList', [])):
                    if value:
                        field = f'preFillStringList[{i}]'
                        rows.append(dict(ID=f'{file}:{pid}:{field}', Context=data['referenceName'],
                            Source=value, Arabic='', File=file, Category='array_candidate',
                            Notes='May be puzzle control, identifier or visible content; review in context',
                            Status='NEEDS_CONTEXT', PathID=pid, Field=field))
            except Exception as error:
                errors.append(dict(file=file,path_id=pid,error=str(error)))
        print(file, count, len(rows), 'errors', len(errors), flush=True)
    write_new(ROOT / 'translation/source/array_candidates.json', rows)
    write_new(ROOT / 'research/array_extraction_errors.json', errors)
    write_new(ROOT / 'research/array_extraction_summary.json', dict(strict_byte_noop_pass=count,
        candidate_occurrences=len(rows), unique_candidate_values=len({r['Source'] for r in rows}),
        errors=len(errors)))


if __name__ == '__main__':
    main()
