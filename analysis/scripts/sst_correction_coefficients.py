#!/usr/bin/env python3
"""
環境タイプ × 温度帯のクロス集計
補正係数の導出
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

print("=" * 70)
print("環境タイプ × 温度帯 クロス集計：補正係数の導出")
print("=" * 70)

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
    df_sites[['site_id', 'spot_id', 'site_name', 'environment_type']],
    on=['site_id', 'spot_id'],
    how='left'
)

df['bias_mur'] = df['sst_mur'] - df['temperature']
df['bias_ct'] = df['sst_ct'] - df['temperature']

print(f"総データ数: {len(df):,}件")

# =============================================================================
# 環境タイプの整理（類似環境をグループ化）
# =============================================================================
print("\n" + "=" * 70)
print("1. 環境タイプの整理")
print("=" * 70)

# 元の環境タイプ別件数
print("\n元の環境タイプ別件数:")
env_counts = df['environment_type'].value_counts()
for env, count in env_counts.items():
    print(f"  {env}: {count:,}件")

# グループ化マッピング
env_group_map = {
    '礁斜面': '外洋系',
    '離礁・礁縁': '外洋系',
    '礁縁': '外洋系',
    '離礁': '外洋系',
    'やや外洋': '外洋系',
    '礁池': '閉鎖系',
    '礁池・礁原': '閉鎖系',
    '内湾': '閉鎖系',
    '礁原': '中間系',
    '礁原～\n礁斜面': '中間系',
}

df['env_group'] = df['environment_type'].map(env_group_map)

print("\nグループ化後:")
for grp in ['外洋系', '中間系', '閉鎖系']:
    n = len(df[df['env_group'] == grp])
    print(f"  {grp}: {n:,}件 ({n/len(df)*100:.1f}%)")

# =============================================================================
# 温度帯の定義
# =============================================================================
print("\n" + "=" * 70)
print("2. 温度帯の定義")
print("=" * 70)

# 3℃刻みの温度帯
def get_temp_band(temp):
    if temp < 24:
        return '<24℃'
    elif temp < 27:
        return '24-27℃'
    elif temp < 30:
        return '27-30℃'
    else:
        return '≥30℃'

df['temp_band'] = df['temperature'].apply(get_temp_band)

print("\n温度帯別件数:")
for band in ['<24℃', '24-27℃', '27-30℃', '≥30℃']:
    n = len(df[df['temp_band'] == band])
    print(f"  {band}: {n:,}件 ({n/len(df)*100:.1f}%)")

# =============================================================================
# クロス集計：環境タイプ × 温度帯
# =============================================================================
print("\n" + "=" * 70)
print("3. クロス集計：環境グループ × 温度帯")
print("=" * 70)

print("\n【MURバイアス】")
print("-" * 80)
print(f"{'環境グループ':<12} {'<24℃':>12} {'24-27℃':>12} {'27-30℃':>12} {'≥30℃':>12}")
print("-" * 80)

cross_stats = []
for env_grp in ['外洋系', '中間系', '閉鎖系']:
    row = {'env_group': env_grp}
    row_str = f"{env_grp:<12}"
    for band in ['<24℃', '24-27℃', '27-30℃', '≥30℃']:
        subset = df[(df['env_group'] == env_grp) & (df['temp_band'] == band)]
        if len(subset) >= 30:
            bias = subset['bias_mur'].mean()
            row[f'bias_{band}'] = bias
            row[f'n_{band}'] = len(subset)
            row_str += f" {bias:>+10.3f}℃"
        else:
            row[f'bias_{band}'] = np.nan
            row[f'n_{band}'] = len(subset)
            row_str += f" {'(n<30)':>12}"
        cross_stats.append({
            'env_group': env_grp,
            'temp_band': band,
            'n': len(subset),
            'mur_bias': subset['bias_mur'].mean() if len(subset) > 0 else np.nan,
            'ct_bias': subset['bias_ct'].mean() if len(subset) > 0 else np.nan,
            'mur_sd': subset['bias_mur'].std() if len(subset) > 0 else np.nan
        })
    print(row_str)

df_cross = pd.DataFrame(cross_stats)

print("\n【サンプルサイズ】")
print("-" * 80)
print(f"{'環境グループ':<12} {'<24℃':>12} {'24-27℃':>12} {'27-30℃':>12} {'≥30℃':>12}")
print("-" * 80)
for env_grp in ['外洋系', '中間系', '閉鎖系']:
    row_str = f"{env_grp:<12}"
    for band in ['<24℃', '24-27℃', '27-30℃', '≥30℃']:
        subset = df[(df['env_group'] == env_grp) & (df['temp_band'] == band)]
        row_str += f" {len(subset):>12,}"
    print(row_str)

# =============================================================================
# 詳細な環境タイプ別（グループ化前）
# =============================================================================
print("\n" + "=" * 70)
print("4. 詳細な環境タイプ別（30℃以上のみ）")
print("=" * 70)

df_30plus = df[df['temperature'] >= 30]

print("\n30℃以上のバイアス（環境タイプ別）:")
print("-" * 70)
print(f"{'環境タイプ':<20} {'n':>6} {'MUR bias':>12} {'SD':>8} {'95%CI':>16}")
print("-" * 70)

env_detail_stats = []
for env_type in sorted(df_30plus['environment_type'].dropna().unique()):
    subset = df_30plus[df_30plus['environment_type'] == env_type]
    if len(subset) >= 10:
        bias = subset['bias_mur'].mean()
        sd = subset['bias_mur'].std()
        se = sd / np.sqrt(len(subset))
        ci_low = bias - 1.96 * se
        ci_high = bias + 1.96 * se
        env_detail_stats.append({
            'environment_type': env_type,
            'n': len(subset),
            'bias': bias,
            'sd': sd,
            'ci_low': ci_low,
            'ci_high': ci_high
        })
        print(f"{env_type:<20} {len(subset):>6} {bias:>+12.3f} {sd:>8.3f} [{ci_low:>+.3f}, {ci_high:>+.3f}]")

# =============================================================================
# 補正係数の導出
# =============================================================================
print("\n" + "=" * 70)
print("5. 補正係数の導出")
print("=" * 70)

print("\n【推奨補正係数（衛星SST → 実測推定）】")
print("補正後SST = 衛星SST - バイアス")
print("-" * 70)

# 環境グループ × 温度帯の補正係数
correction_table = []
for env_grp in ['外洋系', '中間系', '閉鎖系']:
    for band in ['<24℃', '24-27℃', '27-30℃', '≥30℃']:
        subset = df[(df['env_group'] == env_grp) & (df['temp_band'] == band)]
        if len(subset) >= 30:
            bias = subset['bias_mur'].mean()
            correction = -bias  # バイアスを打ち消す
            correction_table.append({
                'env_group': env_grp,
                'temp_band': band,
                'n': len(subset),
                'bias': bias,
                'correction': correction
            })

df_correction = pd.DataFrame(correction_table)

print(f"\n{'環境グループ':<12} {'温度帯':<10} {'n':>8} {'バイアス':>10} {'補正値':>10}")
print("-" * 60)
for _, row in df_correction.iterrows():
    print(f"{row['env_group']:<12} {row['temp_band']:<10} {row['n']:>8} {row['bias']:>+10.3f} {row['correction']:>+10.3f}")

# =============================================================================
# 簡略化モデル（2段階）
# =============================================================================
print("\n" + "=" * 70)
print("6. 簡略化モデル（実用版）")
print("=" * 70)

print("""
【2段階補正モデル】

