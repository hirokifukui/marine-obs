#!/usr/bin/env python3
"""Acropora spawning forecast with a pre-registered, phase-by-phase record.

Outputs
  data/spawning-forecast.json      current forecast (all sites, all models, live conditions)
  data/spawning-log-<year>.json    append-only: the forecast frozen on the day each phase begins
  data/spawning-observations.json  hand-entered field reports (read only here)

Phases (dates relative to the base night B = 6th full moon after the winter solstice + 5 nights)
  1  until 31 March      astronomy only
  2  1 April .. B-8      + SST anomaly over the 30 days before the full moon (all sites)
  3  B-7 .. B-2          + wind / wave / tidal-range forecast for each night of the window
  4  B-1 .. B+3          + evening cloud and rain forecast for each night
  5  after the window    closed; scored against observations

Models, all computed and logged every year so they can be compared afterwards
  M1 astronomy   night B, time = sunset + 2h44m                         (headline)
  M2 temperature night B + clamp(round(-2 x anomaly), -3, +3)           (Sakai et al. 2020 steps)
  M3 neap        the window night with the smallest daily tidal range
Only M1 is published as the prediction. M2 and M3 are recorded, not applied, until they beat M1.

The git history of data/spawning-log-<year>.json (committed daily by GitHub Actions) is the
public timestamp that each phase's forecast was made before the event.

Usage: build_spawning_forecast.py [--as-of YYYY-MM-DD] [--out PATH] [--log-dir DIR] [--no-notify]
       build_spawning_forecast.py hindcast
"""
import argparse, json, os, urllib.request, urllib.parse, datetime as dt
from pathlib import Path
import ephem
from build_site_data import get

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OFFSET = dt.timedelta(minutes=164)       # sunset + 2h44m (calibrated on 4 June 2026, Amami ~22:00)
JST = dt.timedelta(hours=9)
HEADLINE = 'manza'
SITES = {  # code: (ja, en, lat, lon)
    'manza':  ('恩納村（万座）', 'Onna (Manza)', 26.505, 127.853),
    'sesoko': ('瀬底', 'Sesoko', 26.650, 127.860),
    'kerama': ('慶良間', 'Kerama', 26.210, 127.300),
    'amami':  ('奄美（大島海峡）', 'Amami (Oshima Strait)', 28.150, 129.330),
}
PHASE_NAME = {1: ('天文計算', 'Astronomy'), 2: ('水温の観測', 'Sea temperature'),
              3: ('風・波・潮の予報', 'Wind, waves and tide forecast'),
              4: ('当夜の条件', 'Conditions on the night'), 5: ('終了・採点', 'Closed and scored')}


# ---------- astronomy ----------
def jst(d): return ephem.Date(d).datetime() + JST


def sixth_full_moon(year):
    d = ephem.Date(f'{year - 1}/12/21')
    for _ in range(6):
        d = ephem.next_full_moon(d)
    return jst(d)


def sun_moon(day, lat, lon):
    o = ephem.Observer(); o.lat, o.lon = str(lat), str(lon); o.pressure = 0; o.horizon = '-0:34'
    o.date = ephem.Date(dt.datetime(day.year, day.month, day.day, 3))  # 12:00 JST
    return jst(o.next_setting(ephem.Sun())), jst(o.next_rising(ephem.Moon()))


def target_year(as_of):
    return as_of.year if as_of < sixth_full_moon(as_of.year).date() + dt.timedelta(days=10) else as_of.year + 1


# ---------- sea temperature ----------
_ROWS = None


def sst_rows(year):
    """Spawning-season SST (1 Mar - 30 Jun) for the four sites, 2003 to the target year.
    One small request per year instead of paging the whole table."""
    global _ROWS
    if _ROWS is None:
        _ROWS, sites = [], ','.join(SITES)
        for y in range(2003, max(year, dt.date.today().year) + 1):
            _ROWS += [r for r in get(f'/rest/v1/sst_daily?select=site_code,date,sst&site_code=in.({sites})'
                                     f'&date=gte.{y}-03-01&date=lte.{y}-06-30&order=date.asc&limit=1000')
                      if r['sst'] is not None]
    return _ROWS


def sst_anomaly(site, fm_date, as_of):
    rows = [r for r in sst_rows(fm_date.year) if r['site_code'] == site]
    clim = {}
    for r in rows:
        if 2003 <= int(r['date'][:4]) <= 2025:
            clim.setdefault(r['date'][5:], []).append(float(r['sst']))
    # the 30 days before the full moon; before that window opens, the latest 30 days (provisional)
    end = min(fm_date, as_of + dt.timedelta(days=1))
    start = (end - dt.timedelta(days=30)).isoformat(); stop = end.isoformat()
    an = [float(r['sst']) - sum(clim[r['date'][5:]]) / len(clim[r['date'][5:]])
          for r in rows if start <= r['date'] < stop and r['date'][5:] in clim]
    return (round(sum(an) / len(an), 2), len(an)) if an else (None, 0)


