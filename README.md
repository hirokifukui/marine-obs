# marine-obs.org

サンゴ熱ストレスモニタリングプロジェクト

## URLs

| 環境 | URL |
|------|-----|
| **本番** | https://marine-obs.org |
| **Vercel** | https://marine-obs.vercel.app |
| **GitHub** | https://github.com/hirokifukui/marine-obs |

## ローカルパス

```
/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs
```

---

## サイト構成

### ページ

| ページ | 内容 | 状態 |
|--------|------|------|
| index.html | トップページ（ダッシュボード） | ✅ 完成 |
| sst.html | SST詳細（水温解説、高温・低温両方） | ✅ 完成 |
| extreme.html | 極端日数詳細（高温・低温チャート） | ✅ 完成 |
| dhw.html | DHW詳細（2024年記録、瀬底研究引用） | ✅ 完成 |
| species.html | 種別脆弱性（勝者と敗者、16論文レビュー） | ✅ 完成 |

### トップページ構成（index.html）

```
┌─────────────────────────────────────┐
│  ヒーロー                            │
│  「サンゴは声を出せない。            │
│   だから私たちが潜る。」             │
├─────────────────────────────────────┤
│  6枚ダッシュボードカード             │
│  [SST] [極端日数] [DHW]             │  ← 各詳細ページへリンク
│  [種別] [モニ1000] [濁度]           │  ← 種別 ✅ 完成 / 他2枚 SOON
├─────────────────────────────────────┤
│  データソース                        │
├─────────────────────────────────────┤
│  フッター                            │
└─────────────────────────────────────┘
```

### 他ページ（SPAナビ）

- **Divers** - 海況モニター（Stormglassリアルタイム）
- **About** - プロジェクト説明
- **Glossary** - 用語解説

---

## 詳細ページの内容

### sst.html（海水温）
- 高温・低温両方のストレスを説明
- グローバル引用: Sully et al. 2019, El-Khaled et al. 2025, Saxby et al. 2003
- 30日トレンドチャート + 月別気候値チャート
- DHWページへの誘導リンク

### dhw.html（積算熱ストレス）
- **2024年記録イベント**: 万座DHW 7.53（22年間最高）
- 瀬底島研究テーブル: 1998, 2016年のDHWと死亡率
- NOAA Alert Level可視化
- 衛星 vs ローカル測定の乖離説明
- Singh et al. 2023（短期熱順応）

### extreme.html（極端水温日数）
- 高温日（≥30°C）と低温日（≤20°C）の両方
- 2025年サマリー: 🔥 4/14/4 高温 · ❄️ 0/0/49 低温
- 小笠原の低温脆弱性を強調
- 2003-2025年のチャート（2系列）

### species.html（種別脆弱性）**NEW**
- **勝者と敗者の構造**: Acropora/Montipora（敗者）vs Porites/Galaxea（勝者）
- 白化感受性を決める3因子: 形態・組織厚、共生藻タイプ、マイクロバイオーム
- 回復動態: Boom-Bust型（ミドリイシ）vs 緩やかな衰退型
- 大規模白化事例: モルディブ2016、沖縄・本部2002、ムーレア1991-2007
- ダイバーへの観察ポイント
- 16本の査読論文に基づく（Zoteroコレクション: ThermalStress-Bleaching）

---

## 対象地点

**カード表示順序：SST → 極端日数 → DHW → 種別脆弱性**

| コード | 名称 | 座標 | MMM |
|--------|------|------|-----|
| sesoko | 瀬底 | 26.6494, 127.8536 | 29.0℃ |
| manza | 万座 | 26.5080, 127.8540 | 29.0℃ |
| ogasawara | 小笠原 | 27.0942, 142.1919 | 28.5℃ |

---

## データソース

### リアルタイムデータ（Supabase API直接呼び出し）

| データ | テーブル | 更新頻度 | 更新元 |
|--------|----------|----------|--------|
| 海況モニター（Stormglass） | `marine_weather` | 3時間おき | GitHub Actions |
| 日次SST（NASA MUR） | `sst_daily` | 毎日JST 10:00 | GitHub Actions |

**Supabase設定（index.html内）:**
```javascript
const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
const SUPABASE_ANON_KEY = '...' // index.html内に記載
```

