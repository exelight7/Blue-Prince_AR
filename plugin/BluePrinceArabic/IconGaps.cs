using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

namespace BluePrinceArabic
{
    // English sentences leave a blank gap where the game draws an icon (key, die, button...) or a coloured word as a
    // separate object. In Arabic the sentence runs the other way, so those objects must move to where the gap now is.
    // Translations mark each gap with {ICON}; Render turns it into one no-break space (the slot), Expand widens it to the
    // objects' width, and Tick moves the objects (children of the text, and non-text siblings such as sprites) into the slots
    // TMP actually laid out. Several objects in one slot are placed side by side in reading order (first object rightmost).
    // Objects are put back when Arabic is switched off.
    static class IconGaps
    {
        public const char Slot = ' ';
        const int DefaultLen = 6;

        sealed class Item { public Transform tr; public Vector3 orig; public float w; }
        struct SlotBox { public float xL, xR, yC; }

        sealed class State
        {
            public TMP_Text t;
            public int len = DefaultLen, adjust;
            public bool resolved, warned;
            public readonly List<Item> items = new List<Item>();
        }

        static readonly Dictionary<int, State> states = new Dictionary<int, State>();
        static readonly HashSet<int> claimed = new HashSet<int>();

        // called from the parse patch with the shaped Arabic that contains one Slot per {ICON}
        public static string Expand(TMP_Text t, string res)
        {
            int id = t.GetInstanceID();
            if (!states.TryGetValue(id, out var s)) states[id] = s = new State { t = t };
            return res.Replace(Slot.ToString(), new string(Slot, s.len));
        }

        public static void Release(TMP_Text t)
        {
            if (states.Count == 0) return;
            int id = t.GetInstanceID();
            if (states.TryGetValue(id, out var s)) { Restore(s); states.Remove(id); }
        }

        static void Restore(State s)
        {
            foreach (var it in s.items)
            {
                try { if (it.tr != null) it.tr.localPosition = it.orig; claimed.Remove(it.tr.GetInstanceID()); } catch { }
            }
            s.items.Clear(); s.resolved = false;
        }

        public static void Tick()
        {
            if (states.Count == 0) return;
            List<int> dead = null;
            foreach (var kv in states)
            {
                var s = kv.Value;
                if (s.t == null) { (dead ?? (dead = new List<int>())).Add(kv.Key); continue; }
                if (!s.t.gameObject.activeInHierarchy) continue;
                try { Step(s); }
                catch (Exception e) { if (!s.warned) { s.warned = true; Plugin.Log.LogError("icon gaps " + TextOps.PathOf(s.t) + ": " + e.Message); } s.resolved = true; s.items.Clear(); }
            }
            if (dead != null) foreach (var id in dead) states.Remove(id);
        }

        static void Step(State s)
        {
            var t = s.t;
            var ti = t.textInfo;
            int n = ti != null ? ti.characterCount : 0;
            if (n == 0) return;
            var slots = Slots(ti, n);
            if (slots.Count == 0) return;
            // logical order = right to left
            slots.Sort((a, b) => ((b.xL + b.xR) * 0.5f).CompareTo((a.xL + a.xR) * 0.5f));

            if (!s.resolved)
            {
                s.resolved = true;
                Gather(s);
                if (s.items.Count == 0) { Warn(s, "no icon objects near " + slots.Count + " slot(s)"); return; }
                if (slots.Count != 1 && slots.Count != s.items.Count) { Warn(s, slots.Count + " slots but " + s.items.Count + " objects"); Restore(s); return; }
            }
            if (s.items.Count == 0) return;

            var tt = t.transform;
            float unit = Math.Max((slots[0].xR - slots[0].xL) / s.len, 0.01f);   // width of one slot character
            float pad = unit;
            float need = 0f;
            for (int j = 0; j < slots.Count; j++)
            {
                var group = new List<Item>();
                if (slots.Count == 1) group.AddRange(s.items); else group.Add(s.items[j]);
                float total = pad * (group.Count - 1);
                foreach (var it in group) total += it.w;
                need = Math.Max(need, total);
                float start = (slots[j].xL + slots[j].xR) * 0.5f + total * 0.5f;   // right edge of the row
                foreach (var it in group)
                {
                    float cx = start - it.w * 0.5f; start -= it.w + pad;
                    var cur = tt.InverseTransformPoint(Center(it.tr));
                    float dx = cx - cur.x, dy = slots[j].yC - cur.y;
                    if (Math.Abs(dx) + Math.Abs(dy) > 1e-3f) it.tr.position = it.tr.position + tt.TransformVector(new Vector3(dx, dy, 0f));
                }
            }
            // size the slot to the objects (a few corrections at most, each one re-lays the text out once)
            int want = Mathf.Clamp(Mathf.CeilToInt(need / unit) + 1, 3, 40);
            if (want != s.len && s.adjust < 3) { s.adjust++; s.len = want; t.ForceMeshUpdate(true, true); }
        }