# ---------- forecasts (Open-Meteo, no key) ----------
def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'marine-obs.org'}), timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print('fetch failed', url.split('?')[0], e); return None


def hourly(lat, lon, start, end, as_of, kind):
    q = {'latitude': lat, 'longitude': lon, 'timezone': 'Asia/Tokyo',
         'start_date': start.isoformat(), 'end_date': end.isoformat()}
    today = dt.date.today()
    if kind == 'weather':
        q['hourly'] = 'wind_speed_10m,cloud_cover,precipitation'
        base = 'https://api.open-meteo.com/v1/forecast' if as_of >= today else 'https://historical-forecast-api.open-meteo.com/v1/forecast'
    else:
        q['hourly'] = 'wave_height,sea_level_height_msl'
        base = 'https://marine-api.open-meteo.com/v1/marine'
    j = fetch(base + '?' + urllib.parse.urlencode(q))
    if not j or 'hourly' not in j:
        return {}
    h = j['hourly']; out = {}
    for i, t in enumerate(h['time']):
        out[t] = {k: h[k][i] for k in h if k != 'time'}
    return out


def night_conditions(lat, lon, nights, as_of, phase):
    if phase < 3:
        return {}
    start, end = dt.date.fromisoformat(nights[0]), dt.date.fromisoformat(nights[-1])
    if end > as_of + dt.timedelta(days=15):
        return {}
    w = hourly(lat, lon, start, end, as_of, 'weather')
    m = hourly(lat, lon, start, end, as_of, 'marine')
    out = {}
    for d in nights:
        ev = [f'{d}T{h:02d}:00' for h in range(19, 24)]
        day = [f'{d}T{h:02d}:00' for h in range(24)]
        sl = [m[t]['sea_level_height_msl'] for t in day if t in m and m[t].get('sea_level_height_msl') is not None]
        wv = [m[t]['wave_height'] for t in ev if t in m and m[t].get('wave_height') is not None]
        ws = [w[t]['wind_speed_10m'] for t in ev if t in w and w[t].get('wind_speed_10m') is not None]
        cc = [w[t]['cloud_cover'] for t in ev if t in w and w[t].get('cloud_cover') is not None]
        pr = [w[t]['precipitation'] for t in ev if t in w and w[t].get('precipitation') is not None]
        c = {}
        if len(sl) >= 20: c['tidal_range_m'] = round(max(sl) - min(sl), 2)
        if wv: c['wave_max_m'] = round(max(wv), 1)
        if ws: c['wind_kmh'] = round(sum(ws) / len(ws))
        if phase >= 4 and cc: c['cloud_pct'] = round(sum(cc) / len(cc))
        if phase >= 4 and pr: c['rain_mm'] = round(sum(pr), 1)
        if c: out[d] = c
    return out


# ---------- one site ----------
def site_forecast(code, year, as_of):
    ja, en, lat, lon = SITES[code]
    fm = sixth_full_moon(year); B = fm.date() + dt.timedelta(days=5)
    phase = phase_for(as_of, year, B)
    nights = [(B + dt.timedelta(days=k)).isoformat() for k in range(-2, 4)]
    def at(d):
        s, mr = sun_moon(dt.date.fromisoformat(d) if isinstance(d, str) else d, lat, lon)
        return s, mr
    models = {}
    s, _ = at(B)
    models['M1'] = {'night': B.isoformat(), 'time': (s + OFFSET).strftime('%H:%M')}
    anom = n = cand = None
    if phase >= 2:
        anom, n = sst_anomaly(code, fm.date(), as_of)
        if anom is not None and n >= 20:
            cand = max(-3, min(3, round(-2 * anom)))
            d = B + dt.timedelta(days=cand); s, _ = at(d)
            models['M2'] = {'night': d.isoformat(), 'time': (s + OFFSET).strftime('%H:%M'), 'sst_anomaly_30d': anom, 'sst_days': n, 'shift': cand,
                            'provisional': as_of < fm.date() - dt.timedelta(days=1)}
    cond = night_conditions(lat, lon, nights, as_of, phase)
    tr = {d: c['tidal_range_m'] for d, c in cond.items() if 'tidal_range_m' in c}
    if len(tr) == len(nights):
        d = min(tr, key=tr.get); s, _ = at(d)
        models['M3'] = {'night': d, 'time': (s + OFFSET).strftime('%H:%M'), 'tidal_range_m': tr[d]}
    table = []
    for d in nights:
        s, mr = at(d)
        table.append({'date': d, 'sunset': s.strftime('%H:%M'), 'moonrise': mr.strftime('%H:%M'),
                      'predicted': (s + OFFSET).strftime('%H:%M'), 'peak': d == B.isoformat(), **({'conditions': cond[d]} if d in cond else {})})
    return {'code': code, 'ja': ja, 'en': en, 'phase': phase, 'models': models, 'nights': table}


