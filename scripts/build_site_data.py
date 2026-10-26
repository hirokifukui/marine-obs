#!/usr/bin/env python3
"""Regenerate the static JSON files the site reads (data/*.json) from Supabase.

Runs daily in GitHub Actions (.github/workflows/build-site-data.yml).
Uses only the public anon key that the pages already ship, and only the stdlib.

Outputs
  data/sst_card.json        monthly mean SST, previous vs current calendar year (home SST card)
  data/sst_recent.json      last 30 days of daily SST, 7 sites (SST page, gear recs)
  data/extreme_days.json    hot (>=30C) / cold (<=20C) day counts per year (RPC get_extreme_days_historical)
  data/dhw_annual_peak.json annual peak DHW per site (RPC get_dhw_all_years)
"""
import json, urllib.request, datetime as dt
from collections import defaultdict
from pathlib import Path

URL = 'https://pegiuiblpliainpdggfj.supabase.co'
KEY = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwi'
       'cm9sZSI6ImFub24iLCJpYXQiOjE3NjQyMDkzNzQsImV4cCI6MjA3OTc4NTM3NH0.r9dBAsMLoXbgZL93lvA756r74U6YfCCfftHHlxYqZIw')
SITES = ['kushimoto', 'ogasawara', 'amami', 'sesoko', 'manza', 'kerama', 'sekisei']
DATA = Path(__file__).resolve().parent.parent / 'data'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}


def get(path):
    req = urllib.request.Request(URL + path, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def rpc(name):
    req = urllib.request.Request(f'{URL}/rest/v1/rpc/{name}', data=b'{}', headers=H, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def rows_since(start):
    out, off, page = [], 0, 1000
    while True:
        chunk = get(f'/rest/v1/sst_daily?select=site_code,date,sst&date=gte.{start}'
                    f'&order=date.asc,site_code.asc&limit={page}&offset={off}')
        out += chunk
        if len(chunk) < page:
            return out
        off += page


def write(name, obj):
    p = DATA / name
    new = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    if p.exists() and p.read_text() == new:
        print('unchanged', name); return
    p.write_text(new); print('wrote', name)


def main():
    today = dt.date.today().isoformat()
    latest = get('/rest/v1/sst_daily?select=date&order=date.desc&limit=1')[0]['date']
    ly = int(latest[:4])
    rows = rows_since(f'{ly - 1}-01-01')

    # sst_card: monthly means, previous vs current calendar year
    old = json.loads((DATA / 'sst_card.json').read_text())
    mmm = {s: v.get('mmm') for s, v in old['chart'].items() if isinstance(v, dict)}
    card_sites = ['kushimoto', 'ogasawara', 'manza']
    acc = defaultdict(list)
    for r in rows:
        if r['site_code'] in card_sites and r['sst'] is not None:
            acc[(r['site_code'], int(r['date'][:4]), int(r['date'][5:7]))].append(float(r['sst']))
    chart = {'labels': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'], 'years': [str(ly - 1), str(ly)]}
    for s in card_sites:
        chart[s] = {str(y): [round(sum(v) / len(v), 1) if (v := acc.get((s, y, m))) else None for m in range(1, 13)]
                    for y in (ly - 1, ly)}
        chart[s]['mmm'] = mmm.get(s)
    last = {s: next((float(r['sst']) for r in reversed(rows) if r['site_code'] == s and r['sst'] is not None), None)
            for s in card_sites}
    write('sst_card.json', {
        'metadata': {'description': 'SSTカード用データ（月別比較）', 'generated_at': today, 'sites': card_sites,
                     'generator': 'scripts/build_site_data.py'},
        'latest': {**{s: round(v, 1) for s, v in last.items() if v is not None}, 'observed': latest, 'published': today},
        'chart': chart})

    # sst_recent: last 30 days, 7 sites
    cutoff = (dt.date.fromisoformat(latest) - dt.timedelta(days=29)).isoformat()
    recent = {'metadata': {'description': '直近30日SST', 'generated_at': today, 'note': '7地点対応版',
                           'generator': 'scripts/build_site_data.py'}}
    for s in SITES:
        recent[s] = [{'date': r['date'], 'sst': round(float(r['sst']), 2)} for r in rows
                     if r['site_code'] == s and r['date'] >= cutoff and r['sst'] is not None]
    write('sst_recent.json', recent)

    # extreme days (historical, through the latest year)
    ext = rpc('get_extreme_days_historical')
    write('extreme_days.json', {'hot_days': ext['hot_days'], 'cold_days': ext['cold_days']})

    # annual peak DHW
    dhw = rpc('get_dhw_all_years')
    write('dhw_annual_peak.json', {s: dhw[s] for s in SITES if s in dhw})

    print('latest observation', latest)


if __name__ == '__main__':
    main()
