"""Validate translation integrity without changing source or translation files."""
import collections
import json
import re
import sys
import argparse

TOKEN = re.compile(r'\{[^{}\r\n]+\}|%(?:\d+\$)?[-+#0 .\d]*[sdifuxX]|\[[A-Z][A-Z0-9_ ]*\]|\\[nrt]')
TAG = re.compile(r'<[^<>]+>')
ARABIC = re.compile(r'[\u0600-\u06ff\ufb50-\ufdff\ufe70-\ufeff]')


def tokens(text):
    return collections.Counter(TOKEN.findall(text))


def tag_errors(text):
    stack, errors = [], []
    for tag in re.findall(r'<[/A-Za-z][^<>]*(?:>|$)', text):
        match = re.fullmatch(r'<(/?)([A-Za-z][A-Za-z0-9_-]*)([^<>]*)>', tag)
        if not match:
            errors.append('Malformed tag')
            continue
        closing, name, tail = match.groups()
        if tail.endswith('/') or name in {'br', 'sprite', 'space', 'page', 'quad'}:
            continue
        if closing:
            if not stack or stack.pop() != name:
                errors.append('Unbalanced tag')
        else:
            stack.append(name)
    if stack:
        errors.append('Unclosed tag')
    return errors


def validate(rows, source_rows=None):
    errors, seen = [], set()
    baseline = {row['ID']: row for row in source_rows} if source_rows is not None else None
    for row in rows:
        rid = row['ID']
        def fail(message):
            errors.append(dict(ID=rid, error=message))
        if rid in seen:
            fail('Duplicate ID')
        seen.add(rid)
        if baseline is not None:
            expected = baseline.get(rid)
            if expected is None:
                fail('Unknown or changed identifier')
            elif any(row.get(key) != expected.get(key) for key in ('ID', 'Source', 'File')):
                fail('Source identity/text metadata changed')
        source, arabic = row['Source'], row['Arabic']
        if not arabic.strip():
            fail('Missing Arabic')
        if not ARABIC.search(arabic):
            fail('No Arabic characters / unresolved English')
        if tokens(source) != tokens(arabic):
            fail('Placeholder/escape multiset differs')
        if collections.Counter(TAG.findall(source)) != collections.Counter(TAG.findall(arabic)):
            fail('Formatting tag multiset differs')
        for problem in tag_errors(arabic):
            fail(problem)
        if '\ufffd' in arabic or '???' in arabic or re.search(r'\bNULL\b', arabic):
            fail('Replacement character or suspicious sentinel')
        if any(x in arabic for x in ('Ø§', 'Ù„', 'Ã', 'Â')):
            fail('Possible mojibake')
        if '\r' in arabic or '\x00' in arabic:
            fail('Invalid control character')
        if source.count('\n') != arabic.count('\n'):
            fail('Line break count differs; needs explicit layout review')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('translations')
    parser.add_argument('--source')
    args = parser.parse_args()
    with open(args.translations, encoding='utf-8-sig') as stream:
        rows = json.load(stream)
    baseline = None
    if args.source:
        with open(args.source, encoding='utf-8-sig') as stream:
            baseline = json.load(stream)
    errors = validate(rows, baseline)
    print(json.dumps(dict(status='FAIL' if errors else 'PASS', rows=len(rows), errors=errors), ensure_ascii=True))
    raise SystemExit(bool(errors))
