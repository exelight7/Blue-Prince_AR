"""Stage a verified POC only inside the disposable copy; run with the game closed."""
import argparse
from datetime import datetime,timezone
import json
import shutil
import csv
import os
import subprocess
from project import ROOT,sha256,write_new


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant',choices=['a','b','b_layout','b_layout_v4','b_layout_v5','arabic_menu'])
    args=parser.parse_args()
    tasklist=os.path.join(os.environ['WINDIR'],'System32','tasklist.exe')
    running=subprocess.run([tasklist,'/FI','IMAGENAME eq BLUE PRINCE.exe','/FO','CSV','/NH'],
                           capture_output=True,text=True,check=True)
    if any(row and row[0].casefold()=='blue prince.exe' for row in csv.reader(running.stdout.splitlines())):
        raise RuntimeError('Close Blue Prince before staging; no running game file will be replaced')
    target=(ROOT/'runtime_test/BLUE PRINCE_Data/level1').resolve(strict=True)
    if ROOT.resolve() not in target.parents or 'runtime_test' not in target.parts:
        raise ValueError('Target escapes runtime workspace')
    variants=json.loads((ROOT/'tests/runtime_matrix_v2_manifest.json').read_text())
    original_hash=variants[0]['source_sha256']
    layout=json.loads((ROOT/'tests/runtime_layout_typewriter_manifest.json').read_text()) if (ROOT/'tests/runtime_layout_typewriter_manifest.json').exists() else None
    if layout:
        variants.append(dict(variant='b_layout',sha256=layout['sha256'],source_sha256=layout['source_sha256']))
    for revision in (4,5):
        manifest=ROOT/f'tests/runtime_layout_typewriter_v{revision}_manifest.json'
        if manifest.exists():
            entry=json.loads(manifest.read_text())
            variants.append(dict(variant=f'b_layout_v{revision}',sha256=entry['sha256'],source_sha256=entry['source_sha256']))
    menu=ROOT/'tests/arabic_menu_poc_manifest.json'
    if menu.exists():
        entry=json.loads(menu.read_text())
        variants.append(dict(variant='arabic_menu',sha256=entry['sha256'],source_sha256=entry['source_sha256']))
    row=next(r for r in variants if r['variant']==args.variant)
    source=ROOT/'build/runtime_layout_typewriter/BLUE PRINCE_Data/level1' if args.variant=='b_layout' else ROOT/f'build/runtime_matrix_v2/{args.variant}/BLUE PRINCE_Data/level1'
    if args.variant in ('b_layout_v4','b_layout_v5'):
        revision=args.variant.rsplit('_v',1)[1]
        source=ROOT/f'build/runtime_layout_typewriter_v{revision}/BLUE PRINCE_Data/level1'
    if args.variant=='arabic_menu':source=ROOT/'build/arabic_menu_poc/BLUE PRINCE_Data/level1'
    if sha256(source)!=row['sha256']:
        raise ValueError('POC output hash does not match verified build')
    before=sha256(target)
    allowed={r['sha256'] for r in variants}|{original_hash}
    if before not in allowed:
        raise ValueError('Unknown runtime scene; preserve/review it before replacement')
    backup=ROOT/'backups/source/BLUE PRINCE_Data/level1'
    if sha256(backup)!=original_hash:
        raise ValueError('Untouched source backup differs')
    pending=target.with_name('level1.pending')
    if pending.exists():raise FileExistsError('Pending scene already exists; review it before retrying')
    shutil.copyfile(source,pending)
    if sha256(pending)!=row['sha256']:raise ValueError('Pending scene hash mismatch')
    os.replace(pending,target)
    after=sha256(target)
    if after!=row['sha256']:
        raise ValueError('Staged scene hash mismatch')
    entry=dict(utc=datetime.now(timezone.utc).isoformat(),variant=args.variant,
        target=str(target),before_sha256=before,after_sha256=after,
        untouched_backup=str(backup),reason='Seven-case Arabic rendering test; font244/material43 and documented TMP properties')
    logs=ROOT/'tests/runtime_staging';logs.mkdir(exist_ok=True)
    existing=list(logs.glob('stage_*.json'))
    write_new(logs/f'stage_{len(existing)+1:03d}.json',entry)
    print(f'PASS: staged {args.variant.upper()} only in runtime_test')


if __name__=='__main__':main()
