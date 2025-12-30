#!/usr/bin/env python3
"""ヒーローセクションの見栄え改善"""

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 改行位置の修正（日本語: 句点で改行）
old_tagline_ja = '''<h1 class="hero-tagline" data-lang="ja">サンゴは声を出せない。<br><span class="hero-tagline-sub">だから私たちが潜る。</span></h1>'''
new_tagline_ja = '''<h1 class="hero-tagline" data-lang="ja">サンゴは声を出せない。<span class="hero-tagline-sub">だから私たちが潜る。</span></h1>'''

html = html.replace(old_tagline_ja, new_tagline_ja)

# 英語も同様に調整
old_tagline_en = '''<h1 class="hero-tagline" data-lang="en">Coral cannot speak.<br><span class="hero-tagline-sub">So we dive.</span></h1>'''
new_tagline_en = '''<h1 class="hero-tagline" data-lang="en">Coral cannot speak.<span class="hero-tagline-sub">So we dive.</span></h1>'''

html = html.replace(old_tagline_en, new_tagline_en)

# 2. CSS改善：ティールを白に変更、ボタンのコントラスト強化
old_css = '''
/* Hero Impact Version */
.hero-impact {
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(
        180deg,
        rgba(26, 32, 46, 0.75) 0%,
        rgba(26, 32, 46, 0.6) 50%,
        rgba(26, 32, 46, 0.75) 100%
    ), url('hero.jpg');
    background-size: cover;
    background-position: center;
}

.hero-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 900px;
    padding: 0 2rem;
}

.hero-tagline {
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: #ffffff;
    text-shadow: 0 4px 30px rgba(0,0,0,0.4);
    margin-bottom: 3rem;
}

body.ja .hero-tagline {
    font-size: 3rem;
    letter-spacing: 0.08em;
    line-height: 1.4;
}

.hero-tagline-sub {
    display: block;
    margin-top: 0.5rem;
    color: #5b9a94;
}

.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
}

.hero-btn {
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    min-width: 180px;
    text-align: center;
}

.hero-btn-primary {
    background: linear-gradient(135deg, #5b9a94 0%, #3d7a73 100%);
    color: #ffffff;
    box-shadow: 0 4px 20px rgba(91, 154, 148, 0.4);
}

.hero-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(91, 154, 148, 0.5);
}

.hero-btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(4px);
}

.hero-btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 768px) {
    .hero-tagline {
        font-size: 2.2rem;
    }
    body.ja .hero-tagline {
        font-size: 2rem;
    }
    .hero-btn {
        min-width: 160px;
        padding: 0.875rem 1.5rem;
        font-size: 0.95rem;
    }
    .hero-cta-buttons {
        flex-direction: column;
        width: 100%;
        max-width: 280px;
    }
}

'''

new_css = '''
/* Hero Impact Version */
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
    justify-content: center;
    max-width: 900px;
    padding: 0 2rem;
}

.hero-tagline {
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.3;
    color: #ffffff;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
    margin-bottom: 3rem;
}

body.ja .hero-tagline {
    font-size: 2.4rem;
    letter-spacing: 0.05em;
    line-height: 1.5;
}

.hero-tagline-sub {
    display: block;
    margin-top: 0.75rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
    font-style: italic;
}

body.ja .hero-tagline-sub {
    font-style: normal;
    font-weight: 400;
    letter-spacing: 0.1em;
}

.hero-cta-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
}

.hero-btn {
    padding: 1rem 2.5rem;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    min-width: 200px;
    text-align: center;
}

.hero-btn-primary {
    background: #ffffff;
    color: #1a202c;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.hero-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    background: #f0f0f0;
}

.hero-btn-secondary {
    background: transparent;
    color: rgba(255, 255, 255, 0.8);
    border: none;
    font-weight: 500;
    text-decoration: underline;
    text-underline-offset: 4px;
    min-width: auto;
    padding: 0.75rem 1rem;
}

.hero-btn-secondary:hover {
    color: #ffffff;
}

@media (max-width: 768px) {
    .hero-tagline {
        font-size: 2rem;
    }
    body.ja .hero-tagline {
        font-size: 1.75rem;
    }
    .hero-btn {
        min-width: 180px;
        padding: 0.875rem 2rem;
        font-size: 0.95rem;
    }
    .hero-btn-secondary {
        min-width: auto;
    }
    .hero-cta-buttons {
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
    }
}

'''

html = html.replace(old_css, new_css)

with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ ヒーローの見栄えを改善しました")
print("  - 改行位置: 句点後に自然改行")
print("  - 2行目: 白系 + イタリックで上品に")
print("  - ボタン: Primaryを白背景で目立たせ、Secondaryはテキストリンク風に")
