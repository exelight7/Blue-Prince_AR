using System;
using System.Collections.Generic;
using HarmonyLib;
using HutongGames.PlayMaker.Actions;
using TMPro;
using UnityEngine;

namespace BluePrinceArabic
{
    public static class TextOps
    {
        static readonly Dictionary<int, TextAlignmentOptions> origAlign = new Dictionary<int, TextAlignmentOptions>();
        static readonly Dictionary<string, string> cache = new Dictionary<string, string>();

        public static void ClearCache() { cache.Clear(); }

        // logical text -> what TMP should be given. null = leave the text alone.
        public static string Render(string src, string where)
        {
            if (cache.TryGetValue(src, out var hit)) return hit;
            string logical = Shaper.HasArabic(src) ? src : Translator.Translate(src, where);
            // TMP widens every glyph of bold text (boldSpacing), which pulls joined Arabic letters apart and makes it heavy
            if (logical != null) logical = BoldTag.Replace(logical, "").Replace("{ICON}", IconGaps.Slot.ToString());   // {ICON} = a slot for a separate icon object
            string res = logical == null ? null : Shaper.Process(logical, Plugin.StripMarks.Value);
            if (cache.Count > 20000) cache.Clear();
            if (logical != null || !Translator.LooksTranslatable(src)) cache[src] = res;
            return res;
        }

        static TextAlignmentOptions Flip(TextAlignmentOptions a)
        {
            int v = (int)a;
            int h = v & 0x3F;
            // left-aligned Latin text becomes right-aligned Arabic; text already right-aligned (menus anchored to the
            // right edge) must stay there or it jumps across the screen
            if (h == 1) v = (v & ~0x3F) | 4;
            return (TextAlignmentOptions)v;
        }

        struct Spacing { public float ch, line, word; }
        static readonly Dictionary<int, Spacing> origSpacing = new Dictionary<int, Spacing>();
        static readonly Dictionary<int, FontStyles> origStyle = new Dictionary<int, FontStyles>();
        static readonly System.Text.RegularExpressions.Regex BoldTag = new System.Text.RegularExpressions.Regex("</?[bB]>", System.Text.RegularExpressions.RegexOptions.Compiled);

        // a box that holds one line (icon labels, buttons) must keep its anchor side; only paragraph boxes mirror
        public static bool IsParagraph(TMP_Text t, string src) => src.IndexOf((char)10) >= 0 || t.rectTransform.rect.height >= 2f * t.m_fontSize;

        public static void SetDirection(TMP_Text t, bool rtl, string src = "", bool center = false)
        {
            int id = t.GetInstanceID();
            if (!origAlign.ContainsKey(id)) origAlign[id] = t.alignment;
            if (!origSpacing.ContainsKey(id)) origSpacing[id] = new Spacing { ch = t.m_characterSpacing, line = t.m_lineSpacing, word = t.m_wordSpacing };
            // only wrapped paragraphs mirror: single-line labels sit next to icons/boxes and must keep their anchor side
            var want = rtl && IsParagraph(t, src) ? Flip(origAlign[id]) : origAlign[id];
            if (center) want = (TextAlignmentOptions)(((int)origAlign[id] & ~0x3F) | 2);   // keep the vertical part, centre horizontally
            if (t.alignment != want) t.alignment = want;
            if (t.m_isRightToLeft != rtl) t.m_isRightToLeft = rtl;
            // same reason as the <b> tags: the Bold font style spaces glyphs apart and fakes weight on the Arabic fallback fonts
            if (!origStyle.ContainsKey(id)) origStyle[id] = t.fontStyle;
            var st = origStyle[id];
            var wantStyle = rtl ? st & ~FontStyles.Bold : st;
            if (t.fontStyle != wantStyle) t.fontStyle = wantStyle;
            // Latin tracking breaks Arabic joins (and negative tracking/leading makes letters and lines overlap)
            var o = origSpacing[id];
            float ch = rtl ? 0f : o.ch, line = rtl ? Math.Max(o.line, 0f) : o.line, word = rtl ? Math.Max(o.word, 0f) : o.word;
            if (t.m_characterSpacing != ch) t.characterSpacing = ch;
            if (t.m_lineSpacing != line) t.lineSpacing = line;
            if (t.m_wordSpacing != word) t.wordSpacing = word;
        }

        static readonly HashSet<int> fitted = new HashSet<int>();

