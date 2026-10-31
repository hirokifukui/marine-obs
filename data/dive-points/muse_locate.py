# -*- coding: utf-8 -*-
"""Muse Spark（Meta Model API）の Web 検索で、位置不明のポイントの場所を探させる試験。
環境変数: SITE, MODEL_API_KEY。結果は muse_<site>.json に保存（地図の JSON は書き換えない）。"""
import json, os, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE", "chichijima")
D = json.load(open(os.path.join(HERE, f"{SITE}.json"), encoding="utf-8"))
KEY = os.environ["MODEL_API_KEY"]
OUT = os.path.join(HERE, f"muse_{SITE}.json")
PROMPT = """小笠原・父島のダイビングポイント「{name}」{alias}について、Web を日本語で検索して調べてください。
分かっている特徴：{features}（最大水深 {depth}）。
知りたいのは場所です。どの島のどちら側か、近くの岬・浜・島の名前、二見港からの方角や時間など、出典に書かれていることだけを答えてください。
見つからなければ「見つからない」と書いてください。推測するときは推測と明記してください。
最後に、分かった場所を地図に置くなら緯度経度（目安）を「LATLON: 27.xxx, 142.xxx」の形で1行だけ。置けないなら「LATLON: なし」。"""

names = sys.argv[1:] or [p["name"] for p in D["points"] if p.get("lat") is None]
res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
for p in D["points"]:
    if p["name"] not in names or p["name"] in res:
        continue
    body = {"model": "muse-spark-1.3", "max_output_tokens": 12000,
            "tools": [{"type": "web_search", "search_context_size": "high",
                       "user_location": {"type": "approximate", "country": "JP", "timezone": "Asia/Tokyo"}}],
            "include": ["web_search_call.results"],
            "input": PROMPT.format(name=p["name"], alias=f"（別名：{p['alias']}）" if p["alias"] else "",
                                   features=p["features"] or "不明", depth=p["depth"] or "不明")}
    t0 = time.time()
    try:
        r = requests.post("https://api.meta.ai/v1/responses", json=body, timeout=600,
                          headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        j = r.json()
    except Exception as e:
        print(p["name"], "ERR", e, flush=True); continue
    text, cites, hits = "", [], []
    for it in j.get("output", []):
        if it.get("type") == "message":
            for c in it.get("content", []):
                if c.get("type") == "output_text":
                    text += c.get("text", "")
                    cites += [{"url": a.get("url"), "title": a.get("title")} for a in c.get("annotations", []) if a.get("type") == "url_citation"]
        if it.get("type") == "web_search_call":
            hits += [{"url": h.get("url"), "title": h.get("title")} for h in (it.get("results") or [])]
    res[p["name"]] = {"text": text, "citations": cites, "results": hits, "usage": j.get("usage"),
                      "error": j.get("error"), "sec": round(time.time() - t0)}
    print(p["name"], len(text), "chars", len(cites), "cites", len(hits), "hits", res[p["name"]]["sec"], "s", flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done")
