"""Like make_pf_font.py but resolves the shaped glyphs with HarfBuzz (build-time only, pip install uharfbuzz),
so fonts that do their joining through contextual lookups (Aref Ruqaa, Scheherazade, ...) work too.

python make_pf_font_hb.py in.ttf out.ttf
"""
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from make_pf_font import FORMS, LAMALEF


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction, buf.script, buf.language = 'rtl', 'Arab', 'ar'
    hb.shape(font, buf, {'kern': False, 'liga': True, 'rlig': True, 'calt': True, 'init': True, 'medi': True, 'fina': True, 'isol': True})
    return [(i.codepoint, i.cluster) for i in buf.glyph_infos]


def glyph_at(font, text, cluster):
    hit = [g for g, c in shape(font, text) if c == cluster]
    return hit[0] if len(hit) == 1 else None


def main(src, dst):
    tt = TTFont(src)
    cmap = tt.getBestCmap()
    face = hb.Face(hb.Blob.from_file_path(src))
    hbf = hb.Font(face)
    beh = chr(0x0628)
    order = tt.getGlyphOrder()
    added, skipped = {}, []
    for base, cps in FORMS.items():
        if base not in cmap:
            continue
        c = chr(base)
        ctx = {0: c, 1: beh + c, 2: c + beh, 3: beh + c + beh}   # iso, fina, init, medi
        pos = {0: 0, 1: 1, 2: 0, 3: 1}
        for k, cp in enumerate(cps):
            if not cp or cp in cmap:
                continue
            gid = glyph_at(hbf, ctx[k], pos[k])
            if gid is None:
                skipped.append((hex(base), k)); continue
            added[cp] = order[gid]
    for alef, (iso_cp, fin_cp) in LAMALEF.items():
        if alef not in cmap:
            continue
        for text, cp, cl in ((chr(0x0644) + chr(alef), iso_cp, 0), (beh + chr(0x0644) + chr(alef), fin_cp, 1)):
            if cp in cmap:
                continue
            gs = shape(hbf, text)
            hit = [g for g, c in gs if c == cl]
            if len(hit) == 1 and (cl == 0 and len(gs) == 1 or cl == 1 and len(gs) == 2):
                added[cp] = order[hit[0]]
            else:
                skipped.append((hex(alef), 'lamalef', cl))
    for table in tt['cmap'].tables:
        if table.isUnicode() and table.format in (4, 12):
            table.cmap.update(added)
    tt.save(dst)
    print(f'{src}: added {len(added)}, skipped {len(skipped)} {skipped[:6]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
