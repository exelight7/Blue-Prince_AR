using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Video;

namespace BluePrinceArabic
{
    // The intro's English text is burned into the video frames (no text object exists). While the clip plays the plugin
    //  - zooms the video quad until the letterbox bar (where the subtitles sit) is off screen, and shows the translated
    //    subtitle over the picture (intro_subs.tsv = "start<TAB>end<TAB>English line"),
    //  - covers the one big caption inside the picture with a soft dark plate and draws the Arabic on it
    //    (intro_cards.tsv = "in0 in1 out0 out1 u0 v0 u1 v1 English"; times are the clip clock, u/v the area of the 16:9 video frame, top-left origin).
    // The English lines are looked up in ar.json like any other text.
    static class IntroSubs
    {
        struct Line { public float t0, t1; public string en; }
        struct Card { public float in0, in1, out0, out1, u0, v0, u1, v1; public string en; }

        const string Clip = "_INTRO";
        // the picture is 2.39:1 centred in the 16:9 frame (bars of ~139 px of 1080 top and bottom), so 1080/800 = 1.35 pushes them out
        const float Zoom = 1.36f;
        const float ZoomRamp = 1f;          // seconds to push in before the first line and out after the last

        static readonly List<Line> lines = new List<Line>();
        static readonly List<Card> cards = new List<Card>();
        static float firstT, lastT;
        static VideoPlayer player;
        static GameObject root, cardGo;
        static CanvasGroup subGroup, cardGroup;
        static TextMeshProUGUI text, cardText;
        static RectTransform cardRt, cardTextRt;
        static float subAlpha;
        static int shown = -2, shownCard = -2;
        static float nextFind;

        static Transform quad;              // the video quad (the VideoPlayer's own object), scaled while the intro plays
        static Vector3 baseScale, applied;
        static bool hasBase;
        static float zoomK;
        static int fights;

        public static void Load(string dir)
        {
            lines.Clear(); cards.Clear();
            try
            {
                string p = Path.Combine(dir, "intro_subs.tsv");
                if (File.Exists(p))
                    foreach (var l in File.ReadAllLines(p))
                    {
                        var f = l.Split('\t');
                        if (f.Length < 3 || l.StartsWith("#")) continue;
                        lines.Add(new Line { t0 = F(f[0]), t1 = F(f[1]), en = f[2].Replace("\\n", "\n") });
                    }
                if (lines.Count > 0) { firstT = lines[0].t0; lastT = lines[lines.Count - 1].t1; }
                p = Path.Combine(dir, "intro_cards.tsv");
                if (File.Exists(p))
                    foreach (var l in File.ReadAllLines(p))
                    {
                        var f = l.Split('\t');
                        if (f.Length < 9 || l.StartsWith("#")) continue;
                        cards.Add(new Card { in0 = F(f[0]), in1 = F(f[1]), out0 = F(f[2]), out1 = F(f[3]), u0 = F(f[4]), v0 = F(f[5]), u1 = F(f[6]), v1 = F(f[7]), en = f[8].Replace("\\n", "\n") });
                    }
                Plugin.Log.LogInfo("intro subtitles: " + lines.Count + ", cards: " + cards.Count);
            }
            catch (Exception e) { Plugin.Log.LogError("intro_subs: " + e.Message); }
        }

        static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);

        static VideoPlayer FindPlayer()
        {
            foreach (var vp in Resources.FindObjectsOfTypeAll<VideoPlayer>())
            {
                if (vp == null || !vp.gameObject.activeInHierarchy) continue;
                string n = ""; try { n = vp.clip != null ? vp.clip.name : ""; } catch { }
                if (n == Clip) return vp;
            }
            return null;
        }

        static bool wasOnScreen;

        // After the cutscene is skipped the game keeps the clip "playing" out of sight; the captions must not pop up over the game then.
        static bool OnScreen()
        {
            bool v = true; string why = "";
            try
            {
                var mr = player.GetComponent<MeshRenderer>();
                var cam = player.transform.parent != null ? player.transform.parent.GetComponent<Camera>() : null;
                if (mr == null || !mr.enabled) { v = false; why = "renderer off"; }
                else if (cam != null && !cam.isActiveAndEnabled) { v = false; why = "camera off"; }
                else if (!mr.isVisible) { v = false; why = "not visible"; }
            }
            catch { v = true; }
            if (v != wasOnScreen) { wasOnScreen = v; Plugin.Log.LogInfo("intro video " + (v ? "on screen" : "hidden (" + why + ")") + " at " + player.time.ToString("0.0")); }
            return v;
        }

