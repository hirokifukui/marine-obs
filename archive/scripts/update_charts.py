#!/usr/bin/env python3
"""index.htmlのチャートセクションをcanvas要素に置き換え"""

import re

input_file = '/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html'

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 旧チャートセクション（SVG）
old_chart_section = '''            <section class="chart-grid">
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Annual Peak DHW</span>
                            <span data-lang="ja">年間最大DHW</span>
                        </div>
                        <div class="chart-subtitle">
                            <span data-lang="en">Degree Heating Weeks · Sesoko & Manza</span>
                            <span data-lang="ja">熱ストレス指標 · 瀬底・万座</span>
                        </div>
                    </div>
                    <div class="chart-container">
                        <svg class="chart-svg" viewBox="0 0 400 160" preserveAspectRatio="xMidYMid meet">
                            <g class="chart-grid-lines">
                                <line class="chart-grid-line" x1="40" y1="20" x2="380" y2="20" />
                                <line class="chart-grid-line" x1="40" y1="55" x2="380" y2="55" />
                                <line class="chart-grid-line" x1="40" y1="90" x2="380" y2="90" />
                                <line class="chart-grid-line" x1="40" y1="125" x2="380" y2="125" />
                            </g>
                            <text class="chart-label" x="35" y="24" text-anchor="end">12</text>
                            <text class="chart-label" x="35" y="59" text-anchor="end">8</text>
                            <text class="chart-label" x="35" y="94" text-anchor="end">4</text>
                            <text class="chart-label" x="35" y="129" text-anchor="end">0</text>
                            <text class="chart-label" x="55" y="145">2002</text>
                            <text class="chart-label" x="140" y="145">2010</text>
                            <text class="chart-label" x="235" y="145">2017</text>
                            <text class="chart-label" x="355" y="145">2024</text>
                            <path class="chart-line chart-line-1" d="M55,110 L70,115 L85,105 L100,118 L115,112 L130,120 L145,110 L160,100 L175,112 L190,105 L205,110 L220,115 L235,90 L250,65 L265,100 L280,95 L295,105 L310,80 L325,60 L340,70 L355,55 L370,35" />
                            <path class="chart-line chart-line-2" d="M55,105 L70,112 L85,100 L100,115 L115,108 L130,118 L145,105 L160,95 L175,108 L190,100 L205,105 L220,112 L235,85 L250,58 L265,95 L280,90 L295,100 L310,75 L325,55 L340,65 L355,50 L370,30" />
                        </svg>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span data-lang="en">Sesoko</span><span data-lang="ja">瀬底</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-2"></span><span data-lang="en">Manza</span><span data-lang="ja">万座</span></div>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Sea Surface Temperature</span>
                            <span data-lang="ja">海水温の推移</span>
                        </div>
                        <div class="chart-subtitle">
                            <span data-lang="en">Monthly Mean · Sesoko Island</span>
                            <span data-lang="ja">月平均 · 瀬底島</span>
                        </div>
                    </div>
                    <div class="chart-container">
                        <svg class="chart-svg" viewBox="0 0 400 160" preserveAspectRatio="xMidYMid meet">
                            <g class="chart-grid-lines">
                                <line class="chart-grid-line" x1="40" y1="20" x2="380" y2="20" />
                                <line class="chart-grid-line" x1="40" y1="55" x2="380" y2="55" />
                                <line class="chart-grid-line" x1="40" y1="90" x2="380" y2="90" />
                                <line class="chart-grid-line" x1="40" y1="125" x2="380" y2="125" />
                            </g>
                            <text class="chart-label" x="35" y="24" text-anchor="end">30</text>
                            <text class="chart-label" x="35" y="59" text-anchor="end">27</text>
                            <text class="chart-label" x="35" y="94" text-anchor="end">24</text>
                            <text class="chart-label" x="35" y="129" text-anchor="end">21</text>
                            <text class="chart-label" x="55" y="145">Jan</text>
                            <text class="chart-label" x="135" y="145">Apr</text>
                            <text class="chart-label" x="215" y="145">Jul</text>
                            <text class="chart-label" x="295" y="145">Oct</text>
                            <text class="chart-label" x="365" y="145">Dec</text>
                            <path class="chart-line chart-line-1" d="M55,85 L82,90 L109,95 L136,80 L163,60 L190,35 L217,20 L244,18 L271,25 L298,45 L325,65 L352,80 L370,85" />
                            <path class="chart-line chart-line-3" d="M55,90 L82,95 L109,100 L136,85 L163,65 L190,42 L217,28 L244,25 L271,32 L298,52 L325,70 L352,85 L370,90" />
                        </svg>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span>2024</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-3"></span><span>2023</span></div>
                    </div>
                </div>
            </section>'''

# 新チャートセクション（canvas）
new_chart_section = '''            <section class="chart-grid">
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Annual Peak DHW</span>
                            <span data-lang="ja">年間最大DHW</span>
                        </div>
                        <div class="chart-subtitle">
                            <span data-lang="en">Degree Heating Weeks · Sesoko & Manza</span>
                            <span data-lang="ja">熱ストレス指標 · 瀬底・万座</span>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="dhwChart"></canvas>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span data-lang="en">Sesoko</span><span data-lang="ja">瀬底</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-2"></span><span data-lang="en">Manza</span><span data-lang="ja">万座</span></div>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Sea Surface Temperature</span>
                            <span data-lang="ja">海水温の推移</span>
                        </div>
                        <div class="chart-subtitle">
                            <span data-lang="en">Monthly Climatology · 3 Sites</span>
                            <span data-lang="ja">月別気候値 · 3地点</span>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="sstChart"></canvas>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span data-lang="en">Sesoko</span><span data-lang="ja">瀬底</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-2"></span><span data-lang="en">Manza</span><span data-lang="ja">万座</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-3"></span><span data-lang="en">Ogasawara</span><span data-lang="ja">小笠原</span></div>
                    </div>
                </div>
            </section>'''

if old_chart_section in content:
    content = content.replace(old_chart_section, new_chart_section)
    print("✅ チャートセクションを置き換えました")
else:
    print("❌ 置き換え対象が見つかりません")
    exit(1)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 保存完了")
