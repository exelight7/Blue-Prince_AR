import json,re,glob,sys
c=json.load(open("../translation/work/corpus.json",encoding="utf-8"))
done={}
for p in sorted(glob.glob("../translation/arabic/batches/b*.json")): done.update(json.load(open(p,encoding="utf-8")))
keep=json.load(open("../translation/arabic/keep.json",encoding="utf-8"))
norm=lambda k: re.sub(r"<[^>]*>","",k).strip().lower()
dn={norm(k) for k in list(done)+keep}
tw=json.load(open('../translation/arabic/tagwords.json',encoding='utf-8'))
def hdr(s):
    if ',' not in s: return False
    t=re.sub(r'<[^>]*>','',s)
    ws=[w.strip().strip('"').lower() for w in t.split(',') if w.strip()]
    return bool(ws) and all(w in tw for w in ws)
out=[]
for x in c:
    if x["tier"]==3 and norm(x["src"]) not in dn:
        s=x["src"]; w=s.split()
        if len(w)>=4 and re.search(r"[a-z]{3}",s) and (re.search(r"[.!?,:]",s) or re.search(r"\b(please|you|your|the|is|are|will|can)\b",s)) and not s.startswith(("from :","to :")) and "Account Created" not in s and not hdr(s):
            out.append(s)
n=int(sys.argv[1]); off=int(sys.argv[2]) if len(sys.argv)>2 else 0
print(len(out),"left")
for s in out[off:off+n]: print(json.dumps(s,ensure_ascii=False))
