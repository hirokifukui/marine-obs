#!/usr/bin/env python3
"""ヒーロー構造を3分割に変更（space-between方式）"""

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. HTML構造を変更：空のheaderを追加、ボタンをfooterに
old_html = '''            <section class="hero-visual hero-impact">
                <div class="hero-visual-content hero-centered">
                    <h1 class="hero-tagline" data-lang="en">Coral cannot speak.<span class="hero-tagline-sub">So we dive.</span></h1>
                    <h1 class="hero-tagline" data-lang="ja">サンゴは声を出せない。<span class="hero-tagline-sub">だから私たちが潜る。</span></h1>
                    
                    <div class="hero-cta-buttons">
                        <a href="#" class="hero-btn hero-btn-primary" onclick="showPage('divers'); return false;">
                            <span data-lang="en">For Divers</span>
                            <span data-lang="ja">ダイバー向け情報</span>
                        </a>
                        <a href="#" class="hero-btn hero-btn-secondary" onclick="showPage('about'); return false;">
                            <span data-lang="en">About This Project</span>
                            <span data-lang="ja">このプロジェクトについて</span>
                        </a>
                    </div>
                </div>
                

            </section>'''

new_html = '''            <section class="hero-visual hero-impact">
                <div class="hero-spacer"></div>
                
                <div class="hero-body">
                    <h1 class="hero-tagline" data-lang="en">Coral cannot speak.<span class="hero-tagline-sub">So we dive.</span></h1>
                    <h1 class="hero-tagline" data-lang="ja">サンゴは声を出せない。<span class="hero-tagline-sub">だから私たちが潜る。</span></h1>
                </div>
                
                <div class="hero-footer">
                    <a href="#" class="hero-btn hero-btn-primary" onclick="showPage('divers'); return false;">
                        <span data-lang="en">For Divers</span>
                        <span data-lang="ja">ダイバー向け情報</span>
                    </a>
                    <a href="#" class="hero-btn hero-btn-secondary" onclick="showPage('about'); return false;">
                        <span data-lang="en">About This Project</span>
                        <span data-lang="ja">このプロジェクトについて</span>
                    </a>
                </div>
            </section>'''

html = html.replace(old_html, new_html)

# 2. CSSを完全に書き換え
old_css = '''/* Hero Impact Version */
.hero-impact {
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(
        180deg,
        rgba(26, 32, 46, 0.7) 0%,
        rgba(26, 32, 46, 0.5) 50%,
        rgba(26, 32, 46, 0.7) 100%
    ), url('hero.jpg');
    background-size: cover;
    background-position: center;
}

.hero-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    max-width: 900px;
    padding: 0 2rem;
    height: 70vh;
    padding-top: 15vh;
}'''

new_css = '''/* Hero Impact Version */
.hero-impact {
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    text-align: center;
    background: linear-gradient(
        180deg,
        rgba(26, 32, 46, 0.7) 0%,
        rgba(26, 32, 46, 0.5) 50%,
        rgba(26, 32, 46, 0.7) 100%
    ), url('hero.jpg');
    background-size: cover;
    background-position: center;
    padding: 2rem;
}

.hero-spacer {
    height: 5vh;
}

.hero-body {
    display: flex;
    flex-direction: column;
    align-items: center;
    max-width: 900px;
}

.hero-footer {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    justify-content: center;
    padding-bottom: 3vh;
}'''

html = html.replace(old_css, new_css)

# 3. 不要になった.hero-cta-buttons関連CSSを削除・置換
old_cta = '''.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: auto;
    padding-bottom: 5vh;
}'''

html = html.replace(old_cta, '')

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ ヒーロー構造を3分割に変更")
print("  - hero-spacer: 上部スペーサー")
print("  - hero-body: タグライン（中央）")
print("  - hero-footer: ボタン（下部固定）")
print("  - justify-content: space-between で配置")
