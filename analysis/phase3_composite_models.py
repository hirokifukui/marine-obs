#!/usr/bin/env python3
"""
Phase 3 補足: 複合モデルの検証
"""

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("複合モデル検証")
print("=" * 70)

# データ読み込み
df = pd.read_csv('processed/phase3_analysis_with_coraltemp.csv')
print(f"\nデータ: {len(df)} 件")

# 白化二値化
df['bleaching_binary'] = (df['bleaching_all'] > 10).astype(int)

# 緯度帯
df['lat_band'] = pd.cut(
    df['lat'], 
    bins=[23, 26, 28, 30, 35],
    labels=['八重山', '沖縄本島', '奄美', '本州']
)

# 環境タイプをダミー変数化
df['is_outer'] = (df['env_group'] == '外洋系').astype(int)
df['is_closed'] = (df['env_group'] == '閉鎖系').astype(int)
df['is_mid'] = (df['env_group'] == '中間系').astype(int)

# 有効データ
valid = df.dropna(subset=['days30_mur_raw', 'dhw_mur_raw', 'bleaching_binary', 'lat'])
print(f"有効データ: {len(valid)} 件（白化: {valid['bleaching_binary'].sum()} 件）")

y = valid['bleaching_binary'].values

# ============================================================
# 1. 単一指標のベースライン
# ============================================================

print("\n" + "=" * 70)
print("1. 単一指標のベースライン")
print("=" * 70)

single_indicators = {
    'days30_mur_raw': '30℃日数',
    'dhw_mur_raw': 'DHW MUR',
    'dhw_mur_corr_adj': 'DHW補正+MMM調整',
}

baselines = {}
for col, label in single_indicators.items():
    x = valid[col].values
    auc = roc_auc_score(y, x)
    baselines[col] = auc
    print(f"{label:<20}: AUC = {auc:.3f}")

# ============================================================
# 2. 2変数複合モデル
# ============================================================

print("\n" + "=" * 70)
print("2. 2変数複合モデル（ロジスティック回帰）")
print("=" * 70)

