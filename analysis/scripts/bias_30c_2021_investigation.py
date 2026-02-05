#!/usr/bin/env python3
"""
2021年30℃以上負バイアス異常の調査
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

print("=" * 60)
print("2021年30℃以上負バイアス異常の調査")
print("=" * 60)

# =============================================================================
# データ読み込み
# =============================================================================
base_dir = Path(__file__).parent / "processed"

df = pd.read_csv(base_dir / "sst_validation_paired.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id', 
    'temp_mean': 'temperature',
    'mur_sst': 'sst_mur',
    'coraltemp_sst': 'sst_ct'
})

df_sites = pd.read_csv(base_dir / "moni1000_sites.csv")
df_sites = df_sites.rename(columns={
    'site_no': 'site_id',
    'spot_no': 'spot_id',
    'lat': 'latitude',
    'lon': 'longitude',
    'landform': 'environment_type'
})

df = df.merge(
    df_sites[['site_id', 'spot_id', 'site_name', 'spot_name', 'latitude', 'longitude', 'environment_type', 'prefecture']],
    on=['site_id', 'spot_id'],
    how='left'
)

df['bias_mur'] = df['sst_mur'] - df['temperature']
df['bias_ct'] = df['sst_ct'] - df['temperature']
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# 30℃以上のデータ
df_30plus = df[df['temperature'] >= 30].copy()

print(f"\n全30℃以上データ: {len(df_30plus):,}件")

# =============================================================================
# 1. 2021年 vs 他年の基本比較
# =============================================================================
print("\n" + "=" * 60)
print("1. 2021年 vs 他年の基本比較")
print("=" * 60)

years_summary = []
for year in sorted(df_30plus['year'].unique()):
    grp = df_30plus[df_30plus['year'] == year]
    years_summary.append({
        'year': year,
        'n': len(grp),
        'temp_mean': grp['temperature'].mean(),
        'temp_max': grp['temperature'].max(),
        'mur_bias': grp['bias_mur'].mean(),
        'ct_bias': grp['bias_ct'].mean(),
        'n_sites': grp.groupby(['site_id', 'spot_id']).ngroups
    })

print("\n年別サマリー:")
print("-" * 80)
print(f"{'年':>6} {'n':>6} {'実測平均':>8} {'実測最高':>8} {'MUR bias':>10} {'地点数':>6}")
print("-" * 80)
for row in years_summary:
    print(f"{row['year']:>6} {row['n']:>6} {row['temp_mean']:>8.2f} {row['temp_max']:>8.2f} {row['mur_bias']:>+10.3f} {row['n_sites']:>6}")

# =============================================================================
# 2. 2021年の地点別分析
# =============================================================================
print("\n" + "=" * 60)
print("2. 2021年の地点別分析")
print("=" * 60)

df_2021 = df_30plus[df_30plus['year'] == 2021]

print(f"\n2021年30℃以上: {len(df_2021)}件")

site_2021 = []
for (site_id, spot_id), grp in df_2021.groupby(['site_id', 'spot_id']):
    site_info = df_sites[(df_sites['site_id'] == site_id) & (df_sites['spot_id'] == spot_id)]
    if len(site_info) > 0:
        site_2021.append({
            'site_id': site_id,
            'spot_id': spot_id,
            'site_name': site_info.iloc[0]['site_name'],
            'environment_type': site_info.iloc[0]['environment_type'],
            'latitude': site_info.iloc[0]['latitude'],
            'n': len(grp),
            'temp_mean': grp['temperature'].mean(),
            'mur_bias': grp['bias_mur'].mean(),
            'ct_bias': grp['bias_ct'].mean()
        })

df_site_2021 = pd.DataFrame(site_2021).sort_values('mur_bias')

print("\n2021年の地点別バイアス:")
print("-" * 90)
print(f"{'地点名':<25} {'環境':>12} {'n':>4} {'実測平均':>8} {'MUR bias':>10} {'CT bias':>10}")
print("-" * 90)
for _, row in df_site_2021.iterrows():
    print(f"{row['site_name']:<25} {str(row['environment_type'])[:12]:>12} {row['n']:>4} {row['temp_mean']:>8.2f} {row['mur_bias']:>+10.3f} {row['ct_bias']:>+10.3f}")

# =============================================================================
# 3. 同一地点の年別比較
# =============================================================================
print("\n" + "=" * 60)
print("3. 同一地点の年別比較（2021年にデータがある地点）")
print("=" * 60)

# 2021年にデータがある地点
sites_with_2021 = df_2021.groupby(['site_id', 'spot_id']).size().reset_index()[['site_id', 'spot_id']]

print("\n地点別・年別バイアス:")
for _, site_row in sites_with_2021.iterrows():
    site_id = site_row['site_id']
    spot_id = site_row['spot_id']
    
    site_data = df_30plus[(df_30plus['site_id'] == site_id) & (df_30plus['spot_id'] == spot_id)]
    site_info = df_sites[(df_sites['site_id'] == site_id) & (df_sites['spot_id'] == spot_id)]
    
    if len(site_info) > 0 and len(site_data) > 0:
        site_name = site_info.iloc[0]['site_name']
        print(f"\n【{site_name}】")
        
        for year in sorted(site_data['year'].unique()):
            year_data = site_data[site_data['year'] == year]
            print(f"  {year}: n={len(year_data):>3}, 実測={year_data['temperature'].mean():.2f}℃, MUR bias={year_data['bias_mur'].mean():+.3f}℃")

# =============================================================================
# 4. 2021年の月別パターン
# =============================================================================
print("\n" + "=" * 60)
print("4. 2021年の月別パターン")
print("=" * 60)

print("\n2021年の月別:")
print("-" * 50)
for month in sorted(df_2021['month'].unique()):
    grp = df_2021[df_2021['month'] == month]
    print(f"  {month}月: n={len(grp):>3}, 実測={grp['temperature'].mean():.2f}℃, MUR bias={grp['bias_mur'].mean():+.3f}℃")

# 他年との月別比較
print("\n各年の8月（最多月）の比較:")
print("-" * 50)
for year in sorted(df_30plus['year'].unique()):
    aug_data = df_30plus[(df_30plus['year'] == year) & (df_30plus['month'] == 8)]
    if len(aug_data) > 0:
        print(f"  {year}年8月: n={len(aug_data):>4}, 実測={aug_data['temperature'].mean():.2f}℃, MUR bias={aug_data['bias_mur'].mean():+.3f}℃")

# =============================================================================
# 5. 2021年の極端な負バイアスの内訳
# =============================================================================
print("\n" + "=" * 60)
print("5. 2021年の極端な負バイアス（< -1℃）の内訳")
print("=" * 60)

extreme_2021 = df_2021[df_2021['bias_mur'] < -1.0]
print(f"\n極端な負バイアス: {len(extreme_2021)}件 / {len(df_2021)}件 ({len(extreme_2021)/len(df_2021)*100:.1f}%)")

if len(extreme_2021) > 0:
    print("\n日付・地点別:")
    for _, row in extreme_2021.sort_values('bias_mur').head(20).iterrows():
        print(f"  {row['date'].strftime('%Y-%m-%d')} {row['site_name']}: 実測{row['temperature']:.2f}℃, MUR{row['sst_mur']:.2f}℃, bias{row['bias_mur']:+.2f}℃")

# =============================================================================
# 6. 2021年 vs 2022-2024年の統計的比較
# =============================================================================
print("\n" + "=" * 60)
print("6. 2021年 vs 2022-2024年の統計的比較")
print("=" * 60)

df_2021_bias = df_2021['bias_mur'].values
df_2022_24 = df_30plus[df_30plus['year'].isin([2022, 2023, 2024])]
df_2022_24_bias = df_2022_24['bias_mur'].values

print(f"\n2021年: n={len(df_2021_bias)}, mean={df_2021_bias.mean():+.3f}℃, SD={df_2021_bias.std():.3f}")
print(f"2022-24年: n={len(df_2022_24_bias)}, mean={df_2022_24_bias.mean():+.3f}℃, SD={df_2022_24_bias.std():.3f}")

# Mann-Whitney U検定
u_stat, p_val = stats.mannwhitneyu(df_2021_bias, df_2022_24_bias, alternative='less')
print(f"\nMann-Whitney U検定: U={u_stat:.1f}, p={p_val:.4e}")
print(f"→ 2021年のバイアスは2022-24年より有意に{'小さい（より負）' if p_val < 0.05 else '差なし'}")

# =============================================================================
# 7. 環境タイプ別の年次変動
# =============================================================================
print("\n" + "=" * 60)
print("7. 環境タイプ別の年次変動")
print("=" * 60)

main_env_types = ['礁斜面', '礁池', '離礁', '礁縁']

for env_type in main_env_types:
    env_data = df_30plus[df_30plus['environment_type'] == env_type]
    if len(env_data) > 0:
        print(f"\n【{env_type}】")
        for year in sorted(env_data['year'].unique()):
            year_data = env_data[env_data['year'] == year]
            if len(year_data) >= 5:
                print(f"  {year}: n={len(year_data):>4}, MUR bias={year_data['bias_mur'].mean():+.3f}℃")

# =============================================================================
# 8. 2021年の気象条件（参考）
# =============================================================================
print("\n" + "=" * 60)
print("8. 考察：2021年の特徴")
print("=" * 60)

print("""
【2021年のデータ特徴】
- 30℃以上のデータ数が少ない（182件、全体の4.6%）
- バイアスが極端に負（-0.716℃）

【考えられる原因】
1. サンプリングバイアス
   - 2021年に30℃以上になった地点が偏っている可能性
   - 特定の閉鎖的環境（礁池など）に集中？

2. 気象条件
   - 2021年夏は日本周辺で特異的な気象だった可能性
   - 雲量、風速、日射量などの確認が必要

3. 衛星データの品質
   - 2021年に衛星側の問題があった可能性
   - ただしMURとCoralTemp両方で同様の傾向
""")

print("\n" + "=" * 60)
print("分析完了")
print("=" * 60)
