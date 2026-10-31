# -*- coding: utf-8 -*-
import json, os
os.environ.setdefault("SITE", "manza")
import enrich_site as E
QS = ["Manza Okinawa underwater", "万座 ダイビング", "Manza dream hole", "恩納村 ダイビング", "Onna Okinawa diving", "瀬良垣 シュノーケル", "Onna village snorkeling"]
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
print(len(got), [m["title"][:25] for m in got][:20])
D["area_media"] = {a: got[:6] for a in E.AREA_BBOX}
json.dump(D, open(E.P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
