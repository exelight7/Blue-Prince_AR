using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;

namespace BluePrinceArabic
{
    // source text -> logical Arabic. Exact match first, then trimmed, then regex patterns.
    public static class Translator
    {
        public static Dictionary<string, string> Map = new Dictionary<string, string>();
        static Dictionary<string, string> lower = new Dictionary<string, string>();
        static List<KeyValuePair<Regex, string>> patterns = new List<KeyValuePair<Regex, string>>();
        static List<KeyValuePair<Regex, string>> chain = new List<KeyValuePair<Regex, string>>(); // '*' patterns: applied one after another, for multi-line texts built from translated lines
        static Dictionary<string, string> tagwords = new Dictionary<string, string>(); // room-type words used in comma-separated header lines (Drafting, Blueprint, Dead End ...)
        static readonly HashSet<string> logged = new HashSet<string>();
        static readonly StringBuilder pending = new StringBuilder();
        public static int Misses;

        static readonly Regex Tags = new Regex(@"<[^>]*>|\[[A-Za-z_ ]{1,12}\]|\{[A-Za-z0-9_]{1,12}\}", RegexOptions.Compiled);
        static readonly Regex Latin = new Regex(@"[A-Za-z]{2}", RegexOptions.Compiled);

        public static void Load(string dir)
        {
            Map.Clear(); patterns.Clear(); chain.Clear(); TextOps.ClearCache();
            var mp = Path.Combine(dir, "ar.json");
            if (File.Exists(mp)) Map = Json.ReadStringMap(File.ReadAllText(mp, Encoding.UTF8));
            var pp = Path.Combine(dir, "ar_patterns.json");
            if (File.Exists(pp))
                foreach (var kv in Json.ReadStringMap(File.ReadAllText(pp, Encoding.UTF8)))
                {
                    bool ch = kv.Key.StartsWith("*");
                    var item = new KeyValuePair<Regex, string>(new Regex(ch ? kv.Key.Substring(1) : kv.Key, RegexOptions.Compiled | RegexOptions.Singleline), kv.Value);
                    (ch ? chain : patterns).Add(item);
                }
            tagwords.Clear();
            var tp = Path.Combine(dir, "tagwords.json");
            if (File.Exists(tp)) tagwords = Json.ReadStringMap(File.ReadAllText(tp, Encoding.UTF8));
            lower.Clear();
            foreach (var kv in Map) { var k = kv.Key.Trim().ToLowerInvariant(); if (!lower.ContainsKey(k)) lower[k] = kv.Value; }
            Plugin.Log.LogInfo($"translations: {Map.Count} entries, {patterns.Count} patterns");
        }

        public static bool LooksTranslatable(string s) => Latin.IsMatch(Tags.Replace(s, ""));

        // returns logical Arabic, or null when the text should stay as it is
        static readonly Regex Wrapper = new Regex(@"^((?:<[^>]+>|\s)*)(.*?)((?:<[^>]+>|\s)*)$", RegexOptions.Compiled | RegexOptions.Singleline);

        static bool Find(string s, out string ar)
        {
            if (Map.TryGetValue(s, out ar)) return true;
            return lower.TryGetValue(s.Trim().ToLowerInvariant(), out ar); // LocalizedText upper-cases its output
        }

        public static string Translate(string src, string where)
        {
            string res = Resolve(src);
            if (res == null) { if (LooksTranslatable(src)) Miss(src, where); return null; }
            return res == src ? null : res; // identity entry = deliberately kept in English
        }

        static string Resolve(string src)
        {
            if (Map.TryGetValue(src, out var ar)) return ar;
            // outer whitespace/newlines/tags carry layout (stacked menu labels use leading "\n"), so keep them
            var m = Wrapper.Match(src);
            if (m.Success && (m.Groups[1].Length > 0 || m.Groups[3].Length > 0) && m.Groups[2].Length > 0 && Find(m.Groups[2].Value, out ar))
                return m.Groups[1].Value + ar + m.Groups[3].Value;
            if (lower.TryGetValue(src.Trim().ToLowerInvariant(), out ar)) return ar;
            foreach (var p in patterns)
                if (p.Key.IsMatch(src)) return p.Key.Replace(src, mm => Expand(mm, p.Value));
            if (chain.Count > 0)
            {
                string t = src;
                foreach (var p in chain) t = p.Key.Replace(t, p.Value);
                if (t != src) return t;
            }
            return TagLine(src);
        }

