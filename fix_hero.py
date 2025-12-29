#!/usr/bin/env python3
import re

# Read file
with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find and replace the hero section
old_hero = '''            <section class="hero">
                <h1 data-lang="en">Dive into data.</h1>
                <h1 data-lang="ja">潜る海を、知る</h1>
                
                <p class="hero-subtitle" data-lang="en">
                    Tracking coral reef environments through satellite and field observations.
                </p>
                <p class="hero-subtitle" data-lang="ja">
                    海水温、熱ストレス、海況。衛星データと現地情報で、サンゴ礁の変化を記録しています。
                </p>
            </section>'''

new_hero = '''            <!-- Hero Visual -->
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
                    
                    <a href="#" class="hero-visual-link" onclick="showPage('about'); return false;">
                        <span data-lang="en">Read the full story</span>
                        <span data-lang="ja">詳しく見る</span>
                        →
                    </a>
                    
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

content = content.replace(old_hero, new_hero)

# Write back
with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Hero section replaced successfully!")
