# -*- coding: utf-8 -*-
"""エリアごとの Muse 検索で見つかった名前のうち、一覧にないものを候補として出す。
python3 area_candidates.py <site>  → candidates_<site>.json"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1]
D = json.load(open(os.path.join(HERE, f"{SITE}.json"), encoding="utf-8"))
A = json.load(open(os.path.join(HERE, f"muse2_{SITE}_area.json"), encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[（(].*?[)）]", "", s)
    return re.sub(r"[\s・\-－ー〜~/／～＆&]", "", s).lower()


known = set()
for p in D["points"]:
    for n in [p["name"]] + re.split(r"[／/、]", p.get("alias") or "") + (p.get("aliases_found") or []):
        if n:
            known.add(norm(n))
for d in D.get("dropped", []):
    known.add(norm(d["name"]))
cand = {}
for area, v in A.items():
    for it in v.get("items") or []:
        n = (it.get("name") or "").strip()
        names = [n] + (it.get("aliases") or [])
        if not n or any(norm(x) in known for x in names if x):
            continue
        if not it.get("sources"):
            continue
        k = norm(n)
        if k in cand:
            cand[k]["sources"] = list(dict.fromkeys(cand[k]["sources"] + it["sources"]))[:6]
            cand[k]["areas"].append(area)
            continue
        cand[k] = {"name": n, "aliases": it.get("aliases") or [], "where": it.get("where"), "features": it.get("features"),
                   "depth": it.get("depth"), "sources": it["sources"][:6], "areas": [area]}
out = sorted(cand.values(), key=lambda c: -len(c["sources"]))
json.dump(out, open(os.path.join(HERE, f"candidates_{SITE}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(SITE, len(out))
for c in out:
    print(f"- {c['name']} {c['aliases']} | {c['areas'][0]} | {(c['where'] or '')[:60]} | {(c['features'] or '')[:40]} | {len(c['sources'])}")
