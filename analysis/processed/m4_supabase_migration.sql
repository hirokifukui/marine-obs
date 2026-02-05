-- ============================================================
-- Step M4: moni1000_bleaching テーブル再構築
-- 実行日: 2026-02-04
-- 
-- 概要:
--   1. 現行テーブルのバックアップ作成
--   2. カラム名変更（year→fiscal_year, date→survey_date）
--   3. TRUNCATE → CSVからCOPY
--   4. 投入後検証
-- 
-- 投入CSV: moni1000_bleaching_v3_for_supabase.csv（2,288行）
-- ============================================================

-- ■ Step 1: バックアップ
CREATE TABLE moni1000_bleaching_backup_20260204 AS
SELECT * FROM moni1000_bleaching;

-- 件数確認
SELECT count(*) AS backup_count FROM moni1000_bleaching_backup_20260204;
-- 期待: 2286

-- ■ Step 2: カラム名変更
ALTER TABLE moni1000_bleaching RENAME COLUMN "year" TO fiscal_year;
ALTER TABLE moni1000_bleaching RENAME COLUMN "date" TO survey_date;

-- ■ Step 3: TRUNCATE（データ削除、構造は維持）
TRUNCATE TABLE moni1000_bleaching;

-- id列のシーケンスをリセット（SERIAL/IDENTITYの場合）
-- ALTER SEQUENCE moni1000_bleaching_id_seq RESTART WITH 1;
-- ↑ シーケンス名が異なる場合は適宜変更

-- ■ Step 4: CSV投入（Supabase SQL Editorからは直接COPYできないため、
--           以下のいずれかの方法で投入）
-- 
-- 方法A: Supabase Dashboard → Table Editor → Import CSV
--   ファイル: moni1000_bleaching_v3_for_supabase.csv
--   ※ テーブルを選択してImport（Append）
--
-- 方法B: psql経由
--   \copy moni1000_bleaching(fiscal_year, site_no, spot_no, survey_date, coral_cover, bleaching_all, bleaching_acropora, mortality_all, mortality_acropora) FROM 'moni1000_bleaching_v3_for_supabase.csv' WITH CSV HEADER;
--
-- 方法C: Supabase API経由（バッチinsert）
--   → 別途Pythonスクリプトで実行

-- ■ Step 5: 投入後検証
-- 件数
SELECT count(*) AS total FROM moni1000_bleaching;
-- 期待: 2288

-- 年度別
SELECT fiscal_year, count(*) 
FROM moni1000_bleaching 
GROUP BY fiscal_year 
ORDER BY fiscal_year;
-- 期待: 2020=428, 2021=438, 2022=496, 2023=455, 2024=471

-- site19 欠落解消の確認
SELECT fiscal_year, spot_no 
FROM moni1000_bleaching 
WHERE site_no = 19 
ORDER BY fiscal_year, spot_no;
-- 期待: 全年度 spot 1-6（30行）

-- site17 重複キー確認
SELECT fiscal_year, spot_no, bleaching_all, coral_cover
FROM moni1000_bleaching
WHERE site_no = 17 AND spot_no IN (126, 127, 1261, 1271)
ORDER BY fiscal_year, spot_no;
-- 期待: 各年4行（126, 127, 1261, 1271）

-- 重複キーなし確認
SELECT fiscal_year, site_no, spot_no, count(*)
FROM moni1000_bleaching
GROUP BY fiscal_year, site_no, spot_no
HAVING count(*) > 1;
-- 期待: 0行

-- ■ ロールバック手順（問題があった場合）
-- DROP TABLE moni1000_bleaching;
-- ALTER TABLE moni1000_bleaching_backup_20260204 RENAME TO moni1000_bleaching;
