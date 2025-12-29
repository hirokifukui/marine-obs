#!/usr/bin/env python3
"""ボタンをPC版は右下、モバイルは中央下に"""

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# hero-footerを右寄せに変更
old_footer = '''.hero-footer {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    justify-content: center;
    padding-bottom: 3vh;
}'''

new_footer = '''.hero-footer {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: flex-end;
    padding-bottom: 2vh;
    padding-right: 3vw;
    width: 100%;
}'''

html = html.replace(old_footer, new_footer)

# モバイル用のメディアクエリを追加（既存の@mediaの前に）
old_media = '''@media (max-width: 768px) {
    .hero-tagline {
        font-size: 2rem;
    }
    body.ja .hero-tagline {
        font-size: 1.75rem;
    }'''

new_media = '''@media (max-width: 768px) {
    .hero-footer {
        justify-content: center;
        padding-right: 0;
        padding-bottom: 3vh;
    }
    .hero-tagline {
        font-size: 2rem;
    }
    body.ja .hero-tagline {
        font-size: 1.75rem;
    }'''

html = html.replace(old_media, new_media)

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ PC: 右下配置、モバイル: 中央下配置")