def phase_for(as_of, year, B):
    if as_of < dt.date(year, 4, 1): return 1
    if as_of < B - dt.timedelta(days=7): return 2
    if as_of < B - dt.timedelta(days=1): return 3
    if as_of <= B + dt.timedelta(days=3): return 4
    return 5


# ---------- log, scoring, notifications ----------
def load(p, default):
    try: return json.loads(Path(p).read_text())
    except Exception: return default


def score(models, obs_date, obs_time):
    out = {}
    for k, m in models.items():
        e = {'night_error_days': (dt.date.fromisoformat(obs_date) - dt.date.fromisoformat(m['night'])).days}
        if obs_time:
            hh, mm = map(int, obs_time.split(':')); ph, pm = map(int, m['time'].split(':'))
            e['time_error_min'] = (hh * 60 + mm) - (ph * 60 + pm)
        out[k] = e
    return out


def notify(text):
    tok, chat = os.environ.get('TELEGRAM_BOT_TOKEN'), os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not chat:
        print('[notify skipped]', text.splitlines()[0]); return
    data = urllib.parse.urlencode({'chat_id': chat, 'text': text, 'disable_web_page_preview': 'true'}).encode()
    try: urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/sendMessage', data=data, timeout=20)
    except Exception as e: print('telegram failed', e)


def social_draft(kind, year, head):
    m = head['models']['M1']; d = dt.date.fromisoformat(m['night'])
    md_ja = f'{d.month}月{d.day}日'; md_en = d.strftime('%-d %B')
    lead = {'30': ('あと1か月。', 'One month to go.'), '7': ('あと1週間。', 'One week to go.'), '1': ('今夜か、明日の夜。', 'Tonight, or tomorrow night.')}[kind]
    return {'kind': f'{kind} days before', 'ja': f'{lead[0]}恩納村のサンゴの一斉産卵は、{md_ja}の{m["time"]}ごろと予測しています（±30分）。予測は事前に公開し、外れも含めて事後に採点します。\nhttps://marine-obs.org/spawning.html',
            'en': f'{lead[1]} We predict the mass coral spawning in Onna, Okinawa, on {md_en} around {m["time"]} (±30 min). Every forecast is published in advance and scored afterwards, misses included.\nhttps://marine-obs.org/spawning.html'}


