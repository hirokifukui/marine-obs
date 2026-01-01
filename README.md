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
| index.html | トップ（6カード + About + Glossary + For Divers） |
| sst.html | 海水温 |
| extreme.html | 極端水温日数 |
| dhw.html | 積算熱ストレス |
| species.html | 種別脆弱性 |
| spawning.html | サンゴ産卵予測 |

## 構成
```
css/main.css
js/  lang.js, charts.js, marine-monitor.js, gear-recs.js
data/  *.json（チャート用、一部は未使用）
```

## データソース
SST最新値: Supabase動的取得（`sst_daily`テーブル）
極端日数: Supabase RPC `get_extreme_days()`
日次更新: `~/Scripts/scheduled-jobs/sync-sst-daily/`

## デプロイ
```bash
git add . && git commit -m "msg" && git push
```
Vercel自動デプロイ。

---
*2026-01-01*
