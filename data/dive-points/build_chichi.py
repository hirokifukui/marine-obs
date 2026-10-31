# -*- coding: utf-8 -*-
"""父島のダイビングポイントの位置（目安）を作る。
OSM の地名（岬・浜・島）の近くの海側に置く（near）か、エリア内に手で置く（area）。位置が分からないものは地図に置かない。"""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
coast = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/coast_chichi.json"))

SRC = {"OC": ("小笠原チャンネル", "https://www.ogasawara-channel.com/contents/diving.htm"),
       "SY": ("シゲノユウタ", "https://shigenoyuta.com/bonin_iland/"),
       "PP": ("パパスダイビングスタジオ", "https://papasds.com/diving/fundiving/"),
       "WT": ("WTP", "https://www.wtp.co.jp/area/detail/126/Ogasawara/"),
       "PD": ("PADI", "https://www.padi.co.jp/scuba-diving/scuba-vacations/vacation-spotlight/spot.aspx?sptcd=jp_1203"),
       "SM": ("スキューバモンスターズ", "https://scuba-monsters.com/spot/areas/6/spots/68/")}

VERTS = []
for el in coast["elements"]:
    g = el.get("geometry") or []
    for i in range(len(g) - 1):
        VERTS.append((g[i], g[i + 1]))


def near_sea(lat, lon, dist_km=0.2):
    """いちばん近い海岸線の点から、海側（OSM の海岸線は右手が海）へ dist_km ずらす。"""
    k = math.cos(math.radians(lat))
    a, b = min(VERTS, key=lambda ab: (ab[0]["lat"] - lat) ** 2 + ((ab[0]["lon"] - lon) * k) ** 2)
    dy = (b["lat"] - a["lat"]) * 111.0
    dx = (b["lon"] - a["lon"]) * 111.0 * k
    L = math.hypot(dx, dy) or 1
    ox, oy = dy / L * dist_km, -dx / L * dist_km
    return a["lat"] + oy / 111.0, a["lon"] + ox / (111.0 * k)


# near: (OSM 地名の座標, 書く地名)
NEAR = {
    "青灯台": ((27.0936, 142.1957), "青灯台"),
    "洲崎": ((27.0719, 142.1924), "洲崎"),
    "製氷海岸": ((27.0947, 142.2034), "製氷海岸"),
    "宮之浜": ((27.1036, 142.1944), "宮之浜"),
    "釣浜": ((27.1037, 142.2050), "釣浜"),
    "長崎": ((27.1010, 142.2186), "長崎"),
    "バラ沈": ((27.1181, 142.1964), "滝之浦湾"),
    "万作": ((27.1108, 142.2209), "万作浜"),
    "人丸インサイド": ((27.1173, 142.1880), "人丸島"),
    "人丸アウトサイド": ((27.1173, 142.1845), "人丸島"),
    "立神岩": ((27.1304, 142.1871), "立神崎"),
    "ひょうたん": ((27.1281, 142.1794), "瓢箪島"),
    "大岩": ((27.1153, 142.1720), "西島の大岩"),
    "西島北": ((27.1215, 142.1668), "西島"),
    "西島S/W": ((27.1135, 142.1620), "西島"),
    "西島東磯": ((27.1185, 142.1712), "西島"),
    "鹿浜": ((27.1600, 142.1850), "弟島"),
    "孫島平根": ((27.1950, 142.1961), "孫島"),
    "ドブ磯": ((27.0898, 142.2521), "東島・東磯"),
    "鯨崎": ((27.0496, 142.2369), "鯨崎"),
    "HAZAMA": ((27.0439, 142.1779), "閂島"),
    "タコ岩": ((27.0725, 142.1801), "蛸岩"),
}
# area: 地名から位置が決められないもの。エリアの中に手で置く（海の上に置くことだけ確かめている）
AREA = {
    "日吉丸": (27.0890, 142.1885), "駆潜艇": (27.0868, 142.1905), "横倒し": (27.0850, 142.1880),
    "エビ丸": (27.0832, 142.1905), "エダサンゴ": (27.0815, 142.1885), "海洋センター前": (27.0800, 142.1960),
    "イエロー": (27.0905, 142.1840), "赤ブイ": (27.0870, 142.1820), "赤岩": (27.0790, 142.1850),
    "クラゾウ根": (27.0840, 142.1790),
    "ハナヒゲポイント": (27.1065, 142.2120),
    "万作の鼻": (27.1125, 142.2270), "二子岩": (27.1235, 142.2083), "沖二子": (27.1250, 142.2083),
    "イーグルレイロック": (27.1240, 142.1720),
    "スターライトパレード": (27.0850, 142.2540), "南バラバラ": (27.0560, 142.2330),
    "北一つ岩": (27.0600, 142.1700),
}
# area のうち、手で置くと陸に乗るものは近くの海岸から海側へずらす（km）
SNAP = {"万作の鼻": 0.25, "二子岩": 0.5, "沖二子": 1.0, "南バラバラ": 0.5}
# area の目安の範囲（詳細に出す文言）
AREA_NOTE = {"二見湾（湾内・沈船）": "二見湾の中", "父島 北（宮之浜〜長崎）": "釣浜〜長崎の間", "兄島・瀬戸": "兄島のまわり",
             "西島": "西島のまわり", "父島 東": "父島の東側", "父島 南・南島": "父島の南西〜南島"}

rows = list(csv.DictReader(open(os.path.join(HERE, "chichijima_points.csv"), encoding="utf-8")))
out = []
for r in rows:
    nm = r["ポイント"]
    if nm in NEAR:
        (la, lo), note = NEAR[nm]
        la, lo = near_sea(la, lo)
        prec = "near"
    elif nm in AREA:
        la, lo = AREA[nm]; prec = "area"; note = AREA_NOTE[r["エリア"]]
        if nm in SNAP:
            la, lo = near_sea(la, lo, SNAP[nm])
    else:
        la = lo = None; prec = "unknown"; note = ""
    out.append({"name": nm, "alias": r["別名"], "area": r["エリア"], "features": r["特徴"], "depth": r["最大水深"],
                "lat": None if la is None else round(la, 5), "lng": None if lo is None else round(lo, 5),
                "precision": prec, "position_note": note,
                "sources": [{"key": k, "name": SRC[k][0], "url": SRC[k][1]} for k in r["出典"].split()]})
PJ = os.path.join(HERE, "chichijima.json")
if os.path.exists(PJ):  # 写真・解説はそのまま引き継ぐ（位置だけ作り直す）
    old = json.load(open(PJ, encoding="utf-8"))
    prev = {p["name"]: p for p in old["points"]}
    for p in out:
        for k in ("media", "commentary_ja", "commentary_en", "commentary_model"):
            if k in prev.get(p["name"], {}):
                p[k] = prev[p["name"]][k]
    extra = {"area_media": old["area_media"]} if "area_media" in old else {}
else:
    extra = {}
json.dump({"site": "chichijima", "title": "父島", "center": [27.10, 142.20], "points": out, **extra},
          open(os.path.join(HERE, "chichijima.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), "points;", Counter(p["precision"] for p in out))
