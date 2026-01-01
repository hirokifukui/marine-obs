# 海洋の徴候 / marine-obs.org

サンゴ熱ストレスモニタリングプロジェクト。NOAAやNASAの衛星データを翻訳し、日本のダイバーが自分の潜る海の状態を理解できるようにする。

## URL

- **本番**: https://marine-obs.org
- **GitHub**: https://github.com/hirokifukui/marine-obs
- **Vercel**: https://marine-obs.vercel.app

## ローカル

```
/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs
```

---

## ページ一覧

| ページ | 行数 | 内容 |
|--------|------|------|
| index.html | 724 | トップ（ダッシュボード6カード + About + Glossary + For Divers） |
| sst.html | 1,164 | 海水温詳細（高温・低温、30日トレンド、月別気候値） |
| extreme.html | 1,182 | 極端水温日数（2003-2025、高温・低温チャート） |
| dhw.html | 1,296 | 積算熱ストレス（2024年記録、瀬底研究、Singh 2023） |
| species.html | 1,262 | 種別脆弱性（勝者と敗者、16論文、SVG図） |
| spawning.html | 1,871 | サンゴ産卵予測（22論文、Yoshioka 2025、2026年予測） |
| turbidity.html | 939 | 濁度観測（COMING SOON） |

### トップページ構成

```
ヒーロー「サンゴは声を出せない。だから私たちが潜る。」
    ↓
導入セクション（For Divers / About へリンク）
    ↓
6カード: [SST] [極端日数] [DHW] [種別] [産卵予測] [モニ1000 SOON]
    ↓
データソース
    ↓
For Divers（海況モニター + サンゴ熱ストレス + 装備ガイド）
    ↓
About（日英）
    ↓
Glossary（用語解説）
    ↓
フッター
```

---

## ファイル構成

```
marine-obs/
├── index.html
├── sst.html / extreme.html / dhw.html / species.html / spawning.html / turbidity.html
├── css/main.css
├── js/
│   ├── lang.js          # 言語切替
│   ├── charts.js        # 全チャート初期化（JSON fetch）
│   ├── marine-monitor.js # Supabase連携（海況モニター）
│   └── gear-recs.js     # 装備推奨
├── data/
│   ├── sst_card.json / dhw_card.json / spawning_card.json  # カード用
│   ├── extreme_days.json / dhw_annual_peak.json            # 詳細ページ用
│   ├── monthly_clim.json / sst_recent.json                 # SST詳細用
├── hero.jpg / diving.jpg / logo.png
├── archive/             # バックアップ
└── README.md
```

---

## データソース

### リアルタイム（Supabase経由）

| データ | テーブル | 更新 | GitHub Actions |
|--------|----------|------|----------------|
| 海況（Stormglass） | marine_weather | 3時間 | stormglass-updater |
| SST（NASA MUR） | sst_daily | 毎日10:00 JST | sst-daily-updater |

### 静的（JSON）

手動でSQL実行 → JSON生成 → git push。将来的にGitHub Actions化予定。

---

## 対象地点

| コード | 名称 | 座標 | MMM |
|--------|------|------|-----|
| manza | 万座 | 26.5080, 127.8540 | 29.0℃ |
| sesoko | 瀬底 | 26.6494, 127.8536 | 29.0℃ |
| ogasawara | 小笠原 | 27.0942, 142.1919 | 28.5℃ |

---

## カラー

```css
/* 地点 */
--manza: #c05621;      /* オレンジ */
--sesoko: #2b6cb0;     /* 青 */
--ogasawara: #2f855a;  /* 緑 */

/* ステータス */
--alert: #a65d5d;      /* 警報 */
--warning: #c4a35a;    /* 注意 */
--safe: #5a9a7a;       /* 平常 */

/* 極端温度 */
--hot-color: #dc2626;  /* 高温 */
--cold-color: #0891b2; /* 低温 */
```

---

## デプロイ

```bash
cd "/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs"
git add . && git commit -m "変更内容" && git push
```

Vercel自動デプロイ（約1分）。

---

## ローカル開発

JSON fetchのCORS制限回避のためローカルサーバーを使用：

```bash
cd "/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs"
python3 -m http.server 8000
# → http://localhost:8000
```

---

## 主要文献

### 温度ストレス・白化
| 論文 | 内容 | 使用箇所 |
|------|------|----------|
| Sakai 2019 | 瀬底2016白化、DHW現地値 | dhw.html |
| Singh 2023 | 短期熱順応、熱履歴効果 | dhw.html |
| Sully 2019 | グローバル白化3,351サイト | sst.html |
| El-Khaled 2025 | 低温ED50メトリクス | sst.html |

### 種別脆弱性
| 論文 | 内容 |
|------|------|
| van Woesik 2011 | Winners and losers 14年追跡 |
| McClanahan 2020 | 分類群が応答の52%を説明 |
| Loya 2001 | 1998年沖縄、Acropora -85% vs Porites <10% |
| Morais 2021 | Boom-bust vs protracted decline |

### サンゴ産卵
| 論文 | 内容 |
|------|------|
| Yoshioka 2025 | 4波分子カスケード、月光非依存 |
| Lin 2021 (PNAS) | 暗黒期間トリガー |
| Davies 2023 | 光害で産卵1-3日早まる |
| Shlesinger & Loya 2019 (Science) | 同期性崩壊（沈黙の脅威） |

**Zoteroコレクション**
- ThermalStress-Bleaching (RIIHGD8I) — 30件
- CoralSpawning (H6VQ6NK9) — 28件

---

## 今後の開発

| 優先度 | 内容 |
|--------|------|
| **高** | 観察報告フォーム（Supabase） |
| **高** | For Diversページ再構築（実用性重視） |
| **中** | モニ1000カード実装（2026年1月データ受領待ち） |
| **中** | AI解説セクション（ニュース＋文献翻訳） |
| **低** | 静的JSON生成のGitHub Actions化 |
| **低** | 地点拡張（モルディブ、タイ） |

---

## 関連リソース

| リソース | 場所 |
|----------|------|
| Obsidian | 20_Project/MarineObservations/ |
| Agent Skill | /mnt/skills/user/marine-observations/SKILL.md |
| Zotero | ThermalStress-Bleaching, CoralSpawning |
| Supabase | pegiuiblpliainpdggfj |

---

*最終更新: 2025-01-01*
