#!/usr/bin/env python3
"""
Phase 3 Step 7-9: 閾値最適化 + CoralTemp検証
"""

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# データ読み込み
# ============================================================

print("=" * 60)
print("Phase 3 Step 7-9: 閾値最適化 + CoralTemp検証")
print("=" * 60)

# 白化データ（phase3_analysis_dataset.csv）
bleach_df = pd.read_csv('processed/phase3_analysis_dataset.csv')
print(f"\n白化データ: {len(bleach_df)} 件")

# SST検証用ペアデータ（CoralTemp含む）
sst_paired = pd.read_csv('processed/sst_validation_paired.csv')
print(f"SST ペアデータ: {len(sst_paired)} 件")

# サイト情報（env_groupはbleach_dfから取得）
sites_env = bleach_df[['site_no', 'spot_no', 'env_group']].drop_duplicates()
print(f"環境グループ情報: {len(sites_env)} 件")

# ============================================================
# Step 7: 30℃閾値の最適化
# ============================================================

print("\n" + "=" * 60)
print("Step 7: 温度閾値の最適化")
print("=" * 60)

# 白化二値化（>10%）
bleach_df['bleaching_binary'] = (bleach_df['bleaching_all'] > 10).astype(int)
valid_df = bleach_df.dropna(subset=['days30_mur_raw', 'bleaching_binary'])
print(f"\n有効データ: {len(valid_df)} 件（白化発生: {valid_df['bleaching_binary'].sum()} 件）")

# 30℃データでYouden index最適閾値を探索
y_true = valid_df['bleaching_binary'].values
y_score = valid_df['days30_mur_raw'].values

fpr, tpr, thresholds_roc = roc_curve(y_true, y_score)
youden_j = tpr - fpr
optimal_idx = np.argmax(youden_j)
optimal_threshold_days = thresholds_roc[optimal_idx]

print(f"\n【30℃超過日数の最適カットオフ】")
print(f"Youden index最適閾値: {optimal_threshold_days:.1f} 日")
print(f"  - 感度: {tpr[optimal_idx]:.3f}")
print(f"  - 特異度: {1-fpr[optimal_idx]:.3f}")

# DHWの最適閾値も確認
dhw_cols = ['dhw_mur_raw', 'dhw_mur_corr', 'dhw_mur_corr_adj']
print(f"\n【DHWの最適カットオフ】")
for col in dhw_cols:
    valid_dhw = valid_df.dropna(subset=[col])
    if len(valid_dhw) > 0:
        y_true_dhw = valid_dhw['bleaching_binary'].values
        y_score_dhw = valid_dhw[col].values
        fpr_d, tpr_d, thresh_d = roc_curve(y_true_dhw, y_score_dhw)
        youden_d = tpr_d - fpr_d
        opt_idx_d = np.argmax(youden_d)
        print(f"{col}: {thresh_d[opt_idx_d]:.2f} 週 (Sens={tpr_d[opt_idx_d]:.2f}, Spec={1-fpr_d[opt_idx_d]:.2f})")

# ============================================================
# Step 8: CoralTempでの検証
# ============================================================

print("\n" + "=" * 60)
print("Step 8: CoralTemp検証")
print("=" * 60)

# 環境グループをマージ
sst_paired = sst_paired.merge(
    sites_env,
    on=['site_no', 'spot_no'],
    how='left'
)

# 温度帯を定義
def get_temp_band(sst):
    if pd.isna(sst):
        return None
    elif sst < 25:
        return '<25'
    elif sst < 30:
        return '25-30'
    else:
        return '≥30'

sst_paired['temp_band'] = sst_paired['coraltemp_sst'].apply(get_temp_band)

# CoralTemp補正係数を読み込み
try:
    coraltemp_coef = pd.read_csv('processed/sst_correction_coefficients_coraltemp.csv')
    print(f"\nCoralTemp補正係数:")
    print(coraltemp_coef.to_string(index=False))
except:
    # 補正係数がなければMURと同様に計算
    print("\nCoralTemp補正係数を計算中...")
    ct_stats = sst_paired.groupby(['env_group', 'temp_band']).agg(
        bias=('coraltemp_sst', lambda x: (x - sst_paired.loc[x.index, 'temp_mean']).mean())
    ).reset_index()
    ct_stats['correction'] = -ct_stats['bias']
    coraltemp_coef = ct_stats[['env_group', 'temp_band', 'correction']]
    coraltemp_coef.to_csv('processed/sst_correction_coefficients_coraltemp.csv', index=False)
    print(coraltemp_coef.to_string(index=False))