        // Arabic is a bit wider than the Latin label it replaces: shrink single-line labels to the box instead of
        // overflowing onto the neighbouring icon/label (multi-line and wrapped texts are left alone)
        public static void SetFit(TMP_Text t, bool rtl, string src)
        {
            int id = t.GetInstanceID();
            bool want = rtl && !t.enableWordWrapping && src.IndexOf('\n') < 0 && t.rectTransform.rect.width > 1f && t.rectTransform.rect.width < 900f;
            if (want && !fitted.Contains(id) && !t.enableAutoSizing)
            {
                float size = t.m_fontSize;
                t.fontSizeMax = size; t.fontSizeMin = size * 0.55f; t.enableAutoSizing = true;
                fitted.Add(id);
            }
            else if (!want && fitted.Remove(id)) t.enableAutoSizing = false;
        }

        public static string PathOf(Component c)
        {
            try
            {
                var tr = c.transform; string p = tr.name; int n = 0;
                while (tr.parent != null && n++ < 6) { tr = tr.parent; p = tr.name + "/" + p; }
                return p;
            }
            catch { return "?"; }
        }
    }

    [HarmonyPatch(typeof(TMP_Text), "ParseInputText")]
    static class Patch_ParseInputText
    {
        static int errors;

        static void Prefix(TMP_Text __instance, out string __state)
        {
            __state = null;
            try
            {
                string src = __instance.m_text;
                if (!Plugin.Active || string.IsNullOrEmpty(src)) { TextOps.SetDirection(__instance, false); Layout.Apply(__instance, false); DropCaps.Restore(__instance); IconGaps.Release(__instance); DocFont.Restore(__instance); return; }
                string title = DropCaps.For(__instance, src);   // split "You Found" titles: one piece shows the whole Arabic title, the others are empty
                string res = title == null ? TextOps.Render(src, TextOps.PathOf(__instance)) : title.Length == 0 ? "" : Shaper.Process(title, Plugin.StripMarks.Value);
                if (res == null) { TextOps.SetDirection(__instance, false); Layout.Apply(__instance, false); TextOps.SetFit(__instance, false, src); DropCaps.Restore(__instance); IconGaps.Release(__instance); DocFont.Restore(__instance); return; }
                if (res.IndexOf(IconGaps.Slot) >= 0) res = IconGaps.Expand(__instance, res); else IconGaps.Release(__instance);
                if (ArabicFont.Ensure()) ArabicFont.EnsureFallback(__instance.m_fontAsset);
                if (DocFont.IsPaper(__instance)) DocFont.Apply(__instance); else DocFont.Restore(__instance);
                bool shown = !string.IsNullOrEmpty(title);
                TextOps.SetDirection(__instance, true, src, shown);
                Layout.Apply(__instance, true);
                if (shown) DropCaps.Style(__instance); else if (title == null) TextOps.SetFit(__instance, true, src);
                __state = src;
                // Mirza (the handwriting style) has tall ascenders and overlaps neighbouring lines at the Latin size
                if (res.Length > 0 && ArabicFont.StyleFor(__instance.m_fontAsset != null ? __instance.m_fontAsset.name : "") == "hand") res = "<size=85%>" + res + "</size>";
                __instance.m_text = res;
            }
            catch (Exception e) { if (errors++ < 5) Plugin.Log.LogError("ParseInputText prefix: " + e); }
        }

        static void Postfix(TMP_Text __instance, string __state)
        {
            if (__state == null) return;
            try { __instance.m_text = __state; }
            catch (Exception e) { if (errors++ < 5) Plugin.Log.LogError("ParseInputText postfix: " + e); }
        }
    }

    // Typewriter reveals logical Arabic; TMP shapes every partial string via the patch above.
    [HarmonyPatch(typeof(StringTypewriter), "OnEnter")]
    static class Patch_Typewriter
    {
        static void Prefix(StringTypewriter __instance)
        {
            try
            {
                if (!Plugin.Active) return;
                var v = __instance.baseString;
                string s = v?.Value;
                if (string.IsNullOrEmpty(s) || Shaper.HasArabic(s)) return;
                string ar = Translator.Translate(s, "typewriter");
                if (ar != null) v.Value = ar;
            }
            catch (Exception e) { Plugin.Log.LogError("Typewriter prefix: " + e); }
        }
    }
}
