# -*- coding: utf-8 -*-
"""エリアの水中写真を、位置情報ではなく言葉で探し直す（水中写真は位置情報が付いていないことが多いため）。"""
import json, os
import enrich_miyako as E

QUERIES = {
    "下地島": ["Shimojishima diving", "下地島 ダイビング", "Shimoji island underwater", "通り池 ダイビング"],
    "伊良部島": ["Irabu diving", "伊良部 ダイビング", "Irabu island underwater"],
    "八重干瀬": ["Yabiji", "八重干瀬", "Yaebishi reef"],
    "宮古島北（狩俣）": ["Ikema diving", "池間島 シュノーケル", "Miyakojima diving"],
    "宮古島南・来間": ["Miyakojima underwater", "宮古島 ダイビング", "Miyako island diving", "Kurima snorkel"],
}
if __name__ == "__main__":
    E.licenses()
    D = json.load(open(E.P, encoding="utf-8"))
    am = D.get("area_media") or {}
    for area, qs in QUERIES.items():
        got = list(am.get(area) or [])
        for q in qs:
            if len(got) >= 6:
                break
            try:
                for m in E.flickr_search(text=q, n=6):
                    if m["src"] not in [g["src"] for g in got]:
                        m["area"] = True; m["query"] = q; got.append(m)
            except Exception as e:
                print(area, q, e)
        am[area] = got[:6]
        print(area, len(am[area]), [m["title"][:30] for m in am[area]])
    D2 = json.load(open(E.P, encoding="utf-8"))   # 本体の処理と書き込みがぶつからないよう読み直す
    D2["area_media"] = am
    json.dump(D2, open(E.P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
