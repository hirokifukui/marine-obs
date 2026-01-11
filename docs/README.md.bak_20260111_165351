# 海洋の徴候 / marine-obs.org

サンゴ熱ストレスモニタリング。

## URL
- 本番: https://marine-obs.org
- GitHub: https://github.com/hirokifukui/marine-obs

## ローカル
```
/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs
```

## ページ
| ページ | 内容 |
|--------|------|
| index.html | ダッシュボード |
| sst.html | 海水温 |
| extreme.html | 極端水温日数 |
| dhw.html | 積算熱ストレス |
| light-adjusted-dhw.html | 光補正DHW |
| enso.html | ENSO監視 |
| climate-drivers.html | 気候ドライバー |
| climate-trend.html | 長期トレンド |
| chlorophyll-bleaching.html | クロロフィルと白化 |
| dissolved-oxygen-bleaching.html | 溶存酸素と白化 |
| global-bleaching.html | 世界の白化状況 |
| japan-bleaching.html | 日本の白化状況 |
| sekisei-cover.html | 石西礁湖被度グラフ（iframe用） |
| field-monitoring.html | 現場モニタリング（計画中） |
| bleaching.html | 白化とは |
| vulnerability.html | 種別脆弱性 |
| coral-basics.html | サンゴとは |
| species-guide.html | サンゴ図鑑 |
| spawning.html | サンゴ産卵予測 |
| conditions.html | 海況 |
| weather.html | 天気図 |
| about.html | このサイトについて |
| glossary.html | 用語解説 |
| datasources.html | データソース |
| contact.html | お問い合わせ |

## 構成
```
css/  main.css, dhw.css, extreme.css, vulnerability.css, species-guide.css, spawning.css, field-monitoring.css, contact.css, global-bleaching.css, bleaching.css
js/  lang.js, lang-simple.js, charts.js, marine-monitor.js, gear-recs.js
data/  *.json（チャート用、一部は未使用）
sql/  RPC関数定義
```

## データソース
| データ | ソース |
|--------|--------|
| SST最新値 | Supabase `sst_daily` テーブル |
| 極端日数 | Supabase RPC `get_extreme_days()` |
| DHWピーク | Supabase RPC `get_dhw_all_years()` + `dhw_annual_peak` テーブル |
| UV・日出日没 | Supabase `uv_daily` テーブル（OpenWeather） |
| 潮汐 | Supabase `tide_extremes` テーブル |
| 日次更新 | `~/Scripts/scheduled-jobs/sync-sst-daily/` |

## 恩納村予測（月次更新）
```bash
cd ~/Scripts/scheduled-jobs/sync-climate-indices
python3 update_onna_forecast.py
```

## Supabase RPC関数
| 関数 | 用途 |
|------|------|
| `get_extreme_days()` | 年別極端日数（高温・低温） |
| `get_dhw_all_years()` | 2003-現在の全年ピークDHW |
| `get_dhw_annual_peak(site, year)` | 指定年のピークDHW |
| `calc_dhw(site, date)` | 指定日のDHW計算 |

## 画像処理
ImageMagick + Ghostscript でEPS→PNG/ICO変換可能。

## デプロイ
```bash
git add . && git commit -m "msg" && git push
```
Vercel自動デプロイ。

## バックアップ
`backups/` フォルダに保存。**削除禁止**。

---
*2026-01-11*
