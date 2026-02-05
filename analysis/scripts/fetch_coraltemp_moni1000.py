#!/usr/bin/env python3
"""
モニ1000ロガー地点のCoralTemp SST時系列を取得するスクリプト
NOAA CoralTemp (ERDDAP) から2019-2024年のデータを取得

使用方法:
    python fetch_coraltemp_moni1000.py

出力:
    coraltemp_daily_moni1000.csv
"""

import pandas as pd
import requests
import time
import os
import json
from datetime import datetime
from pathlib import Path

# 設定
SCRIPT_DIR = Path(__file__).parent
LOGGER_SITES_FILE = SCRIPT_DIR / "moni1000_logger_sites.json"
OUTPUT_FILE = SCRIPT_DIR / "coraltemp_daily_moni1000.csv"
CHECKPOINT_FILE = SCRIPT_DIR / "coraltemp_checkpoint.csv"

# NOAA CoralTemp ERDDAP
# Dataset: NOAA Coral Reef Watch Daily 5km Satellite Coral Bleaching SST
ERDDAP_BASE = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.csv"

# 取得期間
START_DATE = "2019-01-01"
END_DATE = "2024-12-31"

# リクエスト設定
TIMEOUT = 180  # 秒（MURより長め）
RETRY_COUNT = 3
RETRY_DELAY = 10  # 秒
REQUEST_DELAY = 2  # リクエスト間隔（秒）


def fetch_coraltemp_point(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame | None:
    """指定地点のCoralTemp SST時系列を取得"""
    
    # CoralTempはanalysed_sstを使用（単位: °C）
    url = f"{ERDDAP_BASE}?CRW_SST[({start_date}T12:00:00Z):1:({end_date}T12:00:00Z)][({lat}):1:({lat})][({lon}):1:({lon})]"
    
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []
                for line in lines[2:]:  # 最初の2行はヘッダー
                    parts = line.split(',')
                    if len(parts) >= 4:
                        date = parts[0][:10]  # YYYY-MM-DD
                        try:
                            sst = float(parts[3])  # CoralTempは既に摂氏
                            if sst > -999:  # 欠損値チェック
                                data.append({'date': date, 'sst': round(sst, 2)})
                        except ValueError:
                            continue
                
                if data:
                    return pd.DataFrame(data)
            
            elif response.status_code == 404:
                return None
            
            else:
                print(f"    HTTP {response.status_code}")
                
        except requests.Timeout:
            if attempt < RETRY_COUNT - 1:
                print(f"    タイムアウト、リトライ {attempt + 2}/{RETRY_COUNT}...")
                time.sleep(RETRY_DELAY)
            continue
            
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                print(f"    エラー: {e}, リトライ {attempt + 2}/{RETRY_COUNT}...")
                time.sleep(RETRY_DELAY)
            continue
    
    return None


def main():
    print("=" * 60)
    print("モニ1000 CoralTemp SST取得スクリプト")
    print(f"期間: {START_DATE} 〜 {END_DATE}")
    print("=" * 60)
    
    # ロガー地点リスト読み込み
    if not LOGGER_SITES_FILE.exists():
        print(f"エラー: {LOGGER_SITES_FILE} が見つかりません")
        return
    
    with open(LOGGER_SITES_FILE, 'r', encoding='utf-8') as f:
        sites = json.load(f)
    
    print(f"\n対象地点数: {len(sites)}")
    
    # チェックポイント読み込み（途中再開用）
    completed_sites = set()
    all_sst_data = []
    
    if CHECKPOINT_FILE.exists():
        checkpoint = pd.read_csv(CHECKPOINT_FILE)
        completed_sites = set(checkpoint['site'].unique())
        all_sst_data.append(checkpoint)
        print(f"チェックポイントから再開: {len(completed_sites)}地点完了済み")
    
    # サイトIDを生成
    def make_site_id(site):
        return f"site{site['site_no']:02d}-spot{site['spot_no']:03d}"
    
    # 未処理地点を取得
    remaining = [s for s in sites if make_site_id(s) not in completed_sites]
    print(f"残り: {len(remaining)}地点\n")
    
    if len(remaining) == 0:
        print("全地点完了済み")
        return
    
    # 取得開始
    start_time = datetime.now()
    success_count = 0
    fail_count = 0
    
    for site in remaining:
        site_id = make_site_id(site)
        lat = site['lat']
        lon = site['lon']
        
        progress = len(completed_sites) + success_count + fail_count + 1
        total = len(sites)
        
        print(f"[{progress}/{total}] {site_id} {site['spot_name'][:20]} ({lat:.4f}, {lon:.4f})", end=" ... ")
        
        df = fetch_coraltemp_point(lat, lon, START_DATE, END_DATE)
        
        if df is not None and len(df) > 0:
            df['site'] = site_id
            df['source'] = 'noaa_coraltemp'
            df = df[['site', 'date', 'sst', 'source']]
            all_sst_data.append(df)
            success_count += 1
            print(f"OK ({len(df)}日)")
        else:
            fail_count += 1
            print("失敗")
        
        # 定期的にチェックポイント保存（5地点ごと）
        if (success_count + fail_count) % 5 == 0 and all_sst_data:
            checkpoint_df = pd.concat(all_sst_data, ignore_index=True)
            checkpoint_df.to_csv(CHECKPOINT_FILE, index=False)
            elapsed = datetime.now() - start_time
            print(f"  [チェックポイント保存: {len(checkpoint_df)}行, 経過: {elapsed}]")
        
        time.sleep(REQUEST_DELAY)
    
    # 最終出力
    if all_sst_data:
        final_df = pd.concat(all_sst_data, ignore_index=True)
        final_df = final_df[['site', 'date', 'sst', 'source']]
        final_df.to_csv(OUTPUT_FILE, index=False)
        
        # チェックポイント削除
        if CHECKPOINT_FILE.exists():
            os.remove(CHECKPOINT_FILE)
        
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("完了!")
        print(f"  成功: {success_count}地点")
        print(f"  失敗: {fail_count}地点")
        print(f"  総レコード: {len(final_df)}行")
        print(f"  出力: {OUTPUT_FILE}")
        print(f"  所要時間: {elapsed}")
        print("=" * 60)
    else:
        print("\nデータ取得なし")


if __name__ == "__main__":
    main()