        public static void Tick()
        {
            if (lines.Count == 0 || !Plugin.Active) { Hide(); return; }
            if (player == null || !player.gameObject.activeInHierarchy)
            {
                player = null;
                if (Time.unscaledTime < nextFind) { Hide(); return; }
                nextFind = Time.unscaledTime + 0.5f;
                player = FindPlayer();
                if (player == null) { Hide(); return; }
            }
            if (!player.isPlaying || !OnScreen()) { Hide(); return; }
            Build();
            root.SetActive(true);
            float t = (float)player.time;
            float dt = Time.unscaledDeltaTime;
            zoomK = Mathf.MoveTowards(zoomK, t >= firstT - 1.5f && t < lastT + 0.5f ? 1f : 0f, dt / ZoomRamp);
            SetZoom(player.transform, zoomK);

            int idx = -1;
            for (int i = 0; i < lines.Count; i++) if (t >= lines[i].t0 && t < lines[i].t1) idx = i;   // last match wins when windows overlap
            if (idx != shown) { shown = idx; if (idx >= 0) text.text = lines[idx].en; }
            subAlpha = Mathf.MoveTowards(subAlpha, idx >= 0 ? 1f : 0f, dt / 0.2f);
            subGroup.alpha = subAlpha;

            int ci = -1; float ca = 0f;
            for (int i = 0; i < cards.Count; i++)
            {
                var c = cards[i];
                float a = t < c.in0 ? 0f : t < c.in1 ? Mathf.InverseLerp(c.in0, c.in1, t) : t < c.out0 ? 1f : t < c.out1 ? 1f - Mathf.InverseLerp(c.out0, c.out1, t) : 0f;
                if (a > ca) { ca = a; ci = i; }
            }
            ShowCard(ci, ca);
        }

        // The card covers a fixed area of the video frame; the frame's screen rectangle follows the quad (zoom, window shape).
        static void ShowCard(int ci, float a)
        {
            if (ci < 0 || a <= 0f) { if (cardGo.activeSelf) cardGo.SetActive(false); shownCard = -2; return; }
            if (!cardGo.activeSelf) cardGo.SetActive(true);
            var c = cards[ci];
            if (ci != shownCard) { shownCard = ci; cardText.text = c.en; }
            cardGroup.alpha = a * a * (3f - 2f * a);
            var r = VideoRect();
            float x0 = r.xMin + c.u0 * r.width, x1 = r.xMin + c.u1 * r.width;
            float y1 = r.yMax - c.v0 * r.height, y0 = r.yMax - c.v1 * r.height;
            cardRt.anchoredPosition = new Vector2(x0, y0); cardRt.sizeDelta = new Vector2(x1 - x0, y1 - y0);
            // the Arabic sits inside the plate but never outside the screen
            float tx0 = Mathf.Max(x0, Screen.width * 0.07f), tx1 = Mathf.Min(x1, Screen.width * 0.93f);
            cardTextRt.anchorMin = cardTextRt.anchorMax = Vector2.zero; cardTextRt.pivot = Vector2.zero;
            cardTextRt.anchoredPosition = new Vector2(tx0 - x0, (y1 - y0) * 0.12f); cardTextRt.sizeDelta = new Vector2(tx1 - tx0, (y1 - y0) * 0.76f);   // relative to the card, not the screen
        }

        // screen rectangle (pixels, origin bottom-left) the 16:9 video frame is drawn in
        static Rect VideoRect()
        {
            var full = new Rect(0f, 0f, Screen.width, Screen.height);
            try
            {
                var cam = player.transform.parent != null ? player.transform.parent.GetComponent<Camera>() : null;
                var mr = player.GetComponent<MeshRenderer>();
                if (cam == null || mr == null) return full;
                var b = mr.bounds; var mn = b.min; var mx = b.max;
                float x0 = 1e9f, y0 = 1e9f, x1 = -1e9f, y1 = -1e9f;
                for (int i = 0; i < 8; i++)
                {
                    var s = cam.WorldToScreenPoint(new Vector3((i & 1) == 0 ? mn.x : mx.x, (i & 2) == 0 ? mn.y : mx.y, (i & 4) == 0 ? mn.z : mx.z));
                    x0 = Mathf.Min(x0, s.x); x1 = Mathf.Max(x1, s.x); y0 = Mathf.Min(y0, s.y); y1 = Mathf.Max(y1, s.y);
                }
                var r = Rect.MinMaxRect(x0, y0, x1, y1);
                return r.width > 10f && r.height > 10f ? r : full;
            }
            catch { return full; }
        }

        // Scale the quad's width/height (its local X and Z; Y is the plane normal) about its centre.
        // The game may rewrite the scale itself: a value other than the one we applied becomes the new baseline.
        static void SetZoom(Transform tr, float k)
        {
            if (tr == null) return;
            var cur = tr.localScale;
            if (quad != tr || !hasBase || (cur - applied).sqrMagnitude > 1e-6f)
            {
                if (hasBase && quad == tr && ++fights <= 3) Plugin.Log.LogInfo("intro zoom: scale changed by the game " + applied + " -> " + cur);
                if (quad != tr) { Plugin.Log.LogInfo("intro zoom: quad " + TextOps.PathOf(tr) + " scale " + cur); fights = 0; }
                quad = tr; baseScale = cur; hasBase = true;
            }
            float e = k * k * (3f - 2f * k);
            float s = 1f + (Zoom - 1f) * e;
            applied = new Vector3(baseScale.x * s, baseScale.y, baseScale.z * s);
            tr.localScale = applied;
        }

