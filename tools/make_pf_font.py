"""Give an Arabic font the Unicode "presentation form" cmap entries (U+FB50-FEFC) that TextMeshPro needs.

TMP does no OpenType shaping, so the plugin pre-shapes Arabic into presentation forms. Many modern fonts only
reach those glyphs through GSUB (isol/fina/init/medi + lam-alef ligatures). This script resolves that GSUB
chain per letter and maps the presentation codepoints straight to the resulting glyphs.

python make_pf_font.py in.ttf out.ttf
"""
import sys
from fontTools.ttLib import TTFont

# base char -> (isolated, final, initial, medial) presentation codepoints (same table as Shaper.cs)
FORMS = {
    0x0621: (0xFE80, 0, 0, 0), 0x0622: (0xFE81, 0xFE82, 0, 0), 0x0623: (0xFE83, 0xFE84, 0, 0),
    0x0624: (0xFE85, 0xFE86, 0, 0), 0x0625: (0xFE87, 0xFE88, 0, 0), 0x0626: (0xFE89, 0xFE8A, 0xFE8B, 0xFE8C),
    0x0627: (0xFE8D, 0xFE8E, 0, 0), 0x0628: (0xFE8F, 0xFE90, 0xFE91, 0xFE92), 0x0629: (0xFE93, 0xFE94, 0, 0),
    0x062A: (0xFE95, 0xFE96, 0xFE97, 0xFE98), 0x062B: (0xFE99, 0xFE9A, 0xFE9B, 0xFE9C),
    0x062C: (0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0), 0x062D: (0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4),
    0x062E: (0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8), 0x062F: (0xFEA9, 0xFEAA, 0, 0), 0x0630: (0xFEAB, 0xFEAC, 0, 0),
    0x0631: (0xFEAD, 0xFEAE, 0, 0), 0x0632: (0xFEAF, 0xFEB0, 0, 0), 0x0633: (0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4),
    0x0634: (0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8), 0x0635: (0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC),
    0x0636: (0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0), 0x0637: (0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4),
    0x0638: (0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8), 0x0639: (0xFEC9, 0xFECA, 0xFECB, 0xFECC),
    0x063A: (0xFECD, 0xFECE, 0xFECF, 0xFED0), 0x0641: (0xFED1, 0xFED2, 0xFED3, 0xFED4),
    0x0642: (0xFED5, 0xFED6, 0xFED7, 0xFED8), 0x0643: (0xFED9, 0xFEDA, 0xFEDB, 0xFEDC),
    0x0644: (0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0), 0x0645: (0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4),
    0x0646: (0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8), 0x0647: (0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC),
    0x0648: (0xFEED, 0xFEEE, 0, 0), 0x0649: (0xFEEF, 0xFEF0, 0, 0), 0x064A: (0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4),
    0x067E: (0xFB56, 0xFB57, 0xFB58, 0xFB59), 0x0686: (0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D),
    0x06A4: (0xFB6A, 0xFB6B, 0xFB6C, 0xFB6D), 0x06AF: (0xFB92, 0xFB93, 0xFB94, 0xFB95),
    0x0698: (0xFB8A, 0xFB8B, 0, 0),
}
TAGS = ('isol', 'fina', 'init', 'medi')
# lam + alef ligatures: alef base char -> (isolated-ligature cp, final-ligature cp)
LAMALEF = {0x0622: (0xFEF5, 0xFEF6), 0x0623: (0xFEF7, 0xFEF8), 0x0625: (0xFEF9, 0xFEFA), 0x0627: (0xFEFB, 0xFEFC)}


def lookups_for(gsub, tags):
    idx = []
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag in tags:
            for i in fr.Feature.LookupListIndex:
                if i not in idx:
                    idx.append(i)
    return idx


def subtables(gsub, i):
    lk = gsub.LookupList.Lookup[i]
    for st in lk.SubTable:
        yield getattr(st, 'ExtSubTable', st)


def single_map(gsub, tag):
    """Merged glyph->glyph single substitutions of every lookup under a feature tag."""
    m = {}
    for i in lookups_for(gsub, (tag,)):
        for st in subtables(gsub, i):
            if hasattr(st, 'mapping'):
                for k, v in st.mapping.items():
                    if isinstance(v, list) and len(v) == 1:
                        v = v[0]  # MultipleSubst with a single output behaves like a single substitution
                    if isinstance(v, str):
                        m.setdefault(k, v)
    return m


def ligatures(gsub, tags):
    out = {}  # (first, second...) -> lig glyph
    for i in lookups_for(gsub, tags):
        for st in subtables(gsub, i):
            if hasattr(st, 'ligatures'):
                for first, ligs in st.ligatures.items():
                    for lg in ligs:
                        out.setdefault(tuple([first] + list(lg.Component)), lg.LigGlyph)
    return out


def main(src, dst):
    font = TTFont(src)
    cmap = font.getBestCmap()
    gsub = font['GSUB'].table
    maps = {t: single_map(gsub, t) for t in TAGS}
    added, skipped = {}, []
    for base, cps in FORMS.items():
        g = cmap.get(base)
        if g is None:
            continue
        for tag, cp in zip(TAGS, cps):
            if not cp or cp in cmap:
                continue
            shaped = maps[tag].get(g, g if tag == 'isol' else None)
            if shaped is None:
                skipped.append((hex(base), tag))
                continue
            added[cp] = shaped
    # lam-alef
    lig = ligatures(gsub, ('rlig', 'liga', 'ccmp', 'calt'))
    lam = cmap.get(0x0644)
    for alef, (iso_cp, fin_cp) in LAMALEF.items():
        a = cmap.get(alef)
        if lam is None or a is None:
            continue
        a_fin = maps['fina'].get(a, a)
        for lam_form, cp in (('init', iso_cp), ('medi', fin_cp)):
            l = maps[lam_form].get(lam, lam)
            res = lig.get((l, a_fin)) or lig.get((l, a))
            if res and cp not in cmap:
                added[cp] = res
            elif cp not in cmap:
                skipped.append((hex(alef), 'lamalef-' + lam_form))
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format in (4, 12):
            table.cmap.update(added)
    font.save(dst)
    print(f'{src}: added {len(added)} presentation codepoints, skipped {len(skipped)} {skipped[:8]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
