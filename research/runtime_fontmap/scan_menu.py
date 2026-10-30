"""Read-only main-menu/settings label discovery; no scene changes."""
import json
import sys
from inspect_poc import ROOT,HERE,Schemas,hierarchy,UnityPy


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    schemas=Schemas('AssetsTools')
    env=UnityPy.load(str(ROOT/'backups/source/BLUE PRINCE_Data/level1'))
    rows=[]
    for obj in env.objects:
        if obj.type.name!='MonoBehaviour':continue
        c=obj.read_typetree(check_read=False)
        scriptid=c['m_Script']['m_PathID']
        if scriptid not in [2627,4239]:continue
        name='TextMeshPro' if scriptid==2627 else 'TextMeshProUGUI'
        d=obj.read_typetree(nodes=schemas.get('Unity.TextMeshPro','TMPro.'+name))
        if not d.get('m_text','').strip():continue
        chain=hierarchy(env,d['m_GameObject']['m_PathID'])
        ancestors=[x['name'] for x in chain]
        if not any('MAIN MENU'==n or 'CALIBRATION'==n or 'SETTINGS' in n.upper() for n in ancestors):continue
        rows.append(dict(path_id=obj.path_id,text=d['m_text'],component=name,
            settings={k:v for k,v in d.items() if any(t in k.lower() for t in ['font','align','righttoleft','wrapp','overflow','richtext','spacing','margin','autosiz','maxvisible'])},
            hierarchy=chain,active_in_serialized_hierarchy=all(bool(x['active']) for x in chain)))
    (HERE/'menu_settings_labels.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in rows:
        text=r['text']
        if len(text)>400 or all(ch in '|_ \n\r' for ch in text):continue
        print(r['path_id'],repr(text[:160]),' > '.join(x['name']+(' [OFF]' if not x['active'] else '') for x in r['hierarchy']))


if __name__=='__main__':main()
