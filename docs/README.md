# marine-obs.org

サンゴ熱ストレスモニタリング。

## URL
- 本番: https://marine-obs.org
- GitHub: https://github.com/hirokifukui/marine-obs
- ローカル: `~/Dropbox (個人)/Scripts/marine-obs`

## ナビゲーション構造
| カテゴリ | ページ |
|---------|--------|
| モニタリング | sst, extreme, dhw, light-adjusted-dhw, field-monitoring |
| 気候 | enso, climate-drivers, climate-trend |
| 白化 | bleaching, vulnerability, chlorophyll-bleaching, dissolved-oxygen-bleaching, global-bleaching, japan-bleaching |
| サンゴを知る | coral-basics, species-guide, spawning |
| ダイバー向け | conditions, weather |
| リファレンス | about, glossary, datasources, contact |

その他: index（ダッシュボード）, sekisei-cover（iframe用）

## データソース
| データ | ソース |
|--------|--------|
| SST/DHW | Supabase `sst_daily` + RPC関数 |
| 気象 | Stormglass API |
| 日次更新 | `~/Scripts/scheduled-jobs/sync-sst-daily/` |

## 月次作業
```bash
cd ~/Scripts/scheduled-jobs/sync-climate-indices
python3 update_onna_forecast.py
```

## デプロイ
```bash
git add . && git commit -m "msg" && git push
```

## バックアップ
`backups/` フォルダ。**削除禁止**。

---
*2026-01-11*
