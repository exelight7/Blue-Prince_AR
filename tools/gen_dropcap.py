"""Build translation/arabic/dropcap.json: one full Arabic title (prescription folded in) per "You Found Text" group.

The English titles are split over many TMP pieces (small prefix line, big first letter, rest of the name), so the
plugin shows the whole Arabic title in one piece and blanks the others. Needs translation/work/youfound.tsv
(python dump_youfound.py). Keys: a group name ("You Found Blueprint") or, for variants, group/container.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# normalized item name (group without the "You Found/Bought/Dug Up..." verb) -> Arabic title
ITEMS = {
    "chronograph": "كرونوغراف غريب",
    "compass": "بوصلة ملاحية",
    "emerald bracelet": "سوار زمرد أنيق",
    "key 46": "مفتاح الحرم",
    "key 8": "المفتاح 8",
    "knight's shield": "درع فارس أوريندي قديم",
    "a knight's shield": "درع فارس أوريندي قديم",
    "lock pick": "عدة فتح الأقفال للهواة",
    "mag glass": "عدسة مكبرة من الخشب والنحاس",
    "master key": "المفتاح الرئيسي للعقار",
    "metal detector": "كاشف معادن يعمل",
    "moon pendant": "قلادة قمر غامضة",
    "morning star": "نجمة الصباح المهيبة",
    "ornate compass": "فرجار رسم مزخرف",
    "prism key": "مفتاح المنشور",
    "running shoes": "زوج من أحذية الجري",
    "salt shaker": "مملحة زجاجية",
    "secret garden key": "مفتاح الحديقة السرية",
    "silver key": "المفتاح الفضي",
    "silver spoon": "الملعقة الفضية المضرب بها المثل",
    "sledge hammer": "مطرقة ثقيلة",
    "sleep mask": "قناع نوم حريري أسود",
    "the axe": "فأس ثقيل",
    "torch": "شعلة ذاتية الاشتعال",
    "upgrade disk": "قرص ترقية المخططات",
    "key 149": "مفتاح صندوق أمانات",
    "key 233": "مفتاح صندوق أمانات",
    "key 304": "مفتاح صندوق أمانات",
    "key 370": "مفتاح صندوق أمانات",
    "2 gems": "زوج من الجواهر",
    "3 gems": "ثلاث جواهر عادية",
    "2 keys": "مفتاحان قديمان",
    "3 keys": "ثلاثة مفاتيح قديمة",
    "broken lever": "ما يبدو أنه رافعة مكسورة",
    "scrap": "قصاصة ورق ممزقة ومهملة",
    "treasure map": "خريطة كنز قديمة ممزقة",
    "a floorplan": "ما يبدو أنه مخطط غرفة",
    "a gem": "جوهرة عادية",
    "a stop watch": "ساعة إيقاف فضية أثرية",
    "stopwatch": "ساعة إيقاف فضية أثرية",
    "stopwatch_coatcheck": "ساعة إيقاف فضية أثرية",
    "a turnip": "لفتة ضخمة",
    "a wind up key": "مفتاح تعبئة قديم مهمل",
    "wind-upkey": "مفتاح تعبئة غريب",
    "a boot": "حذاء قديم عديم القيمة",
    "a brick": "طوبة قديمة عديمة القيمة",
    "a can": "علبة صفيح قديمة عديمة القيمة",
    "a coin": "عملة معدنية متسخة",
    "a few coins": "بضع عملات قديمة",
    "a key": "مفتاح عادي",
    "a nail": "مسمار قديم صدئ",
    "a rock": "صخرة عادية",
    "jack": "لا شيء في هذه الطبقة من التربة",
    "pebbles": "بضع حصى عادية",
    "basement key": "مفتاح القبو",
    "battery pack": "حزمة بطارية كبيرة",
    "blueprint": "مخطط ماونت هولي",
    "cabinet key": "مفتاح خزانة ملفات دُفن منذ زمن بعيد",
    "cabinet key 5": "مفتاح خزانة ملفات قديم صدئ",
    "car keys": "طقم احتياطي من مفاتيح السيارة",
    "coin purse": "كيس نقود صغير",
    "coupon book": "دفتر قسائم مخفّضة",
    "crown of the blueprints": "تاج المخططات",
    "cursed effigy": "التمثال الحجري الملعون",
    "diary key": "مفتاح يوميات الليدي إبسن",
    "gear wrench": "مفتاح ربط تروس قابل للضبط",
    "hall pass": "تصريح ممر طلابي",
    "keycard": "بطاقة مفتاح إلكترونية",
    "lucky rabbit's foot": "قدم أرنب محظوظ أصلية",
    "lunch box": "علبة غداء أعدّها الموظفون",
    "microchip 1": "رقاقة بيانات صغيرة مدفونة في جرة قديمة",
    "microchip 1b": "رقاقة بيانات صغيرة",
    "microchip 2": "رقاقة بيانات صغيرة",
    "microchip 3": "رقاقة بيانات صغيرة",
    "paper crown": "تاج ورقي أحمر مألوف",
    "repellent": "علبة بخاخ طارد",
    "royal scepter": "صولجان ملكي أجيري",
    "telescope": "منظار تلسكوبي",
    "the key of aries": "مفتاح آريس الملكي",
    "watering can": "إبريق ري جاهز للحديقة",
    "statue 8": "تحمل الآن التلسكوب",
    "dowsing rod": "عصا تنقيب معدنية",
    "electro magnet": "مغناطيس كهربائي يعمل",
    "burning glass": "عدسة حارقة بدائية",
    "detector shovel": "مجرفة كاشفة محسّنة",
    "jack hammer": "مطرقة هوائية مرتجلة",
    "lucky purse": "كيس محظوظ جدًا",
    "pick sound amplifier": "مضخّم صوت مفيد لفتح الأقفال",
    "power hammer": "مطرقة كهربائية مزوّدة بدارات",
}
# same item, different wording per verb (bought / found / dug up)
BY_GROUP = {
    "You Bought Shovel": "مجرفة حدائق",
    "You Found Shovel": "مجرفة قديمة بالية",
    "You Dug Up Allowance Token": "رمز الحصة الثمين",
    "You Found Allowance Token": "تم منحك رمز الحصة",
}
PAIR, SINGLE = "زوج من النرد العاجي", "قطعة نرد عاجية واحدة"
BY_CONTAINER = {
    "You Dug Up 2 Ivory Dice/Text/reroll dice": PAIR,
    "You Dug Up 3 Ivory Dice/Text/reroll dice": "ثلاث قطع نرد عاجية",
    "You Dug Up Ivory Dice/Text/new dice": PAIR,
    "You Dug Up Ivory Dice/Text/new dice (1)": PAIR,
    "You Dug Up Ivory Dice/Text/old dice": PAIR,
    "You Dug Up Ivory Dice/Text/reroll dice": SINGLE,
    "You Found Ivory Dice/Text/GameObject": PAIR,
    "You Found Ivory Dice/Text/new dice": PAIR,
    "You Found Ivory Dice/Text/new dice (1)": PAIR,
    "You Found Ivory Dice/Text/reroll dice": PAIR,
    "You Found Ivory Die/Text/GameObject": SINGLE,
    "You Found Ivory Die/Text/new dice": PAIR,
    "You Found Ivory Die/Text/new dice (1)": PAIR,
    "You Found Ivory Die/Text/reroll dice": SINGLE,
}
VERB = re.compile(r"^You (Found|Bought|Dug Up|assembled|found|Picked Up)\s+", re.I)


def norm(group):
    return re.sub(r"\s+", " ", VERB.sub("", group.strip())).strip().lower()


def main():
    rows = [l.rstrip("\n").split("\t") for l in (ROOT / "translation/work/youfound.tsv").read_text(encoding="utf-8").splitlines()]
    groups = sorted({r[0].strip() for r in rows if len(r) >= 10})
    out, missing = {}, []
    for g in groups:
        if g in BY_GROUP:
            out[g] = BY_GROUP[g]
        elif norm(g) in ITEMS:
            out[g] = ITEMS[norm(g)]
        elif not any(c.startswith(g + "/") for c in BY_CONTAINER):
            missing.append(g)
    out.update(BY_CONTAINER)
    (ROOT / "translation/arabic/dropcap.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "entries;", len(missing), "groups without title (left English):", missing)


if __name__ == "__main__":
    main()
