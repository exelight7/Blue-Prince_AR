# تعريب Blue Prince (عربي كامل)

تعريب شبه كامل للعبة **Blue Prince** (نسخة Steam، Unity 2021.3.45f1 IL2CPP، الإصدار 1.0.5.0) على شكل إضافة **BepInEx 6** تترجم النصوص أثناء اللعب.
**لا تُعدَّل أي ملفات من اللعبة الأصلية**: التركيب يضيف ملفات جديدة فقط، والإزالة بأمر واحد.

> English summary: an Arabic (RTL, shaped) localization for Blue Prince, delivered as a BepInEx 6 IL2CPP plugin. It patches TextMeshPro at runtime, ships its own Arabic fonts and translations (about 5,200 entries), and never edits the original game files. Install with `release/BluePrince_Arabic/install.ps1`. AI agents and contributors: read [HANDOFF.md](HANDOFF.md) first.

## ما الذي يشمله

- القوائم والإعدادات والإيقاف المؤقت ونهاية اليوم، وأسماء الغرف والعناصر والترقيات، والمستندات والرسائل الطويلة، ونصوص الطرفيات.
- حروف عربية متصلة بالشكل الصحيح، واتجاه من اليمين لليسار، والتفاف الأسطر والمحاذاة، مع خمس عائلات خطوط تناسب أسلوب اللعبة.
- الفيديو الافتتاحي: الترجمة مطبوعة داخل الفيديو نفسه، فتكبّر الإضافة الفيديو لإخفاء الشريط الأسود السفلي وتعرض الترجمة العربية فوق الصورة، مع بطاقة للعبارة الكبيرة داخل الصورة.
- أسماء العناصر المكوّنة من حرف كبير + بقية الاسم، والجمل التي فيها فراغ لأيقونة، تُعاد ترتيبها للعربية.

ما يبقى بالإنجليزية عمدًا: كلمات الألغاز ومفاتيحها (كلمات سر الشبكة، مفاتيح المسؤول، مصطلحات الإيراجية)، وألغاز صناديق الجواهر وقصائد الألغاز، لأن حلها يعتمد على الحروف الإنجليزية. القائمة الكاملة مع السبب في [translation/work/b_exceptions.md](translation/work/b_exceptions.md).

ما لم يكتمل: النصوص المرسومة داخل الصور (الخريطة واللافتات)، والتحقق من الكتابة التدريجية (typewriter) داخل اللعبة، وبعض الأرقام الرومانية على وجه الساعة. التفاصيل في [HANDOFF.md](HANDOFF.md).

## التركيب

المتطلبات: Windows، نسخة Steam من Blue Prince، وPowerShell.

1. أغلق اللعبة.
2. حمّل المستودع (Code ثم Download ZIP) أو استنسخه، وافتح PowerShell داخل المجلد `release/BluePrince_Arabic`.
3. نفّذ:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

إن كانت اللعبة في مسار غير `D:\Games\Blue Prince` أضف `-GameDir "المسار\Blue Prince"`.

4. أول تشغيل بعد التركيب أبطأ: BepInEx يولّد مكتبات الربط (من دقيقة إلى دقيقتين، والنافذة سوداء). بعدها يعود التشغيل طبيعيًا.

المثبّت يتحقق من سلامة كل ملف بالـ SHA256، وينسخ نسخة احتياطية من أي ملف موجود مسبقًا، ويكتب قائمة بما أضافه في `BluePrinceArabic_installed.json` داخل مجلد اللعبة.

## الإزالة

```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

تحذف الملفات المضافة فقط (وذاكرة BepInEx المؤقتة) وتعيد أي ملف كان موجودًا قبل التركيب.

## أثناء اللعب

| المفتاح | الوظيفة |
|---|---|
| F10 | تبديل بين العربية والإنجليزية |
| F11 | إعادة تحميل ملف الترجمة (`BepInEx\plugins\BluePrinceArabic\ar.json`) |
| F12 | لقطة شاشة إلى `BepInEx\bpar` |

إن ظهر نص بالإنجليزية، تسجّله الإضافة في `BepInEx\bpar\untranslated.tsv` (كل نص ظاهر بلا ترجمة). أرسل الملف أو ارفعه كـ Issue ليُترجم في التحديث القادم.

## كيف تعمل

- تعديل Harmony على `TMP_Text.ParseInputText`: يُستبدل النص الإنجليزي بنص عربي مشكَّل مسبقًا (أشكال العرض، بترتيب منطقي) مع تفعيل RTL في TextMeshPro، ثم يُعاد الأصل، فلا يتأثر منطق اللعبة.
- الخطوط تُضاف كاحتياطي (fallback) إلى كل أصول الخطوط المحمّلة. الخطوط العربية: Amiri وIBM Plex Sans Arabic وMirza وKatibeh وRakkas (كلها بترخيص OFL).
- الترجمة: `translation/arabic/batches/*.json` ثم `tools/merge_batches.py` يتحقق منها ويبني `ar.json`.

## خريطة المستودع

| المسار | المحتوى |
|---|---|
| `plugin/BluePrinceArabic/` | شيفرة الإضافة (C#): `Plugin`، `Patches`، `Shaper`، `Translator`، `ArabicFont`، `IntroSubs`، `DropCaps`، `IconGaps`، `Layout`، `DocFont` |
| `translation/arabic/` | الترجمة: `batches/`، `ar.json` (الناتج)، `keep.json`، `ar_patterns.json`، `dropcap.json`، `tagwords.json`، `intro_subs.tsv` |
| `translation/work/` | `corpus.json` (كل نصوص اللعبة المرئية)، ملفات `prefix_b*.json`، `b_exceptions.md` |
| `tools/` | أدوات الترجمة والبناء والاختبار (بايثون) |
| `release/BluePrince_Arabic/` | حزمة التركيب الجاهزة (BepInEx + الإضافة + الخطوط + السكربتات) |
| `fonts/arabic/` | الخطوط العربية |
| `tests/ShaperCheck/` | اختبار صغير لتشكيل الحروف (`dotnet run`) |
| `state/`، `docs/`، `reference/`، `research/` | حالة المشروع وملاحظات الهندسة والأدلة |
| `HANDOFF.md`، `AGENTS.md` | نقطة الدخول لأي ذكاء اصطناعي أو مطوّر يكمل العمل |

## لمن يريد إكمال العمل

ابدأ بـ [HANDOFF.md](HANDOFF.md): فيه الحالة الدقيقة، والمسارات، وخطوات الترجمة والبناء، وما تبقى، وكيف تعيد بناء بيئة الاختبار على جهاز جديد.

## ملاحظة قانونية

المستودع لا يحتوي على أي ملفات من اللعبة (لا أصول ولا خطوط ولا نسخ احتياطية)، فقط الإضافة والترجمة والأدوات وحزمة BepInEx الحرة. Blue Prince حقوقها لأصحابها (Dogubomb / Raw Fury). هذا مشروع معجبين غير رسمي.
