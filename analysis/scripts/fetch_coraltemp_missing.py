#!/usr/bin/env python3
"""CoralTemp 欠損日データ再取得"""
import pandas as pd
import requests
import time
import sys

# 地点マスター読み込み
sites = pd.read_csv('processed/moni1000_sites.csv')
logger_sites = sites[sites['has_logger'] == True][['site_no', 'spot_no', 'lon', 'lat']]

missing_dates = ['2024-01-30', '2024-07-04', '2024-07-05', '2024-07-06', '2024-07-25']
base_url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.csv'

results = []

print(f'=== CoralTemp 欠損データ再取得 ===', flush=True)
print(f'対象: {len(logger_sites)}地点 x {len(missing_dates)}日 = {len(logger_sites) * len(missing_dates)}件', flush=True)
print(flush=True)

for i, (_, site) in enumerate(logger_sites.iterrows()):
    site_no = int(site['site_no'])
    spot_no = int(site['spot_no'])
    lon = site['lon']
    lat = site['lat']
    
    print(f'site{site_no:02d}-spot{spot_no:03d}...', end=' ', flush=True)
    
    site_results = 0
    for date in missing_dates:
        url = f'{base_url}?CRW_SST[({date}T12:00:00Z):1:({date}T12:00:00Z)][({lat}):1:({lat})][({lon}):1:({lon})]'
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                lines = r.text.strip().split('\n')
                if len(lines) >= 3:
                    data = lines[2].split(',')
                    sst = float(data[3])
                    results.append({
                        'site_no': site_no,
                        'spot_no': spot_no,
                        'date': date,
                        'sst': round(sst, 2),
                        'source': 'noaa_coraltemp'
                    })
                    site_results += 1
        except requests.exceptions.Timeout:
            print(f'TIMEOUT({date})', end=' ', flush=True)
        except Exception as e:
            print(f'ERR({date}:{e})', end=' ', flush=True)
        
        time.sleep(0.1)
    
    print(f'{site_results}/5', flush=True)

print(flush=True)
print(f'取得成功: {len(results)}件', flush=True)

df = pd.DataFrame(results)
output_path = 'coraltemp_missing_dates.csv'
df.to_csv(output_path, index=False)
print(f'出力: {output_path}', flush=True)
