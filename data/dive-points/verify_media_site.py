# -*- coding: utf-8 -*-
"""ポイント名で見つけた写真のうち、説明・タグ・撮影地に宮古まわりの地名がないものを外す。"""
import json, re
import enrich_site as E

KEY = re.compile(r"恩納|onna|万座|manza|瀬良垣|seragaki|安富祖|名嘉真|宮古|miyako|伊良部|irabu|下地|shimoji|池間|ikema|来間|kurima|八重干瀬|yabiji|佐良浜|通り池|tooriike|toriike|吉野|yoshino|新城|aragusuku|保良|hora|狩俣|karimata|父島|chichi|小笠原|ogasawara|bonin|二見|futami|兄島|anijima|南島|minamijima|弟島|ototojima", re.I)


def ok(m):
    if m.get("via") != "Flickr":
        return bool(KEY.search(m.get("title", "") + m.get("page", "")))
    pid = m["page"].rstrip("/").split("/")[-1]
    try:
        info = E.flickr("flickr.photos.getInfo", photo_id=pid)["photo"]
    except Exception:
        return False
    text = " ".join([info.get("title", {}).get("_content", ""), info.get("description", {}).get("_content", ""),
                     " ".join(t.get("raw", "") for t in info.get("tags", {}).get("tag", []))])
    loc = info.get("location") or {}
    text += " " + " ".join(str((loc.get(k) or {}).get("_content", "")) for k in ("locality", "county", "region", "neighbourhood"))
    try:
        la, lo = float(loc.get("latitude", 0)), float(loc.get("longitude", 0))
        if (24.6 <= la <= 25.1 and 125.0 <= lo <= 125.6) or (26.43 <= la <= 26.56 and 127.78 <= lo <= 127.95) or (26.95 <= la <= 27.25 and 142.05 <= lo <= 142.35):
            return True
    except Exception:
        pass
    return bool(KEY.search(text))


if __name__ == "__main__":
    D = json.load(open(E.P, encoding="utf-8"))
    for p in D["points"]:
        keep = [m for m in p.get("media", []) if ok(m)]
        seen, uniq = set(), []
        for m in keep:
            if m["src"] not in seen:
                seen.add(m["src"]); uniq.append(m)
        if len(uniq) != len(p.get("media", [])):
            print(p["name"], len(p.get("media", [])), "->", len(uniq))
        p["media"] = uniq
    for a, ms in (D.get("area_media") or {}).items():
        keep = [m for m in ms if ok(m)]
        print("area", a, len(ms), "->", len(keep))
        D["area_media"][a] = keep
    json.dump(D, open(E.P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
