-- 極端日数を計算するRPC関数（7地点対応版）
-- 全地点を必ず返す（データなし = 0）

CREATE OR REPLACE FUNCTION get_extreme_days()
RETURNS JSON
LANGUAGE sql
AS '
WITH sites AS (
  SELECT unnest(ARRAY[''kushimoto'', ''ogasawara'', ''amami'', ''sesoko'', ''manza'', ''kerama'', ''sekisei'']) AS site_code
),
hot_2024 AS (
  SELECT site_code, COUNT(*) as days
  FROM sst_daily
  WHERE date >= ''2024-01-01'' AND date <= ''2024-12-31'' AND sst >= 30
  GROUP BY site_code
),
hot_2025 AS (
  SELECT site_code, COUNT(*) as days
  FROM sst_daily
  WHERE date >= ''2025-01-01'' AND date <= ''2025-12-31'' AND sst >= 30
  GROUP BY site_code
),
cold_2025 AS (
  SELECT site_code, COUNT(*) as days
  FROM sst_daily
  WHERE date >= ''2024-11-01'' AND date <= ''2025-04-30'' AND sst <= 20
  GROUP BY site_code
),
cold_2026 AS (
  SELECT site_code, COUNT(*) as days
  FROM sst_daily
  WHERE date >= ''2025-11-01'' AND sst <= 20
  GROUP BY site_code
)
SELECT json_build_object(
  ''hot_2024'', (SELECT json_object_agg(s.site_code, COALESCE(h.days, 0)) FROM sites s LEFT JOIN hot_2024 h ON s.site_code = h.site_code),
  ''hot_2025'', (SELECT json_object_agg(s.site_code, COALESCE(h.days, 0)) FROM sites s LEFT JOIN hot_2025 h ON s.site_code = h.site_code),
  ''cold_winter_2025'', (SELECT json_object_agg(s.site_code, COALESCE(c.days, 0)) FROM sites s LEFT JOIN cold_2025 c ON s.site_code = c.site_code),
  ''cold_winter_2026'', (SELECT json_object_agg(s.site_code, COALESCE(c.days, 0)) FROM sites s LEFT JOIN cold_2026 c ON s.site_code = c.site_code),
  ''latest_date'', (SELECT MAX(date) FROM sst_daily)
);
';
