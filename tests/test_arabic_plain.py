import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from arabic_plain import wrap_plain,visual_line,width_em

text='هذا اختبار طويل للتأكد من أن النص العربي يلتف داخل مساحة الواجهة بشكل صحيح ولا يخرج خارج حدود العنصر.'
lines,visual=wrap_plain(text,17)
assert len(lines)>1
assert ' '.join(lines)==text
assert all(width_em(line)<=17 for line in lines)
assert visual.split('\n')==[visual_line(line) for line in lines]
assert visual_line('HP: 100')=='HP: 100'
assert '27' in visual_line('الغرفة رقم 27')
assert 'Blue Prince' in visual_line('Blue Prince - الأمير الأزرق')
for unsupported in ('<b>مرحبا</b>','مرحبا {player}','اضغط [KEY]','القيمة %d',r'سطر\nسطر'):
    try:wrap_plain(unsupported,17)
    except ValueError:pass
    else:raise AssertionError('Unsupported runtime/rich input accepted')
import unicodedata
from collections import Counter
sample='مَرْحَبًا بِكَ'
marks=lambda s:Counter(c for c in unicodedata.normalize('NFKD',s) if unicodedata.category(c)=='Mn')
assert marks(visual_line(sample))==marks(sample)
assert wrap_plain('سطر أول\n\nسطر ثان',17)[0]==['سطر أول','','سطر ثان']
try:wrap_plain('Supercalifragilisticexpialidocious',1)
except ValueError:pass
else:raise AssertionError('Overwide unbreakable word accepted silently')
print('PASS: logical line order, measured width, Latin/numbers, diacritic retention, explicit breaks, unsafe-input rejection')