        static void Unzoom()
        {
            if (!hasBase) return;
            hasBase = false;
            try { if (quad != null) quad.localScale = baseScale; } catch { }
        }

        static void Hide()
        {
            if (root != null && root.activeSelf) root.SetActive(false);
            subAlpha = 0f; shown = -2; shownCard = -2; zoomK = 0f;
            Unzoom();
        }

        static TMP_FontAsset Versica()
        {
            foreach (var f in Resources.FindObjectsOfTypeAll<TMP_FontAsset>()) if (f != null && f.name == "Versica SDF") return f;
            return null;
        }

        static TextMeshProUGUI NewText(Transform parent, string name, float size, Color col)
        {
            var go = new GameObject(name); go.transform.SetParent(parent, false);
            var t = go.AddComponent<TextMeshProUGUI>();
            // Amiri's hairline joins fade out in the SDF at this size and look like gaps between letters; Naskh keeps them solid
            var font = ArabicFont.Ensure() ? ArabicFont.Noto : null; if (font == null) font = Versica(); if (font != null) t.font = font;
            t.fontSize = size; t.color = col;
            t.outlineWidth = 0.1f; t.outlineColor = new Color32(0, 0, 0, 255);   // thin: a thick outline made the letters look heavy and fused
            t.enableWordWrapping = true; t.raycastTarget = false;
            return t;
        }

        // 32x32 white square whose alpha falls off over the outer 12 pixels; used 9-sliced it gives a soft-edged plate
        static Sprite Feather()
        {
            const int n = 32, edge = 12;
            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float d = Mathf.Clamp01(Mathf.Min(Mathf.Min(x, n - 1 - x), Mathf.Min(y, n - 1 - y)) / (float)edge);
                    tex.SetPixel(x, y, new Color(1f, 1f, 1f, d * d * (3f - 2f * d)));
                }
            tex.wrapMode = TextureWrapMode.Clamp; tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f), 100f, 0, SpriteMeshType.FullRect, new Vector4(edge, edge, edge, edge));
        }

        static void Build()
        {
            if (root != null) return;
            root = new GameObject("BPAR_IntroSubs");
            UnityEngine.Object.DontDestroyOnLoad(root);
            var canvas = root.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 4000;

            // subtitle line over the picture, bottom of the screen
            var sub = new GameObject("sub");
            var srt = sub.AddComponent<RectTransform>();   // a plain Transform has no rect: the text below got zero width and wrapped one letter per line
            sub.transform.SetParent(root.transform, false);
            srt.anchorMin = Vector2.zero; srt.anchorMax = Vector2.one; srt.offsetMin = srt.offsetMax = Vector2.zero;
            subGroup = sub.AddComponent<CanvasGroup>(); subGroup.interactable = false; subGroup.blocksRaycasts = false;
            text = NewText(sub.transform, "text", Screen.height * 0.036f, new Color(0.95f, 0.95f, 0.92f, 1f));
            text.alignment = TextAlignmentOptions.Bottom;
            var rt = text.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.08f, 0.04f); rt.anchorMax = new Vector2(0.92f, 0.22f); rt.offsetMin = rt.offsetMax = Vector2.zero;

            // caption card: dark soft plate + centred Arabic text, positioned every frame from the video rectangle
            cardGo = new GameObject("card"); cardGo.transform.SetParent(root.transform, false);
            cardGroup = cardGo.AddComponent<CanvasGroup>(); cardGroup.interactable = false; cardGroup.blocksRaycasts = false;
            var img = cardGo.AddComponent<Image>();
            img.sprite = Feather(); img.type = Image.Type.Sliced; img.color = new Color(0.02f, 0.018f, 0.015f, 0.86f); img.raycastTarget = false;
            try { img.pixelsPerUnitMultiplier = 0.25f; } catch { }   // 12 px border -> ~48 px soft edge
            cardRt = cardGo.GetComponent<RectTransform>();
            cardRt.anchorMin = cardRt.anchorMax = Vector2.zero; cardRt.pivot = Vector2.zero;
            cardText = NewText(cardGo.transform, "ctext", Screen.height * 0.05f, new Color(0.95f, 0.95f, 0.92f, 1f));
            cardText.alignment = TextAlignmentOptions.Center;
            cardText.enableAutoSizing = true; cardText.fontSizeMin = Screen.height * 0.02f; cardText.fontSizeMax = Screen.height * 0.055f;
            cardTextRt = cardText.GetComponent<RectTransform>();
            cardGo.SetActive(false);
        }
    }
}
