#!/usr/bin/env python3
"""
NASA MUR 欠損日データ再取得（修正版）
- K→℃変換バグを修正
- 単位は既に摂氏（degree_C）
"""
import pandas as pd
import requests
import time

# 地点マスター読み込み
sites = pd.read_csv('processed/moni1000_sites.csv')
logger_sites = sites[sites['has_logger'] == True][['site_no', 'spot_no', 'lon', 'lat']]

missing_dates = ['2021-02-20', '2021-02-21']
base_url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv'

results = []

print(f'=== NASA MUR 欠損データ再取得（修正版） ===', flush=True)
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
        url = f'{base_url}?analysed_sst[({date}T09:00:00Z):1:({date}T09:00:00Z)][({lat}):1:({lat})][({lon}):1:({lon})]'
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                lines = r.text.strip().split('\n')
                if len(lines) >= 3:
                    data = lines[2].split(',')
                    # 修正: 単位は既に摂氏なので変換不要
                    sst_celsius = float(data[3])
                    
                    # 範囲チェック（10-35℃）
                    if 10.0 <= sst_celsius <= 35.0:
                        results.append({
                            'site_no': site_no,
                            'spot_no': spot_no,
                            'date': date,
                            'sst': round(sst_celsius, 2),
                            'source': 'nasa_mur'
                        })
                        site_results += 1
                    else:
                        print(f'RANGE_ERR({date}:{sst_celsius})', end=' ', flush=True)
        except requests.exceptions.Timeout:
            print(f'TIMEOUT({date})', end=' ', flush=True)
        except Exception as e:
            print(f'ERR({date}:{e})', end=' ', flush=True)
        
        time.sleep(0.2)
    
    print(f'{site_results}/{len(missing_dates)}', flush=True)

print(flush=True)
print(f'取得成功: {len(results)}件（期待: 88件）', flush=True)

# 検証
if len(results) == 88:
    print('✓ 件数OK', flush=True)
else:
    print(f'⚠ 件数不一致: {len(results)} != 88', flush=True)

df = pd.DataFrame(results)

# 統計表示
print(flush=True)
print('--- SST統計 ---', flush=True)
print(df['sst'].describe(), flush=True)

# 異常値チェック
if df['sst'].min() < 10 or df['sst'].max() > 35:
    print('⚠ 異常値あり！', flush=True)
else:
    print('✓ 値の範囲OK (10-35℃)', flush=True)

output_path = 'nasa_mur_missing_fixed.csv'
df.to_csv(output_path, index=False)
print(f'\n出力: {output_path}', flush=True)
