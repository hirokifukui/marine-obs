#!/usr/bin/env python3
"""Home page 'rounds' (回診表): one chart per site -> data/rounds.json

Per site: latest SST, anomaly vs the 2003-2025 climatology for the same calendar day (±3 days),
MMM, current DHW (site method: 8 weeks, no 1C cut-off), DHW 7 days ago, days >= 30C in the
current hot season, last 60 days of SST for the sparkline, a status and a one-line finding.
Status (heat only): 警報 DHW>=8 / 注意 DHW>=4 / 監視 SST above MMM / 平常 otherwise.
"""
import json, datetime as dt
from collections import defaultdict
from pathlib import Path
from build_site_data import get, rows_since, rpc

OUT = Path(__file__).resolve().parent.parent / 'data' / 'rounds.json'
SITES = [  # north to south
    ('kushimoto', '串本', 'Kushimoto', '33.5°N'), ('ogasawara', '小笠原', 'Ogasawara', '27.1°N'),
    ('amami', '奄美', 'Amami', '28.2°N'), ('sesoko', '瀬底', 'Sesoko', '26.6°N'),
    ('manza', '万座', 'Manza', '26.5°N'), ('kerama', '慶良間', 'Kerama', '26.2°N'),
    ('sekisei', '石西礁湖', 'Sekisei Lagoon', '24.3°N')]
STATUS = {'alert': ('警報', 'Alert'), 'watch': ('注意', 'Watch'), 'monitor': ('監視', 'Monitor'), 'normal': ('平常', 'Normal')}


def doy(d): return d.timetuple().tm_yday


def main():
    today = dt.date.today()
    mmm = {r['site_id']: float(r['mmm']) for r in get('/rest/v1/mmm_climatology?select=site_id,mmm')}
    rows = rows_since('2003-01-01')
    by = defaultdict(dict)
    for r in rows:
        if r['sst'] is not None:
            by[r['site_code']][dt.date.fromisoformat(r['date'])] = float(r['sst'])
    ext = rpc('get_extreme_days')
    latest = max(max(v) for v in by.values())
    sites = []
    for code, ja, en, lat in SITES:
        ser = by[code]
        d = max(ser); sst = ser[d]
        clim_vals = [v for k, v in ser.items() if 2003 <= k.year <= 2025 and min(abs(doy(k) - doy(d)), 365 - abs(doy(k) - doy(d))) <= 3]
        clim = sum(clim_vals) / len(clim_vals)
        def dhw(at):
            return sum(max(0.0, ser[at - dt.timedelta(days=i)] - mmm[code]) for i in range(56) if (at - dt.timedelta(days=i)) in ser) / 7
        dhw_now, dhw_week = dhw(d), dhw(d - dt.timedelta(days=7))
        spark = [round(ser[d - dt.timedelta(days=i)], 2) for i in range(59, -1, -1) if (d - dt.timedelta(days=i)) in ser]
        anom = sst - clim
        status = 'alert' if dhw_now >= 8 else 'watch' if dhw_now >= 4 else 'monitor' if sst > mmm[code] else 'normal'
        week = sst - ser.get(d - dt.timedelta(days=7), sst)
        ja_f, en_f = [], []
        if abs(anom) < 0.15:
            ja_f.append('平年並み'); en_f.append('close to normal')
        else:
            ja_f.append(f'平年より{abs(anom):.1f}℃{"高い" if anom >= 0 else "低い"}')
            en_f.append(f'{abs(anom):.1f}°C {"above" if anom >= 0 else "below"} normal')
        if sst > mmm[code]:
            ja_f.append(f'最暖月平均を{sst - mmm[code]:.1f}℃上回る'); en_f.append(f'{sst - mmm[code]:.1f}°C over the warmest-month mean')
        if dhw_now >= 1:
            trend = '上昇中' if dhw_now > dhw_week + 0.1 else '低下中' if dhw_now < dhw_week - 0.1 else '横ばい'
            trend_en = 'rising' if dhw_now > dhw_week + 0.1 else 'falling' if dhw_now < dhw_week - 0.1 else 'steady'
            ja_f.append(f'DHWは{trend}'); en_f.append(f'DHW {trend_en}')
        else:
            ja_f.append(f'この1週間で{abs(week):.1f}℃{"上昇" if week >= 0 else "低下"}')
            en_f.append(f'{"up" if week >= 0 else "down"} {abs(week):.1f}°C this week')
        sites.append({
            'code': code, 'ja': ja, 'en': en, 'lat': lat, 'date': d.isoformat(),
            'sst': round(sst, 1), 'anomaly': round(anom, 1), 'mmm': round(mmm[code], 1),
            'dhw': round(dhw_now, 1), 'dhw_week_ago': round(dhw_week, 1),
            'days30': ext['hot_current'].get(code, 0), 'hot_year': ext['hot_year'],
            'status': status, 'status_ja': STATUS[status][0], 'status_en': STATUS[status][1],
            'finding_ja': '。'.join(ja_f) + '。', 'finding_en': '; '.join(en_f).capitalize() + '.',
            'spark': spark,
        })
    out = {'observed': latest.isoformat(), 'dhw_method': 'site (8 weeks, no 1°C cut-off)', 'sites': sites, 'updated': today.isoformat()}
    new = json.dumps(out, ensure_ascii=False, indent=1) + '\n'
    if OUT.exists() and OUT.read_text().split('"updated"')[0] == new.split('"updated"')[0]:
        print('unchanged rounds.json'); return
    OUT.write_text(new); print('wrote rounds.json', latest, [(s['code'], s['sst'], s['anomaly'], s['dhw'], s['status']) for s in sites])


if __name__ == '__main__':
    main()
