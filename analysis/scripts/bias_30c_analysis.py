#!/usr/bin/env python3
"""
30℃以上負バイアスの原因特定分析
Step A-F を一括実行
ローカルCSVファイル版
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
from pathlib import Path

print("=" * 60)
print("30℃以上負バイアス原因特定分析")
print("=" * 60)

# =============================================================================
# データ読み込み（ローカルCSV）
# =============================================================================
print("\n[データ読み込み中...]")

base_dir = Path(__file__).parent / "processed"

# 結合済みデータ
df = pd.read_csv(base_dir / "sst_validation_paired.csv")
df['date'] = pd.to_datetime(df['date'])
print(f"  結合済みデータ: {len(df):,}行")

# カラム名の標準化
df = df.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id', 
    'temp_mean': 'temperature',
    'mur_sst': 'sst_mur',
    'coraltemp_sst': 'sst_ct'
})

# 地点マスター
df_sites = pd.read_csv(base_dir / "moni1000_sites.csv")
df_sites = df_sites.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id',
    'lat': 'latitude',
    'lon': 'longitude',
    'landform': 'environment_type'
})
print(f"  地点マスター: {len(df_sites):,}行")

# 地点情報を結合
df = df.merge(
    df_sites[['site_id', 'spot_id', 'site_name', 'spot_name', 'latitude', 'longitude', 'environment_type', 'prefecture']],
    on=['site_id', 'spot_id'],
    how='left'
)

# バイアス計算
df['bias_mur'] = df['sst_mur'] - df['temperature']
df['bias_ct'] = df['sst_ct'] - df['temperature']

# 年・月を追加
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

print(f"  結合後データ: {len(df):,}行")

# =============================================================================
# Step A: 30℃以上データの基本統計
# =============================================================================
print("\n" + "=" * 60)
print("Step A: 30℃以上データの基本統計")
print("=" * 60)

df_30plus = df[df['temperature'] >= 30].copy()
n_30plus = len(df_30plus)
n_total = len(df)

print(f"\n全データ: {n_total:,}件")
print(f"30℃以上: {n_30plus:,}件 ({n_30plus/n_total*100:.1f}%)")

print(f"\n30℃以上のバイアス:")
print(f"  MUR:       {df_30plus['bias_mur'].mean():+.3f}℃ (SD={df_30plus['bias_mur'].std():.3f})")
print(f"  CoralTemp: {df_30plus['bias_ct'].mean():+.3f}℃ (SD={df_30plus['bias_ct'].std():.3f})")

print(f"\n30℃未満のバイアス（参考）:")
df_below30 = df[df['temperature'] < 30]
print(f"  MUR:       {df_below30['bias_mur'].mean():+.3f}℃")
print(f"  CoralTemp: {df_below30['bias_ct'].mean():+.3f}℃")

# 月別分布
print(f"\n30℃以上の月別分布:")
month_dist = df_30plus.groupby('month').size()
for m in sorted(month_dist.index):
    print(f"  {m}月: {month_dist[m]:,}件 ({month_dist[m]/n_30plus*100:.1f}%)")

# 年別分布
print(f"\n30℃以上の年別分布:")
year_dist = df_30plus.groupby('year').size()
for y in sorted(year_dist.index):
    print(f"  {y}年: {year_dist[y]:,}件 ({year_dist[y]/n_30plus*100:.1f}%)")

# =============================================================================
# Step B: 環境タイプ別分析（H1検証）
# =============================================================================
print("\n" + "=" * 60)
print("Step B: 環境タイプ別分析（H1検証）")
print("=" * 60)

print("\n30℃以上のバイアス（環境タイプ別）:")
print("-" * 80)
print(f"{'環境タイプ':<25} {'n':>6} {'MUR bias':>10} {'CT bias':>10} {'全温度域MUR':>12}")
print("-" * 80)

env_stats = []
for env_type in sorted(df['environment_type'].dropna().unique()):
    df_env_30 = df_30plus[df_30plus['environment_type'] == env_type]
    df_env_all = df[df['environment_type'] == env_type]
    
    if len(df_env_30) >= 10:  # 最低10件以上
        stats_row = {
            'environment_type': env_type,
            'n_30plus': len(df_env_30),
            'mur_bias_30plus': df_env_30['bias_mur'].mean(),
            'ct_bias_30plus': df_env_30['bias_ct'].mean(),
            'mur_bias_all': df_env_all['bias_mur'].mean(),
            'ct_bias_all': df_env_all['bias_ct'].mean()
        }
        env_stats.append(stats_row)
        print(f"{env_type:<25} {len(df_env_30):>6} {df_env_30['bias_mur'].mean():>+10.3f} {df_env_30['bias_ct'].mean():>+10.3f} {df_env_all['bias_mur'].mean():>+12.3f}")

df_env_stats = pd.DataFrame(env_stats)

# 負バイアスの環境タイプを特定
print("\n【判定】")
neg_bias_envs = df_env_stats[df_env_stats['mur_bias_30plus'] < 0]['environment_type'].tolist()
pos_bias_envs = df_env_stats[df_env_stats['mur_bias_30plus'] >= 0]['environment_type'].tolist()
print(f"  負バイアス環境: {neg_bias_envs}")
print(f"  正/ゼロバイアス環境: {pos_bias_envs}")

# =============================================================================
# Step C: 地点別分析（H3検証）
# =============================================================================
print("\n" + "=" * 60)
print("Step C: 地点別分析（H3検証）")
print("=" * 60)

site_stats = []
for (site_id, spot_id), grp in df_30plus.groupby(['site_id', 'spot_id']):
    if len(grp) >= 5:  # 最低5件以上
        site_info = df_sites[(df_sites['site_id'] == site_id) & (df_sites['spot_id'] == spot_id)]
        if len(site_info) > 0:
            site_stats.append({
                'site_id': site_id,
                'spot_id': spot_id,
                'site_name': site_info.iloc[0]['site_name'],
                'latitude': site_info.iloc[0]['latitude'],
                'environment_type': site_info.iloc[0]['environment_type'],
                'n_30plus': len(grp),
                'mur_bias': grp['bias_mur'].mean(),
                'ct_bias': grp['bias_ct'].mean()
            })

df_site_stats = pd.DataFrame(site_stats)

print(f"\n30℃以上データあり: {len(df_site_stats)}地点")

# 極端な負バイアス地点
print("\n極端な負バイアス地点（MUR bias < -0.5℃）:")
extreme_neg = df_site_stats[df_site_stats['mur_bias'] < -0.5].sort_values('mur_bias')
if len(extreme_neg) > 0:
    for _, row in extreme_neg.iterrows():
        print(f"  {row['site_name']}: MUR {row['mur_bias']:+.3f}℃, CT {row['ct_bias']:+.3f}℃ (n={row['n_30plus']}, {row['environment_type']})")
else:
    print("  なし")

# 正バイアス地点
print("\n正バイアス地点（MUR bias > 0）:")
pos_sites = df_site_stats[df_site_stats['mur_bias'] > 0].sort_values('mur_bias', ascending=False)
if len(pos_sites) > 0:
    for _, row in pos_sites.head(5).iterrows():
        print(f"  {row['site_name']}: MUR {row['mur_bias']:+.3f}℃, CT {row['ct_bias']:+.3f}℃ (n={row['n_30plus']}, {row['environment_type']})")
else:
    print("  なし")

# 緯度との相関
if len(df_site_stats) > 5:
    r_lat, p_lat = stats.pearsonr(df_site_stats['latitude'], df_site_stats['mur_bias'])
    print(f"\n緯度との相関: r={r_lat:.3f}, p={p_lat:.4f}")

# =============================================================================
# Step D-1: 月別分析（H2検証）
# =============================================================================
print("\n" + "=" * 60)
print("Step D-1: 月別分析（H2検証）")
print("=" * 60)

print("\n30℃以上のバイアス（月別）:")
print("-" * 50)
print(f"{'月':>4} {'n':>6} {'MUR bias':>10} {'CT bias':>10}")
print("-" * 50)

month_stats = []
for month in sorted(df_30plus['month'].unique()):
    grp = df_30plus[df_30plus['month'] == month]
    month_stats.append({
        'month': month,
        'n': len(grp),
        'mur_bias': grp['bias_mur'].mean(),
        'ct_bias': grp['bias_ct'].mean()
    })
    print(f"{month:>4} {len(grp):>6} {grp['bias_mur'].mean():>+10.3f} {grp['bias_ct'].mean():>+10.3f}")

# =============================================================================
# Step D-2: 年別分析（H4検証）
# =============================================================================
print("\n" + "=" * 60)
print("Step D-2: 年別分析（H4検証）")
print("=" * 60)

print("\n30℃以上のバイアス（年別）:")
print("-" * 50)
print(f"{'年':>6} {'n':>6} {'MUR bias':>10} {'CT bias':>10}")
print("-" * 50)

year_stats = []
for year in sorted(df_30plus['year'].unique()):
    grp = df_30plus[df_30plus['year'] == year]
    year_stats.append({
        'year': year,
        'n': len(grp),
        'mur_bias': grp['bias_mur'].mean(),
        'ct_bias': grp['bias_ct'].mean()
    })
    print(f"{year:>6} {len(grp):>6} {grp['bias_mur'].mean():>+10.3f} {grp['bias_ct'].mean():>+10.3f}")

# 年による差の検定（Kruskal-Wallis）
print("\n【年次効果の検定】")
year_groups = [df_30plus[df_30plus['year'] == y]['bias_mur'].values for y in df_30plus['year'].unique()]
year_groups = [g for g in year_groups if len(g) >= 5]
if len(year_groups) >= 2:
    h_stat, p_val_year = stats.kruskal(*year_groups)
    print(f"  Kruskal-Wallis検定: H={h_stat:.2f}, p={p_val_year:.4f}")
    if p_val_year < 0.05:
        print("  → 年による有意差あり")
    else:
        print("  → 年による有意差なし（一貫したパターン）")
else:
    p_val_year = 1.0
    print("  → データ不足で検定不可")

# =============================================================================
# Step E: 温度帯細分化分析
# =============================================================================
print("\n" + "=" * 60)
print("Step E: 温度帯細分化分析")
print("=" * 60)

print("\n1℃刻みのバイアス:")
print("-" * 60)
print(f"{'温度帯':>10} {'n':>7} {'MUR bias':>10} {'CT bias':>10} {'転換点?':>8}")
print("-" * 60)

temp_bands = [(i, i+1) for i in range(20, 33)]
prev_sign = None
transition_temp = None
for low, high in temp_bands:
    grp = df[(df['temperature'] >= low) & (df['temperature'] < high)]
    if len(grp) >= 10:
        mur_bias = grp['bias_mur'].mean()
        current_sign = '+' if mur_bias >= 0 else '-'
        transition = ''
        if prev_sign is not None and prev_sign != current_sign:
            transition = '←'
            transition_temp = low
        print(f"{low:>4}-{high:<4}℃ {len(grp):>7} {mur_bias:>+10.3f} {grp['bias_ct'].mean():>+10.3f} {transition:>8}")
        prev_sign = current_sign

if transition_temp:
    print(f"\n【転換点】{transition_temp}℃付近で正→負バイアスに転換")

# =============================================================================
# Step F: MUR vs CoralTemp比較（H6検証）
# =============================================================================
print("\n" + "=" * 60)
print("Step F: MUR vs CoralTemp比較（H6検証）")
print("=" * 60)

print("\n30℃以上でのMUR vs CoralTemp:")
print(f"  MUR平均バイアス:       {df_30plus['bias_mur'].mean():+.4f}℃")
print(f"  CoralTemp平均バイアス: {df_30plus['bias_ct'].mean():+.4f}℃")
print(f"  差（MUR - CT）:        {df_30plus['bias_mur'].mean() - df_30plus['bias_ct'].mean():+.4f}℃")

# 対応t検定
t_stat, p_val_t = stats.ttest_rel(df_30plus['bias_mur'], df_30plus['bias_ct'])
print(f"\n対応t検定: t={t_stat:.3f}, p={p_val_t:.4e}")
if p_val_t < 0.05:
    if df_30plus['bias_mur'].mean() > df_30plus['bias_ct'].mean():
        print("  → MURの方がバイアスが大きい（より高温を示す）")
    else:
        print("  → CoralTempの方がバイアスが大きい（より高温を示す）")
else:
    print("  → 両者に有意差なし（同様の挙動）")

# =============================================================================
# 総合判定
# =============================================================================
print("\n" + "=" * 60)
print("総合判定")
print("=" * 60)

print("\n仮説の検証結果:")
print("-" * 60)

# H1: 環境タイプ依存
if len(df_env_stats) > 0:
    all_neg = all(df_env_stats['mur_bias_30plus'] < 0)
    print(f"H1（環境タイプ依存）: {'棄却' if all_neg else '部分支持'}")
    if all_neg:
        print("   → 全環境タイプで負バイアス（環境タイプ固有ではない）")
    else:
        print(f"   → 負バイアス環境: {neg_bias_envs}")
        print(f"   → 正バイアス環境: {pos_bias_envs}")

# H3: 地点固有
if len(df_site_stats) > 0:
    n_extreme = len(df_site_stats[df_site_stats['mur_bias'] < -0.5])
    print(f"H3（地点固有効果）: {'支持' if n_extreme > 0 else '棄却'}")
    print(f"   → 極端な負バイアス地点: {n_extreme}地点")

# H4: 年次効果
print(f"H4（年次効果）: {'支持' if p_val_year < 0.05 else '棄却'}")
if p_val_year >= 0.05:
    print("   → 年による有意差なし（一貫した構造的問題）")

# H6: 衛星アルゴリズム
print(f"H6（衛星アルゴリズム差）: {'支持' if p_val_t < 0.05 else '棄却'}")
if p_val_t >= 0.05:
    print("   → MURとCoralTempで同様の挙動（共通の原因）")

print("\n" + "=" * 60)
print("分析完了")
print("=" * 60)