# 補正を適用
def apply_coraltemp_correction(row, coef_df):
    env = row.get('env_group', 'その他')
    band = row.get('temp_band', '25-30')
    sst = row.get('coraltemp_sst', np.nan)
    
    if pd.isna(sst) or pd.isna(env):
        return sst  # 補正なしで返す
    
    match = coef_df[(coef_df['env_group'] == env) & (coef_df['temp_band'] == band)]
    if len(match) > 0:
        correction = match['correction'].values[0]
    else:
        # デフォルト補正（全体平均）
        correction = coef_df['correction'].mean() if len(coef_df) > 0 else 0
    
    return sst + correction

sst_paired['coraltemp_corrected'] = sst_paired.apply(
    lambda row: apply_coraltemp_correction(row, coraltemp_coef), axis=1
)

# 白化観測と結合するためのDHW・30℃日数計算
print("\n【CoralTempでDHW・30℃日数を計算中...】")

# MMM計算（CoralTemp）
sst_paired['month'] = sst_paired['date'].str[5:7]
mmm_coraltemp = sst_paired.groupby(['site_no', 'spot_no', 'month'])['coraltemp_sst'].mean().reset_index()
mmm_coraltemp = mmm_coraltemp.groupby(['site_no', 'spot_no'])['coraltemp_sst'].max().reset_index(name='mmm_coraltemp')

mmm_coraltemp_corr = sst_paired.groupby(['site_no', 'spot_no', 'month'])['coraltemp_corrected'].mean().reset_index()
mmm_coraltemp_corr = mmm_coraltemp_corr.groupby(['site_no', 'spot_no'])['coraltemp_corrected'].max().reset_index(name='mmm_coraltemp_corr')

mmm_merged = mmm_coraltemp.merge(mmm_coraltemp_corr, on=['site_no', 'spot_no'])
print(f"MMM計算完了: {len(mmm_merged)} 地点")

# 日付型に変換
sst_paired['date_dt'] = pd.to_datetime(sst_paired['date'])

def calc_dhw_for_observation(site_no, spot_no, obs_date, sst_data, mmm_val, sst_col):
    """観測日時点のDHWを計算（Lachs 2021: 8週間累積）"""
    end_date = pd.to_datetime(obs_date)
    start_date = end_date - pd.Timedelta(days=56)
    
    site_data = sst_data[
        (sst_data['site_no'] == site_no) & 
        (sst_data['spot_no'] == spot_no) &
        (sst_data['date_dt'] >= start_date) &
        (sst_data['date_dt'] <= end_date)
    ][sst_col].dropna()
    
    if len(site_data) == 0:
        return np.nan
    
    hotspots = np.maximum(site_data - mmm_val, 0)
    dhw = hotspots.sum() / 7
    return dhw

def calc_days30_for_observation(site_no, spot_no, obs_date, sst_data, sst_col, threshold=30):
    """観測日90日前からの超過日数を計算"""
    end_date = pd.to_datetime(obs_date)
    start_date = end_date - pd.Timedelta(days=90)
    
    site_data = sst_data[
        (sst_data['site_no'] == site_no) & 
        (sst_data['spot_no'] == spot_no) &
        (sst_data['date_dt'] >= start_date) &
        (sst_data['date_dt'] <= end_date)
    ][sst_col].dropna()
    
    if len(site_data) == 0:
        return np.nan
    
    return (site_data >= threshold).sum()

# 白化観測リストを取得
bleach_obs = bleach_df[['site_no', 'spot_no', 'year', 'date', 'bleaching_all', 'env_group', 'lat']].copy()
bleach_obs['obs_date'] = pd.to_datetime(bleach_obs['date'])

# CoralTempでの計算
print("CoralTemp DHW・30℃日数を計算中...")
dhw_ct_raw = []
dhw_ct_corr = []
days30_ct_raw = []
days30_ct_corr = []

