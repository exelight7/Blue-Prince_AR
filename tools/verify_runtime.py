"""Verify the final disposable copy against its baseline and reviewed menu scene."""
import json
from project import ROOT,sha256,write_new


def main():
    baseline=json.loads((ROOT/'tests/runtime_copy_manifest.json').read_text())
    menu=json.loads((ROOT/'tests/arabic_menu_poc_manifest.json').read_text())
    root=ROOT/'runtime_test'
    expected={r['path']:r for r in baseline['files']}
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    errors=[dict(path=p,reason='Added or removed path') for p in sorted(set(expected)^actual)]
    rows=[]
    for relative,row in expected.items():
        file=root/relative
        if not file.exists():continue
        digest=sha256(file)
        wanted=menu['sha256'] if relative=='BLUE PRINCE_Data/level1' else row['source_sha256']
        ok=digest==wanted
        rows.append(dict(path=relative,original_sha256=row['source_sha256'],expected_sha256=wanted,
                         actual_sha256=digest,modified_from_original=digest!=row['source_sha256'],match=ok))
        if not ok:errors.append(dict(path=relative,reason='Unexpected hash'))
    result=dict(status='FAIL' if errors else 'PASS',root=str(root),files=len(rows),
        changed_files=[r['path'] for r in rows if r['modified_from_original']],errors=errors,records=rows,
        game_launched_by_this_check=False)
    write_new(ROOT/'tests/runtime_integrity_003.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
