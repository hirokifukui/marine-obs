# -*- coding: utf-8 -*-
"""万座のダイビングポイントの位置（目安）を作る。手順は build_miyako.py と同じ。"""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
coast = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/coast_manza.json"))

SRC = {"DB": ("ディアブルー", "https://www.dearblue.jp/manza/"),
       "BC": ("青の洞窟ダイビング", "https://bluecave-okinawa.jp/manza/"),
       "DO": ("ディ・オア・ディ", "https://www.dordokinawa.jp/point"),
       "LV": ("リヴァイアサン", "https://www.ds-leviathan.com/point05/"),
       "FS": ("フリースタイル沖縄", "https://www.freestyle-diving.okinawa/fun/boat/manza/"),
       "HY": ("HYM", "https://hym.jp/okinawa-diving/diving/diving-point/post-1149")}

ANCHOR = {"万座毛下": (24.0, 0.0), "ミッションビーチ": (26.5195, 127.9060)}
ANCHOR["万座毛下"] = (26.5072, 127.8503)
# 海岸線の向きのずれで陸寄りに置かれたものを手で沖へ（位置はエリアの目安のまま）
NUDGE = {"ナカユクイ": (26.5105, 127.8625), "恋人岬": (26.5085, 127.8800)}
ANCHOR_NOTE = {"万座毛下": "万座毛", "ミッションビーチ": "ミッションビーチ"}

SEGMENTS = [
    ("万座毛 北側の崖", (26.5035, 26.5085, 127.8440, 127.8545), ["万座ドリームホール", "ミニドリームホール", "ゴジラ", "オーバーヘッドロック", "顔面ホール"]),
    ("万座毛の南〜恩納", (26.4930, 26.5035, 127.8400, 127.8500), ["万座毛南", "アポガマ", "トライアングル", "恩納ポイント"]),
    ("万座岬（ホテルの岬）", (26.5050, 26.5130, 127.8540, 127.8620), ["ホーシュー北", "ホーシュー", "ホテルエッジ", "コーラル"]),
    ("万座湾〜瀬良垣", (26.5050, 26.5140, 127.8620, 127.8760), ["ナカユクイ", "クロスライン", "瀬良垣インリーフ", "瀬良垣アウトリーフ"]),
    ("安富祖〜名嘉真", (26.5000, 26.5180, 127.8800, 127.9020), ["恋人岬", "シルジナー"]),
]


def seaward_points(bbox, n, dist_km=0.25):
    s, nn, w, e = bbox
    pts = []
    for el in coast["elements"]:
        g = el.get("geometry") or []
        for i in range(len(g) - 1):
            a, b = g[i], g[i + 1]
            if s <= a["lat"] <= nn and w <= a["lon"] <= e:
                dy = (b["lat"] - a["lat"]) * 111.0
                dx = (b["lon"] - a["lon"]) * 111.0 * math.cos(math.radians(a["lat"]))
                L = math.hypot(dx, dy) or 1
                ox, oy = dy / L * dist_km, -dx / L * dist_km
                pts.append((a["lat"] + oy / 111.0, a["lon"] + ox / (111.0 * math.cos(math.radians(a["lat"])))))
    if not pts:
        raise SystemExit(f"no coastline in {bbox}")
    pts.sort(key=lambda p: (p[1], p[0]))
    if n == 1:
        return [pts[len(pts) // 2]]
    return [pts[round(i * (len(pts) - 1) / (n - 1))] for i in range(n)]


rows = list(csv.DictReader(open(os.path.join(HERE, "manza_points.csv"), encoding="utf-8")))
pos = {nm: (la, lo, "near", ANCHOR_NOTE.get(nm, "")) for nm, (la, lo) in ANCHOR.items()}
for seg, bbox, names in SEGMENTS:
    for name, (la, lo) in zip(names, seaward_points(bbox, len(names))):
        pos[name] = (la, lo, "area", seg)
for nm, (la, lo) in NUDGE.items():
    pos[nm] = (la, lo, "area", pos[nm][3])
out = []
for r in rows:
    nm = r["ポイント"]
    if nm not in pos:
        raise SystemExit(f"no position for {nm}")
    la, lo, prec, note = pos[nm]
    out.append({"name": nm, "alias": r["別名"], "area": r["エリア"], "features": r["特徴"], "depth": r["最大水深"],
                "lat": round(la, 5), "lng": round(lo, 5), "precision": prec, "position_note": note,
                "sources": [{"key": k, "name": SRC[k][0], "url": SRC[k][1]} for k in r["出典"].split()]})
json.dump({"site": "manza", "title": "万座", "center": [26.506, 127.865], "points": out},
          open(os.path.join(HERE, "manza.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "points;", sum(p["precision"] == "near" for p in out), "near")
