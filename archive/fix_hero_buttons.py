#!/usr/bin/env python3
"""ボタン位置を下げ、スクロールインジケーターを削除"""

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. スクロールインジケーターを削除
old_scroll = '''                <div class="scroll-indicator">
                    <span data-lang="en">Scroll for data</span>
                    <span data-lang="ja">スクロールでデータへ</span>
                    ↓
                </div>'''

html = html.replace(old_scroll, '')

# 2. CSSでボタンの位置を調整（margin-topを増やす）
old_css_buttons = '''.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
}'''

new_css_buttons = '''.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 2rem;
}'''

html = html.replace(old_css_buttons, new_css_buttons)

# 3. タグラインのmargin-bottomも調整
old_margin = '''    margin-bottom: 3rem;
}

body.ja .hero-tagline {'''

new_margin = '''    margin-bottom: 4rem;
}

body.ja .hero-tagline {'''

html = html.replace(old_margin, new_margin)

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 修正完了")
print("  - スクロールインジケーター: 削除")
print("  - ボタン位置: 下げ（margin調整）")
