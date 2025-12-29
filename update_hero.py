#!/usr/bin/env python3
"""ヒーローセクションをインパクト重視に変更"""

import re

# ファイル読み込み
with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 旧ヒーローセクション
old_hero = '''            <!-- Hero Visual -->
            <section class="hero-visual">
                <div class="hero-visual-content">
                    <h1 data-lang="en">Dive into data.</h1>
                    <h1 data-lang="ja">潜る海を、知る</h1>
                    
                    <div class="hero-visual-text" data-lang="en">
                        <p>In 2024, I saw coral bleaching in Okinawa with my own eyes. I had known the data before. It never moved me. Seeing it did.</p>
                        <p>I am a physician, not a marine scientist. But I dive over a hundred times a year. Divers feel the change—warmer water, fewer fish, whiter coral. Yet these observations stay unrecorded, unshared.</p>
                        <p>MarineObservations exists to change that: to document what is happening in the waters where I dive, and to make it visible to others.</p>
                    </div>
                    
                    <div class="hero-visual-text" data-lang="ja">
                        <p>転機は2024年、沖縄で目にしたサンゴの白化だった。地元の人々が長年かけて養殖してきたサンゴが、ほぼ全滅していた。地球温暖化はどこか遠い政治の話だと思っていたが、目の前の光景がその認識を覆した。</p>
                        <p>本業は医師であり、海洋の専門家ではない。ただ、年間100本以上潜るダイバーとして、変化を肌で感じている。その感覚を言葉にし、記録し、データとして残すことで、何かが生まれる可能性を信じている。</p>
                    </div>
                    
                    <div class="hero-visual-links">
                        <a href="#" class="hero-visual-link" onclick="showPage('about'); return false;">
                            <span data-lang="en">About this project</span>
                            <span data-lang="ja">このプロジェクトについて</span>
                        </a>
                        <span class="hero-link-sep">|</span>
                        <a href="#" class="hero-visual-link" onclick="showPage('divers'); return false;">
                            <span data-lang="en">For Divers</span>
                            <span data-lang="ja">ダイバー向け情報</span>
                        </a>
                    </div>
                    
                    <p class="hero-visual-signature" data-lang="en">
                        A project by a physician and diver, documenting ocean conditions from outside formal expertise.
                    </p>
                    <p class="hero-visual-signature" data-lang="ja">
                        医師・ダイバーが、専門外の立場から海洋環境の観察と発信に取り組むプロジェクト。
                    </p>
                </div>
                
                <div class="scroll-indicator">
                    <span data-lang="en">Scroll for data</span>
                    <span data-lang="ja">スクロールでデータへ</span>
                    ↓
                </div>
            </section>'''

# 新ヒーローセクション
new_hero = '''            <!-- Hero Visual - Impact Version -->
            <section class="hero-visual hero-impact">
                <div class="hero-visual-content hero-centered">
                    <h1 class="hero-tagline" data-lang="en">Coral cannot speak.<br><span class="hero-tagline-sub">So we dive.</span></h1>
                    <h1 class="hero-tagline" data-lang="ja">サンゴは声を出せない。<br><span class="hero-tagline-sub">だから私たちが潜る。</span></h1>
                    
                    <div class="hero-cta-buttons">
                        <a href="#" class="hero-btn hero-btn-primary" onclick="showPage('divers'); return false;">
                            <span data-lang="en">Start Observing</span>
                            <span data-lang="ja">観察をはじめる</span>
                        </a>
                        <a href="#" class="hero-btn hero-btn-secondary" onclick="showPage('about'); return false;">
                            <span data-lang="en">About This Project</span>
                            <span data-lang="ja">このプロジェクトについて</span>
                        </a>
                    </div>
                </div>
                
                <div class="scroll-indicator">
                    <span data-lang="en">Scroll for data</span>
                    <span data-lang="ja">スクロールでデータへ</span>
                    ↓
                </div>
            </section>'''

# 置換
html = html.replace(old_hero, new_hero)

# 新しいCSS（hero-impact用）
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

# CSS追加（</style>の直前に挿入）
html = html.replace('</style>', new_css + '</style>')

# 保存
with open('/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ ヒーローセクションを更新しました")
