using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

namespace BluePrinceArabic
{
    // Papers (letters, memos, lists, books: scene roots named "... - doc") use many different Latin fonts, so the Arabic
    // fallback gave them different looks (and digits/punctuation stayed in the Latin font). All of them get the one
    // Arabic serif face (Amiri) as their main font while Arabic is shown; the original font comes back in English mode.
    static class DocFont
    {
        static readonly Dictionary<int, bool> paper = new Dictionary<int, bool>();
        static readonly Dictionary<int, TMP_FontAsset> orig = new Dictionary<int, TMP_FontAsset>();

        static bool IsDocName(string n) =>
            n.EndsWith("doc", StringComparison.OrdinalIgnoreCase) && (n.Length == 3 || !char.IsLetter(n[n.Length - 4]));

        public static bool IsPaper(TMP_Text t)
        {
            int id = t.GetInstanceID();
            if (paper.TryGetValue(id, out var p)) return p;
            p = false;
            var tr = t.transform;
            for (int i = 0; tr != null && i < 16; i++, tr = tr.parent)
                if (IsDocName(tr.name)) { p = true; break; }
            paper[id] = p;
            return p;
        }

        public static void Apply(TMP_Text t)
        {
            var f = ArabicFont.Serif;
            if (f == null) return;
            var cur = t.font;
            if (cur == null || cur.GetInstanceID() == f.GetInstanceID()) return;
            orig[t.GetInstanceID()] = cur;
            t.font = f;
        }

        public static void Restore(TMP_Text t)
        {
            if (orig.Count == 0) return;
            int id = t.GetInstanceID();
            if (!orig.TryGetValue(id, out var o)) return;
            orig.Remove(id);
            if (o != null) t.font = o;
        }
    }
}
