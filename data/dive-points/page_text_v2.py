# -*- coding: utf-8 -*-
"""ポイントマップのページ文言（このページについて＋位置の注記）を入れる。選び方の段落は「このページについて」にまとめた。"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXTRA = {"chichijima": ("Keta islands not included. ", "ケータ列島は含めていません。"),
         "miyako": ("", ""), "manza": ("", "")}
NOTE = '''<p class="dp-note"><span data-lang="en">Positions are approximate. Solid circles use the coordinates on PADI’s dive-spot page or sit beside a named cape, beach or islet; dashed circles are rough positions guessed from shop logs, or simply placed in the area. Not for navigation or dive planning.</span><span data-lang="ja">位置は目安です。実線の丸は PADI のスポット情報の座標か、名前のある岬・浜・島のそばに置いたもの、点線の丸はショップのログから推測した目安か、エリアの中に置いただけのものです。航行や潜水計画には使えません。</span></p>'''

for site in sys.argv[1:]:
    d = json.load(open(os.path.join(ROOT, "data", "dive-points", f"{site}.json"), encoding="utf-8"))
    n = len(d["points"])
    xe, xj = EXTRA[site]
    about = (f'<div class="dp-about"><span data-lang="en"><b>About this page.</b> An AI (Claude) compiled {n} sites from dive shops’ pages, '
             f'PADI’s coordinates and dive logs found by web search (Meta’s Muse Spark); sources are under each site. {xe}Nothing was checked on site, '
             f'so positions, names and depths may be off and some sites may be missing or duplicated. Confirm plans with a local shop.</span>'
             f'<span data-lang="ja"><b>このページについて：</b>ショップのページに載っていたポイント名を集め、PADI の座標と、Web検索（Meta の Muse Spark）で見つけたダイビングログで補って、'
             f'生成AI（Claude）が{n}か所にまとめました。出典は各ポイントに載せています。{xj}現地では確かめていないため、位置・名前・水深の違いや、抜け・重複があります。'
             f'計画は現地のショップで確かめてください。</span></div>')
    f = os.path.join(ROOT, "dive", f"{site}.html")
    s = open(f, encoding="utf-8").read()
    s = re.sub(r'<div class="dp-about">.*?</div>', about, s, count=1, flags=re.S)
    s = re.sub(r'\s*<p class="dp-how">.*?</p>', '', s, count=1, flags=re.S)
    s = re.sub(r'<p class="dp-note">.*?</p>', NOTE, s, count=1, flags=re.S)
    open(f, "w", encoding="utf-8").write(s)
    print(site, n)
