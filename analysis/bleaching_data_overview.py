#!/usr/bin/env python3
"""
白化観測データの確認
- どの年・地点で白化が起きているか
- SST取得の優先順位を決定
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("モニ1000 白化観測データの確認")
print("=" * 70)

# =============================================================================
# データ読み込み
# =============================================================================
base_dir = Path(__file__).parent / "processed"

df_bleach = pd.read_csv(base_dir / "moni1000_bleaching.csv")
df_sites = pd.read_csv(base_dir / "moni1000_sites.csv")
df_sites = df_sites.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id',
    'lat': 'latitude',
    'lon': 'longitude',
    'landform': 'environment_type'
})

# カラム名の標準化
df_bleach = df_bleach.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id'
})

print(f"\n白化観測データ: {len(df_bleach):,}件")
print(f"地点マスター: {len(df_sites):,}件")

# =============================================================================
# 基本統計
# =============================================================================
print("\n" + "=" * 70)
print("1. 基本統計")
print("=" * 70)

print(f"\nカラム: {df_bleach.columns.tolist()}")
print(f"\n年の範囲: {df_bleach['year'].min()} - {df_bleach['year'].max()}")
print(f"地点数: {df_bleach.groupby(['site_id', 'spot_id']).ngroups}")

# 年別件数
print("\n年別観測件数:")
for year in sorted(df_bleach['year'].unique()):
    n = len(df_bleach[df_bleach['year'] == year])
    print(f"  {year}: {n}件")

# =============================================================================
# 白化の発生状況
# =============================================================================
print("\n" + "=" * 70)
print("2. 白化の発生状況")
print("=" * 70)

# bleaching_all > 0 を白化ありとする
df_bleach['has_bleaching'] = df_bleach['bleaching_all'] > 0
df_bleach['has_mortality'] = df_bleach['mortality_all'] > 0

print("\n年別白化発生:")
print("-" * 60)
print(f"{'年':>6} {'観測数':>8} {'白化あり':>10} {'白化率':>10} {'死亡あり':>10}")
print("-" * 60)

year_summary = []
for year in sorted(df_bleach['year'].unique()):
    yr_data = df_bleach[df_bleach['year'] == year]
    n_total = len(yr_data)
    n_bleach = yr_data['has_bleaching'].sum()
    n_mortality = yr_data['has_mortality'].sum()
    
    year_summary.append({
        'year': year,
        'n_obs': n_total,
        'n_bleach': n_bleach,
        'pct_bleach': n_bleach / n_total * 100 if n_total > 0 else 0,
        'n_mortality': n_mortality
    })
    
    print(f"{year:>6} {n_total:>8} {n_bleach:>10} {n_bleach/n_total*100:>9.1f}% {n_mortality:>10}")

# =============================================================================
# 白化の程度
# =============================================================================
print("\n" + "=" * 70)
print("3. 白化の程度（白化ありの地点のみ）")
print("=" * 70)

df_with_bleach = df_bleach[df_bleach['has_bleaching']]

print(f"\n白化あり観測数: {len(df_with_bleach)}件")
print(f"\n白化率（bleaching_all）の統計:")
print(f"  平均: {df_with_bleach['bleaching_all'].mean():.1f}%")
print(f"  中央値: {df_with_bleach['bleaching_all'].median():.1f}%")
print(f"  最大: {df_with_bleach['bleaching_all'].max():.1f}%")

print("\n白化率の分布:")
bins = [0, 10, 30, 50, 80, 100]
labels = ['1-10%', '10-30%', '30-50%', '50-80%', '80-100%']
df_with_bleach['bleach_category'] = pd.cut(df_with_bleach['bleaching_all'], bins=bins, labels=labels)
for cat in labels:
    n = len(df_with_bleach[df_with_bleach['bleach_category'] == cat])
    print(f"  {cat}: {n}件")

# =============================================================================
# 白化が多い年・地域
# =============================================================================
print("\n" + "=" * 70)
print("4. 白化が多い年・地域の組み合わせ")
print("=" * 70)

# 地点情報を結合
df_bleach_with_site = df_bleach.merge(
    df_sites[['site_id', 'spot_id', 'site_name', 'latitude', 'environment_type', 'prefecture']],
    on=['site_id', 'spot_id'],
    how='left'
)

# サイト別の白化集計
print("\nサイト別白化発生回数（多い順）:")
site_bleach = df_bleach_with_site[df_bleach_with_site['has_bleaching']].groupby('site_name').size().sort_values(ascending=False)
print("-" * 50)
for site, count in site_bleach.head(15).items():
    total = len(df_bleach_with_site[df_bleach_with_site['site_name'] == site])
    print(f"  {site}: {count}/{total}回 ({count/total*100:.0f}%)")

# =============================================================================
# 重点年の特定
# =============================================================================
print("\n" + "=" * 70)
print("5. 重点年の特定（SST取得優先順位）")
print("=" * 70)

print("\n【白化イベント年】")
for row in year_summary:
    if row['pct_bleach'] > 10:
        print(f"  {row['year']}年: 白化率{row['pct_bleach']:.1f}% ({row['n_bleach']}/{row['n_obs']}地点)")

# =============================================================================
# 白化発生地点のリスト
# =============================================================================
print("\n" + "=" * 70)
print("6. 白化発生地点（重度：bleaching_all >= 30%）")
print("=" * 70)

severe = df_bleach_with_site[df_bleach_with_site['bleaching_all'] >= 30].copy()
severe = severe.sort_values(['year', 'bleaching_all'], ascending=[True, False])

print(f"\n重度白化観測: {len(severe)}件")
print("-" * 80)
print(f"{'年':>6} {'地点名':<25} {'白化率':>8} {'死亡率':>8} {'環境':>12}")
print("-" * 80)

for _, row in severe.iterrows():
    env = str(row['environment_type'])[:12] if pd.notna(row['environment_type']) else ''
    print(f"{row['year']:>6} {str(row['site_name'])[:25]:<25} {row['bleaching_all']:>7.1f}% {row['mortality_all']:>7.1f}% {env:>12}")

# =============================================================================
# 水温ロガーとの重複確認
# =============================================================================
print("\n" + "=" * 70)
print("7. 水温ロガー地点との重複")
print("=" * 70)

# ロガーありの地点
logger_sites = df_sites[df_sites['has_logger'] == True][['site_id', 'spot_id', 'site_name']]
print(f"\n水温ロガー設置地点: {len(logger_sites)}地点")

# 白化発生 × ロガーあり
bleach_with_logger = df_bleach_with_site[df_bleach_with_site['has_bleaching']].merge(
    logger_sites[['site_id', 'spot_id']],
    on=['site_id', 'spot_id'],
    how='inner'
)

print(f"白化発生 × ロガーあり: {len(bleach_with_logger)}件")

if len(bleach_with_logger) > 0:
    print("\n白化発生したロガー地点（年別）:")
    for year in sorted(bleach_with_logger['year'].unique()):
        yr_data = bleach_with_logger[bleach_with_logger['year'] == year]
        print(f"\n  {year}年 ({len(yr_data)}件):")
        for _, row in yr_data.iterrows():
            print(f"    {row['site_name']}: 白化{row['bleaching_all']:.1f}%")

# =============================================================================
# SST取得の優先順位
# =============================================================================
print("\n" + "=" * 70)
print("8. SST取得の優先順位")
print("=" * 70)

print("""
【優先度1】既にロガーデータがある44地点
→ 衛星SSTは取得済み（Supabase）

【優先度2】白化発生地点（bleaching_all > 0）
→ DHW検証に必須

【優先度3】白化なし地点
→ 「白化しなかった条件」の検証に有用
""")

# 白化発生した地点（ロガーなし）の数
bleach_sites = df_bleach_with_site[df_bleach_with_site['has_bleaching']][['site_id', 'spot_id']].drop_duplicates()
logger_site_set = set(zip(logger_sites['site_id'], logger_sites['spot_id']))
bleach_site_set = set(zip(bleach_sites['site_id'], bleach_sites['spot_id']))
bleach_no_logger = bleach_site_set - logger_site_set

print(f"\n白化発生地点（ロガーなし）: {len(bleach_no_logger)}地点")
print(f"→ これらの地点のSST取得が最優先")

# 全地点数
all_sites = df_sites[['site_id', 'spot_id']].drop_duplicates()
no_logger = set(zip(all_sites['site_id'], all_sites['spot_id'])) - logger_site_set
print(f"\n全ロガーなし地点: {len(no_logger)}地点")

print("\n" + "=" * 70)
print("確認完了")
print("=" * 70)
