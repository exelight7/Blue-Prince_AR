"""List every text piece under "You Found Text" (the item pickup titles are split into a big first letter, the rest of the
name and a small prefix line) from the original scene files -> translation/work/youfound.tsv.

python dump_youfound.py     columns: group, container (path from the group down to the pieces' parent), piece, font size, kind,
                            local x, local y, active, english text (\\n escaped), runtime path
"""
import json
from project import ROOT
import UnityPy
from schemas import Schemas

schemas = Schemas('AssetsTools')
scripts = json.loads((ROOT / 'research/mono_scripts.json').read_text())
OUT = ROOT / 'translation/work/youfound.tsv'


def path_of(go):
    names = []
    cur = go
    for _ in range(12):
        names.append(cur.m_Name)
        tr = next((c.component.deref() for c in cur.m_Component if c.component.deref().type.name in ('Transform', 'RectTransform')), None)
        if tr is None:
            break
        t = tr.read()
        if not t.m_Father.m_PathID:
            break
        cur = t.m_Father.deref().read().m_GameObject.read()
    return '/'.join(reversed(names))


def kind(name):
    for k in ('First Letter', 'Item Name', 'Prescription', 'Description'):
        if name.startswith(k):
            return k
    return 'other'


rows = []
for lvl in ('level1', 'level2'):
    env = UnityPy.load(str(ROOT / 'backups/source/BLUE PRINCE_Data' / lvl))
    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        common = o.read_typetree(check_read=False)
        sc = scripts.get(str(common['m_Script']['m_PathID']), {})
        if sc.get('name') not in ('TextMeshPro', 'TextMeshProUGUI'):
            continue
        go_id = common.get('m_GameObject', {}).get('m_PathID')
        go = o.assets_file.objects.get(go_id)
        if go is None:
            continue
        g = go.read()
        # cheap pre-filter: only read the path for objects whose name is one of the title pieces
        if kind(g.m_Name) == 'other':
            continue
        p = path_of(g)
        if 'You Found Text' not in p:
            continue
        d = o.read_typetree(nodes=schemas.get(sc['assembly'], 'TMPro.' + sc['name']))
        parts = p.split('/')
        i = parts.index('You Found Text') + 1
        tr = next(c.component.deref() for c in g.m_Component if c.component.deref().type.name in ('Transform', 'RectTransform')).read()
        rows.append((parts[i], '/'.join(parts[i:-1]), g.m_Name, round(d['m_fontSize'], 1), kind(g.m_Name),
                     round(tr.m_LocalPosition.x, 2), round(tr.m_LocalPosition.y, 2), int(g.m_IsActive),
                     d['m_text'].replace('\n', '\\n'), p))
    print(lvl, len(rows), flush=True)
rows.sort()
OUT.write_text('\n'.join('\t'.join(str(x) for x in r) for r in rows) + '\n', encoding='utf-8')
print(len(rows), 'pieces ->', OUT, '|', len({r[0] for r in rows}), 'groups')
