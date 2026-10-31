# -*- coding: utf-8 -*-
"""第2版：PADI の座標と Muse Spark の Web 検索の結果を、地図の JSON に反映する。
python3 apply_v2.py <site>   （<site>.json を書き換える。元は <site>.v1.json に一度だけ保存）"""
import json, math, os, re, sys, unicodedata
from collections import OrderedDict
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1]
P = os.path.join(HERE, f"{SITE}.json")
V1 = os.path.join(HERE, f"{SITE}.v1.json")
if not os.path.exists(V1):
    json.dump(json.load(open(P, encoding="utf-8")), open(V1, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
D = json.load(open(V1, encoding="utf-8"))
PADI = json.load(open(os.path.join(HERE, f"padi_{SITE}.json"), encoding="utf-8"))
MUSE = json.load(open(os.path.join(HERE, f"muse2_{SITE}.json"), encoding="utf-8"))
AREA = json.load(open(os.path.join(HERE, f"muse2_{SITE}_area.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, f"muse2_{SITE}_area.json")) else {}
REVIEW = json.load(open(os.path.join(HERE, "review_v2.json"), encoding="utf-8")).get(SITE, {}) if os.path.exists(os.path.join(HERE, "review_v2.json")) else {}
COAST = json.load(open(os.path.join(HERE, ".coast", {"chichijima": "coast_chichi.json"}.get(SITE, f"coast_{SITE}.json"))))
PADI_URL = {"chichijima": "https://www.padi.co.jp/scuba-diving/scuba-vacations/vacation-spotlight/spot.aspx?sptcd=jp_1203",
            "miyako": "https://www.padi.co.jp/scuba-diving/scuba-vacations/vacation-spotlight/spot.aspx?sptcd=jp_1219",
            "manza": "https://www.padi.co.jp/scuba-diving/scuba-vacations/vacation-spotlight/spot.aspx?sptcd=jp_1236"}[SITE]
BBOX = {"miyako": (24.68, 25.08, 125.05, 125.50), "manza": (26.48, 26.53, 127.82, 127.93),
        "chichijima": (27.02, 27.21, 142.14, 142.27)}[SITE]
# PADI の名前 → こちらの名前（表記が違うもの）
PADI_ALIAS = {"釣り浜": "釣浜", "HAZAMA（閂ロック）": "HAZAMA", "ホワイトシティー": "ホワイトシティ", "アントニオガウディ": "アントニオ・ガウディ",
              "ミニグロット": "ミニ通り池＆ホワイトロード", "トリプルスリー（３３３）": "トリプルスリー", "Ｌ字アーチ": "L字アーチ＆ワープホール",
              "白鳥崖下": "がけ下", "万座毛": "万座毛下"}
PADI_SKIP = {"デベソ"}  # 八重干瀬のデベソ1/2 と同じか分からない


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[（(].*?[)）]", "", s)
    return re.sub(r"[\s・\-－ー〜~/／]", "", s).lower()


VERTS = []
for el in COAST["elements"]:
    g = el.get("geometry") or []
    for i in range(len(g) - 1):
        VERTS.append((g[i]["lat"], g[i]["lon"], g[i + 1]["lat"], g[i + 1]["lon"]))


def seaward(lat, lon, push_km=0.12):
    """いちばん近い海岸線の線分の、陸側（OSM の海岸線は左が陸）にあれば海側へ押し出す。"""
    k = math.cos(math.radians(lat))
    best = None
    for a, b, c, d in VERTS:
        if abs(a - lat) > 0.05 or abs(b - lon) > 0.05:
            continue
        dx, dy = (d - b) * k, c - a
        L2 = dx * dx + dy * dy or 1e-12
        t = max(0, min(1, (((lon - b) * k) * dx + (lat - a) * dy) / L2))
        px, py = b * k + t * dx, a + t * dy
        dist = math.hypot(lon * k - px, lat - py)
        if best is None or dist < best[0]:
            best = (dist, a, b, c, d, px, py)
    if best is None:
        return lat, lon, False
    dist, a, b, c, d, px, py = best
    dx, dy = (d - b) * k, c - a
    cross = dx * (lat - a) - dy * ((lon - b) * k)  # >0 なら線の左（陸）
    if cross <= 0 and dist * 111 > 0.04:
        return lat, lon, False
    L = math.hypot(dx, dy) or 1
    nx, ny = dy / L, -dx / L  # 右手（海）
    s = push_km / 111.0
    return py + ny * s, (px + nx * s) / k, True


def on_land(lat, lon):
    n = 0
    for a, b, c, d in VERTS:
        if (b > lon) != (d > lon) and lat < a + (lon - b) * (c - a) / (d - b):
            n += 1
    return n % 2 == 1


def off_land(lat, lon):
    """陸の上なら、いちばん近い海岸線の外側へ出す。"""
    if not on_land(lat, lon):
        return lat, lon, False
    k = math.cos(math.radians(lat))
    a, b, c, d = min(VERTS, key=lambda v: (v[0] - lat) ** 2 + ((v[1] - lon) * k) ** 2)
    dx, dy = (d - b) * k, c - a
    L = math.hypot(dx, dy) or 1
    for km in (0.12, 0.25, 0.4):
        for sgn in (1, -1):
            s = km / 111.0 * sgn
            la, lo = a + (-dx / L) * s, b + (dy / L) * s / k
            if not on_land(la, lo):
                return la, lo, True
    return lat, lon, False


def in_bbox(la, lo):
    s, n, w, e = BBOX
    return la is not None and lo is not None and s <= la <= n and w <= lo <= e


def domain_name(u):
    h = urlparse(u).netloc.replace("www.", "")
    return h


REEF = {"miyako": (24.94, 25.07, 125.17, 125.36)}.get(SITE)
_cnt = {}
for _m in MUSE.values():
    _l = ((_m.get("data") or {}).get("location") or {})
    if _l.get("lat") is not None:
        _k = (round(_l["lat"], 3), round(_l.get("lng") or 0, 3))
        _cnt[_k] = _cnt.get(_k, 0) + 1


def coast_km(lat, lon):
    k = math.cos(math.radians(lat))
    return min((math.hypot((a - lat), (b - lon) * k) for a, b, c, d in VERTS), default=9) * 111


def has_coord_basis(loc):
    return bool(re.search(r"座標|緯度|経度|lat|°", (loc.get("basis") or "") + (loc.get("text") or ""), re.I))


def muse_ok(loc):
    """Muse の緯度経度を使ってよいか：範囲内・同じ値の使い回しでない・岸から離れすぎていない（八重干瀬は礁の範囲内）。"""
    la, lo = loc.get("lat"), loc.get("lng")
    if not in_bbox(la, lo) or _cnt.get((round(la, 3), round(lo, 3)), 0) > 1:
        return False
    if REEF and REEF[0] <= la <= REEF[1] and REEF[2] <= lo <= REEF[3]:
        return True
    return coast_km(la, lo) < 2.0


padi_by = {}
for x in PADI:
    if x["lat"] is None or x["name"] in PADI_SKIP:
        continue
    padi_by[norm(PADI_ALIAS.get(x["name"], x["name"]))] = x

drop = set(REVIEW.get("drop", []))
EXF = os.path.join(HERE, f"extras_{SITE}.json")
if os.path.exists(EXF):  # エリアの検索で見つかった、一覧になかったポイント
    for x in json.load(open(EXF, encoding="utf-8")):
        if x["name"] in drop:
            continue
        D["points"].append({"name": x["name"], "alias": x.get("alias", ""), "area": "（追加）", "features": x.get("features", ""),
                            "depth": x.get("depth") or "", "lat": None, "lng": None, "precision": "unknown", "position_note": "",
                            "sources": [], "media": [], "added": "web",
                            "_cand": [u for u in x.get("cand_sources", []) if u.startswith("http")]})
pts = []
for p in D["points"]:
    if p["name"] in drop:
        continue
    keys = [norm(p["name"])] + [norm(a) for a in re.split(r"[／/、]", p.get("alias") or "") if a]
    px = next((padi_by[k] for k in keys if k in padi_by), None)
    m = MUSE.get(p["name"], {})
    md = m.get("data") or {}
    loc = md.get("location") or {}
    p.pop("padi", None)
    # 位置
    if px and in_bbox(px["lat"], px["lng"]):
        p["lat"], p["lng"], p["precision"] = px["lat"], px["lng"], "source"
        p["position_note"] = "PADI"
    elif muse_ok(loc) and loc.get("status") in ("stated", "guess") and p["precision"] in ("area", "unknown"):
        p["lat"], p["lng"], p["precision"], p["position_note"] = loc["lat"], loc["lng"], "guess", loc.get("text") or ""
    if p["name"] in REVIEW.get("pos", {}):
        la, lo, prec, note = REVIEW["pos"][p["name"]]
        p["lat"], p["lng"], p["precision"], p["position_note"] = la, lo, prec, note
    if p.get("lat") is not None and p["precision"] != "unknown":
        la, lo, moved = seaward(p["lat"], p["lng"])
        la, lo, moved2 = off_land(la, lo)
        moved = moved or moved2
        p["lat"], p["lng"] = round(la, 5), round(lo, 5)
        if moved:
            p["nudged"] = True
    if p["name"] in REVIEW.get("area", {}):
        p["area"] = REVIEW["area"][p["name"]]
    p["location_text"] = loc.get("text") if loc.get("status") in ("stated", "guess") else None
    # 生き物（PADI の一覧＋ログ）
    cr = OrderedDict()
    for c in md.get("creatures") or []:
        n = (c.get("name") or "").strip()
        if n and n not in cr:
            cr[n] = c.get("season")
        elif n and c.get("season") and not cr.get(n):
            cr[n] = c.get("season")
    if px and px.get("fish"):
        for n in re.split(r"[、,，]", px["fish"]):
            n = n.strip()
            if n and n not in cr:
                cr[n] = None
    p["creatures"] = [{"name": n, "season": s} for n, s in list(cr.items())[:16]]
    cond = md.get("conditions") or {}
    p["conditions"] = {"wind": cond.get("wind"), "current": cond.get("current") or (px or {}).get("current") or None,
                       "level": cond.get("level") or (px or {}).get("level") or None, "access": (px or {}).get("access") or None}
    if px:
        p["padi"] = {"depth": px["depth"], "access": px["access"], "level": px["level"], "current": px["current"]}
    al = [a for a in md.get("aliases") or [] if a and a != p["name"] and a not in (p.get("alias") or "")]
    p["aliases_found"] = al[:4]
    # 出典
    src = [s for s in p["sources"] if s.get("key") != "PADI2" and s.get("kind") != "web"]
    if px and not any(s["url"] == PADI_URL for s in src):
        src.append({"key": "PADI2", "name": "PADI ダイビングスポット情報", "url": PADI_URL})
    seen = set(s["url"] for s in src)
    web = []
    for u in (md.get("sources") or []) + [c["url"] for c in m.get("citations") or [] if c.get("url")]:
        if not u or u in seen or not u.startswith("http") or "wikipedia" in u:
            continue
        seen.add(u)
        web.append({"kind": "web", "name": domain_name(u), "url": u})
    for u in p.pop("_cand", []):
        if u not in seen:
            seen.add(u); web.insert(0, {"kind": "web", "name": domain_name(u), "url": u})
    p["sources"] = src
    p["web_sources"] = web[:6]
    p["scope"] = {"in": md.get("in_scope"), "note": md.get("scope_note")}
    pts.append(p)

# 追加したポイントのエリアは、いちばん近い既存のポイントのエリアにする
for p in pts:
    if p["name"] in REVIEW.get("area", {}):
        p["area"] = REVIEW["area"][p["name"]]
    if p["area"] == "（追加）":
        if p.get("lat") is None:
            p["area"] = "（位置不明）"
        else:
            q = min((q for q in pts if q["area"] not in ("（追加）", "（位置不明）") and q.get("lat") is not None),
                    key=lambda q: (q["lat"] - p["lat"]) ** 2 + (q["lng"] - p["lng"]) ** 2)
            p["area"] = q["area"]
# PADI にあって一覧にないもの・レビューで足すもの
have = set(norm(x) for p in pts for x in [p["name"]] + re.split(r"[／/、]", p.get("alias") or ""))
for k, x in padi_by.items():
    if k in have or not in_bbox(x["lat"], x["lng"]):
        continue
    la, lo, _ = seaward(x["lat"], x["lng"])
    area = REVIEW.get("padi_area", {}).get(x["name"]) or min(
        pts, key=lambda q: (q["lat"] - x["lat"]) ** 2 + (q["lng"] - x["lng"]) ** 2 if q.get("lat") is not None else 9)["area"]
    pts.append({"name": x["name"], "alias": "", "area": area, "features": "", "depth": x["depth"], "lat": round(la, 5), "lng": round(lo, 5),
                "precision": "source", "position_note": "PADI", "sources": [{"key": "PADI2", "name": "PADI ダイビングスポット情報", "url": PADI_URL}],
                "creatures": [{"name": n.strip(), "season": None} for n in re.split(r"[、,，]", x.get("fish") or "") if n.strip()][:16],
                "conditions": {"wind": None, "current": x["current"] or None, "level": x["level"] or None, "access": x["access"] or None},
                "padi": {"depth": x["depth"], "access": x["access"], "level": x["level"], "current": x["current"]},
                "web_sources": [], "aliases_found": [], "added": "PADI", "media": []})
for x in REVIEW.get("add", []):
    if norm(x["name"]) in have:
        continue
    la, lo, _ = seaward(x["lat"], x["lng"]) if x.get("lat") is not None else (None, None, False)
    pts.append({"name": x["name"], "alias": x.get("alias", ""), "area": x["area"], "features": x.get("features", ""), "depth": x.get("depth") or "",
                "lat": None if la is None else round(la, 5), "lng": None if lo is None else round(lo, 5),
                "precision": x.get("precision", "log"), "position_note": x.get("where", ""), "location_text": x.get("where"),
                "sources": [], "web_sources": [{"kind": "web", "name": domain_name(u), "url": u} for u in x.get("sources", [])][:6],
                "creatures": [], "conditions": {}, "aliases_found": [], "added": "web", "media": []})

# 第1版の解説は捨てる。第2版で作った解説は残す（REGEN=1 で作り直し）
cur = json.load(open(P, encoding="utf-8"))
keep = {} if os.environ.get("REGEN") or cur.get("version") != 2 else {q["name"]: q for q in cur["points"] if q.get("commentary_ja")}
for p in pts:
    for k in ("commentary_ja", "commentary_en", "commentary_model"):
        p.pop(k, None)
        if p["name"] in keep:
            p[k] = keep[p["name"]].get(k)
D["points"] = pts
am = D.get("area_media") or {}
pool = []
for v in am.values():
    for m in v:
        if m["src"] not in [x["src"] for x in pool]:
            pool.append(m)
for a in set(p["area"] for p in pts):
    if not am.get(a):
        am[a] = pool[:6]
D["area_media"] = {a: am[a] for a in sorted(set(p["area"] for p in pts))}
D["dropped"] = [{"name": n, "note": REVIEW.get("drop_note", {}).get(n, "")} for n in REVIEW.get("drop", [])]
D["version"] = 2
json.dump(D, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(SITE, len(pts), Counter(p["precision"] for p in pts), "nudged", sum(1 for p in pts if p.get("nudged")),
      "added", sum(1 for p in pts if p.get("added")))