        static void Warn(State s, string msg)
        {
            if (s.warned) return;
            s.warned = true;
            Plugin.Log.LogInfo("icon gaps: " + msg + " [" + TextOps.PathOf(s.t) + "]");
        }

        // runs of consecutive Slot characters = one slot each (positions are in the text's local space)
        static List<SlotBox> Slots(TMP_TextInfo ti, int n)
        {
            var list = new List<SlotBox>();
            bool inRun = false; SlotBox cur = default;
            for (int i = 0; i < n; i++)
            {
                var ci = ti.characterInfo[i];
                if (ci.character == Slot)
                {
                    float l = Math.Min(ci.origin, ci.xAdvance), r = Math.Max(ci.origin, ci.xAdvance);
                    if (!inRun) { cur = new SlotBox { xL = l, xR = r, yC = (ci.ascender + ci.descender) * 0.5f }; inRun = true; }
                    else { cur.xL = Math.Min(cur.xL, l); cur.xR = Math.Max(cur.xR, r); }
                }
                else if (inRun) { list.Add(cur); inRun = false; }
            }
            if (inRun) list.Add(cur);
            return list;
        }

        // objects that sit in the English gap: children of the text and, among its siblings, objects that are not text
        static void Gather(State s)
        {
            var t = s.t; var tt = t.transform;
            var tb = t.textBounds;
            float ex = Math.Max(tb.size.x * 0.6f, t.fontSize * 2f), ey = Math.Max(tb.size.y * 0.6f, t.fontSize * 1.5f);
            var cand = new List<Transform>();
            for (int i = 0; i < tt.childCount; i++)
            {
                var c = tt.GetChild(i);
                if (!c.gameObject.activeInHierarchy || c.name.StartsWith("TMP SubMesh")) continue;
                if (HasVisual(c)) cand.Add(c);
            }
            var p = tt.parent;
            if (p != null)
                for (int i = 0; i < p.childCount; i++)
                {
                    var c = p.GetChild(i);
                    if (c == tt || !c.gameObject.activeInHierarchy || c.name.StartsWith("TMP SubMesh")) continue;
                    if (c.GetComponent<TMP_Text>() == null && HasVisual(c)) cand.Add(c);
                }
            foreach (var c in cand)
            {
                int id = c.GetInstanceID();
                if (claimed.Contains(id)) continue;
                var cl = tt.InverseTransformPoint(Center(c));
                if (cl.x < tb.min.x - ex || cl.x > tb.max.x + ex || cl.y < tb.min.y - ey || cl.y > tb.max.y + ey) continue;
                s.items.Add(new Item { tr = c, orig = c.localPosition, w = Math.Max(Width(c) / Math.Max(Math.Abs(tt.lossyScale.x), 1e-6f), 0.01f) });
                claimed.Add(id);
            }
            // English reading order: top line first, left to right
            s.items.Sort((a, b) =>
            {
                var pa = tt.InverseTransformPoint(Center(a.tr)); var pb = tt.InverseTransformPoint(Center(b.tr));
                float ly = Math.Max(t.fontSize, 0.1f);
                int ra = Mathf.RoundToInt(-pa.y / ly), rb = Mathf.RoundToInt(-pb.y / ly);
                return ra != rb ? ra.CompareTo(rb) : pa.x.CompareTo(pb.x);
            });
        }

        static bool HasVisual(Transform c)
        {
            if (c.GetComponent<Renderer>() != null) return true;
            return c.GetComponent<UnityEngine.UI.Graphic>() != null;
        }

        static Vector3 Center(Transform c)
        {
            var r = c.GetComponent<Renderer>();
            if (r != null) return r.bounds.center;
            var rt = c as RectTransform;
            return rt != null ? rt.TransformPoint(rt.rect.center) : c.position;
        }

        static float Width(Transform c)
        {
            var r = c.GetComponent<Renderer>();
            if (r != null) return r.bounds.size.x;
            var rt = c as RectTransform;
            return rt != null ? rt.rect.width * Math.Abs(rt.lossyScale.x) : 0.1f;
        }
    }
}
