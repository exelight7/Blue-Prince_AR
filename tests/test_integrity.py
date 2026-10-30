"""Small checks for the boundaries that guard asset modification."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from validate import validate
from project import safe_roots, ROOT


def row(source='Press [ENTER] {0} <b>Open</b>', arabic='اضغط [ENTER] {0} <b>افتح</b>'):
    return dict(ID='sample', Source=source, Arabic=arabic)


assert validate([row()]) == []
assert validate([row()], [row()]) == []
assert validate([dict(row(), ID='changed')], [row()])
assert validate([dict(row(), Source='changed')], [row()])
assert validate([row('Text', 'نص <b')])
assert validate([row(arabic='اضغط {0} <b>افتح</b>')])
assert validate([row(arabic='اضغط [ENTER] {1} <b>افتح</b>')])
assert validate([row(arabic='اضغط [ENTER] {0} <b>افتح')])
assert validate([row(), row()])
assert validate([row(arabic='???')])
assert validate([row('Line\nLine', 'سطر سطر')])
for bad in (ROOT, ROOT.parent, ROOT / 'build'):
    try:
        safe_roots(bad)
    except (ValueError, FileNotFoundError):
        pass
    else:
        raise AssertionError(f'Unsafe nested source path accepted: {bad}')
print('PASS: placeholders, tags, duplicates, encoding sentinels, line breaks, path separation')
