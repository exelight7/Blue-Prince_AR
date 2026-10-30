using System.Collections.Generic;
using System.Text;

namespace BluePrinceArabic
{
    // Logical Arabic -> pre-shaped (presentation forms) string for TMP running with RTL on.
    // TMP's RTL layout places the first char at the right edge, so Arabic stays in logical order,
    // while LTR runs (Latin, digits) are stored reversed so they read correctly.
    public static class Shaper
    {
        // iso, final, initial, medial (0 = form missing)
        static readonly Dictionary<char, int[]> Forms = new Dictionary<char, int[]>
        {
            ['ء'] = new[] { 0xFE80, 0, 0, 0 },
            ['آ'] = new[] { 0xFE81, 0xFE82, 0, 0 },
            ['أ'] = new[] { 0xFE83, 0xFE84, 0, 0 },
            ['ؤ'] = new[] { 0xFE85, 0xFE86, 0, 0 },
            ['إ'] = new[] { 0xFE87, 0xFE88, 0, 0 },
            ['ئ'] = new[] { 0xFE89, 0xFE8A, 0xFE8B, 0xFE8C },
            ['ا'] = new[] { 0xFE8D, 0xFE8E, 0, 0 },
            ['ب'] = new[] { 0xFE8F, 0xFE90, 0xFE91, 0xFE92 },
            ['ة'] = new[] { 0xFE93, 0xFE94, 0, 0 },
            ['ت'] = new[] { 0xFE95, 0xFE96, 0xFE97, 0xFE98 },
            ['ث'] = new[] { 0xFE99, 0xFE9A, 0xFE9B, 0xFE9C },
            ['ج'] = new[] { 0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0 },
            ['ح'] = new[] { 0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4 },
            ['خ'] = new[] { 0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8 },
            ['د'] = new[] { 0xFEA9, 0xFEAA, 0, 0 },
            ['ذ'] = new[] { 0xFEAB, 0xFEAC, 0, 0 },
            ['ر'] = new[] { 0xFEAD, 0xFEAE, 0, 0 },
            ['ز'] = new[] { 0xFEAF, 0xFEB0, 0, 0 },
            ['س'] = new[] { 0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4 },
            ['ش'] = new[] { 0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8 },
            ['ص'] = new[] { 0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC },
            ['ض'] = new[] { 0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0 },
            ['ط'] = new[] { 0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4 },
            ['ظ'] = new[] { 0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8 },
            ['ع'] = new[] { 0xFEC9, 0xFECA, 0xFECB, 0xFECC },
            ['غ'] = new[] { 0xFECD, 0xFECE, 0xFECF, 0xFED0 },
            ['ـ'] = new[] { 0x0640, 0x0640, 0x0640, 0x0640 },
            ['ف'] = new[] { 0xFED1, 0xFED2, 0xFED3, 0xFED4 },
            ['ق'] = new[] { 0xFED5, 0xFED6, 0xFED7, 0xFED8 },
            ['ك'] = new[] { 0xFED9, 0xFEDA, 0xFEDB, 0xFEDC },
            ['ل'] = new[] { 0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0 },
            ['م'] = new[] { 0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4 },
            ['ن'] = new[] { 0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8 },
            ['ه'] = new[] { 0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC },
            ['و'] = new[] { 0xFEED, 0xFEEE, 0, 0 },
            ['ى'] = new[] { 0xFEEF, 0xFEF0, 0, 0 },
            ['ي'] = new[] { 0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4 },
            // extras used for foreign sounds in names
            ['پ'] = new[] { 0xFB56, 0xFB57, 0xFB58, 0xFB59 },
            ['چ'] = new[] { 0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D },
            ['ڤ'] = new[] { 0xFB6A, 0xFB6B, 0xFB6C, 0xFB6D },
            ['گ'] = new[] { 0xFB92, 0xFB93, 0xFB94, 0xFB95 },
            ['ژ'] = new[] { 0xFB8A, 0xFB8B, 0, 0 },
        };

        static bool Dual(char c) => Forms.TryGetValue(c, out var f) && f[2] != 0;
        static bool Joinable(char c) => Forms.ContainsKey(c) && c != 'ء';
        static bool IsMark(char c) => (c >= 'ً' && c <= 'ٟ') || c == 'ٰ' || (c >= 'ۖ' && c <= 'ۭ');
        public static bool IsArabic(char c) => (c >= '؀' && c <= 'ۿ') || (c >= 'ݐ' && c <= 'ݿ') || (c >= 'ﭐ' && c <= '﻿');
        public static bool HasArabic(string s) { foreach (var c in s) if (IsArabic(c)) return true; return false; }

        static readonly Dictionary<char, char> Mirror = new Dictionary<char, char>
        {
            ['('] = ')', [')'] = '(', ['['] = ']', [']'] = '[', ['{'] = '}', ['}'] = '{', ['«'] = '»', ['»'] = '«',
        };

        enum D : byte { R, L, E, N, Tag }

        // A token is one char, or a whole <tag> kept atomic.
        sealed class Tok { public string S; public char Src; public D Dir; public bool IsTag; }

        public static string Process(string logical, bool stripMarks = true)
        {
            var toks = Tokenize(logical, stripMarks);
            Shape(toks);
            ResolveDirections(toks);
            return Emit(toks);
        }

        static List<Tok> Tokenize(string s, bool stripMarks)
        {
            var list = new List<Tok>(s.Length);
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<')
                {
                    int e = s.IndexOf('>', i);
                    if (e > i && e - i < 80 && !char.IsWhiteSpace(s[i + 1]))
                    {
                        list.Add(new Tok { S = s.Substring(i, e - i + 1), IsTag = true, Dir = D.Tag });
                        i = e; continue;
                    }
                }
                if (stripMarks && IsMark(c)) continue;
                list.Add(new Tok { S = c.ToString(), Src = c });
            }
            return list;
        }