### 静的データ（JSONファイル）

| ファイル | 内容 | 更新方法 |
|----------|------|----------|
| `data/dhw_annual_peak.json` | DHW年次ピーク（2003-2025、3地点） | 手動でSQL実行→JSON生成→git push |
| `data/monthly_clim.json` | 月別気候値（3地点） | 同上 |
| `data/extreme_days.json` | 極端水温日数（高温・低温、2003-2025、3地点） | 同上 |
| `data/sst_recent.json` | SST最新値（3地点） | 同上 |

---

## ファイル構成

```
marine-obs/
├── index.html          # トップページ（ダッシュボード）
├── sst.html            # SST詳細ページ
├── dhw.html            # DHW詳細ページ
├── extreme.html        # 極端日数詳細ページ
├── species.html        # 種別脆弱性ページ **NEW**
├── hero.jpg            # ヒーロー背景（iStock 965393632）
├── diving.jpg          # Aboutページ用画像
├── logo.png            # ロゴ
├── data/
│   ├── dhw_annual_peak.json
│   ├── extreme_days.json
│   ├── monthly_clim.json
│   └── sst_recent.json
├── archive/            # 過去のバックアップ・スクリプト
└── README.md           # このファイル
```

---

## カラースキーム

```css
/* 地点別カラー（チャート用） */
--manza: #c05621;        /* 万座（オレンジ） */
--sesoko: #2b6cb0;       /* 瀬底（青） */
--ogasawara: #2f855a;    /* 小笠原（緑） */

/* ステータス */
--alert: #a65d5d;        /* 警報（渋い赤茶） */
--warning: #c4a35a;      /* 注意（落ち着いた琥珀） */
--safe: #5a9a7a;         /* 平常 */

/* 極端温度 */
--hot-color: #dc2626;    /* 高温（赤） */
--cold-color: #0891b2;   /* 低温（シアン） */
```

---

## 引用文献（詳細ページで使用）

| 論文 | 内容 | 使用箇所 |
|------|------|----------|
| Sully et al. 2019 (Nature Comms) | 3,351サイト、81カ国のグローバル白化分析 | sst.html, dhw.html |
| El-Khaled et al. 2025 (Comms Bio) | 低温ED50メトリクス | sst.html |
| Saxby et al. 2003 | Montipora低温ストレス | sst.html |
| Sakai et al. 2019 | 瀬底島2016年白化・死亡率 | dhw.html |
| Singh et al. 2023 | 短期熱順応・熱履歴効果 | dhw.html |
| van Woesik et al. 2011 | Winners and losers（14年追跡） | species.html |
| McClanahan et al. 2004 | 分類群が白化応答の52%を説明 | species.html |
| Sampayo et al. 2008 | 共生藻亜クレードによる耐性差異 | species.html |
| Pratchett et al. 2013 | ムーレア繰り返し白化 | species.html |
| Morais et al. 2021 | Boom-bust vs protracted decline | species.html |
| Pisapia et al. 2019 | モルディブ2016年白化 | species.html |

Zoteroコレクション: `ThermalStress-Bleaching` (RIIHGD8I)

---

## デプロイ

```bash
cd "/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs"
git add . && git commit -m "変更内容" && git push
```

Vercelが自動検知して約1分でデプロイ完了。

---

## 自動更新ジョブ（GitHub Actions）

### Stormglass → Supabase

| 項目 | 値 |
|------|-----|
| リポジトリ | https://github.com/hirokifukui/stormglass-updater |
| 実行間隔 | 3時間おき |
| 対象地点 | 9地点 |

### NASA MUR SST → Supabase

| 項目 | 値 |
|------|-----|
| リポジトリ | https://github.com/hirokifukui/sst-daily-updater |
| 実行間隔 | 毎日 JST 10:00 |
| データ遅延 | 3日（衛星公開遅延） |

---

## 今後の開発予定

### 優先度：高
1. ~~詳細ページ作成（dhw.html, sst.html, extreme.html）~~ ✅ 完了
2. ~~種別脆弱性ページ（species.html）~~ ✅ 完了
3. 用語解説（Glossary）の充実
4. 6カードの残り2枚（モニ1000、濁度）

