"""Generate translation/arabic/ar_patterns.json: regex -> replacement for dynamic strings (dates, counters).

The plugin tries these only after an exact/case-insensitive dictionary lookup fails. Replacement uses .NET syntax ($1).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [('Jan', 'January', 'يناير'), ('Feb', 'February', 'فبراير'), ('Mar', 'March', 'مارس'), ('Apr', 'April', 'أبريل'),
          ('May', 'May', 'مايو'), ('Jun', 'June', 'يونيو'), ('Jul', 'July', 'يوليو'), ('Aug', 'August', 'أغسطس'),
          ('Sep', 'September', 'سبتمبر'), ('Oct', 'October', 'أكتوبر'), ('Nov', 'November', 'نوفمبر'), ('Dec', 'December', 'ديسمبر')]
DAYS = [('Mon', 'الاثنين'), ('Tue', 'الثلاثاء'), ('Wed', 'الأربعاء'), ('Thu', 'الخميس'), ('Fri', 'الجمعة'), ('Sat', 'السبت'), ('Sun', 'الأحد')]
MODES = [('DARE MODE', 'وضع التحدي'), ('CURSE MODE', 'وضع اللعنة'), ('BEQUEST MODE', 'وضع الإرث')]

P = {}
for ab, full, ar in MONTHS:
    m = f'(?:{full}|{ab}\\.?)'
    P[f'(?i)^{m}\\s+(\\d{{1,2}})\\s+\'(\\d{{2}})$'] = f"$1 {ar} '$2"
    P[f'(?i)^{m}\\s+\'(\\d{{2}})$'] = f"{ar} '$1"
    P[f'(?i)^{m}\\s+(\\d{{1,2}})$'] = f"$1 {ar}"
    P[f'(?i)^{m}\\s+(\\d{{1,2}})\\s*-\\s*(\\d+)$'] = f"$1 {ar} - $2"
    P[f'(?i)^{m}\\s+(\\d{{4}})\\s*-\\s*$'] = f"{ar} $1 - "
    P[f'(?i)^{m}\\s+ISSUE$'] = f"عدد {ar}"
for d, ar in DAYS:
    for ab, full, mar in MONTHS:
        P[f'(?i)^{d}[a-z]*\\s+{ab}[a-z]*\\s+(\\d{{1,2}})$'] = f'{ar} $1 {mar}'
P['(?i)^((?:<[^>]+>)*)day\\s+(\\d+)((?:<[^>]+>)*)$'] = '$1اليوم $2$3'
P['(?i)^rooms\\s+(\\d+)\\s*-\\s*(\\d+)$'] = 'الغرف $1-$2'
P['(?i)^days?\\s+(\\d+)\\s*&\\s*(\\d+)$'] = 'اليومان $1 و$2'
P['(?i)^(\\d+)\\s+days?$'] = '$1 يوم'
P['(?i)^total\\s*:\\s*(\\d+)$'] = 'المجموع: $1'
P['^(\\d+)h (\\d+)m$'] = '$1س $2د'
for en, ar in MODES:
    P[f'^PROFILE (\\d+) : <b>DAY (\\d+)</b> \\| {en} \\| (\\d+) TROPHIES$'] = f'الملف $1 : <b>اليوم $2</b> | {ar} | $3 كؤوس'
    P[f'^PROFILE (\\d+) : <b>DAY (\\d+)</b> \\| {en} \\| 1 TROPHY$'] = f'الملف $1 : <b>اليوم $2</b> | {ar} | كأس واحدة'
P['^PROFILE (\\d+) : <b>DAY (\\d+)</b> \\| (\\d+) TROPHIES$'] = 'الملف $1 : <b>اليوم $2</b> | $3 كؤوس'
P['^PROFILE (\\d+)$'] = 'الملف $1'
P['(?i)^room\\s+(\\d+)$'] = 'الغرفة $1'
P['(?i)^rank\\s+(\\d+)$'] = 'الصف $1'

# '*' = chained line patterns (applied cumulatively): terminal account cards are typed in stages
for en, ar in (('Account Created :', 'تاريخ إنشاء الحساب :'), ('Last Login :', 'آخر تسجيل دخول :'),
               ('Most Drafted Room :', 'أكثر غرفة اختيارًا :'), ('Personnel Notes :', 'ملاحظات الموظف :')):
    P['*<b>' + en + '</b>'] = '<b>' + ar + '</b>'
for en, ar in (('Laboratory', 'المختبر'), ('Office', 'المكتب'), ("Servant's Quarters", 'مساكن الخدم'), ('Greenhouse', 'الدفيئة')):
    P['*:</b> ' + en + '(?=\n|$)'] = ':</b> ' + ar
for en, ar in (('Lead Lab Technician for SYNKA, setup\nestate terminals and Blackbridge network.', 'كبير فنيي المختبر في SYNKA، أعدّ\nأجهزة العقار وشبكة Blackbridge.'),
               ("The Baron's valet (for 20 years).\nSubstituting for Mr. Moore until we find a\nsuitable assistant admin.", 'خادم البارون الخاص (منذ 20 عامًا).\nيحلّ محل السيد مور إلى أن نجد\nمساعد مسؤول مناسبًا.'),
               ('Author of all personnel notes.', 'كاتب جميع ملاحظات الموظفين.'),
               ('Terminated March 1992 for suspicion of\nblackmail and not watering the plants.', 'فُصل في مارس 1992 للاشتباه في\nالابتزاز وعدم سقي النباتات.'),
               ('Recent transfer from SYNKA, former\nexecutive assistant to H.S. Sinclair.\nTrusted with full admin privileges.', 'منقول حديثًا من SYNKA، المساعد التنفيذي\nالسابق لـ ه.س. سنكلير.\nموثوق بصلاحيات إدارية كاملة.')):
    P['*' + re.escape(en)] = ar
# terminal admin-key list and e-mail headers: cumulative line patterns
for en, ar in (('ADMIN ACCESS', 'صلاحية مسؤول'), ('PERSONNEL ACCESS', 'صلاحية موظفين'), ('KEY EXPIRED', 'انتهى المفتاح')):
    P['*\\[' + en + '\\]'] = '[' + ar + ']'
P['*\\+ three additional delisted admin keys'] = '+ ثلاثة مفاتيح إدارة أخرى محذوفة'
P['*\\bfrom :'] = 'من :'
P['*\\bto :'] = 'إلى :'
for en, ar in (('stop recording', 'إيقاف التسجيل'), ('security measures', 'إجراءات الأمن'), ('Another Request', 'طلب آخر'),
               ('Precautions', 'احتياطات'), ('freezer access', 'الوصول إلى المجمّد'), ('stay put', 'ابقَ مكانك'),
               ('the situation', 'الوضع'), ('electronic mail', 'البريد الإلكتروني')):
    P['*<b>\\s*re: ' + en + '\\s*</b>'] = '<b>رد: ' + ar + ' </b>'
    P['*<b>\\s*' + en + '\\s*</b>'] = '<b>' + ar + ' </b>'
# template with a room name inside: {T1} is translated through the dictionary by the plugin
P['(?s)^You found a secret Floorplan!\\s*<size=1>Would you like to <b><size=1.2>permanently</b></size> add\\s*</size><size=1.8><b>(.+?)</b></size>\\s*to your drafting pool\\?\\s*$'] = \
    'عثرت على مخطط سري!\n\n<size=1>هل تريد إضافة <b><size=1.2>بشكل دائم</b></size>\n</size><size=1.8><b>{T1}</b></size>\nإلى مجموعة اختياراتك؟'
P['(?s)^You dug up a secret Floorplan!\\s*<size=1>Would you like to <b><size=1.2>permanently</b></size> add\\s*</size><size=1.5><b>(.+?)</b></size>\\s*to your drafting pool\\?\\s*$'] = \
    'عثرت أثناء الحفر على مخطط سري!\n\n<size=1>هل تريد إضافة <b><size=1.2>بشكل دائم</b></size>\n</size><size=1.5><b>{T1}</b></size>\nإلى مجموعة اختياراتك؟'
P['(?s)^You found a secret Floor Plan!\\s*<size=\\.73>Would you like to <b>permanently</b> add\\s*</size><size=1\\.1><b>(.+?)</b></size>\\s*to your drafting pool\\?\\s*$'] = \
    'عثرت على مخطط سري!\n\n<size=.73>هل تريد إضافة <b>بشكل دائم</b>\n</size><size=1.1><b>{T1}</b></size>\nإلى مجموعة اختياراتك؟'
P['(?is)^This room will be added back to<br>the drafting pool in (\\d+) days?\\.?\\s*$'] = 'ستُضاف هذه الغرفة مجددًا إلى<br>مجموعة الاختيارات خلال $1 يوم.'
out = ROOT / 'translation/arabic/ar_patterns.json'
out.write_text(json.dumps(P, ensure_ascii=False, indent=0), encoding='utf-8')
print(len(P), 'patterns ->', out)
