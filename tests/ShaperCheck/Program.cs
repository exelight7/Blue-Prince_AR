using System;
using System.Linq;
using BluePrinceArabic;

// expected presentation-form codepoints (logical order, as TMP RTL consumes them)
var cases = new[]
{
    ("الإعدادات", "FE8D FEF9 FECB FEAA FE8D FEA9 FE8D FE95"),
    ("الملاحق",   "FE8D FEDF FEE4 FEFC FEA3 FED6"),
    ("الأخيرة",   "FE8D FEF7 FEA7 FEF4 FEAE FE93"),
    ("سلام",      "FEB3 FEFC FEE1"),
};
int bad = 0;
foreach (var (src, want) in cases)
{
    string got = string.Join(" ", Shaper.Process(src).Select(c => ((int)c).ToString("X4")));
    if (got != want) { bad++; Console.WriteLine("FAIL " + src + "\n  got  " + got + "\n  want " + want); }
}
// the closing dot of "D.C." stays inside the (reversed) Latin run: ".C.D" is stored as one piece
foreach (var w in new[] { "بشركة D.C. للطاقة", "مؤشرات V.A.C." })
{
    string o = Shaper.Process(w);
    string run = w.Contains("D.C.") ? ".C.D" : ".C.A.V";
    if (!o.Contains(run)) { bad++; Console.WriteLine("FAIL abbreviation " + w + " -> " + string.Join(" ", o.Select(c => ((int)c).ToString("X4")))); }
}
Console.WriteLine(bad == 0 ? "ShaperCheck OK" : bad + " failed");
return bad;
