#!/usr/bin/env python3
"""
NASA MUR SST データ再取得・Supabaseアップロード
制約変更後に消失したNASA MURデータを再取得

使用方法:
    python reupload_nasa_mur.py

対象地点: 44ロガー設置地点（has_logger=True）
期間: 2019-01-01 〜 2025-01-31
"""

import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path

# ==== 設定 ====
SCRIPT_DIR = Path(__file__).parent
SITES_FILE = SCRIPT_DIR / "processed" / "moni1000_sites.csv"

# Supabase
SUPABASE_URL = "https://pegiuiblpliainpdggfj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDIwOTM3NCwiZXhwIjoyMDc5Nzg1Mzc0fQ.V3C2newkAdn6gW2TR_ct-_WupVKZapXKtD9Cr3aMk2M"

# ERDDAP
ERDDAP_SERVERS = [
    "https://upwell.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv",
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv",
]

# 期間
START_DATE = "2019-01-01"
END_DATE = "2025-01-31"

# リクエスト設定
TIMEOUT = 120
RETRY_COUNT = 3
RETRY_DELAY = 5
REQUEST_DELAY = 1
BATCH_SIZE = 500  # Supabase一括挿入サイズ


def fetch_sst_point(lat: float, lon: float) -> list[dict] | None:
    """指定地点のSST時系列を取得"""
    
    for server in ERDDAP_SERVERS:
        url = f"{server}?analysed_sst[({START_DATE}):1:({END_DATE})][({lat}):1:({lat})][({lon}):1:({lon})]"
        
        for attempt in range(RETRY_COUNT):
            try:
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
                    return data if data else None
                
                elif response.status_code == 404:
                    return None
                
            except requests.Timeout:
                if attempt < RETRY_COUNT - 1:
                    print(f"    タイムアウト、リトライ {attempt + 2}/{RETRY_COUNT}...")
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                if attempt < RETRY_COUNT - 1:
                    print(f"    エラー: {e}, リトライ {attempt + 2}/{RETRY_COUNT}...")
                    time.sleep(RETRY_DELAY)
    
    return None


def upload_to_supabase(records: list[dict]) -> int:
    """Supabaseにバッチアップロード"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=ignore-duplicates"  # 重複スキップ
    }
    
    uploaded = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/moni1000_sst_satellite",
            headers=headers,
            json=batch
        )
        
        if resp.status_code in [200, 201]:
            uploaded += len(batch)
        else:
            print(f"    アップロードエラー: {resp.status_code} - {resp.text[:100]}")
    
    return uploaded


def main():
    print("=" * 60)
    print("NASA MUR SST 再取得・アップロード")
    print(f"期間: {START_DATE} 〜 {END_DATE}")
    print("=" * 60)
    
    # ロガー設置地点のみ読み込み
    sites = pd.read_csv(SITES_FILE, encoding='utf-8-sig')
    logger_sites = sites[sites['has_logger'] == True].copy()
    
    print(f"\n対象地点: {len(logger_sites)} 箇所（has_logger=True）")
    
    total_uploaded = 0
    
    for idx, row in logger_sites.iterrows():
        site_no = int(row['site_no'])
        spot_no = int(row['spot_no'])
        lat = row['lat']
        lon = row['lon']
        
        print(f"\n[{idx+1}/{len(logger_sites)}] site{site_no:02d}-spot{spot_no:03d} ({lat:.4f}, {lon:.4f})")
        
        # SST取得
        data = fetch_sst_point(lat, lon)
        
        if data is None:
            print(f"  → データなし（スキップ）")
            continue
        
        print(f"  → {len(data)} 日分取得")
        
        # Supabase形式に変換
        records = [
            {
                "site_no": site_no,
                "spot_no": spot_no,
                "date": d['date'],
                "sst": d['sst'],
                "source": "nasa_mur"
            }
            for d in data
        ]
        
        # アップロード
        uploaded = upload_to_supabase(records)
        total_uploaded += uploaded
        print(f"  → {uploaded} 件アップロード")
        
        time.sleep(REQUEST_DELAY)
    
    print("\n" + "=" * 60)
    print(f"完了: 合計 {total_uploaded:,} 件アップロード")
    print("=" * 60)


if __name__ == "__main__":
    main()
