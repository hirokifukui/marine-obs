#!/usr/bin/env python3
"""ヒーローのレイアウトを調整：コピー上、ボタン下"""

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# hero-centeredにjustify-content: space-betweenを適用し、
# コピーとボタンを分離する

old_centered = '''.hero-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 900px;
    padding: 0 2rem;
}'''

new_centered = '''.hero-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    max-width: 900px;
    padding: 0 2rem;
    height: 70vh;
    padding-top: 15vh;
}'''

html = html.replace(old_centered, new_centered)

# ボタンを下に固定
old_buttons = '''.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 2rem;
}'''

new_buttons = '''.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: auto;
    padding-bottom: 5vh;
}'''

html = html.replace(old_buttons, new_buttons)

# margin-bottomを戻す（autoで制御するため）
html = html.replace('margin-bottom: 8rem;', 'margin-bottom: 2rem;')

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ レイアウト調整完了")
print("  - コピー: 上寄せ（padding-top: 15vh）")
print("  - ボタン: 下寄せ（margin-top: auto）")