def fit_logistic_auc(X, y):
    """ロジスティック回帰でAUCを計算"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_scaled, y)
    y_prob = model.predict_proba(X_scaled)[:, 1]
    auc = roc_auc_score(y, y_prob)
    return auc, model, scaler

# 2変数の組み合わせ
combos_2var = [
    (['days30_mur_raw', 'dhw_mur_raw'], '30℃日数 + DHW'),
    (['days30_mur_raw', 'lat'], '30℃日数 + 緯度'),
    (['days30_mur_raw', 'is_outer'], '30℃日数 + 外洋系ダミー'),
    (['dhw_mur_raw', 'lat'], 'DHW + 緯度'),
    (['dhw_mur_raw', 'is_outer'], 'DHW + 外洋系ダミー'),
]

results_2var = []
for cols, label in combos_2var:
    X = valid[cols].values
    auc, model, _ = fit_logistic_auc(X, y)
    improvement = auc - baselines['days30_mur_raw']
    results_2var.append({
        'model': label,
        'vars': cols,
        'auc': auc,
        'improvement': improvement
    })
    print(f"{label:<30}: AUC = {auc:.3f} (Δ{improvement:+.3f})")

# ============================================================
# 3. 3変数以上の複合モデル
# ============================================================

print("\n" + "=" * 70)
print("3. 3変数以上の複合モデル")
print("=" * 70)

combos_3plus = [
    (['days30_mur_raw', 'dhw_mur_raw', 'lat'], '30℃日数 + DHW + 緯度'),
    (['days30_mur_raw', 'dhw_mur_raw', 'is_outer'], '30℃日数 + DHW + 外洋系'),
    (['days30_mur_raw', 'lat', 'is_outer'], '30℃日数 + 緯度 + 外洋系'),
    (['days30_mur_raw', 'dhw_mur_raw', 'lat', 'is_outer'], '30℃日数 + DHW + 緯度 + 外洋系'),
    (['days30_mur_raw', 'dhw_mur_raw', 'lat', 'is_outer', 'is_closed'], 'フルモデル'),
]

results_3plus = []
for cols, label in combos_3plus:
    X = valid[cols].values
    auc, model, scaler = fit_logistic_auc(X, y)
    improvement = auc - baselines['days30_mur_raw']
    results_3plus.append({
        'model': label,
        'vars': cols,
        'auc': auc,
        'improvement': improvement
    })
    print(f"{label:<40}: AUC = {auc:.3f} (Δ{improvement:+.3f})")

# ============================================================
# 4. 最良複合モデルの詳細
# ============================================================

print("\n" + "=" * 70)
print("4. 最良複合モデルの詳細")
print("=" * 70)

# 全結果を統合
all_results = results_2var + results_3plus
best_model = max(all_results, key=lambda x: x['auc'])

print(f"\n最良モデル: {best_model['model']}")
print(f"AUC: {best_model['auc']:.3f}")
print(f"改善幅: {best_model['improvement']:+.3f}")

# 最良モデルの係数を確認
X_best = valid[best_model['vars']].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_best)
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_scaled, y)

print(f"\n【係数（標準化後）】")
for var, coef in zip(best_model['vars'], model.coef_[0]):
    print(f"  {var:<20}: {coef:+.3f}")
print(f"  切片: {model.intercept_[0]:+.3f}")

# ROC曲線用のデータ
y_prob_best = model.predict_proba(X_scaled)[:, 1]
fpr, tpr, thresh = roc_curve(y, y_prob_best)
youden = tpr - fpr
opt_idx = np.argmax(youden)

print(f"\n【最適閾値での性能】")
print(f"  確率閾値: {thresh[opt_idx]:.3f}")
print(f"  感度: {tpr[opt_idx]:.3f}")
print(f"  特異度: {1 - fpr[opt_idx]:.3f}")

# ============================================================
# 5. 交互作用項の検証
# ============================================================

print("\n" + "=" * 70)
print("5. 交互作用項の検証")
print("=" * 70)

# 30℃日数 × 緯度
valid['days30_x_lat'] = valid['days30_mur_raw'] * valid['lat']
# DHW × 緯度
valid['dhw_x_lat'] = valid['dhw_mur_raw'] * valid['lat']
# 30℃日数 × 外洋系
valid['days30_x_outer'] = valid['days30_mur_raw'] * valid['is_outer']

interaction_models = [
    (['days30_mur_raw', 'lat', 'days30_x_lat'], '30℃日数 × 緯度（交互作用）'),
    (['dhw_mur_raw', 'lat', 'dhw_x_lat'], 'DHW × 緯度（交互作用）'),
    (['days30_mur_raw', 'is_outer', 'days30_x_outer'], '30℃日数 × 外洋系（交互作用）'),
    (['days30_mur_raw', 'dhw_mur_raw', 'lat', 'days30_x_lat'], '30℃日数 + DHW + 緯度交互作用'),
]

for cols, label in interaction_models:
    X = valid[cols].values
    auc, _, _ = fit_logistic_auc(X, y)
    improvement = auc - baselines['days30_mur_raw']
    print(f"{label:<45}: AUC = {auc:.3f} (Δ{improvement:+.3f})")

# ============================================================
# 6. 緯度帯別の最適モデル
# ============================================================

print("\n" + "=" * 70)
print("6. 緯度帯別の最適モデル")
print("=" * 70)

for band in ['八重山', '沖縄本島', '奄美', '本州']:
    subset = valid[valid['lat_band'] == band]
    if len(subset) < 15 or subset['bleaching_binary'].sum() < 3:
        print(f"{band}: データ不足")
        continue
    
    y_sub = subset['bleaching_binary'].values
    
    # 単一指標
    auc_days30 = roc_auc_score(y_sub, subset['days30_mur_raw'])
    auc_dhw = roc_auc_score(y_sub, subset['dhw_mur_raw'])
    
    # 複合モデル
    X_combo = subset[['days30_mur_raw', 'dhw_mur_raw']].values
    auc_combo, _, _ = fit_logistic_auc(X_combo, y_sub)
    
    print(f"\n{band} (n={len(subset)}, 白化率={y_sub.mean():.1%}):")
    print(f"  30℃日数: {auc_days30:.3f}")
    print(f"  DHW:     {auc_dhw:.3f}")
    print(f"  複合:    {auc_combo:.3f}")
    
    if auc_dhw > auc_days30:
        print(f"  → DHWが優位")
    elif auc_combo > max(auc_days30, auc_dhw) + 0.02:
        print(f"  → 複合モデルが有効")
    else:
        print(f"  → 30℃日数で十分")

# ============================================================
# 7. 結果まとめ
# ============================================================

print("\n" + "=" * 70)
print("7. 結論")
print("=" * 70)

# 全モデルをAUC順にソート
all_models = [
    {'model': '30℃日数（単独）', 'auc': baselines['days30_mur_raw'], 'vars': 1},
    {'model': 'DHW（単独）', 'auc': baselines['dhw_mur_raw'], 'vars': 1},
]
for r in results_2var + results_3plus:
    all_models.append({
        'model': r['model'],
        'auc': r['auc'],
        'vars': len(r['vars'])
    })

all_models_df = pd.DataFrame(all_models).sort_values('auc', ascending=False)

print("\n【全モデルランキング】")
print("-" * 60)
print(f"{'モデル':<40} {'変数数':>4} {'AUC':>6}")
print("-" * 60)
for _, row in all_models_df.head(10).iterrows():
    print(f"{row['model']:<40} {row['vars']:>4} {row['auc']:>6.3f}")

# 改善の有意性
best_auc = all_models_df.iloc[0]['auc']
baseline_auc = baselines['days30_mur_raw']
improvement = best_auc - baseline_auc

print(f"\n【結論】")
print(f"ベースライン（30℃日数単独）: AUC = {baseline_auc:.3f}")
print(f"最良複合モデル: AUC = {best_auc:.3f}")
print(f"改善幅: {improvement:+.3f}")

if improvement < 0.02:
    print(f"\n→ 複合モデルの改善効果は限定的（Δ < 0.02）")
    print(f"→ シンプルな30℃日数単独モデルを推奨")
elif improvement < 0.05:
    print(f"\n→ 複合モデルに小さな改善効果あり")
    print(f"→ 実装コストとのトレードオフで判断")
else:
    print(f"\n→ 複合モデルに明確な改善効果あり")
    print(f"→ 複合モデルの採用を推奨")

# 結果保存
all_models_df.to_csv('processed/phase3_composite_model_comparison.csv', index=False)
print(f"\n保存: processed/phase3_composite_model_comparison.csv")
