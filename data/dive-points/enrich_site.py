# -*- coding: utf-8 -*-
"""miyako.json に 写真（再利用が許可されたものだけ）と Claude の解説を足す。
写真: Flickr（CC0・PDM・CC BY・CC BY-SA）→ Wikimedia Commons。ポイント名で見つからなければ、エリアの水中写真（area=True）。
解説: 出典からまとめた事実（特徴・水深・エリア）だけを渡して書かせる。
環境変数: FLICKR_KEY, ANTHROPIC_API_KEY
"""
import json, os, re, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE", "miyako")
P = os.path.join(HERE, f"{SITE}.json")
D = json.load(open(P, encoding="utf-8"))
FK = os.environ["FLICKR_KEY"]
AK = os.environ["ANTHROPIC_API_KEY"]
UA = {"User-Agent": "marine-obs.org dive-sites (fukui)"}

# Flickr license ids: 4 CC BY 2.0, 5 CC BY-SA 2.0, 9 CC0, 10 PDM, 11 CC BY 4.0, 12 CC BY-SA 4.0
OK_LIC = "4,5,9,10,11,12"
LIC = {}


def flickr(method, **kw):
    kw.update({"method": method, "api_key": FK, "format": "json", "nojsoncallback": 1})
    r = requests.get("https://api.flickr.com/services/rest/", params=kw, headers=UA, timeout=30)
    r.raise_for_status()
    return r.json()


def licenses():
    for l in flickr("flickr.photos.licenses.getInfo")["licenses"]["license"]:
        LIC[str(l["id"])] = (l["name"], l.get("url", ""))


def flickr_search(text=None, bbox=None, n=3, tags=None):
    kw = {"license": OK_LIC, "media": "photos", "per_page": n, "sort": "relevance", "content_type": 1,
          "extras": "owner_name,license,url_m,url_l,geo,date_taken"}
    if text:
        kw["text"] = text
    if bbox:
        kw["bbox"] = bbox
    if tags:
        kw["tags"] = tags
        kw["tag_mode"] = "any"
    ph = flickr("flickr.photos.search", **kw)["photos"]["photo"]
    out = []
    for p in ph:
        url = p.get("url_l") or p.get("url_m")
        if not url:
            continue
        ln, lu = LIC.get(str(p["license"]), ("", ""))
        out.append({"type": "photo", "src": url, "page": f"https://www.flickr.com/photos/{p['owner']}/{p['id']}",
                    "title": p.get("title", ""), "author": p.get("ownername", ""), "license": ln, "license_url": lu,
                    "via": "Flickr"})
    return out


