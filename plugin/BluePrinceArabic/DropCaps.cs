using System.Collections.Generic;
using System.IO;
using System.Text;
using TMPro;
using UnityEngine;

namespace BluePrinceArabic
{
    // "You Found / Bought / Dug Up" titles are split over several TMP pieces (small prefix line, big first letter,
    // rest of the name), which cannot be reordered for Arabic. dropcap.json holds one full Arabic title per group
    // (or group/container for variants); the biggest "Item Name" piece shows it and the other pieces are hidden.
    static class DropCaps
    {
        const string Root = "You Found Text";
        static Dictionary<string, string> map = new Dictionary<string, string>();
        static readonly Dictionary<int, int> mainOf = new Dictionary<int, int>();   // parent instance id -> instance id of the piece that shows the title

        struct Saved { public bool wrap; public Vector4 margin; }
        static readonly Dictionary<int, Saved> saved = new Dictionary<int, Saved>();

        public static void Load(string dir)
        {
            map.Clear(); mainOf.Clear();
            var p = Path.Combine(dir, "dropcap.json");
            if (File.Exists(p)) map = Json.ReadStringMap(File.ReadAllText(p, Encoding.UTF8));
            Plugin.Log.LogInfo("drop-cap titles: " + map.Count);
        }

        // 1 = First Letter, 2 = Item Name, 3 = Prescription
        static int Kind(string n)
        {
            if (n.StartsWith("Item Name")) return 2;
            if (n.StartsWith("First Letter")) return 1;
            if (n.StartsWith("Prescription")) return 3;
            return 0;
        }

        // null = not a title piece (normal translation), "" = hide this piece, otherwise the Arabic title this piece shows
        public static string For(TMP_Text t, string src)
        {
            if (map.Count == 0) return null;
            string name = t.name;
            int kind = Kind(name);
            if (kind == 0) return null;
            // sentences that happen to sit in a First Letter piece (curse mode message) are translated normally
            if (kind == 1 && (src.Length > 4 || src.IndexOf(' ') >= 0)) return null;

            var names = new List<string>();
            var tr = t.transform;
            for (int guard = 0; tr != null && guard < 24; guard++) { names.Add(tr.name); tr = tr.parent; }
            names.Reverse();
            int i = names.IndexOf(Root);
            if (i < 0 || i + 2 >= names.Count) return null;
            string container = string.Join("/", names.GetRange(i + 1, names.Count - 2 - i));   // group/.../parent of the piece
            if (!map.TryGetValue(container, out var ar))
            {
                if (container.Contains("Item Anchor")) return null;
                if (!map.TryGetValue(names[i + 1].Trim(), out ar)) return null;
            }
            if (kind != 2 && kind != 3) return "";
            var parent = t.transform.parent;
            int pid = parent.GetInstanceID();
            if (!mainOf.TryGetValue(pid, out int mainId)) mainOf[pid] = mainId = PickMain(parent);
            return t.GetInstanceID() == mainId ? ar : "";
        }

        // the biggest Item Name piece of the container; a container with only a Prescription piece uses that one
        static int PickMain(Transform parent)
        {
            TMP_Text best = null, presc = null;
            for (int c = 0; c < parent.childCount; c++)
            {
                var x = parent.GetChild(c).GetComponent<TMP_Text>();
                if (x == null) continue;
                int k = Kind(x.name);
                if (k == 2 && (best == null || x.fontSize > best.fontSize || (x.fontSize == best.fontSize && string.CompareOrdinal(x.name, best.name) < 0))) best = x;
                else if (k == 3 && (presc == null || string.CompareOrdinal(x.name, presc.name) < 0)) presc = x;
            }
            var m = best ?? presc;
            return m != null ? m.GetInstanceID() : 0;
        }

        // the title piece is narrow and wrapped for one Latin word: show the Arabic title on one centred line
        public static void Style(TMP_Text t)
        {
            int id = t.GetInstanceID();
            if (!saved.ContainsKey(id)) saved[id] = new Saved { wrap = t.enableWordWrapping, margin = t.margin };
            if (t.enableWordWrapping) t.enableWordWrapping = false;
            var m = t.margin;
            if (m.x != 0f || m.z != 0f) t.margin = new Vector4(0f, m.y, 0f, m.w);
        }

        public static void Restore(TMP_Text t)
        {
            if (saved.Count == 0) return;
            int id = t.GetInstanceID();
            if (!saved.TryGetValue(id, out var s)) return;
            saved.Remove(id);
            t.enableWordWrapping = s.wrap;
            t.margin = s.margin;
        }
    }
}