        static readonly Regex TagOrWord = new Regex(@"<[^>]*>|[A-Za-z](?:[A-Za-z '’]*[A-Za-z])?", RegexOptions.Compiled);

        // "Drafting, <color=..>Blueprint,</color> Dead End" : every word must be a known room-type word, otherwise leave the text alone
        static string TagLine(string src)
        {
            if (tagwords.Count == 0 || src.IndexOf(',') < 0) return null;
            bool ok = true, any = false;
            string t = TagOrWord.Replace(src, mm =>
            {
                if (mm.Value[0] == '<') return mm.Value;
                if (tagwords.TryGetValue(mm.Value.ToLowerInvariant(), out var a)) { any = true; return a; }
                ok = false; return mm.Value;
            });
            return ok && any ? t.Replace(",", "،") : null;
        }

        static readonly Regex TGroup = new Regex(@"\{T(\d)\}", RegexOptions.Compiled);

        // pattern replacement: $1 as usual, {T1} = group 1 run through the dictionary (room names inside templates)
        static string Expand(Match m, string repl)
        {
            repl = TGroup.Replace(repl, t =>
            {
                string g = m.Groups[int.Parse(t.Groups[1].Value)].Value;
                string r = Resolve(g);
                return (r ?? g).Replace("$", "$$");
            });
            return m.Result(repl);
        }

        static void Miss(string s, string where)
        {
            lock (logged)
            {
                if (!logged.Add(s)) return;
                Misses++;
                pending.Append(s.Replace("\\", "\\\\").Replace("\n", "\\n").Replace("\t", "\\t")).Append('\t').Append(where).Append('\n');
            }
        }

        public static void Flush(string path)
        {
            string text;
            lock (logged) { if (pending.Length == 0) return; text = pending.ToString(); pending.Clear(); }
            File.AppendAllText(path, text, new UTF8Encoding(false));
        }
    }

    // Tiny reader for flat {"key":"value"} objects; avoids a JSON dependency.
    public static class Json
    {
        public static Dictionary<string, string> ReadStringMap(string s)
        {
            var d = new Dictionary<string, string>();
            int i = 0;
            Skip(s, ref i); if (i >= s.Length || s[i] != '{') return d; i++;
            while (true)
            {
                Skip(s, ref i);
                if (i >= s.Length || s[i] == '}') break;
                if (s[i] == ',') { i++; continue; }
                string k = Str(s, ref i); Skip(s, ref i);
                if (s[i] != ':') throw new FormatException("expected ':' at " + i);
                i++; Skip(s, ref i);
                string v = Str(s, ref i);
                d[k] = v;
            }
            return d;
        }

        static void Skip(string s, ref int i) { while (i < s.Length && char.IsWhiteSpace(s[i])) i++; }

        static string Str(string s, ref int i)
        {
            if (s[i] != '"') throw new FormatException("expected string at " + i);
            i++;
            var sb = new StringBuilder();
            while (s[i] != '"')
            {
                char c = s[i++];
                if (c != '\\') { sb.Append(c); continue; }
                c = s[i++];
                switch (c)
                {
                    case 'n': sb.Append('\n'); break;
                    case 't': sb.Append('\t'); break;
                    case 'r': sb.Append('\r'); break;
                    case 'b': sb.Append('\b'); break;
                    case 'f': sb.Append('\f'); break;
                    case 'u': sb.Append((char)Convert.ToInt32(s.Substring(i, 4), 16)); i += 4; break;
                    default: sb.Append(c); break;
                }
            }
            i++;
            return sb.ToString();
        }
    }
}
