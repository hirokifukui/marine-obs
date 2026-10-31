# -*- coding: utf-8 -*-
"""Muse Spark（Meta Model API）の Web 検索で、ポイントごとに場所・ログに出る生き物・潜る条件を調べる。
使い方: SITE=miyako MODEL_API_KEY=... python3 muse_research.py [points|area]
結果: muse2_<site>.json（地図の JSON は書き換えない）"""
import json, os, re, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE", "chichijima")
D = json.load(open(os.path.join(HERE, f"{SITE}.json"), encoding="utf-8"))
if os.environ.get("EXTRA"):  # 追加候補だけを調べる
    D = {"points": json.load(open(os.path.join(HERE, f"extras_{SITE}.json"), encoding="utf-8"))}
KEY = os.environ["MODEL_API_KEY"]
OUT = os.path.join(HERE, f"muse2_{SITE}.json")
LOCK = threading.Lock()

REGION = {
    "miyako": ("宮古島（沖縄県・宮古島市）", "宮古島・伊良部島・下地島・池間島・来間島とその周り、八重干瀬", "平良港・佐良浜港・長山港など", "24.6–25.1, 125.0–125.5"),
    "manza": ("万座（沖縄本島・恩納村）", "恩納村の万座毛まわり、万座ビーチ・万座岬・瀬良垣・安富祖・名嘉真あたり（真栄田岬・青の洞窟や読谷・北部は含めない）", "恩納村の各港", "26.48–26.53, 127.83–127.92"),
    "chichijima": ("小笠原・父島", "父島・兄島・弟島・孫島・西島・東島・南島とその周り（父島列島）。ケータ列島（聟島列島）や母島は含めない", "二見港", "27.03–27.20, 142.15–142.27"),
}[SITE]

PROMPT = """{region}のダイビングポイント「{name}」{alias}について、日本語の Web（ダイビングショップのログ・ブログ、ガイドの紹介ページ、個人のダイビング日記など）を検索して調べてください。
今わかっていること：エリア「{area}」、特徴「{features}」、最大水深「{depth}」。
対象の範囲：{scope}。

調べてほしいこと（出典に書かれていることだけ。推測は guess と明記）：
1. 場所：どの島のどちら側か、近くの岬・浜・島・港の名前、{port}からの方角や時間。出典に緯度経度があればそれも。
2. このポイントは本当に対象の範囲にあるか（別の海域のポイントと名前が同じだけ、などでないか）。
3. ログや紹介に実際に出てくる生き物（季節が書いてあれば季節も）。
4. どんな日に潜るか：風向き・季節・うねりとの関係（例：「北風の日は南側で」）、流れの強さ、難易度。
5. 別名・表記ゆれ。

最後に、次の形の JSON を ```json で1つだけ出してください（値は日本語。わからない項目は null か空の配列）：
{{"location": {{"status": "stated|guess|not_found", "text": "場所の説明（1〜2文）", "lat": 数値かnull, "lng": 数値かnull, "basis": "根拠の短い要約"}},
 "in_scope": true|false|null, "scope_note": "範囲外ならどこのポイントか",
 "aliases": ["…"],
 "creatures": [{{"name": "生き物の名前", "season": "季節かnull"}}],
 "conditions": {{"wind": "向いている／避ける風向きや季節（出典どおり）かnull", "current": "流れかnull", "level": "難易度かnull"}},
 "depth": "水深（出典どおり）かnull",
 "sources": ["使った出典のURL"]}}
緯度経度は、場所が分かったときだけ、その場所の海の上の目安を入れてください（範囲 {bbox}）。"""


