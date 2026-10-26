#!/usr/bin/env python3
"""Onna Village Acropora spawning forecast -> data/spawning-forecast.json

Phase 1 (astronomy, any time):
  month  = 6th full moon after the winter solstice (Baird et al. 2022)
  night  = full moon date (JST) + 5
  time   = local sunset + 2h44m (calibrated on 4 June 2026, Amami ~22:00)
Phase 2 (from 1 April): report the Manza SST anomaly over the 30 days before the full moon
  and the night shift the temperature steps (Sakai et al. 2020, as used on this site) would give:
  shift = clamp(round(-2 x anomaly), -3, +3) nights  (+1C -> -2, +2C -> -3, -1C -> +2)
  NOT APPLIED: the hindcast failed in both years with field records
  (2025: +0.39C -> June 15, observed June 19; 2026: -0.40C -> June 6, observed June 4).
  Set APPLY_SST_SHIFT = True only after the rule validates.
"""
import json, datetime as dt
from pathlib import Path
import ephem
from build_site_data import get, rows_since

OUT = Path(__file__).resolve().parent.parent / 'data' / 'spawning-forecast.json'
LAT, LON = '26.505', '127.853'      # Onna Village
OFFSET = dt.timedelta(minutes=164)  # sunset + 2h44m
APPLY_SST_SHIFT = False
JST = dt.timedelta(hours=9)


def jst(d): return ephem.Date(d).datetime() + JST


def sixth_full_moon(year):
    d = ephem.Date(f'{year - 1}/12/21')
    for _ in range(6):
        d = ephem.next_full_moon(d)
    return jst(d)


def night(day):
    o = ephem.Observer(); o.lat, o.lon = LAT, LON; o.pressure = 0; o.horizon = '-0:34'
    o.date = ephem.Date(dt.datetime(day.year, day.month, day.day, 3))  # 12:00 JST
    s = jst(o.next_setting(ephem.Sun())); m = jst(o.next_rising(ephem.Moon()))
    return s, m


def sst_anomaly(fm_date):
    """Mean Manza SST anomaly (vs 2003-2025 daily-of-month climatology) for the 30 days before the full moon."""
    rows = [r for r in rows_since(f'{fm_date.year - 23}-01-01') if r['site_code'] == 'manza' and r['sst'] is not None]
    clim = {}
    for r in rows:
        y = int(r['date'][:4])
        if 2003 <= y <= 2025:
            clim.setdefault(r['date'][5:], []).append(float(r['sst']))
    start = (fm_date - dt.timedelta(days=30)).isoformat()
    an = [float(r['sst']) - sum(clim[r['date'][5:]]) / len(clim[r['date'][5:]])
          for r in rows if start <= r['date'] < fm_date.isoformat() and r['date'][5:] in clim]
    return (round(sum(an) / len(an), 2), len(an)) if an else (None, 0)


def main():
    today = dt.date.today()
    year = today.year if today < sixth_full_moon(today.year).date() + dt.timedelta(days=10) else today.year + 1
    fm = sixth_full_moon(year)
    base = fm.date() + dt.timedelta(days=5)
    phase, shift, anom, n, candidate = 1, 0, None, 0, None
    if today >= dt.date(year, 4, 1):
        anom, n = sst_anomaly(fm.date())
        if anom is not None and n >= 20:
            phase = 2
            candidate = max(-3, min(3, round(-2 * anom)))
            shift = candidate if APPLY_SST_SHIFT else 0
    peak = base + dt.timedelta(days=shift)
    nights = []
    for k in range(-2, 4):
        d = peak + dt.timedelta(days=k)
        s, m = night(d)
        nights.append({'date': d.isoformat(), 'sunset': s.strftime('%H:%M'), 'moonrise': m.strftime('%H:%M'),
                       'predicted': (s + OFFSET).strftime('%H:%M'), 'peak': k == 0})
    s, m = night(peak)
    out = {
        'year': year, 'site': 'Onna Village (Manza)', 'phase': phase,
        'full_moon': fm.strftime('%Y-%m-%d %H:%M'),
        'base_night': base.isoformat(), 'sst_anomaly_30d': anom, 'sst_days': n, 'sst_shift_candidate': candidate, 'sst_shift_applied': APPLY_SST_SHIFT, 'shift_nights': shift,
        'peak': {'date': peak.isoformat(), 'time': (s + OFFSET).strftime('%H:%M'), 'tolerance_min': 30,
                 'sunset': s.strftime('%H:%M'), 'moonrise': m.strftime('%H:%M')},
        'window': [nights[0]['date'], nights[-1]['date']],
        'nights': nights,
        'method': 'scripts/build_spawning_forecast.py',
        'updated': today.isoformat(),
    }
    new = json.dumps(out, ensure_ascii=False, indent=2) + '\n'
    if OUT.exists() and OUT.read_text().split('"updated"')[0] == new.split('"updated"')[0]:
        print('unchanged spawning-forecast.json'); return
    OUT.write_text(new); print('wrote spawning-forecast.json', out['peak'], 'phase', phase, 'shift', shift)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'hindcast':
        for y in (2025, 2026):
            fm = sixth_full_moon(y); a, n = sst_anomaly(fm.date())
            sh = max(-3, min(3, round(-2 * a)))
            print(y, 'FM', fm.strftime('%m-%d %H:%M'), 'anom', a, 'n', n, 'shift', sh, '-> night', fm.date() + dt.timedelta(days=5 + sh))
    else:
        main()