### 優先度：中
5. 観察報告フォームの実装
6. レスポンシブ調整（モバイル表示）

### 優先度：低
7. 静的JSON生成のGitHub Actions化
8. 地点拡張（モルディブ、タイなど）

---

## 関連リソース

| リソース | 場所 |
|----------|------|
| **Obsidian** | `20_Project/MarineObservations/` |
| **Agent Skill** | `/mnt/skills/user/marine-observations/SKILL.md` |
| **Zotero** | ThermalStress-Bleaching (RIIHGD8I) |
| **Supabase** | https://supabase.com/dashboard/project/pegiuiblpliainpdggfj |

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2025-12-30 | **species.html完成**: 種別脆弱性ページ新規作成、index.htmlからリンク |
| 2025-12-30 | 詳細ページ3枚完成（sst.html, dhw.html, extreme.html） |
| 2025-12-30 | トップページUI整理: KPIカード削除、6枚カードをヒーロー直下に移動 |
| 2025-12-30 | カード順序変更: SST → 極端日数 → DHW |
| 2025-12-30 | extreme_days.json に2025年データ追加 |
| 2025-12-30 | グローバル引用追加（Sully 2019, El-Khaled 2025, Saxby 2003, Singh 2023） |
| 2025-12-30 | SST日次更新をGitHub Actions化 |
| 2025-12-30 | ダイバー向けページ拡張: 装備ガイド、サンゴ熱ストレス追加 |

---

*最終更新: 2025-12-30*

---

## spawning.html（サンゴ産卵予測）

### 概要
サンゴ産卵の科学的予測モデルに基づく解説ページ。22本の査読論文をベースに、産卵タイミングを分単位で予測する仕組みを解説。

### 構成
1. **ヒーロー**: 予測時刻（21:42 ± 23min）+ Dark period可視化
2. **導入**: なぜ分単位で予測できるか
3. **環境キュー階層**: 季節・月・日の3スケール予測モデル
4. **分子カスケード**: Yoshioka 2025の4波モデル（月光非依存）
5. **人為的攪乱**: 光害シフト、同期性崩壊（沈黙の脅威）
6. **産卵カレンダー**: 2026年6月（時刻ヒント付き）
7. **ダイバーガイド**: 観察推奨時期・機材
8. **参考文献**: 20本（DOIリンク、5カテゴリ分類）

### 科学的ハイライト
- **暗黒期間トリガー**: 日没→月の出の暗黒時間が産卵を誘発（Lin et al. 2021, PNAS）
- **月光非依存**: 内部プログラムは月光がなくても作動（Yoshioka et al. 2025）
- **光害の影響**: 人工光で産卵が1-3日早まる（Davies et al. 2023）
- **沈黙の脅威**: 同期性崩壊は目に見えない（Shlesinger & Loya 2019, Science）

### 文献管理
- Zoteroコレクション: `CoralSpawning` (H6VQ6NK9) — 28本
- 将来: Zotero Public Group化予定（構想: Obsidian `Inbox/Zotero_Public_Group構想_marine-obs文献共有.md`）

### バージョン履歴
| ファイル | 内容 |
|----------|------|
| spawning.html | v3（現行版、科学解説拡充） |
| spawning_v2.html | v2バックアップ |
| spawning_old.html | v1（初期版） |


| 2025-12-30 | **spawning.html完成**: サンゴ産卵予測ページ新規作成（22論文ベース） |
| 2025-12-30 | **sst.htmlデバッグ解決**: DOMContentLoaded問題 → GitHub Pages再デプロイで解決 |
| 2025-12-30 | フォルダ整理: バックアップファイル5件をarchive/に移動 |

---

## species.html（種別脆弱性）v2 詳細

### 2025-12-30 v2アップデート

| 項目 | v1 | v2 |
|------|-----|-----|
| ヒーローセクション | なし | ✅ 追加（52%統計ハイライト） |
| Story-box導入 | なし | ✅ 1998年沖縄白化の物語 |
| COMING SOON | 2箇所 | ✅ SVG図で実装 |
| 参考文献 | 6本（リストのみ） | ✅ 12本（DOI付、4カテゴリ） |

