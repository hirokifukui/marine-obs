# -*- coding: utf-8 -*-
"""万座：スローライフ（ログ）とラグーン（ポイント紹介）の情報をまとめて shops_manza.json にする。
スローライフのログは /tmp/sl/logs.json（parse 済み）から。"""
import collections, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SL_URL = "https://slowlife-ms.com/blog/category/onnason-fun-diving/manza-diving"
LG_URL = "https://www.lagoon-diving.com/diving-spots"

# ログの表記 → 地図の名前
SL_NAME = {"ドリームホール": "万座ドリームホール", "ミニドリーム": "ミニドリームホール", "ナカユキ": "ナカユクイ", "ナカユキ（体験）": "ナカユクイ",
           "ナカユクイ（体験ダイビング）": "ナカユクイ", "ゴジラの足あと": "ゴジラ", "コシラ": "ゴジラ", "トライアングルホール": "トライアングル",
           "万座毛メイン": "万座毛下", "万座毛クレパス": "万座毛下", "ドリームホール横": "万座ドリームホール"}
KNOWN = {"クロスライン", "万座ドリームホール", "オーバーヘッドロック", "ミニドリームホール", "ナカユクイ", "ホーシュー", "ホテルエッジ",
         "ゴジラ", "アポガマ", "コーラル", "トライアングル", "万座毛下"}


def split_names(s):
    s = re.sub(r"^(AM|PM)：", "", s)
    if s == "ナカクロス":
        return ["ナカユクイ", "クロスライン"]
    out = []
    for part in re.split(r"[〜→～]|\s+[②③④]", s):
        part = re.sub(r"^[①-⑩]\s*", "", part).strip()
        n = SL_NAME.get(part, part)
        if n in KNOWN:
            out.append(n)
    return out


def clean(c):
    c = re.sub(r"[（(].*?[)）]", "", c)
    c = re.sub(r"\s*(\d+\s*(匹|個体|ペア)|×\d+|yg|幼魚|と卵|の卵|ペア|たくさん|多数|いっぱい).*$", "", c)
    return c.strip(" ・、♪!！")


logs = json.load(open("/tmp/sl/logs.json", encoding="utf-8"))
stats = collections.defaultdict(lambda: {"dives": 0, "months": collections.Counter(), "creatures": collections.Counter(), "urls": []})
for o in logs:
    if not o.get("date"):
        continue
    month = int(o["date"][5:7])
    names = []
    for p in o["points"]:
        names += split_names(p)
    for n in dict.fromkeys(names):
        stats[n]["dives"] += 1
        stats[n]["months"][month] += 1
        if len(stats[n]["urls"]) < 3:
            stats[n]["urls"].append(o["url"])
    for key, items in (o.get("creatures") or {}).items():
        for n in dict.fromkeys(split_names(key)):
            for c in dict.fromkeys(clean(x) for x in items):
                if 1 < len(c) <= 20 and not re.search(r"[。！？]|ポイント|本目", c):
                    stats[n]["creatures"][c] += 1

SL = {}
for n, s in stats.items():
    SL[n] = {"dives": s["dives"], "months": sorted(s["months"]), "urls": s["urls"],
             "creatures": [{"name": c, "n": k} for c, k in s["creatures"].most_common(14)]}

# ラグーンのポイント紹介（https://www.lagoon-diving.com/diving-spots）
LG = {
    "恩納ポイント": ("最大18〜25m", "初級〜", "クレバスが迷路のように続く地形"),
    "アポガマ": ("最大25m", "中級〜", "縦穴を20mほど下りる地形"),
    "ホーシュー": ("最大20〜40m", "初級〜", "崖のドロップオフ、万座らしいダブルアーチ"),
    "ホーシュー北": ("最大20〜40m", "中級〜", "カマストガリザメ狙い"),
    "トライアングル": ("最大10m", "中級〜・上級者", "鍾乳洞の水中洞窟、満潮時のみ"),
    "万座毛洞窟": ("最大10m", "初級〜", "もう一つの「青の洞窟」、満潮時のみ"),
    "万座毛下": ("最大18〜40m", "初級〜", "万座毛の真下から沖の根へ"),
    "コーラル": ("最大18〜40m", "初級〜", "魚影が濃く地形も面白い"),
    "ホテルエッジ": ("最大20〜40m", "中級〜・上級者", "大物狙いのドリフト"),
    "オーバーヘッドロック": ("最大18〜40m", "初級〜", "地形・マクロ・ワイド"),
    "スネークホール": ("最大30〜40m", "中級〜・上級者", "ドリームホールの沖、アナゴと小魚、穴の中には入らない"),
    "万座ドリームホール": ("最大25〜40m", "中級〜・上級者", "沖縄本島屈指の地形ポイント"),
    "ゴジラ": ("最大18〜40m", "初級〜", "「ゴジラの割れ目」、竜宮城のような地形"),
    "ミニドリームホール": ("最大18〜40m", "初級〜", "ドリームホールの小型版、出口が18m"),
    "顔面ホール": ("最大18〜30m", "初級〜", "水深10m前後の横穴、天井から光のカーテン"),
    "ナカユクイ": ("最大12〜35m", "初級〜", "砂地とサンゴ"),
    "クロスライン": ("最大18〜25m", "初級〜", "砂地のマクロ"),
    "サンゴ畑": ("最大6m", "初級〜", "恩納らしい浅場のサンゴ"),
    "リトルグロット": ("最大18〜25m", "初級〜", "クレバスがトンネルにつながる浅い地形"),
}
# スローライフのポイント紹介（ログ以外）
SLN = {
    "万座ドリームホール": "別名ピカチューホール。港からボートで約10分、水深-5〜-35m、流れがあることが多い。-5mの狭い穴から入り-20mまで縦穴",
    "ホーシュー": "港からボートで約15分、万座毛のすぐ近く。-5〜-35m、流れがあることが多い。入口近くに2段のらせん状トンネル",
    "ナカユクイ": "港からボートで約5分（港から一番近い）。水深約6〜30m、流れはない。白い砂地とサンゴ、アオウミガメの休み場",
    "クロスライン": "港からボートで約5分。流れはない。砂地のマクロ、アオウミガメの休み場",
    "オーバーヘッドロック": "流れがあることが多い。アオウミガメ、深場に珍しいハゼやピグミーシーホース",
}
json.dump({"slowlife": SL, "lagoon": LG, "slowlife_notes": SLN, "sl_url": SL_URL, "lg_url": LG_URL},
          open(os.path.join(HERE, "shops_manza.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n, s in sorted(SL.items(), key=lambda x: -x[1]["dives"]):
    print(n, s["dives"], s["months"], [c["name"] for c in s["creatures"][:6]])
