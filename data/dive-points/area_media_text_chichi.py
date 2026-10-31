# -*- coding: utf-8 -*-
import json, os
os.environ.setdefault("SITE", "chichijima")
import enrich_site as E
QS = ["Chichijima underwater", "Ogasawara diving", "小笠原 ダイビング", "父島 ダイビング", "Bonin Islands underwater",
      "Ogasawara snorkeling", "父島 シュノーケル", "Chichijima reef"]
E.licenses()
D = json.load(open(E.P, encoding="utf-8"))
got = []
for q in QS:
    try:
        for m in E.flickr_search(text=q, n=8):
            if m["src"] not in [g["src"] for g in got]:
                m["area"] = True; m["query"] = q; got.append(m)
    except Exception as e:
        print(q, e)
print(len(got), [m["title"][:25] for m in got][:30])
am = D.get("area_media") or {}
for a in E.AREA_BBOX:
    if len(am.get(a) or []) < 2:
        am[a] = got[:6]
D["area_media"] = am
json.dump(D, open(E.P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
