"""Merge every extracted source into one deduplicated translation corpus keyed by the English string.

Output translation/work/corpus.json: [{src, n, ctx, from}] sorted by priority, plus translation/work/skipped.json.
The plugin matches on the exact source text, so one entry covers every occurrence.
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'translation/source'
WORK = ROOT / 'translation/work'

TAG = re.compile(r'<[^>]*>')
WORDS = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
IDENT = re.compile(r'^[A-Za-z0-9_.\-/\\:]+$')
CAMEL = re.compile(r'^[a-z]+[A-Z]')
ROMAN = re.compile(r'^[IVXLCDM\s\\n]+$')


def visible_text(s):
    return TAG.sub('', s)


def classify(s, origin):
    """Return None to keep, or a short reason to skip."""
    t = visible_text(s).strip()
    if not t:
        return 'empty'
    if not re.search(r'[A-Za-z]{2}', t):
        return 'no-words'
    if ROMAN.match(t):
        return 'roman-numerals'
    if re.fullmatch(r'[0-9A-Z,;:\s]+', t) and re.search(r'\d', t):
        return 'code'
    if re.fullmatch(r'[A-Z]{1,3}', t):
        return 'short-caps-puzzle'
    if origin in ('fsm', 'array', 'custom'):
        if '_' in t and ' ' not in t:
            return 'identifier'
        if CAMEL.match(t) and ' ' not in t:
            return 'identifier'
        if IDENT.match(t) and ' ' not in t and (t.islower() or '.' in t or '/' in t or '\\' in t or t.isdigit()):
            return 'identifier'
        if '://' in t or t.endswith(('.json', '.txt', '.png', '.asset', '.es3', '.dat')):
            return 'identifier'
    if origin == 'fsm' and ' ' not in t and not t[:1].isupper():
        return 'fsm-lowercase-token'
    return None


def load(name):
    return json.loads((SRC / name).read_text(encoding='utf-8'))


def main():
    entries = defaultdict(lambda: dict(n=0, ctx=[], origins=set()))
    skipped = defaultdict(int)
    for origin, name in (('tmp', 'strings.json'), ('array', 'array_candidates.json'),
                         ('fsm', 'playmaker_candidates.json'), ('custom', 'custom_candidates.json')):
        path = SRC / name
        if not path.exists():
            continue
        for r in load(name):
            s = r['Source']
            why = classify(s, origin)
            if why:
                skipped[why] += 1
                continue
            e = entries[s]
            e['n'] += 1
            e['origins'].add(origin)
            c = f"{origin}:{r.get('Context', '')}"
            if len(e['ctx']) < 3 and c not in e['ctx']:
                e['ctx'].append(c)
    out = []
    for s, e in entries.items():
        w = len(WORDS.findall(visible_text(s)))
        o = e['origins']
        if 'tmp' in o:
            tier = 0 if w <= 12 else 2
        elif o & {'array', 'custom'}:
            tier = 1
        elif TAG.search(s) or w >= 4 or re.search(r'[.!?]$', s.strip()):
            tier = 3
        else:
            tier = 9  # fsm-only internal-looking value; translated only if the runtime log shows it on screen
        out.append(dict(src=s, n=e['n'], ctx=e['ctx'], origins=sorted(o), words=w, tier=tier))
    out.sort(key=lambda x: (x['tier'], -x['n'], x['src']))
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'corpus.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    (WORK / 'skipped.json').write_text(json.dumps(skipped, indent=1), encoding='utf-8')
    tot = sum(x['words'] for x in out)
    print('entries', len(out), 'words', tot, 'skipped', dict(skipped))
    by = defaultdict(lambda: [0, 0])
    for x in out:
        by[x['tier']][0] += 1; by[x['tier']][1] += x['words']
    print('tier -> [entries, words]', dict(by))


if __name__ == '__main__':
    main()