total = len(bleach_obs)
for i, (idx, row) in enumerate(bleach_obs.iterrows()):
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{total} 完了...")
    
    site_no = row['site_no']
    spot_no = row['spot_no']
    obs_date = row['obs_date']
    
    # MMM取得
    mmm_row = mmm_merged[(mmm_merged['site_no'] == site_no) & (mmm_merged['spot_no'] == spot_no)]
    if len(mmm_row) == 0:
        dhw_ct_raw.append(np.nan)
        dhw_ct_corr.append(np.nan)
        days30_ct_raw.append(np.nan)
        days30_ct_corr.append(np.nan)
        continue
    
    mmm_raw = mmm_row['mmm_coraltemp'].values[0]
    mmm_corr = mmm_row['mmm_coraltemp_corr'].values[0]
    
    # DHW計算
    dhw_raw = calc_dhw_for_observation(site_no, spot_no, obs_date, sst_paired, mmm_raw, 'coraltemp_sst')
    dhw_corr = calc_dhw_for_observation(site_no, spot_no, obs_date, sst_paired, mmm_corr, 'coraltemp_corrected')
    
    # 30℃日数計算
    d30_raw = calc_days30_for_observation(site_no, spot_no, obs_date, sst_paired, 'coraltemp_sst')
    d30_corr = calc_days30_for_observation(site_no, spot_no, obs_date, sst_paired, 'coraltemp_corrected')
    
    dhw_ct_raw.append(dhw_raw)
    dhw_ct_corr.append(dhw_corr)
    days30_ct_raw.append(d30_raw)
    days30_ct_corr.append(d30_corr)

bleach_obs['dhw_coraltemp_raw'] = dhw_ct_raw
bleach_obs['dhw_coraltemp_corr'] = dhw_ct_corr
bleach_obs['days30_coraltemp_raw'] = days30_ct_raw
bleach_obs['days30_coraltemp_corr'] = days30_ct_corr

# 既存のMURデータと結合
analysis_df = bleach_df.merge(
    bleach_obs[['site_no', 'spot_no', 'year', 'dhw_coraltemp_raw', 'dhw_coraltemp_corr', 
                'days30_coraltemp_raw', 'days30_coraltemp_corr']],
    on=['site_no', 'spot_no', 'year'],
    how='left'
)
analysis_df['bleaching_binary'] = (analysis_df['bleaching_all'] > 10).astype(int)

print(f"\n統合データ: {len(analysis_df)} 件")

# ============================================================
# Step 9: 全モデル比較（MUR + CoralTemp）
# ============================================================

print("\n" + "=" * 60)
print("Step 9: 全モデル比較")
print("=" * 60)

# 評価対象の指標
indicators = {
    # MUR系
    'dhw_mur_raw': 'DHW MUR生',
    'dhw_mur_corr': 'DHW MUR補正',
    'dhw_mur_corr_adj': 'DHW MUR補正+MMM調整',
    'days30_mur_raw': '30℃日数 MUR生',
    'days30_mur_corr': '30℃日数 MUR補正',
    # CoralTemp系
    'dhw_coraltemp_raw': 'DHW CoralTemp生',
    'dhw_coraltemp_corr': 'DHW CoralTemp補正',
    'days30_coraltemp_raw': '30℃日数 CoralTemp生',
    'days30_coraltemp_corr': '30℃日数 CoralTemp補正',
    # 実測
    'dhw_logger': 'DHW 実測',
    'days30_logger': '30℃日数 実測',
}

results = []

for col, label in indicators.items():
    valid = analysis_df.dropna(subset=[col, 'bleaching_binary'])
    if len(valid) < 20:
        continue
    
    y_true = valid['bleaching_binary'].values
    y_score = valid[col].values
    
    try:
        auc = roc_auc_score(y_true, y_score)
        fpr, tpr, thresh = roc_curve(y_true, y_score)
        youden = tpr - fpr
        opt_idx = np.argmax(youden)
        
        # Spearman相関
        rho, p = stats.spearmanr(valid[col], valid['bleaching_all'])
        
        results.append({
            'indicator': col,
            'label': label,
            'n': len(valid),
            'n_bleached': int(y_true.sum()),
            'auc': auc,
            'optimal_threshold': thresh[opt_idx],
            'sensitivity': tpr[opt_idx],
            'specificity': 1 - fpr[opt_idx],
            'spearman_r': rho,
            'spearman_p': p
        })
    except Exception as e:
        print(f"  {col}: エラー - {e}")

results_df = pd.DataFrame(results).sort_values('auc', ascending=False)

print("\n【全モデル比較結果（AUC順）】")
print("-" * 80)
print(f"{'指標':<25} {'n':>5} {'AUC':>6} {'Sens':>6} {'Spec':>6} {'Spearman':>8}")
print("-" * 80)
for _, row in results_df.iterrows():
    print(f"{row['label']:<25} {row['n']:>5} {row['auc']:>6.3f} {row['sensitivity']:>6.2f} {row['specificity']:>6.2f} {row['spearman_r']:>8.3f}")

# ============================================================
# サブグループ分析（緯度帯別）
# ============================================================

print("\n" + "=" * 60)
print("緯度帯別サブグループ分析")
print("=" * 60)

