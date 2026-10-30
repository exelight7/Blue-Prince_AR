using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using TMPro;

namespace BluePrinceArabic
{
    // Hand-tuned size factors for labels where the Arabic is wider than the English word the plate was made for.
    // layout.tsv: "scene path substring <TAB> font size factor"; the original size comes back in English mode.
    static class Layout
    {
        static readonly List<KeyValuePair<string, float>> rules = new List<KeyValuePair<string, float>>();
        static readonly Dictionary<int, float> factor = new Dictionary<int, float>();   // instance id -> factor (1 = untouched)
        static readonly Dictionary<int, float> orig = new Dictionary<int, float>();

        public static void Load(string dir)
        {
            rules.Clear(); factor.Clear();
            var p = Path.Combine(dir, "layout.tsv");
            if (File.Exists(p))
                foreach (var l in File.ReadAllLines(p))
                {
                    var f = l.Split('\t');
                    if (f.Length < 2 || l.StartsWith("#")) continue;
                    rules.Add(new KeyValuePair<string, float>(f[0], float.Parse(f[1], CultureInfo.InvariantCulture)));
                }
            Plugin.Log.LogInfo("layout rules: " + rules.Count);
        }

        public static void Apply(TMP_Text t, bool rtl)
        {
            if (rules.Count == 0) return;
            int id = t.GetInstanceID();
            if (!factor.TryGetValue(id, out var k))
            {
                k = 1f; string path = TextOps.PathOf(t);
                foreach (var r in rules) if (path.Contains(r.Key)) { k = r.Value; break; }
                factor[id] = k;
            }
            if (k == 1f) return;
            if (!orig.ContainsKey(id)) orig[id] = t.fontSize;
            float want = rtl ? orig[id] * k : orig[id];
            if (Math.Abs(t.fontSize - want) > 0.001f) t.fontSize = want;
        }
    }
}
