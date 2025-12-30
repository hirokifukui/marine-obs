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

### トップページ構成（index.html）

```
┌─────────────────────────────────────┐
│  ヒーロー                            │
│  「サンゴは声を出せない。            │
│   だから私たちが潜る。」             │
├─────────────────────────────────────┤
│  6枚ダッシュボードカード             │
│  [SST] [極端日数] [DHW]             │  ← 各詳細ページへリンク
│  [種別] [モニ1000] [濁度] ← SOON    │
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

---

## 対象地点

**カード表示順序：SST → 極端日数 → DHW**

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
2. 用語解説（Glossary）の充実
3. 6カードの残り3枚（種別脆弱性、モニ1000、濁度）

### 優先度：中
4. 観察報告フォームの実装
5. レスポンシブ調整（モバイル表示）

### 優先度：低
6. 静的JSON生成のGitHub Actions化
7. 地点拡張（モルディブ、タイなど）

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
| 2025-12-30 | 詳細ページ3枚完成（sst.html, dhw.html, extreme.html） |
| 2025-12-30 | トップページUI整理: KPIカード削除、6枚カードをヒーロー直下に移動 |
| 2025-12-30 | カード順序変更: SST → 極端日数 → DHW |
| 2025-12-30 | extreme_days.json に2025年データ追加 |
| 2025-12-30 | グローバル引用追加（Sully 2019, El-Khaled 2025, Saxby 2003, Singh 2023） |
| 2025-12-30 | SST日次更新をGitHub Actions化 |

---

*最終更新: 2025-12-30*

| 2025-12-30 | ダイバー向けページ拡張: コンディション判定バー、装備ガイド、サンゴ熱ストレス状況 追加 |
