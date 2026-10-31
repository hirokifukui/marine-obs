# -*- coding: utf-8 -*-
"""第2版のページ文言（このページについて・選び方・位置の注記）を各ページに入れる。"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ABOUT = '''<div class="dp-about"><span data-lang="en"><b>About this page.</b> An AI (Claude) compiled this from dive shops’ pages, PADI’s dive-spot page and dive logs found by web search (Meta’s Muse Spark). Nothing was checked on site, and positions, names and depths can differ from reality. Use it as a rough overview and confirm plans with a local shop.</span><span data-lang="ja"><b>このページについて：</b>ショップの公開ページ、PADI のスポット情報、Web検索（Meta の Muse Spark）で見つけたダイビングログを、生成AI（Claude）がまとめた参考資料です。現地では確かめていません。位置・名前・水深は実際と違うことがあるので、見取り図として使い、計画は現地のショップで確かめてください。</span></div>'''
NOTE = '''<p class="dp-note"><span data-lang="en">Positions are approximate. Solid circles use the coordinates on PADI’s dive-spot page or sit beside a named cape, beach or islet; dashed circles are rough positions guessed from shop logs, or simply placed in the area. Even solid ones can be off from the actual spot. Not for navigation or dive planning.</span><span data-lang="ja">位置は目安です。実線の丸は PADI のスポット情報の座標か、名前のある岬・浜・島のそばに置いたもの、点線の丸はショップのログから推測した目安か、エリアの中に置いただけのものです。実線でも実際の場所とはずれることがあります。航行や潜水計画には使えません。</span></p>'''
HOW = {
    "miyako": ("names from nine dive-shop and guide pages, plus {added} more found on PADI or in logs — {n} sites in all. Shops name and divide sites differently, so some are missing or duplicated, and many Yabiji (Yaebishi) sites are names only. Sources are listed under each site.",
               "ショップ・ガイドのページ9つに載っていた名前に、PADI やログで見つかった{added}か所を足して、{n}か所にしました。呼び名や区切り方はショップで違うため、抜けや重複があります。八重干瀬の多くは名前くらいしか分かっていません。出典は各ポイントに載せています。"),
    "manza": ("names from six pages of shops that run boats to Manza, plus {added} more found on PADI or in logs — {n} sites from Onna to Afuso. Shops name and divide sites differently, so some are missing or duplicated. Sources are listed under each site.",
              "万座にボートを出すショップのページ6つに載っていた名前に、PADI やログで見つかった{added}か所を足して、恩納から安富祖までの{n}か所にしました。呼び名や区切り方はショップで違うため、抜けや重複があります。出典は各ポイントに載せています。"),
    "chichijima": ("names from six dive-shop, guide and travel pages, plus {added} more found in logs — {n} sites around Chichijima, Anijima, Nishijima, Ototojima and Minamijima (the Keta islands are left out). Shops name and divide sites differently, so some are missing or duplicated. Sources are listed under each site.",
                   "ショップ・ガイド・旅行サイトのページ6つに載っていた名前に、ログで見つかった{added}か所を足して、父島・兄島・西島・弟島・南島まわりの{n}か所にしました（ケータ列島は含めていません）。呼び名や区切り方はショップで違うため、抜けや重複があります。出典は各ポイントに載せています。"),
}

for site in sys.argv[1:]:
    d = json.load(open(os.path.join(ROOT, "data", "dive-points", f"{site}.json"), encoding="utf-8"))
    n = len(d["points"])
    added = sum(1 for p in d["points"] if p.get("added"))
    en, ja = HOW[site]
    en = en.format(n=n, added=added)
    ja = ja.format(n=n, added=added)
    how = f'<p class="dp-how"><span data-lang="en"><b>How the sites were chosen:</b> {en}</span><span data-lang="ja"><b>ポイントの選び方：</b>{ja}</span></p>'
    f = os.path.join(ROOT, "dive", f"{site}.html")
    s = open(f, encoding="utf-8").read()
    s = re.sub(r'<div class="dp-about">.*?</div>', ABOUT, s, count=1, flags=re.S)
    s = re.sub(r'<p class="dp-how">.*?</p>', how, s, count=1, flags=re.S)
    s = re.sub(r'<p class="dp-note">.*?</p>', NOTE, s, count=1, flags=re.S)
    open(f, "w", encoding="utf-8").write(s)
    print(site, n, "added", added)
