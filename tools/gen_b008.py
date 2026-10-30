"""Build batch b008 (entrance letter, ground rules, final advice, energy tips): the game ships several near-identical
variants that differ only in blank-line runs, so each Arabic template gets the runs copied from the source variant."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
corpus = json.loads((ROOT / 'translation/work/corpus.json').read_text(encoding='utf-8'))
srcs = [x['src'] for x in corpus]


def runs(src):
    return re.findall(r'\n+', src)


def fill(src, tpl):
    r = runs(src)
    for i, run in enumerate(r, 1):
        tpl = tpl.replace('{R%d}' % i, run)
    assert '{R' not in tpl, (src[:40], r)
    return tpl


LETTER = ('سايمون،{R1}أهلاً بك في ماونت هولي.{R2}ربما لا تتذكر، لكنني أحتفظ بذكريات عزيزة عن زياراتك الكثيرة إلى هنا وأنت '
          'صبيٌّ صغير، وآمل أن تمنحك هذه الغرف من المتعة ما منحتك إياه في تلك الصيفيات الضائعة.{R3}'
          'حين تقرأ هذه الرسالة سأفترض أنك على علم تام برغباتي الأخيرة وبكل تفاصيل الوصية. أرجو ألا تفهم نيتي من تكليفك '
          'بهذا التحدي على أنها قلة ثقة. أؤكد لك أن هذا كان أبعد ما يكون عن بالي حين اخترتك وريثًا لي.')
LETTER_A = LETTER.replace('أنك على علم', 'أنك على علم')
RULES = ('ومع ذلك، هناك بعض القواعد الأساسية لهذه المهمة وردت في البنود الدقيقة من وصيتي، وأرى أن عليّ لفت انتباهك إليها:{R1}\n\n\n'
         'لا أظن أن أيًّا من هذه الشروط سيشكّل عائقًا لشخص واسع الحيلة مثلك، لكن من المهم جدًا عندي أن "تبدأ من جديد" '
         'كل صباح وألا تعتمد على نجاحات اليوم السابق.')
ADVICE_COLON = 'كلمة أخيرة من النصح:{R1}لا تفترض أن الغرف التي تجدها اليوم ستكون نفسها التي ستجدها غدًا. لقد كانت هذه الأراضي بيتي طوال نصف القرن الماضي، وحتى أنا لست على يقين من الغرفة التي تقع خلف أي باب بعينه.{R2}كانت جدتك تقول: "لا تذهب حيث يقودك الطريق. اترك الطريق واذهب حيث تريده أن يقودك."{R3}'
ADVICE_COMMA = 'كلمة أخيرة من النصح.{R1}لا تفترض أن الغرف التي تجدها اليوم ستكون نفسها التي ستجدها غدًا. لقد كانت هذه الأراضي بيتي طوال نصف القرن الماضي، وحتى أنا لست على يقين من الغرفة التي تقع خلف أي باب بعينه.{R2}كانت جدتك تقول: "لا تذهب حيث يقودك الطريق. اترك الطريق واذهب حيث تريده أن يقودك."{R3}'
ADVICE_OLD = 'كلمة أخيرة من النصح.{R1}لا تفترض أن الغرف التي تجدها اليوم ستكون نفسها التي ستجدها غدًا. لقد كانت هذه الأراضي بيتي طوال نصف القرن الماضي، وحتى أنا لست على يقين من الغرفة التي تقع خلف أي باب بعينه.{R2}كانت جدتك تقول:{R3}"لا تذهب حيث يقودك الطريق . . .{R4}اترك الطريق واذهب حيث تريده أن يقودك."{R5}'

out = {}
for s in srcs:
    if s.startswith('Simon,') and 'Welcome to Mount Holly' in s[:40]:
        out[s] = fill(s, LETTER)
    elif s.startswith('With that said'):
        out[s] = fill(s, RULES)
    elif s.startswith('One final word of advice:'):
        out[s] = fill(s, ADVICE_COLON)
    elif s.startswith('One final word of advice.') and 'You grandmother' in s:
        out[s] = fill(s, ADVICE_OLD)
    elif s.startswith('One final word of advice.'):
        out[s] = fill(s, ADVICE_COMMA)

TIP = {
    'Each time you enter a room you will lose': 'في كل مرة تدخل فيها غرفة ستفقد {GAP}.{R1}وحين لا يتبقى لديك أي {GAP} ستكون مرهقًا جدًا بحيث لا تستطيع مواصلة البحث في القصر، وعليك أن <i><color={C}>تنهي اليوم.',
}
for s in srcs:
    if s.startswith('Each time you enter a room you will lose'):
        gaps = re.findall(r' {4,}', s)
        c = re.search(r'<color=(#[0-9A-Fa-f]{6})>', s).group(1)
        ar = TIP['Each time you enter a room you will lose'].replace('{C}', c)
        r = runs(s)
        # first blank-run after the first sentence is the paragraph break
        brk = [x for x in r if len(x) >= 2][0]
        ar = ar.replace('{R1}', brk)
        ar = ar.replace('{GAP}', gaps[0], 1).replace('{GAP}', gaps[1] if len(gaps) > 1 else gaps[0], 1)
        out[s] = ar
    if s.startswith('     represent how much energy'):
        gaps = re.findall(r' {4,}', s)
        out[s] = ('     تمثّل مقدار الطاقة المتبقية لديك\nللاستكشاف.\n\nفي كل مرة تدخل فيها غرفة،\nستفقد 1    .\n\n'
                  'وحين لا يتبقى لديك أي     \nعليك أن                   .')
    if s.startswith('You must have') and 'to draft' in s:
        out[s] = 'يجب أن يكون لديك                                    للاختيار.'

(ROOT / 'translation/arabic/batches/b008.json').write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
print(len(out), 'entries')
