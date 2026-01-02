# marine-obs.org

Coral thermal stress monitoring for Japanese waters.

## Live Site
https://marine-obs.org

## Pages
| Page | Description |
|------|-------------|
| index.html | Home (6 cards + About + Glossary + For Divers) |
| sst.html | Sea Surface Temperature |
| extreme.html | Extreme Temperature Days |
| dhw.html | Degree Heating Weeks |
| species.html | Species Vulnerability |
| spawning.html | Coral Spawning Forecast |
| contact.html | Contact Form |

## Structure
```
css/  main.css, dhw.css, extreme.css, species.css, spawning.css, turbidity.css, contact.css, global-bleaching.css
js/  lang.js, charts.js, marine-monitor.js, gear-recs.js
data/  *.json (chart data)
sql/  RPC function definitions
```

## Data Sources
| Data | Source |
|------|--------|
| Latest SST | Supabase `sst_daily` table |
| Extreme Days | Supabase RPC `get_extreme_days()` |
| DHW Peak | Supabase RPC `get_dhw_all_years()` + `dhw_annual_peak` table |
| Daily Sync | Scheduled job via cron |

## Deploy
```bash
git add . && git commit -m "msg" && git push
```
Auto-deployed via Vercel.

---
*2026-01-01*