        static void Shape(List<Tok> t)
        {
            for (int i = 0; i < t.Count; i++)
            {
                var tk = t[i];
                if (tk.IsTag || tk.S.Length != 1) continue;
                char c = tk.Src;
                if (!Forms.TryGetValue(c, out var f)) continue;

                int p = Neighbor(t, i, -1), n = Neighbor(t, i, +1);
                bool prevJoins = p >= 0 && Dual(t[p].Src);
                if (c == 'ل' && n >= 0)
                {
                    int lig = 0; char a = t[n].Src;
                    if (a == 'آ') lig = 0xFEF5; else if (a == 'أ') lig = 0xFEF7; else if (a == 'إ') lig = 0xFEF9; else if (a == 'ا') lig = 0xFEFB;
                    if (lig != 0)
                    {
                        tk.S = ((char)(prevJoins ? lig + 1 : lig)).ToString();
                        t[n].S = "";
                        continue;
                    }
                }
                bool nextJoins = n >= 0 && Dual(c) && Joinable(t[n].Src);
                int idx = prevJoins ? (nextJoins ? 3 : 1) : (nextJoins ? 2 : 0);
                int cp = f[idx]; if (cp == 0) cp = f[prevJoins ? 1 : 0]; if (cp == 0) cp = f[0];
                tk.S = ((char)cp).ToString();
            }
        }

        // nearest non-empty non-tag neighbour that is an Arabic letter (by source char); -1 if something else breaks the join
        static int Neighbor(List<Tok> t, int i, int dir)
        {
            for (int k = i + dir; k >= 0 && k < t.Count; k += dir)
            {
                if (t[k].IsTag || t[k].Src == '\0') continue;
                return Forms.ContainsKey(t[k].Src) ? k : -1;
            }
            return -1;
        }

        static bool IsLatin(char c) => (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= 'À' && c <= 'ɏ');
        static bool IsDigit(char c) => c >= '0' && c <= '9';

        // Simplified UBA for an RTL paragraph: letters = L, digits = EN (turn L after a Latin strong, W7),
        // neutrals become LTR only between two LTR strongs.
        static void ResolveDirections(List<Tok> t)
        {
            foreach (var k in t)
            {
                if (k.IsTag) { k.Dir = D.Tag; continue; }
                if (k.S.Length == 0) { k.Dir = D.N; continue; }
                char c = k.Src;
                k.Dir = IsArabic(c) ? D.R : IsLatin(c) ? D.L : IsDigit(c) ? D.E : D.N;
            }
            // W4/ET: one separator between digits, % after digits, currency/# before digits stay with the number
            for (int i = 0; i < t.Count; i++)
            {
                if (t[i].Dir != D.N || t[i].S.Length != 1) continue;
                char c = t[i].Src;
                bool pe = i > 0 && t[i - 1].Dir == D.E, ne = i + 1 < t.Count && t[i + 1].Dir == D.E;
                if (((c == '.' || c == ',' || c == ':' || c == '/' || c == '+' || c == '-') && pe && ne) ||
                    (c == '%' && pe) || ((c == '$' || c == '#' || c == '€' || c == '£') && ne))
                    t[i].Dir = D.E;
            }
            // W7: digits following a Latin strong are LTR letters
            D last = D.R;
            foreach (var k in t)
            {
                if (k.Dir == D.L || k.Dir == D.R) last = k.Dir;
                else if (k.Dir == D.E && last == D.L) k.Dir = D.L;
            }
            // "D.C." / "R.T.A.": the dot that closes a dotted Latin abbreviation stays with it (plain UBA would throw it to the far side of the word)
            for (int i = 3; i < t.Count; i++)
                if (t[i].Dir == D.N && t[i].Src == '.' && t[i - 1].Dir == D.L && t[i - 2].Src == '.' && t[i - 3].Dir == D.L) t[i].Dir = D.L;
            for (int i = 0; i < t.Count; i++)
            {
                if (t[i].Dir != D.N) continue;
                int b = i;
                while (b + 1 < t.Count && (t[b + 1].Dir == D.N || t[b + 1].Dir == D.Tag)) b++;
                D before = D.R, after = D.R;
                for (int k = i - 1; k >= 0; k--) if (t[k].Dir != D.N && t[k].Dir != D.Tag) { before = t[k].Dir; break; }
                if (b + 1 < t.Count) after = t[b + 1].Dir;
                D res = (before == D.L && after == D.L) ? D.L : D.R;
                for (int k = i; k <= b; k++) if (t[k].Dir == D.N) t[k].Dir = res;
                i = b;
            }
        }

        static string Emit(List<Tok> t)
        {
            var sb = new StringBuilder();
            int i = 0;
            while (i < t.Count)
            {
                var tk = t[i];
                if (tk.IsTag || tk.S.Length == 0) { sb.Append(tk.S); i++; continue; }
                if (tk.Dir == D.L || tk.Dir == D.E)
                {
                    int j = i;
                    var run = new List<string>();
                    while (j < t.Count && !t[j].IsTag && (t[j].Dir == D.L || t[j].Dir == D.E || t[j].S.Length == 0))
                    {
                        if (t[j].S.Length > 0) run.Add(t[j].S == " " ? " " : t[j].S);
                        j++;
                    }
                    for (int k = run.Count - 1; k >= 0; k--) sb.Append(run[k]);
                    i = j; continue;
                }
                string s = tk.S;
                if (s.Length == 1 && Mirror.TryGetValue(s[0], out var m)) s = m.ToString();
                sb.Append(s); i++;
            }
            return sb.ToString();
        }
    }
}
