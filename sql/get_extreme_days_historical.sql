-- 年別極端日数を全地点・全年分取得するRPC関数
CREATE OR REPLACE FUNCTION get_extreme_days_historical()
RETURNS JSON
LANGUAGE sql
AS '
WITH sites AS (
  SELECT unnest(ARRAY[''kushimoto'', ''ogasawara'', ''amami'', ''sesoko'', ''manza'', ''kerama'', ''sekisei'']) AS site_code
),
years AS (
  SELECT generate_series(2003, 2025) AS year
),
site_years AS (
  SELECT s.site_code, y.year FROM sites s CROSS JOIN years y
),
hot_counts AS (
  SELECT site_code, EXTRACT(YEAR FROM date)::int AS year, COUNT(*) AS days
  FROM sst_daily
  WHERE sst >= 30
  GROUP BY site_code, EXTRACT(YEAR FROM date)
),
cold_counts AS (
  SELECT site_code, EXTRACT(YEAR FROM date)::int AS year, COUNT(*) AS days
  FROM sst_daily
  WHERE sst <= 20
  GROUP BY site_code, EXTRACT(YEAR FROM date)
)
SELECT json_build_object(
  ''hot_days'', (
    SELECT json_object_agg(site_code, year_data)
    FROM (
      SELECT sy.site_code, json_agg(json_build_object(''year'', sy.year, ''days'', COALESCE(h.days, 0)) ORDER BY sy.year) AS year_data
      FROM site_years sy
      LEFT JOIN hot_counts h ON sy.site_code = h.site_code AND sy.year = h.year
      GROUP BY sy.site_code
    ) t
  ),
  ''cold_days'', (
    SELECT json_object_agg(site_code, year_data)
    FROM (
      SELECT sy.site_code, json_agg(json_build_object(''year'', sy.year, ''days'', COALESCE(c.days, 0)) ORDER BY sy.year) AS year_data
      FROM site_years sy
      LEFT JOIN cold_counts c ON sy.site_code = c.site_code AND sy.year = c.year
      GROUP BY sy.site_code
    ) t
  )
);
';
