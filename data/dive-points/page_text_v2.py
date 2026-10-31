# -*- coding: utf-8 -*-
"""第2版のページ文言（このページについて・選び方・位置の注記）を各ページに入れる。"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ABOUT = '''<div class="dp-about"><span data-lang="en"><b>About this page.</b> An AI (Claude) compiled this from dive shops’ public pages and dive logs found by web search; nothing was checked on site. Positions can be off, and names, depths and features vary between shops or may be dated, so it can differ a lot from reality. Use it as a rough overview and confirm sites and plans with a local shop.</span><span data-lang="ja"><b>このページについて：</b>ショップやガイドの公開情報と、Web検索で見つけたダイビングログを、生成AI（Claude）が自動でまとめた参考資料で、現地では確かめていません。位置はずれていることがあり、名前・水深・特徴もショップで違ったり古かったりして、実際とはかなり違うところがあります。見取り図として使い、ポイントと計画は現地のショップで確かめてください。</span></div>'''
NOTE = '''<p class="dp-note"><span data-lang="en">Positions are approximate. Solid circles use the coordinates on PADI’s dive-spot page or sit beside a named cape, beach or islet; dashed circles are rough positions guessed from shop logs, or simply placed in the area. Even solid ones can be off from the actual spot. Not for navigation or dive planning.</span><span data-lang="ja">位置は目安です。実線の丸は PADI のスポット情報の座標か、名前のある岬・浜・島のそばに置いたもの、点線の丸はショップのログから推測した目安か、エリアの中に置いただけのものです。実線でも実際の場所とはずれることがあります。航行や潜水計画には使えません。</span></p>'''
HOW = {
    "miyako": ("we collected the names listed on nine public pages of Miyako dive shops and guides, merged obvious aliases{added_en}, and ended with {n} sites. For each site, Meta’s Muse Spark searched the web — mainly shop logs and dive blogs — for its location, the creatures mentioned and the conditions it is dived in; positions also use the coordinates on PADI’s dive-spot page. Sources are listed under each site. Shops name and divide sites differently, so some places may be missing or duplicated; many Yabiji (Yaebishi) sites are still names only.",
               "宮古島のダイビングショップ・ガイドが公開しているページ9つに載っていた名前を集め、明らかな別名をまとめて{added_ja}、{n}か所にしました。そのうえで、ポイントごとに Meta の Muse Spark にWeb検索をさせ、ショップのログやダイビングブログから、場所・出てくる生き物・潜る条件を拾いました。位置には PADI のスポット情報の座標も使っています。出典は各ポイントに載せています。ショップによって呼び名や区切り方が違うため、載っていないポイントや二重になっているポイントがあります。八重干瀬の多くは、まだ名前くらいしか分かっていません。"),
    "manza": ("we collected the names listed on six public pages of dive shops and guides that run boats to Manza, merged obvious aliases{added_en}, and ended with {n} sites from Onna to Afuso. For each site, Meta’s Muse Spark searched the web — mainly shop logs and dive blogs — for its location, the creatures mentioned and the conditions it is dived in; positions also use the coordinates on PADI’s dive-spot page. Sources are listed under each site. Shops name and divide sites differently, so some places may be missing or duplicated.",
              "万座にボートを出すショップ・ガイドが公開しているページ6つに載っていた名前を集め、明らかな別名をまとめて{added_ja}、恩納から安富祖までの{n}か所にしました。そのうえで、ポイントごとに Meta の Muse Spark にWeb検索をさせ、ショップのログやダイビングブログから、場所・出てくる生き物・潜る条件を拾いました。位置には PADI のスポット情報の座標も使っています。出典は各ポイントに載せています。ショップによって呼び名や区切り方が違うため、載っていないポイントや二重になっているポイントがあります。"),
    "chichijima": ("we collected the names listed on six public pages of Ogasawara dive shops, guides and dive-travel sites, merged obvious aliases{added_en}, and kept {n} sites around Chichijima, Anijima, Nishijima, Ototojima and Minamijima (the Keta / Mukojima islands are left out). For each site, Meta’s Muse Spark searched the web — mainly shop logs and dive blogs — for its location, the creatures mentioned and the conditions it is dived in; positions also use the coordinates on PADI’s dive-spot page. Sources are listed under each site. Shops name and divide sites differently, so some places may be missing or duplicated.",
                   "小笠原のダイビングショップ・ガイド・旅行サイトが公開しているページ6つに載っていた名前を集め、明らかな別名をまとめて{added_ja}、父島・兄島・西島・弟島・南島まわりの{n}か所にしました（ケータ列島は入れていません）。そのうえで、ポイントごとに Meta の Muse Spark にWeb検索をさせ、ショップのログやダイビングブログから、場所・出てくる生き物・潜る条件を拾いました。位置には PADI のスポット情報の座標も使っています。出典は各ポイントに載せています。ショップによって呼び名や区切り方が違うため、載っていないポイントや二重になっているポイントがあります。"),
}

for site in sys.argv[1:]:
    d = json.load(open(os.path.join(ROOT, "data", "dive-points", f"{site}.json"), encoding="utf-8"))
    n = len(d["points"])
    added = sum(1 for p in d["points"] if p.get("added"))
    en, ja = HOW[site]
    en = en.format(n=n, added_en=f", added {added} sites found on PADI or in logs" if added else "")
    ja = ja.format(n=n, added_ja=f"、PADI やログで見つかった{added}か所を足して" if added else "")
    how = f'<p class="dp-how"><span data-lang="en"><b>How the sites were chosen:</b> {en}</span><span data-lang="ja"><b>ポイントの選び方：</b>{ja}</span></p>'
    f = os.path.join(ROOT, "dive", f"{site}.html")
    s = open(f, encoding="utf-8").read()
    s = re.sub(r'<div class="dp-about">.*?</div>', ABOUT, s, count=1, flags=re.S)
    s = re.sub(r'<p class="dp-how">.*?</p>', how, s, count=1, flags=re.S)
    s = re.sub(r'<p class="dp-note">.*?</p>', NOTE, s, count=1, flags=re.S)
    open(f, "w", encoding="utf-8").write(s)
    print(site, n, "added", added)