def run(as_of, out_path, log_dir, do_notify=True):
    year = target_year(as_of)
    fm = sixth_full_moon(year); B = fm.date() + dt.timedelta(days=5)
    sites = {c: site_forecast(c, year, as_of) for c in SITES}
    head = sites[HEADLINE]; phase = head['phase']

    log_p = Path(log_dir) / f'spawning-log-{year}.json'
    log = load(log_p, {'year': year, 'base_night': B.isoformat(), 'full_moon': fm.strftime('%Y-%m-%d %H:%M'),
                       'note': 'Forecasts frozen on the first day of each phase. Never edited afterwards; see git history.',
                       'snapshots': [], 'drafts': []})
    frozen = {(s['phase'], s['site']) for s in log['snapshots']}
    new = []
    for c, f in sites.items():
        if (f['phase'], c) not in frozen and f['phase'] <= 4:
            snap = {'phase': f['phase'], 'site': c, 'frozen_on': as_of.isoformat(), 'models': f['models']}
            conds = {n['date']: n['conditions'] for n in f['nights'] if 'conditions' in n}
            if conds: snap['conditions'] = conds
            log['snapshots'].append(snap); new.append(snap)
    for k in ('30', '7', '1'):
        if as_of >= B - dt.timedelta(days=int(k)) and as_of <= B + dt.timedelta(days=3) and k not in {d['kind'].split()[0] for d in log['drafts']}:
            dr = social_draft(k, year, head); dr['made_on'] = as_of.isoformat(); log['drafts'].append(dr)
            if do_notify: notify(f'【産卵予測・投稿下書き】{dr["kind"]}\n\n{dr["ja"]}\n\n{dr["en"]}')
    log_p.write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n')
    if new and do_notify:
        h = [s for s in new if s['site'] == HEADLINE]
        if h:
            m = h[0]['models']; nm = PHASE_NAME[h[0]['phase']]
            lines = [f'【産卵予測】{year}年 フェーズ{h[0]["phase"]}（{nm[0]}）に入りました。予測を記録に固定しました。',
                     f'M1 天文: {m["M1"]["night"]} {m["M1"]["time"]}（公表値）']
            if 'M2' in m: lines.append(f'M2 水温: {m["M2"]["night"]}（偏差 {m["M2"]["sst_anomaly_30d"]:+.2f}℃）')
            if 'M3' in m: lines.append(f'M3 小潮: {m["M3"]["night"]}（潮位差 {m["M3"]["tidal_range_m"]} m）')
            lines.append('https://marine-obs.org/spawning.html')
            notify('\n'.join(lines))

    # scorecard: every year that has a log and observations
    obs = load(DATA / 'spawning-observations.json', {'observations': []})['observations']
    card = []
    for o in obs:
        y = int(o['date'][:4]); lp = Path(log_dir) / f'spawning-log-{y}.json'
        lg = load(lp, None)
        if lg:
            for s in lg['snapshots']:
                if s['site'] == o.get('site'):
                    card.append({'year': y, 'site': s['site'], 'phase': s['phase'], 'observed': o['date'], 'observed_time': o.get('time'),
                                 'scores': score(s['models'], o['date'], o.get('time'))})
    hind = hindcast_rows(obs)

    out = {
        'year': year, 'site': SITES[HEADLINE][1], 'phase': phase,
        'phase_name': {'ja': PHASE_NAME[phase][0], 'en': PHASE_NAME[phase][1]},
        'phase_dates': {'2': f'{year}-04-01', '3': (B - dt.timedelta(days=7)).isoformat(),
                        '4': (B - dt.timedelta(days=1)).isoformat(), '5': (B + dt.timedelta(days=4)).isoformat()},
        'full_moon': fm.strftime('%Y-%m-%d %H:%M'), 'base_night': B.isoformat(),
        'sst_anomaly_30d': head['models'].get('M2', {}).get('sst_anomaly_30d'),
        'sst_days': head['models'].get('M2', {}).get('sst_days', 0),
        'sst_shift_candidate': head['models'].get('M2', {}).get('shift'), 'sst_shift_applied': False, 'shift_nights': 0,
        'peak': {'date': B.isoformat(), 'time': head['models']['M1']['time'], 'tolerance_min': 30,
                 'sunset': next(n['sunset'] for n in head['nights'] if n['peak']),
                 'moonrise': next(n['moonrise'] for n in head['nights'] if n['peak'])},
        'window': [head['nights'][0]['date'], head['nights'][-1]['date']],
        'nights': head['nights'],
        'sites': list(sites.values()),
        'models_note': 'M1 is the published prediction. M2 (temperature) and M3 (neap tide) are recorded for comparison and not applied until they outperform M1.',
        'log': f'data/spawning-log-{year}.json',
        'scorecard': card, 'hindcast': hind,
        'method': 'scripts/build_spawning_forecast.py',
        'updated': as_of.isoformat(),
    }
    new_s = json.dumps(out, ensure_ascii=False, indent=2) + '\n'
    op = Path(out_path)
    if op.exists() and op.read_text().split('"updated"')[0] == new_s.split('"updated"')[0]:
        print('unchanged', op.name); return out
    op.write_text(new_s); print('wrote', op.name, 'phase', phase, {k: v['night'] for k, v in head['models'].items()})
    return out


def hindcast_rows(obs):
    """M1 and M2 recomputed for past years with observations (M3 needs archived tide forecasts; omitted)."""
    rows = []
    for o in obs:
        y = int(o['date'][:4]); code = o.get('site') if o.get('site') in SITES else HEADLINE
        fm = sixth_full_moon(y); B = fm.date() + dt.timedelta(days=5)
        m = {'M1': {'night': B.isoformat(), 'time': (sun_moon(B, *SITES[code][2:])[0] + OFFSET).strftime('%H:%M')}}
        a, n = sst_anomaly(code, fm.date(), fm.date())
        if a is not None and n >= 20:
            sh = max(-3, min(3, round(-2 * a))); d = B + dt.timedelta(days=sh)
            m['M2'] = {'night': d.isoformat(), 'time': (sun_moon(d, *SITES[code][2:])[0] + OFFSET).strftime('%H:%M'), 'sst_anomaly_30d': a, 'shift': sh}
        rows.append({'year': y, 'site': o.get('site'), 'observed': o['date'], 'observed_time': o.get('time'),
                     'source': o.get('source'), 'models': m, 'scores': score(m, o['date'], o.get('time'))})
    return rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?')
    ap.add_argument('--as-of'); ap.add_argument('--out', default=str(DATA / 'spawning-forecast.json'))
    ap.add_argument('--log-dir', default=str(DATA)); ap.add_argument('--no-notify', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'hindcast':
        for r in hindcast_rows(load(DATA / 'spawning-observations.json', {'observations': []})['observations']):
            print(r['year'], r['site'], r['observed'], {k: (v['night'], r['scores'][k]) for k, v in r['models'].items()})
    else:
        run(dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today(), a.out, a.log_dir, not a.no_notify)
