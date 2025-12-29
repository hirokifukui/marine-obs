#!/usr/bin/env python3
"""DHWチャートに小笠原を追加"""

input_file = '/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html'

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 旧: 2サイトのみ
old_datasets = '''                        datasets: [
                            {
                                label: '瀬底',
                                data: dhwData.sesoko.map(d => d.peak_dhw),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: '万座',
                                data: dhwData.manza.map(d => d.peak_dhw),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
                                borderWidth: 1
                            }
                        ]'''

# 新: 3サイト
new_datasets = '''                        datasets: [
                            {
                                label: '瀬底',
                                data: dhwData.sesoko.map(d => d.peak_dhw),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: '万座',
                                data: dhwData.manza.map(d => d.peak_dhw),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
                                borderWidth: 1
                            },
                            {
                                label: '小笠原',
                                data: dhwData.ogasawara.map(d => d.peak_dhw),
                                backgroundColor: chartColors.ogasawara + '99',
                                borderColor: chartColors.ogasawara,
                                borderWidth: 1
                            }
                        ]'''

if old_datasets in content:
    content = content.replace(old_datasets, new_datasets)
    print("✅ 小笠原を追加しました")
else:
    print("❌ 置き換え対象が見つかりません")
    exit(1)

# 凡例も更新（瀬底・万座 → 3地点）
old_legend = '''                        <div class="chart-subtitle">
                            <span data-lang="en">Degree Heating Weeks · Sesoko & Manza</span>
                            <span data-lang="ja">熱ストレス指標 · 瀬底・万座</span>
                        </div>'''

new_legend = '''                        <div class="chart-subtitle">
                            <span data-lang="en">Degree Heating Weeks · 3 Sites</span>
                            <span data-lang="ja">熱ストレス指標 · 3地点</span>
                        </div>'''

if old_legend in content:
    content = content.replace(old_legend, new_legend)
    print("✅ サブタイトルを更新しました")

# 凡例に小笠原を追加
old_chart_legend = '''                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span data-lang="en">Sesoko</span><span data-lang="ja">瀬底</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-2"></span><span data-lang="en">Manza</span><span data-lang="ja">万座</span></div>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Sea Surface Temperature</span>'''

new_chart_legend = '''                    <div class="chart-legend">
                        <div class="legend-item"><span class="legend-line legend-line-1"></span><span data-lang="en">Sesoko</span><span data-lang="ja">瀬底</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-2"></span><span data-lang="en">Manza</span><span data-lang="ja">万座</span></div>
                        <div class="legend-item"><span class="legend-line legend-line-3"></span><span data-lang="en">Ogasawara</span><span data-lang="ja">小笠原</span></div>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span data-lang="en">Sea Surface Temperature</span>'''

if old_chart_legend in content:
    content = content.replace(old_chart_legend, new_chart_legend)
    print("✅ DHWチャートの凡例に小笠原を追加しました")

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 保存完了")
