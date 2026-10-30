using System;
using System.IO;
using System.Text;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using Il2CppInterop.Runtime.Injection;
using TMPro;
using UnityEngine;

namespace BluePrinceArabic
{
    [BepInPlugin("local.blueprince.arabic", "Blue Prince Arabic", "0.1.0")]
    public class Plugin : BasePlugin
    {
        public static ManualLogSource Log;
        public static bool Active = true;
        public static ConfigEntry<bool> StripMarks;
        public static string Dir;

        public override void Load()
        {
            Log = base.Log;
            Dir = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
            StripMarks = Config.Bind("Text", "StripDiacritics", true, "Remove Arabic diacritics (not reliably placed by TMP).");
            Translator.Load(Dir); DropCaps.Load(Dir); Layout.Load(Dir); IntroSubs.Load(Dir);
            new Harmony("local.blueprince.arabic").PatchAll(typeof(Plugin).Assembly);
            ClassInjector.RegisterTypeInIl2Cpp<Runner>();
            var go = new GameObject("BPAR_Runner");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.hideFlags = HideFlags.HideAndDontSave;
            go.AddComponent<Runner>();
            Log.LogInfo("Blue Prince Arabic loaded. Commands: BepInEx/bpar/cmd.txt (shot/scan/reload/toggle). F10 toggle, F11 reload, F12 shot.");
        }
    }

    public class Runner : MonoBehaviour
    {
        public Runner(IntPtr ptr) : base(ptr) { }

        float nextCmd, nextFlush, nextTrace; bool tracing;
        string cmdPath, outDir;

        void Start()
        {
            outDir = Path.Combine(Paths.BepInExRootPath, "bpar");
            Directory.CreateDirectory(outDir);
            cmdPath = Path.Combine(outDir, "cmd.txt");
        }

        void Update()
        {
            try
            {
                var kb = UnityEngine.InputSystem.Keyboard.current;
                if (kb != null)
                {
                    if (kb.f10Key.wasPressedThisFrame) Toggle();
                    if (kb.f11Key.wasPressedThisFrame) Reload();
                    if (kb.f12Key.wasPressedThisFrame) Shot("manual_" + DateTime.Now.ToString("HHmmss"));
                }
            }
            catch { }
            float t = Time.unscaledTime;
            if (t > nextFlush)
            {
                nextFlush = t + 2f; Translator.Flush(Path.Combine(outDir, "untranslated.tsv"));
                try { if (Plugin.Active) ArabicFont.PatchAllLoaded(); } catch (Exception e) { Plugin.Log.LogError("patch fonts: " + e.Message); }
            }
            if (t > nextCmd) { nextCmd = t + 0.5f; PollCommands(); }
            try { IntroSubs.Tick(); } catch (Exception e) { Plugin.Log.LogError("intro subs: " + e.Message); }
            IconGaps.Tick();
            if (tracing && t > nextTrace) { nextTrace = t + 0.25f; TraceFrame(); }
        }

        // after TMP has laid the texts out, so icons follow the final slot positions in the same frame
        void LateUpdate() { IconGaps.Tick(); }

        void PollCommands()
        {
            if (!File.Exists(cmdPath)) return;
            string[] lines;
            try { lines = File.ReadAllLines(cmdPath); File.Delete(cmdPath); } catch { return; }
            // one command per poll (screenshots land at end of frame); the rest go back to the file
            if (lines.Length > 1) File.WriteAllLines(cmdPath, System.Linq.Enumerable.Skip(lines, 1), new UTF8Encoding(false));
            foreach (var l in new[] { lines[0] })
            {
                var p = l.Trim().Split(new[] { ' ' }, 2);
                try
                {
                    switch (p[0])
                    {
                        case "shot": Shot(p.Length > 1 ? p[1] : "shot"); break;
                        case "scan": Scan(); break;
                        case "video": VideoInfo(); break;
                        case "trace": tracing = !tracing; Plugin.Log.LogInfo("trace=" + tracing); break;
                        case "dump": Dump(); break;
                        case "gallery": Gallery(); break;
                        case "style": { var kv = p[1].Split('='); ArabicFont.Override[kv[0].ToLowerInvariant()] = kv[1]; ArabicFont.Reapply(); Refresh(); break; }
                        case "reload": Reload(); break;
                        case "toggle": Toggle(); break;
                        case "set": SetFirstMatching(p[1]); break;
                        case "act": SetActiveByName(p[1], true); break;
                        case "deact": SetActiveByName(p[1], false); break;
                    }
                }
                catch (Exception e) { Plugin.Log.LogError("cmd '" + l + "': " + e); }
            }
        }