### 新規追加コンテンツ

**1. ヒーローセクション**
- キーメッセージ: 「分類群が白化応答の52%を説明する」（McClanahan 2020）
- サブメッセージ: 14年追跡が示す構造的持続性
- 統計ハイライト: 1998年沖縄大規模白化

**2. Story-box導入**
- 問いかけ: なぜ同じリーフで異なる応答が起きるか
- 3層の適応戦略: 形態、共生藻遺伝子型、マイクロバイオーム
- Loya et al. 2001の発見: Acropora -85% vs Porites <10%

**3. SVG図（COMING SOON解消）**

| 図 | 内容 |
|-----|------|
| 形態比較図 | 分岐型（薄い組織・高曝露）vs 塊状（厚い組織・緩衝）|
| 回復動態チャート | Boom-Bust型 vs Protracted Decline型の時系列 |

**4. 強化された参考文献（12本、4カテゴリ）**

| カテゴリ | 論文 |
|----------|------|
| **基盤研究** | Loya 2001, van Woesik 2011, Grottoli 2014 |
| **メカニズム** | McClanahan 2020, Wooldridge 2014, Maor-Landaw 2016, Sampayo 2007 |
| **回復動態** | Morais 2021, Pratchett 2013 |
| **事例研究** | Pisapia 2019, Sakai 2019, Singh 2023 |

### ファイルサイズ変化
- v1: 約900行
- v2: 1,262行（+40%）

### アーカイブ
- `archive/species_v1.html` — v1バックアップ

---

## CSS/JS外部化（2025-12-31）

### 背景
index.htmlが3,378行・120KBに肥大化し、Claude編集時に頻繁に停止する問題が発生。CSS/JSを外部ファイルに分割して軽量化。

### 実施内容

**分割前:**
```
index.html: 3,378行 / 120KB（CSS・JS全てインライン）
```

**分割後:**
```
index.html: 700行 / 44KB（63%削減）
css/main.css: 38KB
js/
├── lang.js: 2KB（言語切替）
├── chart-data.js: 5KB（SST/DHWチャートデータ）
├── marine-monitor.js: 14KB（Supabase連携）
├── gear-recs.js: 8KB（装備推奨）
└── charts.js: 10KB（Chart.js初期化・Extremeチャート）
```

### 修正点
- `css/main.css`内の画像パスを修正: `url('hero.jpg')` → `url('../hero.jpg')`
- Chart.js CDNの重複読み込みを削除

### 既知の問題：チャートデータの不整合

現在、チャートデータの取得方法が統一されていない:

| チャート | データ取得方法 | ファイル |
|----------|----------------|----------|
| SST | JSにハードコード | js/chart-data.js |
| DHW | JSにハードコード | js/chart-data.js |
| Extreme | fetch()でJSON取得 | js/charts.js |

**問題:**
- ローカル（file://）では fetch() がCORS制限でブロックされる
- Extremeチャートのみローカルで表示されない（デプロイ後は正常）

**TODO（優先度：中）:**
- 全チャートをJSON fetch方式に統一する
- `data/sst_monthly.json`, `data/dhw_trend.json` を作成
- `chart-data.js` を廃止し、`charts.js` に統合

### ファイル構成（更新後）

```
marine-obs/
├── index.html          # 700行に軽量化
├── css/
│   └── main.css        # 全CSS
├── js/
│   ├── lang.js
│   ├── chart-data.js   # TODO: JSON化して廃止予定
│   ├── marine-monitor.js
│   ├── gear-recs.js
│   └── charts.js
├── data/
│   ├── dhw_annual_peak.json
│   ├── extreme_days.json
│   ├── monthly_clim.json
│   └── sst_recent.json
├── (HTMLページ群)
├── (画像ファイル群)
└── archive/            # バックアップ
```

### 変更履歴追記

| 日付 | 変更内容 |
|------|----------|
| 2025-12-31 | **CSS/JS外部化**: index.html 3,378行→700行に軽量化、css/・js/フォルダ作成 |
| 2025-12-31 | フォルダ整理: .bakファイル4件をarchive/に移動、重複画像・空ファイル削除 |

---

*最終更新: 2025-12-31*
