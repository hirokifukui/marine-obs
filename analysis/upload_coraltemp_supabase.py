#!/usr/bin/env python3
"""
CoralTemp SST → Supabase アップロードスクリプト

使用方法:
    python upload_coraltemp_supabase.py           # 実行
    python upload_coraltemp_supabase.py --dry-run # 確認のみ
"""

import pandas as pd
import json
from pathlib import Path
from supabase import create_client

# 設定
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "coraltemp_daily_moni1000.csv"
CONFIG_PATH = Path.home() / ".config" / "supabase_marine.json"
TABLE_NAME = "moni1000_sst_satellite"
BATCH_SIZE = 1000

def parse_site(site_str: str) -> tuple[int, int]:
    """'site03-spot013' → (3, 13)"""
    parts = site_str.split('-')
    site_no = int(parts[0].replace('site', ''))
    spot_no = int(parts[1].replace('spot', ''))
    return site_no, spot_no

def main(dry_run: bool = False):
    print("=" * 60)
    print("CoralTemp → Supabase アップロード")
    print("=" * 60)
    
    # 認証情報読み込み
    if not CONFIG_PATH.exists():
        print(f"エラー: {CONFIG_PATH} が見つかりません")
        print("以下の形式で作成してください:")
        print('{"url": "https://xxx.supabase.co", "key": "eyJ..."}')
        return
    
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    # データ読み込み
    print(f"\n[1] データ読み込み: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"    レコード数: {len(df):,}")
    
    # site列をsite_no, spot_noに分解
    print("\n[2] データ変換中...")
    df[['site_no', 'spot_no']] = df['site'].apply(
        lambda x: pd.Series(parse_site(x))
    )
    
    # アップロード用データ作成
    records = df[['site_no', 'spot_no', 'date', 'sst', 'source']].to_dict('records')
    print(f"    変換完了: {len(records):,}件")
    
    # サンプル表示
    print("\n[3] サンプルデータ（最初の3件）:")
    for r in records[:3]:
        print(f"    {r}")
    
    if dry_run:
        print("\n[DRY RUN] アップロードをスキップ")
        return
    
    # Supabase接続
    print("\n[4] Supabase接続...")
    supabase = create_client(config["url"], config["key"])
    
    # バッチアップロード
    print(f"\n[5] アップロード開始（{BATCH_SIZE}件ずつ）...")
    total_uploaded = 0
    errors = []
    
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        try:
            supabase.table(TABLE_NAME).insert(batch).execute()
            total_uploaded += len(batch)
            progress = (i + len(batch)) / len(records) * 100
            print(f"    {total_uploaded:,} / {len(records):,} ({progress:.1f}%)")
        except Exception as e:
            errors.append(f"Batch {i//BATCH_SIZE}: {e}")
            print(f"    エラー at batch {i//BATCH_SIZE}: {e}")
    
    # 結果
    print("\n" + "=" * 60)
    print("結果")
    print("=" * 60)
    print(f"アップロード成功: {total_uploaded:,}件")
    if errors:
        print(f"エラー: {len(errors)}件")
        for e in errors[:5]:
            print(f"  - {e}")
    
    # 確認クエリ
    print("\n確認用SQL:")
    print("SELECT source, COUNT(*) FROM moni1000_sst_satellite GROUP BY source;")

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
