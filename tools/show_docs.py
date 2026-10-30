"""Print the next N untranslated long (tier 2/3) documents in full for translation. usage: show_docs.py N [tier]"""
import json, re, glob, sys
c = json.load(open("../translation/work/corpus.json", encoding="utf-8"))
done = {}
for p in sorted(glob.glob("../translation/arabic/batches/b*.json")):
    done.update(json.load(open(p, encoding="utf-8")))
keep = json.load(open("../translation/arabic/keep.json", encoding="utf-8"))
norm = lambda k: re.sub(r"<[^>]*>", "", k).strip().lower()
dn = {norm(k) for k in list(done) + keep}
tier = int(sys.argv[2]) if len(sys.argv) > 2 else 2
skip = ("\n<b>Account Created", "You found a secret Floorplan", "<b>MoorR</b>", "to : <b>", "from : <b>", "You dug up a secret Floorplan", "You found a secret Floor Plan")  # handled by ar_patterns.json
todo = [x for x in c if x["tier"] == tier and norm(x["src"]) not in dn and not x["src"].startswith(skip)]
todo.sort(key=lambda x: (-x["n"], x["words"]))
print(len(todo), "left", sum(x["words"] for x in todo), "words")
for x in todo[:int(sys.argv[1])]:
    print(json.dumps(x["src"], ensure_ascii=False)); print()
