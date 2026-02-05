#!/usr/bin/env python3
"""
NASA MUR SST データ取得 → CSV出力
Supabaseには手動でインポート

使用方法:
    python fetch_nasa_mur_csv.py
"""

import pandas as pd
import requests
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SITES_FILE = SCRIPT_DIR / "processed" / "moni1000_sites.csv"
OUTPUT_FILE = SCRIPT_DIR / "nasa_mur_moni1000.csv"

ERDDAP_SERVERS = [
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv",
    "https://upwell.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv",
]

START_DATE = "2019-01-01"
END_DATE = "2025-01-31"

TIMEOUT = 180
RETRY_COUNT = 3
RETRY_DELAY = 10


def fetch_sst_point(lat: float, lon: float) -> list[dict] | None:
    for server in ERDDAP_SERVERS:
        url = f"{server}?analysed_sst[({START_DATE}):1:({END_DATE})][({lat}):1:({lat})][({lon}):1:({lon})]"
        
        for attempt in range(RETRY_COUNT):
            try:
                print(f"    試行 {attempt+1}/{RETRY_COUNT}...", end=" ", flush=True)
                response = requests.get(url, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    data = []
                    for line in lines[2:]:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            date = parts[0][:10]
                            try:
                                sst = float(parts[3]) - 273.15
                                data.append({'date': date, 'sst': round(sst, 2)})
                            except ValueError:
                                continue
                    print(f"OK ({len(data)}件)")
                    return data if data else None
                
                elif response.status_code == 404:
                    print("データなし")
                    return None
                else:
                    print(f"HTTP {response.status_code}")
                
            except requests.Timeout:
                print("タイムアウト")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"エラー: {e}")
                time.sleep(RETRY_DELAY)
        
        print(f"    サーバー切替: {server[:30]}...")
    
    return None


def main():
    print("=" * 60)
    print("NASA MUR SST 取得 → CSV")
    print(f"期間: {START_DATE} 〜 {END_DATE}")
    print("=" * 60)
    
    sites = pd.read_csv(SITES_FILE, encoding='utf-8-sig')
    logger_sites = sites[sites['has_logger'] == True].reset_index(drop=True)
    
    print(f"\n対象地点: {len(logger_sites)} 箇所")
    
    all_records = []
    
    for i, row in logger_sites.iterrows():
        site_no = int(row['site_no'])
        spot_no = int(row['spot_no'])
        lat = row['lat']
        lon = row['lon']
        
        print(f"\n[{i+1}/{len(logger_sites)}] site{site_no:02d}-spot{spot_no:03d} ({lat:.4f}, {lon:.4f})")
        
        data = fetch_sst_point(lat, lon)
        
        if data:
            for d in data:
                all_records.append({
                    "site_no": site_no,
                    "spot_no": spot_no,
                    "date": d['date'],
                    "sst": d['sst'],
                    "source": "nasa_mur"
                })
        
        time.sleep(0.5)
    
    # CSV出力
    df = pd.DataFrame(all_records)
    df.to_csv(OUTPUT_FILE, index=False)
    
    print("\n" + "=" * 60)
    print(f"完了: {len(all_records):,} 件")
    print(f"出力: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