Step 1: 温度で分岐
  - 30℃未満 → 全環境で +0.3℃（衛星が高め）
  - 30℃以上 → Step 2へ

Step 2: 環境タイプで分岐（30℃以上のみ）
  - 外洋系（礁斜面、離礁・礁縁など）: 補正不要（バイアス≒0）
  - 中間系（礁原など）: -0.1℃補正
  - 閉鎖系（礁池、内湾など）: +0.4℃補正
""")

# 実際の数値で検証
print("\n【検証】")
for env_grp in ['外洋系', '中間系', '閉鎖系']:
    below30 = df[(df['env_group'] == env_grp) & (df['temperature'] < 30)]
    above30 = df[(df['env_group'] == env_grp) & (df['temperature'] >= 30)]
    print(f"\n{env_grp}:")
    print(f"  30℃未満: n={len(below30):,}, bias={below30['bias_mur'].mean():+.3f}℃")
    if len(above30) >= 10:
        print(f"  30℃以上: n={len(above30):,}, bias={above30['bias_mur'].mean():+.3f}℃")

# =============================================================================
# 補正式のコード
# =============================================================================
print("\n" + "=" * 70)
print("7. 補正式（Pythonコード）")
print("=" * 70)

code = '''
def correct_satellite_sst(sst_satellite, temperature_estimated, environment_type):
    """
    衛星SSTから実測SST推定値を計算
    
    Parameters:
    -----------
    sst_satellite : float
        衛星SST（MURまたはCoralTemp）
    temperature_estimated : float
        推定される実測水温（衛星SSTで近似可）
    environment_type : str
        環境タイプ（'外洋系', '中間系', '閉鎖系'）
        または詳細タイプ（'礁斜面', '礁池', etc.）
    
    Returns:
    --------
    float : 補正後の推定実測水温
    """
    
    # 環境タイプをグループに変換
    env_group_map = {
        '礁斜面': '外洋系', '離礁・礁縁': '外洋系', '礁縁': '外洋系',
        '離礁': '外洋系', 'やや外洋': '外洋系',
        '礁池': '閉鎖系', '礁池・礁原': '閉鎖系', '内湾': '閉鎖系',
        '礁原': '中間系', '礁原～礁斜面': '中間系',
    }
    
    env_group = env_group_map.get(environment_type, environment_type)
    
    # 30℃未満：全環境で同じ補正
    if temperature_estimated < 30:
        # 衛星が+0.3℃高いので引く
        return sst_satellite - 0.30
    
    # 30℃以上：環境タイプ別
    if env_group == '外洋系':
        # バイアスほぼゼロ、補正不要
        return sst_satellite
    elif env_group == '中間系':
        # やや負バイアス
        return sst_satellite + 0.10
    elif env_group == '閉鎖系':
        # 負バイアス大
        return sst_satellite + 0.40
    else:
        # 不明な環境タイプはデフォルト補正
        return sst_satellite - 0.20
'''

print(code)

# =============================================================================
# 補正効果のシミュレーション
# =============================================================================
print("\n" + "=" * 70)
print("8. 補正効果のシミュレーション")
print("=" * 70)

# 補正を適用
def apply_correction(row):
    env_group = row['env_group']
    temp = row['temperature']
    sst = row['sst_mur']
    
    if temp < 30:
        return sst - 0.30
    elif env_group == '外洋系':
        return sst
    elif env_group == '中間系':
        return sst + 0.10
    elif env_group == '閉鎖系':
        return sst + 0.40
    else:
        return sst - 0.20

df['sst_corrected'] = df.apply(apply_correction, axis=1)
df['bias_corrected'] = df['sst_corrected'] - df['temperature']

print("\n補正前後のバイアス比較:")
print("-" * 60)
print(f"{'区分':<20} {'補正前':>12} {'補正後':>12} {'改善':>12}")
print("-" * 60)

# 全体
print(f"{'全体':<20} {df['bias_mur'].mean():>+12.3f} {df['bias_corrected'].mean():>+12.3f} {abs(df['bias_mur'].mean()) - abs(df['bias_corrected'].mean()):>12.3f}")

# 30℃以上
above30 = df[df['temperature'] >= 30]
print(f"{'30℃以上':<20} {above30['bias_mur'].mean():>+12.3f} {above30['bias_corrected'].mean():>+12.3f} {abs(above30['bias_mur'].mean()) - abs(above30['bias_corrected'].mean()):>12.3f}")

# 環境グループ別（30℃以上）
for env_grp in ['外洋系', '中間系', '閉鎖系']:
    subset = df[(df['env_group'] == env_grp) & (df['temperature'] >= 30)]
    if len(subset) >= 10:
        label = f"30℃+ {env_grp}"
        print(f"{label:<20} {subset['bias_mur'].mean():>+12.3f} {subset['bias_corrected'].mean():>+12.3f} {abs(subset['bias_mur'].mean()) - abs(subset['bias_corrected'].mean()):>12.3f}")

# RMSE比較
rmse_before = np.sqrt((df['bias_mur'] ** 2).mean())
rmse_after = np.sqrt((df['bias_corrected'] ** 2).mean())
print(f"\n全体RMSE: {rmse_before:.3f}℃ → {rmse_after:.3f}℃ (改善: {rmse_before - rmse_after:.3f}℃)")

# =============================================================================
# CSVエクスポート
# =============================================================================
output_dir = base_dir
df_cross.to_csv(output_dir / "sst_correction_cross_table.csv", index=False)
df_correction.to_csv(output_dir / "sst_correction_coefficients.csv", index=False)

print(f"\n出力ファイル:")
print(f"  {output_dir / 'sst_correction_cross_table.csv'}")
print(f"  {output_dir / 'sst_correction_coefficients.csv'}")

print("\n" + "=" * 70)
print("分析完了")
print("=" * 70)
