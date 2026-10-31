# -*- coding: utf-8 -*-
"""宮古島ダイビングポイントの位置（目安）を作る。
- 名前のある場所（通り池・白鳥岬・各ビーチなど）の近くは、その場所を手がかりに置く（precision=near）
- 手がかりのないポイントは、エリアの海岸線に沿って沖側へ約250mずらして均等に並べる（precision=area）
- 八重干瀬は礁域の中に散らして置く（precision=area）
入力: miyako_points.csv / /tmp/coast.json（OSM natural=coastline）
出力: miyako.json
"""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
coast = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/coast.json"))

SRC = {"E": ("エミナマリン", "https://eminamarine-diving.net/divingpoint"),
       "O": ("おきらく", "https://oki-raku.net/diving/miyako/diving_spot/"),
       "G": ("ガイド屋さん", "https://guide-ya-san.com/article/305.html"),
       "D": ("ダイブナビ", "https://www.divenavi.com/miyakojima/diving/"),
       "R": ("リーフ宮古", "https://reefmiyako.com/point-map/"),
       "K": ("KANCHI", "https://kanchi32.com/pointmap"),
       "A": ("アクアストーリー", "https://www.aqua-story.com/point.html"),
       "B": ("BIG HOLIDAY", "https://bigholiday-miyakojima.com/diving/point/yabiji"),
       "Y": ("碧海", "https://hekikai-okinawa.com/miyakojima/3694/"),
       "S": ("観光情報", "https://miyako-tour.com/")}

ANCHOR = {  # 名前のある場所の近く
    "通り池": (24.8236, 125.1326), "中の島チャネル": (24.8113, 125.1418),
    "中ノ島ビーチ": (24.8130, 125.1449), "白鳥ホール": (24.8672, 125.1612), "白鳥幼稚園": (24.8678, 125.1640),
    "沈船（カーフェリー）": (24.8345, 125.2205), "サシバ沖": (24.8450, 125.1520),
    "インギャーマリンガーデン": (24.7222, 125.3560), "シギラビーチ": (24.7193, 125.3410),
    "来間ビーチ": (24.7232, 125.2398), "クリマビーチ": (24.7178, 125.2480),
    "吉野海岸": (24.7495, 125.4442), "新城海岸": (24.7610, 125.4252),
    "保良漁港の浜": (24.7228, 125.4628), "フナクス": (24.9347, 125.2433),
}
ANCHOR_NOTE = {"通り池": "通り池（下地島）", "中の島チャネル": "中の島海岸", "中ノ島ビーチ": "中の島海岸",
               "白鳥ホール": "白鳥岬", "白鳥幼稚園": "白鳥岬", "沈船（カーフェリー）": "佐良浜港",
               "サシバ沖": "佐和田の浜の沖"}

# エリアの海岸線（緯度・経度の範囲）と、そこに並べるポイント
SEGMENTS = [
    ("下地島 西〜南", (24.806, 24.852, 125.124, 125.150),
     ["ミニ通り池＆ホワイトロード", "魔王の宮殿", "アントニオ・ガウディ", "中の島ホール", "マリンレイク", "本ドロップ", "津波岩",
      "津波岩ドロップ", "35ホール", "一の瀬ホール", "一の瀬ドロップ", "サンゴホール", "なるほど・ザ・ケーブ", "女王の部屋",
      "ツインケーブ", "ウォールケーブ", "だんご岩", "悪魔の館", "光の迷宮"]),
    ("下地島・伊良部 南（渡口〜中の島の内側）", (24.802, 24.814, 125.146, 125.186),
     ["トリプルスリー", "パナタ", "クリスタルパーク", "ロックビューティー", "石庭", "ウミウシ御殿", "マッドシティー", "フィッシュパーク", "オアシティ"]),
    ("伊良部 北", (24.858, 24.880, 125.166, 125.212),
     ["L字アーチ＆ワープホール", "クロスホール", "Wアーチ", "Zアーチ", "サバ沖ヒルズ", "スネークホール＆ハナダイの根", "デンターロック",
      "サプライズホール", "タートルタウン", "オーバーハング", "サージョンリーフ", "グルクンの根"]),
    ("伊良部 東（佐良浜）", (24.842, 24.862, 125.205, 125.226), ["ツインホール", "がけ下"]),
    ("狩俣", (24.884, 24.906, 125.252, 125.272), ["狩俣ツインケーブ＆エイトポールアーチ", "狩俣下"]),
    ("来間・前浜", (24.708, 24.732, 125.232, 125.262), ["ハマパラダイス", "インガマコーラル", "コーラルガーデン"]),
    ("宮古島 南（博愛〜上野）", (24.712, 24.730, 125.290, 125.335),
     ["七又アーチ", "5番アーチ", "11番ホール", "うしさんありがとう", "うしさんこわいよホール", "ラビリンス", "ガオー", "沈船ラビリンス"]),
    ("宮古島 南東（新城〜ムイガー）", (24.756, 24.782, 125.425, 125.450), ["ムイガードロップ"]),
]
YABIJI = (24.995, 125.262, 0.032, 0.040)   # 中心と半径（緯度・経度）


def seaward_points(bbox, n):
    """bbox 内の海岸線の点を集め、進行方向の右（OSM の海側）へ約250mずらして n 個を均等に選ぶ。"""
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
                ox, oy = dy / L * 0.25, -dx / L * 0.25      # 右側の法線 × 0.25 km
                pts.append((a["lat"] + oy / 111.0, a["lon"] + ox / (111.0 * math.cos(math.radians(a["lat"])))))
    if not pts:
        raise SystemExit(f"no coastline in {bbox}")
    # 緯度・経度で並べて、端から端まで均等に
    pts.sort(key=lambda p: (p[0], p[1]))
    if n == 1:
        return [pts[len(pts) // 2]]
    return [pts[round(i * (len(pts) - 1) / (n - 1))] for i in range(n)]


rows = list(csv.DictReader(open(os.path.join(HERE, "miyako_points.csv"), encoding="utf-8")))
pos = {}
for name, (la, lo) in ANCHOR.items():
    pos[name] = (la, lo, "near", ANCHOR_NOTE.get(name, ""))
for seg, bbox, names in SEGMENTS:
    for name, (la, lo) in zip(names, seaward_points(bbox, len(names))):
        pos[name] = (la, lo, "area", seg)
yab = [r["ポイント"] for r in rows if r["エリア"] == "八重干瀬"]
cy, cx, ry, rx = YABIJI
golden = math.pi * (3 - math.sqrt(5))
for i, name in enumerate(yab):
    r = math.sqrt((i + 0.5) / len(yab))
    t = i * golden
    pos[name] = (cy + ry * r * math.sin(t), cx + rx * r * math.cos(t), "area", "八重干瀬（礁域の中の目安）")

out = []
for r in rows:
    nm = r["ポイント"]
    if nm not in pos:
        raise SystemExit(f"no position for {nm}")
    la, lo, prec, note = pos[nm]
    out.append({"name": nm, "alias": r["別名"], "area": r["エリア"], "features": r["特徴"], "depth": r["最大水深"],
                "lat": round(la, 5), "lng": round(lo, 5), "precision": prec, "position_note": note,
                "sources": [{"key": k, "name": SRC[k][0], "url": SRC[k][1]} for k in r["出典"].split()]})
json.dump({"site": "miyako", "title": "宮古島", "center": [24.83, 125.26], "points": out},
          open(os.path.join(HERE, "miyako.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "points;", sum(p["precision"] == "near" for p in out), "near")
