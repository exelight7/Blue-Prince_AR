"""Plain static Arabic only: wrap logical words before shaping/BiDi per line."""
from functools import lru_cache
import re
import arabic_reshaper
from bidi.algorithm import get_display
from fontTools.ttLib import TTFont
from project import ROOT
from validate import tokens

RESHAPER=arabic_reshaper.ArabicReshaper(configuration={
    'delete_harakat':False,'shift_harakat_position':True})


@lru_cache(maxsize=1)
def font_metrics():
    font=TTFont(ROOT/'fonts/original/sharedassets1.assets__211__NotoNaskhArabic-Medium.ttf')
    cmap=font.getBestCmap()
    return cmap,dict(font['hmtx'].metrics),font['head'].unitsPerEm


def visual_line(text):
    if any(c in text for c in '<>{}[]') or tokens(text):
        raise ValueError('Plain static text only; handle tags, variables and escapes separately')
    return get_display(RESHAPER.reshape(text),base_dir='R') if re.search(r'[\u0600-\u06ff]',text) else text


def width_em(text):
    cmap,metrics,units=font_metrics()
    visual=visual_line(text)
    missing=[ord(c) for c in visual if ord(c) not in cmap]
    if missing:raise ValueError(f'Missing font glyphs: {missing}')
    return sum(metrics[cmap[ord(c)]][0] for c in visual)/units


def wrap_plain(text,max_em):
    if any(c in text for c in '<>{}[]') or tokens(text):
        raise ValueError('Expand placeholders and handle rich text separately; this probe is plain text only')
    if max_em<=0:raise ValueError('Width must be positive')
    logical=[]
    for paragraph in text.split('\n'):
        line=''
        for word in paragraph.split():
            if width_em(word)>max_em:
                raise ValueError('Unbreakable token exceeds the measured width; review layout')
            candidate=(line+' '+word).strip()
            if line and width_em(candidate)>max_em:
                logical.append(line);line=word
            else:line=candidate
        logical.append(line)
    if ' '.join(' '.join(logical).split())!=' '.join(text.split()):
        raise ValueError('Wrapping lost or reordered words')
    return logical,'\n'.join(visual_line(line) for line in logical)