def commons_search(q, n=2):
    r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=30, params={
        "action": "query", "format": "json", "generator": "search", "gsrsearch": f"filetype:bitmap {q}",
        "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1024})
    pages = (r.json().get("query") or {}).get("pages") or {}
    out = []
    for pg in pages.values():
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        lic = (md.get("LicenseShortName") or {}).get("value", "")
        if not re.search(r"CC0|Public domain|CC BY(-SA)? \d", lic, re.I) or re.search(r"NC|ND", lic):
            continue
        author = re.sub("<[^>]+>", "", (md.get("Artist") or {}).get("value", "")).strip()
        out.append({"type": "photo", "src": ii.get("thumburl") or ii.get("url"), "page": ii.get("descriptionurl"),
                    "title": pg.get("title", "").replace("File:", ""), "author": author, "license": lic,
                    "license_url": (md.get("LicenseUrl") or {}).get("value", ""), "via": "Wikimedia Commons"})
    return out


AREA_BBOX_MIYAKO = {  # エリアの水中写真用（minlon,minlat,maxlon,maxlat）
    "下地島": "125.12,24.80,125.16,24.86", "伊良部島": "125.15,24.82,125.23,24.89", "八重干瀬": "125.18,24.94,125.34,25.06",
    "宮古島北（狩俣）": "125.24,24.87,125.29,24.94", "宮古島南・来間": "125.22,24.70,125.46,24.79",
}


AREA_BBOX_MANZA = {"万座毛まわり": "127.835,26.495,127.860,26.515", "万座毛南〜恩納": "127.830,26.485,127.855,26.505",
                   "万座岬（ホテル前）": "127.850,26.500,127.870,26.520", "万座湾〜瀬良垣": "127.855,26.500,127.885,26.520",
                   "安富祖〜名嘉真": "127.875,26.495,127.925,26.530"}
AREA_BBOX_CHICHI = {"二見湾（湾内・沈船）": "142.175,27.070,142.205,27.098", "父島 北（宮之浜〜長崎）": "142.190,27.098,142.225,27.110",
                    "兄島・瀬戸": "142.175,27.105,142.240,27.140", "西島": "142.155,27.105,142.180,27.130",
                    "弟島・孫島": "142.170,27.145,142.210,27.205", "父島 東": "142.225,27.040,142.260,27.100",
                    "父島 南・南島": "142.160,27.030,142.200,27.075", "（位置不明）": "142.150,27.030,142.260,27.140"}
AREA_BBOX = {"manza": AREA_BBOX_MANZA, "chichijima": AREA_BBOX_CHICHI}.get(SITE, AREA_BBOX_MIYAKO)
PLACE = {"manza": "恩納", "chichijima": "父島"}.get(SITE, "宮古島")


def media_for(p):
    q = re.sub(r"[（(].*?[)）]", "", p["name"]).replace("＆", " ")
    got = []
    for text in (f"{q} {PLACE}", {"manza": f"{q} 万座", "chichijima": f"{q} 小笠原"}.get(SITE, f"{q} diving"), (p["alias"] or "").split("／")[0] + f" {PLACE}" if p["alias"] else None):
        if text and len(got) < 3:
            try:
                got += [m for m in flickr_search(text=text, n=3) if m["src"] not in [g["src"] for g in got]]
            except Exception as e:
                print("flickr", e)
    if len(got) < 2:
        try:
            got += commons_search(f"{q} {PLACE}")
        except Exception as e:
            print("commons", e)
    for m in got:
        m["area"] = False
    return got[:4]


def area_media():
    out = {}
    for a, bb in AREA_BBOX.items():
        try:
            ms = flickr_search(bbox=bb, n=8, tags="underwater,diving,scuba,reef,coral,ダイビング,水中")
        except Exception as e:
            print("area", a, e); ms = []
        for m in ms:
            m["area"] = True
        out[a] = ms
    return out


SYS = """あなたはダイビングポイント解説の書き手です。marine-obs.org の「{TITLE}のダイビングポイント」に載る短い解説を書きます。
守ること：
- 与えた事実（エリア・特徴・最大水深・別名）と、{CONTEXT}だけを使う。
- 与えていない生き物・地形・数字を作らない。情報が名前しかないポイントは、そう正直に書く（例：名前のほかに公開情報がほとんどない）。
- 宣伝の言い回しや断定（「必見」「最高」）を避け、落ち着いた中立の文にする。安全の指示はしない。
- ショップの文章を写さない。
出力はタグのみ：<ja>日本語 120〜180字</ja><en>English, 2–3 sentences</en>"""


CTX = {"miyako": ("宮古島", "宮古島の一般的な事情（夏は南風で伊良部島の北側、秋〜春は北風で下地島の南〜西側を潜ることが多い、八重干瀬は池間島の北の広い礁域で海況が良い日に行く、など）"),
       "manza": ("万座", "万座の一般的な事情（沖縄本島の西海岸、恩納村の万座毛まわり。北西に開けているため、冬の北寄りの季節風の時期はうねりが入りやすく、穏やかな日が多いのは夏。ボートで短時間で行けるポイントが多い、など）"),
       "chichijima": ("父島", "小笠原・父島の一般的な事情（本土から船で約24時間の外洋の島。ポイントの多くは二見港からボートで10〜40分ほど。父島の北に兄島・弟島、北西に西島、南に南島がある。二見湾の中は比較的穏やかで、外側は潮やうねりの影響を受けやすい。ケータ列島（聟島列島）のポイントはこの一覧に含めていない、など）")}
SYS = SYS.replace("{TITLE}", CTX[SITE][0]).replace("{CONTEXT}", CTX[SITE][1])


def commentary(p):
    facts = {k: p[k] for k in ("name", "alias", "area", "features", "depth")}
    for attempt in range(3):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=120,
                              headers={"x-api-key": AK, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                              json={"model": "claude-opus-5-5", "max_tokens": 4000, "system": SYS,
                                    "messages": [{"role": "user", "content": json.dumps(facts, ensure_ascii=False)}]})
            r.raise_for_status()
            t = "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text")
            ja = re.search(r"<ja>(.*?)</ja>", t, re.S); en = re.search(r"<en>(.*?)</en>", t, re.S)
            if ja and en:
                return ja.group(1).strip(), en.group(1).strip()
        except Exception as e:
            print("claude", p["name"], e); time.sleep(3)
    return "", ""


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    licenses()
    if only in ("all", "media"):
        D["area_media"] = area_media()
        for i, p in enumerate(D["points"]):
            p["media"] = media_for(p)
            print(i, p["name"], len(p["media"]), flush=True)
            json.dump(D, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if only in ("all", "text"):
        for i, p in enumerate(D["points"]):
            if p.get("commentary_ja"):
                continue
            p["commentary_ja"], p["commentary_en"] = commentary(p)
            p["commentary_model"] = "claude-opus-5-5"
            print(i, p["name"], len(p["commentary_ja"]), flush=True)
            json.dump(D, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done")