analysis_df['lat_band'] = pd.cut(
    analysis_df['lat'], 
    bins=[23, 26, 28, 30, 35],
    labels=['24-26°N (八重山)', '26-28°N (沖縄本島)', '28-30°N (奄美)', '30-35°N (本州)']
)

subgroup_results = []
for band in analysis_df['lat_band'].dropna().unique():
    subset = analysis_df[analysis_df['lat_band'] == band]
    valid = subset.dropna(subset=['days30_mur_raw', 'bleaching_binary'])
    
    if len(valid) < 10 or valid['bleaching_binary'].sum() < 3:
        continue
    
    y_true = valid['bleaching_binary'].values
    y_score_days30 = valid['days30_mur_raw'].values
    
    try:
        auc_days30 = roc_auc_score(y_true, y_score_days30)
        
        # DHWも計算
        valid_dhw = subset.dropna(subset=['dhw_mur_raw', 'bleaching_binary'])
        if len(valid_dhw) >= 10:
            auc_dhw = roc_auc_score(valid_dhw['bleaching_binary'], valid_dhw['dhw_mur_raw'])
        else:
            auc_dhw = np.nan
        
        subgroup_results.append({
            'lat_band': band,
            'n': len(valid),
            'n_bleached': int(y_true.sum()),
            'bleach_rate': y_true.mean(),
            'auc_days30': auc_days30,
            'auc_dhw': auc_dhw
        })
    except:
        pass

if subgroup_results:
    subgroup_df = pd.DataFrame(subgroup_results)
    print("\n【緯度帯別 30℃日数 vs DHW の予測力比較】")
    print("-" * 70)
    print(f"{'緯度帯':<20} {'n':>5} {'白化率':>8} {'AUC(30℃)':>10} {'AUC(DHW)':>10}")
    print("-" * 70)
    for _, row in subgroup_df.iterrows():
        print(f"{row['lat_band']:<20} {row['n']:>5} {row['bleach_rate']:>8.1%} {row['auc_days30']:>10.3f} {row['auc_dhw']:>10.3f}")

# ============================================================
# 結果保存
# ============================================================

results_df.to_csv('processed/phase3_full_model_comparison.csv', index=False)
analysis_df.to_csv('processed/phase3_analysis_with_coraltemp.csv', index=False)

if subgroup_results:
    subgroup_df.to_csv('processed/phase3_subgroup_analysis.csv', index=False)

print("\n" + "=" * 60)
print("保存完了")
print("=" * 60)
print("- processed/phase3_full_model_comparison.csv")
print("- processed/phase3_analysis_with_coraltemp.csv")
print("- processed/phase3_subgroup_analysis.csv")

# ============================================================
# 結論サマリー
# ============================================================

print("\n" + "=" * 60)
print("【結論サマリー】")
print("=" * 60)

best = results_df.iloc[0]
print(f"\n最良モデル: {best['label']}")
print(f"  AUC: {best['auc']:.3f}")
print(f"  最適閾値: {best['optimal_threshold']:.1f}")
print(f"  感度/特異度: {best['sensitivity']:.2f} / {best['specificity']:.2f}")

# MUR vs CoralTemp比較
mur_days30 = results_df[results_df['indicator'] == 'days30_mur_raw']['auc'].values
ct_days30 = results_df[results_df['indicator'] == 'days30_coraltemp_raw']['auc'].values

if len(mur_days30) > 0 and len(ct_days30) > 0:
    print(f"\n【MUR vs CoralTemp（30℃日数）】")
    print(f"  MUR:       AUC = {mur_days30[0]:.3f}")
    print(f"  CoralTemp: AUC = {ct_days30[0]:.3f}")
    diff = mur_days30[0] - ct_days30[0]
    if abs(diff) < 0.02:
        print(f"  → 差は小さい（Δ={diff:+.3f}）")
    elif diff > 0:
        print(f"  → MURが優位（Δ={diff:+.3f}）")
    else:
        print(f"  → CoralTempが優位（Δ={diff:+.3f}）")

# 30℃日数 vs DHW 比較
best_days30 = results_df[results_df['indicator'].str.contains('days30')]['auc'].max()
best_dhw = results_df[results_df['indicator'].str.contains('dhw')]['auc'].max()
print(f"\n【30℃日数 vs DHW】")
print(f"  30℃日数最良: AUC = {best_days30:.3f}")
print(f"  DHW最良:     AUC = {best_dhw:.3f}")
print(f"  → 30℃日数が {best_days30 - best_dhw:+.3f} 優位")