        void Shot(string name)
        {
            string path = Path.Combine(outDir, name + ".png");
            ScreenCapture.CaptureScreenshot(path);
            Plugin.Log.LogInfo("screenshot -> " + path);
        }

        void Toggle() { Plugin.Active = !Plugin.Active; Plugin.Log.LogInfo("Arabic active = " + Plugin.Active); Refresh(); }
        void Reload() { Translator.Load(Plugin.Dir); DropCaps.Load(Plugin.Dir); Layout.Load(Plugin.Dir); IntroSubs.Load(Plugin.Dir); Refresh(); }

        static void Refresh()
        {
            foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
                if (t != null && t.gameObject.activeInHierarchy) { try { t.ForceMeshUpdate(true, true); } catch { } }
        }

        // `set <text>` : write a test string into the first active TMP whose name is "text_probe" (debug aid)
        static void SetFirstMatching(string spec)
        {
            int sep = spec.IndexOf('|');
            string name = sep > 0 ? spec.Substring(0, sep) : spec; string val = sep > 0 ? spec.Substring(sep + 1).Replace("\\n", "\n") : "";
            foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
                if (t != null && t.gameObject.activeInHierarchy && t.name == name) { t.text = val; return; }
        }

        // `act <name>` / `deact <name>`: switch on/off every scene object with that exact name (layout checks of screens that are normally hidden)
        static void SetActiveByName(string name, bool on)
        {
            int n = 0;
            foreach (var go in Resources.FindObjectsOfTypeAll<GameObject>())
                if (go != null && go.name == name && go.scene.IsValid()) { go.SetActive(on); n++; }
            Plugin.Log.LogInfo("act " + name + " = " + on + " (" + n + " objects)");
        }

        // all text held by the game's own language ScriptableObjects (upgrades, video subtitles, dirigiblocks)
        void Dump()
        {
            var sb = new StringBuilder();
            void Add(string kind, string owner, int idx, string v)
            {
                if (string.IsNullOrEmpty(v)) return;
                sb.Append(kind).Append('\t').Append(owner).Append('\t').Append(idx).Append('\t').Append(v.Replace("\n", "\\n")).Append('\n');
            }
            var texts = new System.Collections.Generic.List<BluePrince.Language.LanguageText>();
            foreach (var lt in Resources.FindObjectsOfTypeAll<BluePrince.Language.LanguageText>()) texts.Add(lt);
            var all = Resources.FindObjectsOfTypeAll<BluePrince.Language.Languages>();
            Plugin.Log.LogInfo($"dump: LanguageText={texts.Count} Languages={all.Length}");
            foreach (var lg in all)
                if (lg.languages != null) for (int i = 0; i < lg.languages.Count; i++) { var x = lg.languages[i]; if (x != null && !texts.Exists(e => e.Pointer == x.Pointer)) texts.Add(x); }
            foreach (var lt in texts)
            {
                string o = lt.name;
                void L(string kind, Il2CppSystem.Collections.Generic.List<string> l) { if (l == null) return; for (int i = 0; i < l.Count; i++) Add(kind, o, i, l[i]); }
                L("dirigiblocksTextRef", lt.dirigiblocksTextRef); L("dirigiblocksText", lt.dirigiblocksText);
                L("upgradeName", lt.bd_UpgradeNames); L("upgradeDesc", lt.bd_UpgradeDescriptions); L("upgradedDesc", lt.bd_UpgradedDescriptions);
                var vl = lt.videoTextList;
                if (vl != null) for (int i = 0; i < vl.Count; i++) { var v = vl[i]; if (v?.text == null) continue; for (int j = 0; j < v.text.Count; j++) Add("video:" + v.videoName, o, j, v.text[j]); }
            }
            File.WriteAllText(Path.Combine(outDir, "dump.tsv"), sb.ToString(), new UTF8Encoding(false));
            Plugin.Log.LogInfo("dump written");
        }

