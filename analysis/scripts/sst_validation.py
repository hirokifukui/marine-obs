#!/usr/bin/env python3
"""
モニ1000 衛星SST vs 実測水温 検証分析
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Supabase接続
from supabase import create_client
config_path = Path.home() / ".config" / "supabase_marine.json"
with open(config_path) as f:
    config = json.load(f)
supabase = create_client(config["url"], config["key"])

print("=" * 60)
print("モニ1000 衛星SST vs 実測水温 検証分析")
print("=" * 60)

# 1. データ取得
print("\n[1] データ取得中...")

sat_response = supabase.table("moni1000_sst_satellite").select("*").execute()
sat_df = pd.DataFrame(sat_response.data)
sat_df['date'] = pd.to_datetime(sat_df['date'])
sat_df = sat_df.rename(columns={'sst': 'sst_satellite'})
print(f"  衛星SST: {len(sat_df):,}件")

insitu_path = Path.home() / "Dropbox (個人)" / "Scripts" / "marine-obs" / "analysis" / "processed" / "moni1000_temperature_daily_v2.csv"
insitu_df = pd.read_csv(insitu_path)
insitu_df['date'] = pd.to_datetime(insitu_df['date'])
insitu_df = insitu_df.rename(columns={'temp_mean': 'sst_insitu'})
print(f"  実測水温: {len(insitu_df):,}件")

# 2. データマージ
print("\n[2] データマージ...")
merged = pd.merge(
    sat_df[['site_no', 'spot_no', 'date', 'sst_satellite']],
    insitu_df[['site_no', 'spot_no', 'date', 'sst_insitu', 'depth']],
    on=['site_no', 'spot_no', 'date'],
    how='inner'
)
print(f"  マッチしたペア: {len(merged):,}件")
print(f"  地点数: {merged.groupby(['site_no', 'spot_no']).ngroups}")

# 3. 全体の基本統計
print("\n[3] 全体の基本統計")
print("-" * 40)

merged['bias'] = merged['sst_satellite'] - merged['sst_insitu']
bias_mean = merged['bias'].mean()
bias_std = merged['bias'].std()
rmse = np.sqrt((merged['bias'] ** 2).mean())
mae = merged['bias'].abs().mean()
r, p = stats.pearsonr(merged['sst_satellite'], merged['sst_insitu'])

print(f"  バイアス（平均誤差）: {bias_mean:+.3f}℃ (±{bias_std:.3f})")
print(f"  RMSE: {rmse:.3f}℃")
print(f"  MAE: {mae:.3f}℃")
print(f"  相関係数: r = {r:.4f} (p < 0.001)")

# 4. 地点別の相関係数
print("\n[4] 地点別相関係数")
print("-" * 40)

site_stats = []
for (site, spot), group in merged.groupby(['site_no', 'spot_no']):
    if len(group) >= 30:
        r_site, _ = stats.pearsonr(group['sst_satellite'], group['sst_insitu'])
        bias_site = group['bias'].mean()
        rmse_site = np.sqrt((group['bias'] ** 2).mean())
        site_stats.append({
            'site_no': site, 'spot_no': spot, 'n': len(group),
            'r': r_site, 'bias': bias_site, 'rmse': rmse_site
        })

site_df = pd.DataFrame(site_stats)
print(f"  分析対象地点: {len(site_df)}")
print(f"  相関係数 r:")
print(f"    中央値: {site_df['r'].median():.4f}")
print(f"    範囲: {site_df['r'].min():.4f} - {site_df['r'].max():.4f}")

# 5. 異質性検定
print("\n[5] 異質性検定")
print("-" * 40)

site_df['z'] = 0.5 * np.log((1 + site_df['r']) / (1 - site_df['r']))
site_df['w'] = site_df['n'] - 3
z_bar = (site_df['z'] * site_df['w']).sum() / site_df['w'].sum()
Q = ((site_df['w'] * (site_df['z'] - z_bar) ** 2)).sum()
df_q = len(site_df) - 1
p_q = 1 - stats.chi2.cdf(Q, df_q)
I2 = max(0, (Q - df_q) / Q * 100) if Q > 0 else 0

print(f"  Cochran's Q = {Q:.2f} (df = {df_q})")
print(f"  p値 = {p_q:.4f}")
print(f"  I² = {I2:.1f}%")

# 6. 線形回帰
print("\n[6] 線形回帰（全体）")
print("-" * 40)
slope, intercept, r_value, p_value, std_err = stats.linregress(
    merged['sst_satellite'], merged['sst_insitu']
)
print(f"  実測 = {slope:.4f} × 衛星 + {intercept:.4f}")
print(f"  R² = {r_value**2:.4f}")

# 7. 混合効果モデル
print("\n[7] 混合効果モデル")
print("-" * 40)
try:
    import statsmodels.formula.api as smf
    merged['site_spot'] = merged['site_no'].astype(str) + '_' + merged['spot_no'].astype(str)
    
    model = smf.mixedlm("sst_insitu ~ sst_satellite", merged, groups=merged["site_spot"], re_formula="~sst_satellite")
    result = model.fit()
    
    print(f"  固定効果（傾き）: {result.fe_params['sst_satellite']:.4f}")
    print(f"  固定効果（切片）: {result.fe_params['Intercept']:.4f}")
    re_cov = result.cov_re
    print(f"  ランダム効果SD（傾き）: {np.sqrt(re_cov.iloc[1,1]):.4f}")
    slope_sd = np.sqrt(re_cov.iloc[1,1])
    cv = slope_sd / result.fe_params['sst_satellite'] * 100
    print(f"  傾きの変動係数: {cv:.2f}%")
except Exception as e:
    print(f"  エラー: {e}")

# 8. サマリー
print("\n" + "=" * 60)
print("結果サマリー")
print("=" * 60)
print(f"バイアス: {bias_mean:+.2f}℃ | RMSE: {rmse:.2f}℃ | r = {r:.3f}")
print(f"I² = {I2:.1f}% → {'地点間で一貫' if I2 < 25 else '地点間にばらつき'}")
print(f"補正式: 実測 = {slope:.3f} × 衛星 + {intercept:.2f}")

# CSV出力
site_df.to_csv('processed/sst_validation_by_site.csv', index=False)
merged[['site_no','spot_no','date','sst_satellite','sst_insitu','bias']].to_csv('processed/sst_validation_paired.csv', index=False)
print("\nCSV出力完了")
