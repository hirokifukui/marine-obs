#!/usr/bin/env python3
"""Onna Village (Manza) summer bleaching-risk outlook -> data/onna-forecast.json

Replaces the old point-score model (scheduled-jobs/sync-climate-indices/update_onna_forecast.py),
which scored El Nino as lowering risk. In this record the opposite holds: the summers that follow
a strong El Nino (1998, 2016, 2024) are Okinawa's mass-bleaching summers.

Method (transparent, hindcast-based):
  * predictor available in autumn: ONI for JAS of the year before the target summer
  * outcome: Manza summer days >= 30C (Jun-Oct) and annual peak DHW (site method)
  * "extreme summer" = peak DHW >= 8 (site method)
  * reports the analog years and base rates; no composite score.
The 'manual' block (official ENSO outlook text) is preserved between runs and edited by hand.
"""
import json, datetime as dt
from pathlib import Path
from build_site_data import get, rows_since  # same Supabase access

DATA = Path(__file__).resolve().parent.parent / 'data'
OUT = DATA / 'onna-forecast.json'
SITE = 'manza'
EXTREME_DHW = 8.0
ANALOG_ONI = 1.0


def main():
    today = dt.date.today()
    oni = get('/rest/v1/oni_monthly?select=year,season,anomaly&order=year.asc,id.asc')
    oni_jas = {r['year']: float(r['anomaly']) for r in oni if r['season'] == 'JAS'}
    latest_oni = oni[-1]
    peaks = {r['year']: float(r['peak_dhw']) for r in get(f'/rest/v1/dhw_annual_peak?select=year,peak_dhw&site_code=eq.{SITE}')}
    rows = rows_since('2003-01-01')
    hot = {}
    for r in rows:
        if r['site_code'] == SITE and r['sst'] is not None and 6 <= int(r['date'][5:7]) <= 10:
            y = int(r['date'][:4]); hot[y] = hot.get(y, 0) + (float(r['sst']) >= 30)
    latest_year = max(peaks)
    complete = [y for y in sorted(peaks) if y >= 2003 and (y < today.year or today.month >= 11)]
    record = [{'year': y, 'days30': hot.get(y, 0), 'peak_dhw': round(peaks[y], 2),
               'prev_jas_oni': oni_jas.get(y - 1), 'extreme': peaks[y] >= EXTREME_DHW} for y in complete]

    analogs = [r for r in record if (r['prev_jas_oni'] or -9) >= ANALOG_ONI]
    others = [r for r in record if (r['prev_jas_oni'] or -9) < ANALOG_ONI]
    rate = lambda rs: round(sum(r['extreme'] for r in rs) / len(rs), 2) if rs else None
    target = today.year + 1 if today.month >= 7 else today.year
    pred = oni_jas.get(target - 1)
    in_analog = pred is not None and pred >= ANALOG_ONI
    level = 'elevated' if in_analog else 'baseline'

    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    manual = old.get('manual', {})
    out = {
        'target': {'location': '恩納村（万座）', 'location_en': 'Onna Village (Manza)', 'site_code': SITE,
                   'season': f'{target}年夏', 'season_en': f'Summer {target}', 'period': '6〜10月', 'period_en': 'Jun–Oct'},
        'predictor': {'name': f'ONI, Jul–Sep {target - 1}', 'value': pred, 'threshold': ANALOG_ONI,
                      'latest_oni': {'year': latest_oni['year'], 'season': latest_oni['season'], 'value': float(latest_oni['anomaly'])}},
        'outlook': {'level': level,
                    'extreme_rate_analog': rate(analogs), 'n_analog': len(analogs),
                    'extreme_rate_other': rate(others), 'n_other': len(others),
                    'extreme_rate_all': rate(record), 'n_all': len(record),
                    'definition': f'extreme summer = peak DHW >= {EXTREME_DHW:g} (site method, 8-week, no 1C cut-off)'},
        'analog_years': [r['year'] for r in analogs],
        'record': record,
        'manual': manual,
        'method': 'scripts/build_onna_outlook.py',
        'updated': today.isoformat(),
    }
    new = json.dumps(out, ensure_ascii=False, indent=2) + '\n'
    if OUT.exists() and OUT.read_text().split('"updated"')[0] == new.split('"updated"')[0]:
        print('unchanged onna-forecast.json'); return
    OUT.write_text(new); print('wrote onna-forecast.json', level, pred, rate(analogs), rate(others))


if __name__ == '__main__':
    main()