        GameObject gallery;

        // `gallery`: overlay listing every game font asset with the Latin sample and the Arabic text it will get
        void Gallery()
        {
            if (gallery != null) { UnityEngine.Object.Destroy(gallery); gallery = null; return; }
            ArabicFont.PatchAllLoaded();
            gallery = new GameObject("BPAR_Gallery");
            var canvas = gallery.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 5000;
            var bg = new GameObject("bg"); bg.transform.SetParent(gallery.transform, false);
            var img = bg.AddComponent<UnityEngine.UI.Image>(); img.color = new Color(0.04f, 0.05f, 0.08f, 0.96f);
            var brt = bg.GetComponent<RectTransform>(); brt.anchorMin = Vector2.zero; brt.anchorMax = Vector2.one; brt.offsetMin = brt.offsetMax = Vector2.zero;
            var fonts = new System.Collections.Generic.List<TMP_FontAsset>();
            foreach (var f in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
                if (f != null && !f.name.StartsWith("BPAR") && !f.name.StartsWith("Noto") && !f.name.Contains("Fallback") && f.name != "Frames SDF" && f.name != "Ornaments SDF") fonts.Add(f);
            fonts.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            int cols = 2, rows = (fonts.Count + cols - 1) / cols;
            for (int i = 0; i < fonts.Count; i++)
            {
                int col = i / rows, row = i % rows;
                float x = 20 + col * 960f, y = -20 - row * 68f;
                Label(fonts[i].name + "  [" + ArabicFont.StyleFor(fonts[i].name) + "]", fonts[i], x, y, 440, 30, 18f, false, Color.cyan);
                Label("The Great Hall 27", fonts[i], x, y - 24, 330, 40, 30f, false, Color.white);
                Label("الغرفة الكبرى 27 - اليوم الأول", fonts[i], x + 330, y - 24, 600, 44, 30f, true, Color.white);
            }
            Plugin.Log.LogInfo("gallery with " + fonts.Count + " fonts");
        }

        void Label(string text, TMP_FontAsset font, float x, float y, float w, float h, float size, bool arabic, Color col)
        {
            var go = new GameObject("lbl"); go.transform.SetParent(gallery.transform, false);
            var t = go.AddComponent<TextMeshProUGUI>();
            t.font = font; t.fontSize = size; t.color = col; t.enableWordWrapping = false; t.text = text;
            var rt = go.GetComponent<RectTransform>(); rt.anchorMin = rt.anchorMax = rt.pivot = new Vector2(0, 1);
            rt.anchoredPosition = new Vector2(x, y); rt.sizeDelta = new Vector2(w, h);
        }



        // subtitle hunt: while a video plays, save a screenshot named after the video clock every ~0.25s
        UnityEngine.Video.VideoPlayer tracePlayer;
        void TraceFrame()
        {
            try
            {
                if (tracePlayer == null || !tracePlayer.isPlaying)
                {
                    tracePlayer = null;
                    foreach (var vp in Resources.FindObjectsOfTypeAll<UnityEngine.Video.VideoPlayer>())
                        if (vp != null && vp.isPlaying && vp.gameObject.activeInHierarchy) { tracePlayer = vp; break; }
                    if (tracePlayer == null) return;
                }
                string dir = Path.Combine(outDir, "trace"); Directory.CreateDirectory(dir);
                ScreenCapture.CaptureScreenshot(Path.Combine(dir, ((int)(tracePlayer.time * 100)).ToString("00000") + ".png"));
            }
            catch (Exception e) { Plugin.Log.LogError("trace: " + e.Message); tracing = false; }
        }

        // what plays video and which writers exist (subtitle hunt)
        void VideoInfo()
        {
            var sb = new StringBuilder();
            foreach (var vp in Resources.FindObjectsOfTypeAll<UnityEngine.Video.VideoPlayer>())
            {
                if (vp == null) continue;
                string clip = "?"; try { clip = vp.clip != null ? vp.clip.name : vp.url; } catch { }
                sb.Append("VP ").Append(TextOps.PathOf(vp)).Append(" active=").Append(vp.gameObject.activeInHierarchy).Append(" playing=").Append(vp.isPlaying).Append(" clip=").Append(clip).Append(" time=").Append(vp.time.ToString("0.0")).Append(" len=").Append(vp.length.ToString("0.0")).Append(" mode=").Append(vp.renderMode).Append((char)10);
            }
            foreach (var w in Resources.FindObjectsOfTypeAll<BluePrince.VideoTextWriter>())
            {
                if (w == null) continue;
                string tp = "null", st = "null";
                try { if (w.textMeshPro != null) tp = TextOps.PathOf(w.textMeshPro) + " active=" + w.textMeshPro.gameObject.activeInHierarchy + " text=" + w.textMeshPro.m_text; } catch { }
                try { if (w.subTitles != null) st = TextOps.PathOf(w.subTitles) + " active=" + w.subTitles.gameObject.activeInHierarchy + " text=" + w.subTitles.m_text; } catch { }
                string vc = "?"; try { vc = w.videoClip != null ? w.videoClip.name : "null"; } catch { }
                sb.Append("VTW ").Append(TextOps.PathOf(w)).Append(" active=").Append(w.gameObject.activeInHierarchy).Append(" clip=").Append(vc).Append(" line=").Append(w.currentLine).Append(" idx=").Append(w.videoTextIndex).Append(" tmp=").Append(tp).Append(" subTitles=").Append(st).Append((char)10);
            }
            File.WriteAllText(Path.Combine(outDir, "video.txt"), sb.ToString(), new UTF8Encoding(false));
            Plugin.Log.LogInfo("video written");
        }

        void Scan()
        {
            var sb = new StringBuilder();
            foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
            {
                if (t == null || !t.gameObject.activeInHierarchy) continue;
                string s = t.m_text;
                if (string.IsNullOrEmpty(s)) continue;
                string fa = t.m_fontAsset != null ? t.m_fontAsset.name : "?";
                sb.Append(TextOps.PathOf(t)).Append('\t').Append(fa).Append('\t').Append(ArabicFont.StyleFor(fa)).Append('\t').Append(t.m_fontSize).Append('\t').Append(t.color.a.ToString("0.00")).Append('/').Append(t.alpha.ToString("0.00")).Append('/').Append(t.maxVisibleCharacters).Append('/').Append(t.enabled ? "E" : "d").Append('/').Append(t.alignment).Append('/').Append(t.enableWordWrapping ? "wrap" : "nowrap").Append('/').Append(t.overflowMode).Append('/').Append(t.enableAutoSizing ? "auto" : "fix").Append('/').Append(t.rectTransform.rect.width.ToString("0")).Append('x').Append(t.rectTransform.rect.height.ToString("0")).Append('\t').Append(s.Replace("\n", "\\n")).Append('\n');
            }
            // subtitle hunt: active TMP objects whose m_text is empty (text may be set via SetText(StringBuilder)/char buffers), plus legacy Text / TextMesh
            foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
            {
                if (t == null || !t.gameObject.activeInHierarchy || !string.IsNullOrEmpty(t.m_text)) continue;
                int n = 0; try { n = t.textInfo != null ? t.textInfo.characterCount : 0; } catch { }
                if (n == 0) continue;
                sb.Append("EMPTYTMP ").Append(TextOps.PathOf(t)).Append((char)9).Append(t.m_fontAsset != null ? t.m_fontAsset.name : "?").Append((char)9).Append(n).Append(" chars").Append((char)9).Append(t.GetParsedText()).Append((char)10);
            }
            foreach (var t in Resources.FindObjectsOfTypeAll<UnityEngine.UI.Text>())
                if (t != null && t.gameObject.activeInHierarchy && !string.IsNullOrEmpty(t.text)) sb.Append("UITEXT ").Append(TextOps.PathOf(t)).Append((char)9).Append(t.text).Append((char)10);
            foreach (var t in Resources.FindObjectsOfTypeAll<TextMesh>())
                if (t != null && t.gameObject.activeInHierarchy && !string.IsNullOrEmpty(t.text)) sb.Append("TEXTMESH ").Append(TextOps.PathOf(t)).Append((char)9).Append(t.text).Append((char)10);
            File.WriteAllText(Path.Combine(outDir, "scan.txt"), sb.ToString(), new UTF8Encoding(false));
            Plugin.Log.LogInfo("scan written");
        }
    }
}
