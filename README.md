# marine-obs.org

サンゴ熱ストレスモニタリングプロジェクト

## URLs

| 環境 | URL |
|------|-----|
| **本番** | https://marine-obs.org |
| **Vercel** | https://marine-obs.vercel.app |
| **GitHub** | https://github.com/hirokifukui/marine-obs |

---

## データソース

### リアルタイムデータ（Supabase API直接呼び出し）

| データ | テーブル | 更新頻度 | 更新元 |
|--------|----------|----------|--------|
| 海況モニター（Stormglass） | `marine_weather` | 3時間おき | GitHub Actions |

**Supabase設定（index.html内）:**
```javascript
const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
// または https://api.marine-obs.org
```

### 静的データ（JSONファイル）

| ファイル | 内容 | 更新方法 |
|----------|------|----------|
| `data/dhw_annual_peak.json` | DHW年次ピーク（2003-2024） | 手動でSQL実行→JSON生成→git push |
| `data/monthly_clim.json` | 月別気候値 | 同上 |
| `data/extreme_days.json` | 極端水温日数 | 同上 |
| `data/sst_recent.json` | SST最新値 | 同上 |

---

## 自動更新ジョブ

### Stormglass → Supabase（GitHub Actions）

| 項目 | 値 |
|------|-----|
| リポジトリ | https://github.com/hirokifukui/stormglass-updater |
| 実行間隔 | 3時間おき（JST 0,3,6,9,12,15,18,21時） |
| 対象地点 | 9地点（瀬底、万座、小笠原、八丈島、竹富、モルディブ4地点） |

### SST → Supabase（ローカル launchd）

| 項目 | 値 |
|------|-----|
| スクリプト | `~/Dropbox (個人)/Scripts/scheduled-jobs/sync-sst-daily/sync.py` |
| データソース | NASA MUR SST |
| 遅延 | 3日（衛星データの公開遅延） |

---

## デプロイ

```bash
cd "/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot"
git add . && git commit -m "変更内容" && git push
```

Vercelが自動検知して約1分でデプロイ完了。

---

## ファイル構成

```
marine-obs-pilot/
├── index.html          # メインページ（全セクション含む）
├── logo.png            # ロゴ（色調整済み）
├── hero.jpg            # ヒーロー背景画像
├── data/
│   ├── dhw_annual_peak.json
│   ├── extreme_days.json
│   ├── monthly_clim.json
│   └── sst_recent.json
├── archive/            # バックアップ
└── README.md           # このファイル
```

---

## カラースキーム

```css
/* メインカラー */
--accent-teal: #2b6cb0;      /* 瀬底（青） */
--accent-warm: #c05621;      /* 万座（オレンジ） */
--accent-green: #2f855a;     /* 小笠原（緑） */

/* ステータス */
--alert: #a65d5d;            /* 警報（渋い赤茶） */
--warning: #c4a35a;          /* 注意（落ち着いた琥珀） */
--safe: #5a9a7a;             /* 平常 */
```

---

## DNS設定

| レコード | タイプ | 値 | 管理場所 |
|----------|--------|-----|---------|
| marine-obs.org | A | 216.198.79.1 | Xserver |
| api.marine-obs.org | CNAME | pegiuiblpliainpdggfj.supabase.co | Xserver |

---

## 静的データの更新手順

### 1. Supabaseからデータ取得

```sql
-- DHW年次ピーク
SELECT * FROM get_dhw_annual_peak('sesoko', 2024);

-- 極端日数
SELECT * FROM count_extreme_days('sesoko', 2024, 30, 'above');
```

### 2. JSONファイル更新

`data/` 内の該当ファイルを更新

### 3. デプロイ

```bash
git add . && git commit -m "Update data" && git push
```

---

## 関連リソース

- **Obsidian**: `20_Project/MarineObservations/`
- **Agent Skill**: `/mnt/skills/user/marine-observations/SKILL.md`
- **Zotero**: ThermalStress-Bleaching (RIIHGD8I)
- **Supabase**: https://supabase.com/dashboard/project/pegiuiblpliainpdggfj

---

## 今後の開発予定

### 優先度：高
1. 詳細ページ作成（dhw.html, sst.html, extreme.html）
2. 用語解説（Glossary）の充実
3. 先行文献の紹介

### 優先度：中
4. 観察報告フォームの実装
5. 6カードの充実（COMING SOON解消）

### 優先度：低
6. レスポンシブ調整
7. SST自動更新のGitHub Actions化

---

*最終更新: 2025-12-30*