def call(p):
    body = {"model": "muse-spark-1.3", "max_output_tokens": 16000,
            "tools": [{"type": "web_search", "search_context_size": "medium",
                       "user_location": {"type": "approximate", "country": "JP", "timezone": "Asia/Tokyo"}}],
            "input": PROMPT.format(region=REGION[0], scope=REGION[1], port=REGION[2], bbox=REGION[3], name=p["name"],
                                   alias=f"（別名：{p['alias']}）" if p.get("alias") else "", area=p["area"],
                                   features=p.get("features") or "不明", depth=p.get("depth") or "不明")}
    t0 = time.time()
    for attempt in range(3):
        try:
            r = requests.post("https://api.meta.ai/v1/responses", json=body, timeout=900,
                              headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            j = r.json()
            if r.status_code == 429 or (j.get("error") and "rate" in json.dumps(j["error"]).lower()):
                time.sleep(30 * (attempt + 1)); continue
            break
        except Exception as e:
            j = {"error": str(e)}; time.sleep(10)
    text, cites = "", []
    for it in j.get("output", []) or []:
        if it.get("type") == "message":
            for c in it.get("content", []):
                if c.get("type") == "output_text":
                    text += c.get("text", "")
                    cites += [{"url": a.get("url"), "title": a.get("title")} for a in c.get("annotations", []) if a.get("type") == "url_citation"]
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    data = None
    if m:
        try:
            data = json.loads(m[-1])
        except Exception:
            data = None
    return {"text": text, "data": data, "citations": cites, "usage": j.get("usage"), "error": j.get("error"),
            "sec": round(time.time() - t0)}


def run_points(workers=4):
    res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    todo = [p for p in D["points"] if p["name"] not in res or not res[p["name"]].get("data")]

    def job(p):
        out = call(p)
        with LOCK:
            res[p["name"]] = out
            json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        d = out["data"] or {}
        print(p["name"], "|", (d.get("location") or {}).get("status"), "| in_scope", d.get("in_scope"),
              "|", len(d.get("creatures") or []), "creatures |", out["sec"], "s", "| ERR" if out["error"] else "", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, todo))
    print("done points", len(res))


AREA_PROMPT = """{region}のダイビングポイントの名前を、日本語の Web（ショップのログ・ブログ、ポイント紹介、ダイビング日記）から、できるだけ多く集めてください。
対象の範囲：{scope}。エリア「{area}」を中心に。
すでに知っている名前：{known}
この一覧にない名前を探すのが目的です。名前ごとに、どのあたりか（出典どおり）と出典URLを付けてください。範囲外のものは入れないでください。
最後に ```json で [{{"name": "…", "aliases": [], "where": "…", "features": "…", "depth": null, "sources": ["…"]}}] を1つだけ出してください。"""


def salvage(text):
    """```json [ ... ] の配列から、閉じている {...} だけを拾う（途中で切れていても）。"""
    i = text.rfind("```json")
    if i < 0:
        return []
    body = text[i + 7:]
    out, depth, start, ins, esc = [], 0, None, False, False
    for k, ch in enumerate(body):
        if ins:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': ins = False
            continue
        if ch == '"': ins = True
        elif ch == "{":
            if depth == 0: start = k
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try: out.append(json.loads(body[start:k + 1]))
                except Exception: pass
    return out


def run_area():
    out = {}
    areas = sorted(set(p["area"] for p in D["points"] if not p["area"].startswith("（")))
    prev = os.path.join(HERE, f"muse2_{SITE}_area.json")
    if os.path.exists(prev):
        out.update({a: v for a, v in json.load(open(prev, encoding="utf-8")).items() if v.get("items")})
    areas = [a for a in areas if a not in out]
    known = "、".join(p["name"] for p in D["points"])
    def job(a):
        body = {"model": "muse-spark-1.3", "max_output_tokens": 48000,
                "tools": [{"type": "web_search", "search_context_size": "high",
                           "user_location": {"type": "approximate", "country": "JP", "timezone": "Asia/Tokyo"}}],
                "input": AREA_PROMPT.format(region=REGION[0], scope=REGION[1], area=a, known=known)}
        r = requests.post("https://api.meta.ai/v1/responses", json=body, timeout=900,
                          headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}).json()
        text = "".join(c.get("text", "") for it in r.get("output", []) or [] if it.get("type") == "message"
                       for c in it.get("content", []) if c.get("type") == "output_text")
        items = salvage(text)
        with LOCK:
            out[a] = {"items": items, "text": text, "usage": r.get("usage")}
            json.dump(out, open(os.path.join(HERE, f"muse2_{SITE}_area.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("area", a, len(items), flush=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(job, areas))
    print("done area")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "points"
    if mode == "points":
        run_points(int(os.environ.get("WORKERS", "4")))
    else:
        run_area()
