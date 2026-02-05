#!/usr/bin/env python3
"""
NASA MUR SST データ取得（モニ1000 ロガー44地点、2019-2024年）
fetch_2025_all_sites.py をベースに改修

使用方法:
    cd ~/Dropbox\ \(個人\)/Scripts/marine-obs/analysis
    python3 fetch_nasa_mur_moni1000.py

出力:
    ./nasa_mur_moni1000_2019_2024.csv
    → Supabase Table Editor で moni1000_sst_satellite にインポート
"""

import urllib.request
import json
import time
import csv
import ssl
import pandas as pd
from pathlib import Path
from calendar import monthrange

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ============================================================
# 設定
# ============================================================

SCRIPT_DIR = Path(__file__).parent
SITES_FILE = SCRIPT_DIR / "processed" / "moni1000_sites.csv"
OUTPUT_FILE = SCRIPT_DIR / "nasa_mur_moni1000_2019_2024.csv"

# 取得期間
START_YEAR = 2019
END_YEAR = 2024

# ERDDAP設定
BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json"
RETRY_COUNT = 3
RETRY_DELAY = 10
TIMEOUT = 120

# ============================================================
# 関数
# ============================================================

def fetch_sst_month(year: int, month: int, lat: float, lon: float) -> list[dict]:
    """1ヶ月分のSSTデータを取得"""
    
    last_day = monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"
    
    lat_min = lat - 0.01
    lat_max = lat + 0.01
    lon_min = lon - 0.01
    lon_max = lon + 0.01
    
    url = (
        f"{BASE_URL}?"
        f"analysed_sst[({start_date}T09:00:00Z):1:({end_date}T09:00:00Z)]"
        f"[({lat_min}):1:({lat_max})]"
        f"[({lon_min}):1:({lon_max})]"
    )
    
    for attempt in range(RETRY_COUNT):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl_context) as response:
                data = json.loads(response.read().decode())
            
            units = data.get("table", {}).get("columnUnits", [])
            sst_unit = units[3] if len(units) > 3 else "unknown"
            
            rows = data.get("table", {}).get("rows", [])
            results = []
            
            for row in rows:
                time_str, lat_val, lon_val, sst_value = row
                
                if sst_value is not None:
                    if sst_unit == "K" or sst_value > 100:
                        sst_celsius = sst_value - 273.15
                    else:
                        sst_celsius = sst_value
                    
                    if 10.0 <= sst_celsius <= 40.0:  # 範囲を広めに
                        date_str = time_str[:10]
                        results.append({
                            "date": date_str,
                            "sst": round(sst_celsius, 2)
                        })
            
            # 同一日付を平均化
            daily_data = {}
            for r in results:
                d = r["date"]
                if d not in daily_data:
                    daily_data[d] = []
                daily_data[d].append(r["sst"])
            
            averaged = []
            for d, ssts in sorted(daily_data.items()):
                avg_sst = round(sum(ssts) / len(ssts), 2)
                averaged.append({"date": d, "sst": avg_sst})
            
            return averaged
            
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                print(f"(retry)", end="", flush=True)
                time.sleep(RETRY_DELAY)
            else:
                print(f"[ERR]", end="", flush=True)
    
    return []


def main():
    print("=" * 70)
    print("NASA MUR SST 取得（モニ1000 ロガー地点）")
    print(f"期間: {START_YEAR}-01 〜 {END_YEAR}-12")
    print("=" * 70)
    
    # ロガー地点を読み込み
    sites_df = pd.read_csv(SITES_FILE, encoding='utf-8-sig')
    logger_sites = sites_df[sites_df['has_logger'] == True].reset_index(drop=True)
    
    print(f"\n対象地点: {len(logger_sites)} 箇所")
    print(f"出力先: {OUTPUT_FILE}")
    print("=" * 70)
    
    all_data = []
    total_months = len(logger_sites) * (END_YEAR - START_YEAR + 1) * 12
    done_months = 0
    
    for idx, row in logger_sites.iterrows():
        site_no = int(row['site_no'])
        spot_no = int(row['spot_no'])
        lat = row['lat']
        lon = row['lon']
        spot_name = row['spot_name']
        
        print(f"\n[{idx+1}/{len(logger_sites)}] site{site_no:02d}-spot{spot_no:03d} ({spot_name})")
        print(f"    座標: ({lat:.4f}, {lon:.4f})")
        
        site_count = 0
        
        for year in range(START_YEAR, END_YEAR + 1):
            print(f"    {year}: ", end="", flush=True)
            year_count = 0
            
            for month in range(1, 13):
                month_data = fetch_sst_month(year, month, lat, lon)
                
                for d in month_data:
                    all_data.append({
                        "site_no": site_no,
                        "spot_no": spot_no,
                        "date": d["date"],
                        "sst": d["sst"],
                        "source": "nasa_mur"
                    })
                    year_count += 1
                
                if month_data:
                    print("✓", end="", flush=True)
                else:
                    print("✗", end="", flush=True)
                
                done_months += 1
                time.sleep(1)  # サーバー負荷軽減
            
            print(f" → {year_count}日")
            site_count += year_count
        
        print(f"    小計: {site_count}件")
    
    # CSV出力
    print("\n" + "=" * 70)
    print(f"CSV出力中...")
    
    df = pd.DataFrame(all_data)
    df = df.sort_values(['site_no', 'spot_no', 'date']).reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"完了: {OUTPUT_FILE}")
    print(f"合計: {len(all_data):,} 件")
    
    # サイト別サマリー
    print("\n--- サイト別件数 ---")
    summary = df.groupby(['site_no', 'spot_no']).size().reset_index(name='count')
    for _, r in summary.iterrows():
        print(f"  site{int(r['site_no']):02d}-spot{int(r['spot_no']):03d}: {r['count']:,}件")
    
    print("\n" + "=" * 70)
    print("次のステップ:")
    print("1. Supabase Table Editor を開く")
    print("2. moni1000_sst_satellite テーブルを選択")
    print("3. Import data from CSV でこのファイルをインポート")
    print("=" * 70)


if __name__ == "__main__":
    main()
