-- Supabase SQL Editor で実行する関数
-- 極端日数を計算するRPC関数

CREATE OR REPLACE FUNCTION get_extreme_days()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'hot_2024', (
      SELECT json_object_agg(site_code, days)
      FROM (
        SELECT site_code, COUNT(*) as days
        FROM sst_daily
        WHERE date >= '2024-01-01' AND date <= '2024-12-31' AND sst >= 30
        GROUP BY site_code
      ) t
    ),
    'hot_2025', (
      SELECT json_object_agg(site_code, days)
      FROM (
        SELECT site_code, COUNT(*) as days
        FROM sst_daily
        WHERE date >= '2025-01-01' AND date <= '2025-12-31' AND sst >= 30
        GROUP BY site_code
      ) t
    ),
    'cold_winter_2025', (
      SELECT json_object_agg(site_code, days)
      FROM (
        SELECT site_code, COUNT(*) as days
        FROM sst_daily
        WHERE date >= '2024-11-01' AND date <= '2025-04-30' AND sst <= 20
        GROUP BY site_code
      ) t
    ),
    'cold_winter_2026', (
      SELECT json_object_agg(site_code, days)
      FROM (
        SELECT site_code, COUNT(*) as days
        FROM sst_daily
        WHERE date >= '2025-11-01' AND sst <= 20
        GROUP BY site_code
      ) t
    ),
    'latest_date', (
      SELECT MAX(date) FROM sst_daily
    )
  ) INTO result;
  
  RETURN result;
END;
$$;
