"""Build a small, meaningful Arabic menu POC from the untouched scene."""
import json
import UnityPy
from project import ROOT,sha256,write_new
from schemas import Schemas
from build_poc import encode
from arabic_plain import visual_line
from validate import validate

LABELS={3568:'لعبة جديدة',3481:'متابعة',3534:'الإعدادات',3500:'إنهاء اللعبة',
        3411:'الصوت',3380:'التحكم',3446:'الرسومات',3429:'بيانات الحفظ',
        3527:'فريق العمل',3456:'رجوع',3379:'الإعدادات'}


def main():
    if not __debug__:raise RuntimeError('Run normal Python; integrity assertions are required')
    source=ROOT/'backups/source/BLUE PRINCE_Data/level1'
    scene=UnityPy.load(str(source));originals={o.path_id:o.get_raw_data() for o in scene.objects}
    scripts=json.loads((ROOT/'research/mono_scripts.json').read_text());schemas=Schemas()
    expected,nodes,rows,changes={},{},[],[]
    for pid,arabic in LABELS.items():
        obj=scene.file.objects[pid];header=obj.read_typetree(check_read=False)
        script=scripts[str(header['m_Script']['m_PathID'])]
        node=schemas.get(script['assembly'],'.'.join(filter(None,[script['namespace'],script['name']])))
        data=obj.read_typetree(nodes=node);assert encode(data,node)==originals[pid]
        row=dict(ID=f'level1:{pid}:m_text',Source=data['m_text'],Arabic=arabic,File='level1',
            Context='Main Menu / Settings; original GameObject retained',Category='menu_poc',
            Status='REVIEWED_POC',Notes='Short static UI only; not a complete localization')
        rows.append(row);before=dict(data)
        data['m_text']=visual_line(arabic)
        data['m_fontAsset']=dict(m_FileID=2,m_PathID=244)
        data['m_sharedMaterial']=dict(m_FileID=2,m_PathID=43)
        data['m_isRightToLeft']=0
        data['m_characterSpacing']=0.0;data['m_wordSpacing']=0.0;data['m_lineSpacing']=0.0
        data['m_fontStyle']=0;data['m_enableAutoSizing']=0
        expected[pid],nodes[pid]=data,node
        changes.append(dict(path_id=pid,source=row['Source'],arabic=arabic,
            fields={k:dict(before=before.get(k),after=v) for k,v in data.items() if before.get(k)!=v}))
        obj.set_raw_data(encode(data,node))
    errors=validate(rows,json.loads((ROOT/'translation/source/strings.json').read_text()))
    if errors:raise ValueError(errors)
    output=scene.file.save();path=ROOT/'build/arabic_menu_poc/BLUE PRINCE_Data/level1'
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=output:raise FileExistsError(path)
    if not path.exists():path.write_bytes(output)
    reopened=UnityPy.load(str(path));assert len(reopened.file.objects)==len(originals)
    for pid,raw in originals.items():
        if pid in expected:assert reopened.file.objects[pid].read_typetree(nodes=nodes[pid])==expected[pid]
        else:assert reopened.file.objects[pid].get_raw_data()==raw
    assert reopened.file.save()==output
    write_new(ROOT/'translation/arabic/menu_poc.json',rows)
    write_new(ROOT/'tests/arabic_menu_poc_manifest.json',dict(status='PASS_OFFLINE',source=str(source),
        source_sha256=sha256(source),output=str(path),sha256=sha256(path),
        modified_objects=list(LABELS),unchanged_objects=len(originals)-len(LABELS),
        added_objects=0,removed_objects=0,changes=changes,
        note='Rebuilt from original scene; all diagnostic text and added experimental typewriter removed'))
    print('PASS: 11 context-reviewed menu labels; 4,249 other objects unchanged; no diagnostic FSM')


if __name__=='__main__':main()
