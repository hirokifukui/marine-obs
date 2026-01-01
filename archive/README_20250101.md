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
data/  *.json（カード・詳細ページ用）
```

## デプロイ
```bash
git add . && git commit -m "msg" && git push
```
Vercel自動デプロイ。

## データ更新
- Stormglass → marine_weather（3時間、GitHub Actions）
- NASA SST → sst_daily（毎日10:00、GitHub Actions）
- 静的JSON → 手動SQL実行 → git push

---
*2025-01-01*
