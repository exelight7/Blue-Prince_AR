"""Turn {source-prefix: arabic} into a validated batch so long sources need not be retyped.

python tr_prefix.py in_prefix.json bNNN
Each prefix must match exactly one corpus entry (startswith). Output: translation/arabic/batches/bNNN.json
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
corpus = json.loads((ROOT / 'translation/work/corpus.json').read_text(encoding='utf-8'))
srcs = [x['src'] for x in corpus]
pairs = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
out, bad = {}, []
for prefix, ar in pairs.items():
    hits = [s for s in srcs if s.startswith(prefix)]
    if not hits:
        bad.append((prefix[:50], 0))
        continue
    for h in hits:  # near-duplicate variants share the translation; merge_batches validates each one
        out[h] = ar + h[len(h.rstrip()):] if ar == ar.rstrip() else ar   # keep the variant's own trailing whitespace
(ROOT / f'translation/arabic/batches/{sys.argv[2]}.json').write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
print(len(out), 'ok;', len(bad), 'unresolved', bad)
