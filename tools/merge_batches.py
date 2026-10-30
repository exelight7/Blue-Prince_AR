"""Validate all translation batches and write translation/arabic/ar.json (source -> Arabic).

A value equal to its key means "deliberately kept in English" (puzzle words, passwords, signatures).
Entries failing a hard check are left out of ar.json and listed in translation/work/rejects.json.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r'<[^>]*>')
KEY = re.compile(r'\[[A-Za-z]{1,10}\]|\{[A-Za-z0-9_]{1,12}\}|%[sd]')
NUM = re.compile(r'\d+')
LAT = re.compile(r"[A-Za-z]{2,}")
ARABIC = re.compile(r'[؀-ۿ]')
INDIC = re.compile(r'[٠-٩۰-۹]')


def check(src, ar):
    hard, soft = [], []
    if src == ar:
        return hard, soft
    ar = ar.replace('{ICON}', '')  # icon slot marker: allowed in Arabic only
    norm = lambda l: sorted(t.lower().replace(' ', '') for t in l)
    if norm(TAG.findall(src)) != norm(TAG.findall(ar)):
        hard.append('tags differ')
    if sorted(KEY.findall(src)) != sorted(KEY.findall(ar)):
        hard.append('keys/placeholders differ')
    if sorted(NUM.findall(TAG.sub('', src))) != sorted(NUM.findall(TAG.sub('', ar))):
        hard.append('numbers differ')
    if INDIC.search(ar):
        hard.append('arabic-indic digits')
    if not ARABIC.search(ar):
        hard.append('no arabic letters')
    if '‏' in ar or '‮' in ar or '�' in ar or '??' in ar:
        hard.append('bad control chars')
    extra = {w.lower() for w in LAT.findall(TAG.sub('', ar))} - {w.lower() for w in LAT.findall(src)} - {'ok'}
    extra -= {w.lower() for w in KEY.findall(ar)}
    if extra:
        soft.append('new latin words: ' + ','.join(sorted(extra)))
    if src.count('\n') != ar.count('\n'):
        soft.append(f'newlines {src.count(chr(10))}->{ar.count(chr(10))}')
    return hard, soft


def main():
    merged, rejects, warns = {}, [], []
    for p in sorted((ROOT / 'translation/arabic/batches').glob('b*.json')):
        for src, ar in json.loads(p.read_text(encoding='utf-8')).items():
            hard, soft = check(src, ar)
            if hard:
                rejects.append(dict(file=p.name, src=src, ar=ar, why=hard))
                continue
            merged[src] = ar
            if soft:
                warns.append(dict(file=p.name, src=src[:60], why=soft))
    keep = ROOT / 'translation/arabic/keep.json'
    kept_list = json.loads(keep.read_text(encoding='utf-8')) if keep.exists() else []
    for k in kept_list:
        merged.setdefault(k, k)
    out = ROOT / 'translation/arabic/ar.json'
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=0), encoding='utf-8')
    work = ROOT / 'translation/work'
    (work / 'rejects.json').write_text(json.dumps(rejects, ensure_ascii=False, indent=1), encoding='utf-8')
    (work / 'warnings.json').write_text(json.dumps(warns, ensure_ascii=False, indent=1), encoding='utf-8')
    kept = sum(1 for k, v in merged.items() if k == v)
    print(f'merged {len(merged)} ({kept} kept-as-is); rejected {len(rejects)}; warnings {len(warns)}')
    for r in rejects[:15]:
        print('REJECT', r['file'], r['why'], json.dumps(r['src'][:60], ensure_ascii=False))


if __name__ == '__main__':
    main()
