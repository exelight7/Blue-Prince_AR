"""Print the next N untranslated corpus entries (compact, with context) for translation.

python next_batch.py [N] [--long] [--origin tmp|fsm|array|custom] [--skip K]
"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
corpus = json.loads((ROOT / 'translation/work/corpus.json').read_text(encoding='utf-8'))
def norm(s):
    return re.sub(r'<[^>]*>', '', s).strip().lower()


done = {}
for p in sorted((ROOT / 'translation/arabic/batches').glob('b*.json')):
    done.update(json.loads(p.read_text(encoding='utf-8')))
keep = ROOT / 'translation/arabic/keep.json'
if keep.exists():
    done.update({k: k for k in json.loads(keep.read_text(encoding='utf-8'))})
done_norm = {norm(k) for k in done}
args = sys.argv[1:]
n = int(args[0]) if args and args[0].isdigit() else 100
origin = args[args.index('--origin') + 1] if '--origin' in args else None
skip = int(args[args.index('--skip') + 1]) if '--skip' in args else 0
todo, seen = [], set()
for x in corpus:
    k = norm(x['src'])
    if x['src'] in done or k in done_norm or k in seen or (origin is not None and origin not in x['origins']):
        continue
    seen.add(k); todo.append(x)
maxtier = int(args[args.index('--tier') + 1]) if '--tier' in args else 3
todo = [x for x in todo if x['tier'] <= maxtier]
todo.sort(key=lambda x: (x['tier'], -x['n'], x['words'], x['src']))
print(f'# translated {len(done)} / {len(corpus)}; remaining {len(todo)}', file=sys.stderr)
for x in todo[skip:skip + n]:
    print(json.dumps(x['src'], ensure_ascii=False), '|', x['n'], '|', x['ctx'][0][:48])
