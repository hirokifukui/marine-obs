-- クロロフィルa 長期データ用テーブル
-- データソース: ERDDAP erdSW2018chla8day (SeaWiFS/MODIS融合, 1997年〜)
-- 実行: Supabase Dashboard > SQL Editor

-- 1. 月次クロロフィルa（1997年9月〜）
CREATE TABLE IF NOT EXISTS chl_monthly_erddap (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    year_month DATE NOT NULL,      -- 月初日（例: 1997-09-01）
    chl_a NUMERIC(8,4),            -- 月平均クロロフィルa (mg/m³)
    anomaly NUMERIC(8,4),          -- 気候値からの偏差 (mg/m³)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site, year_month)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_chl_monthly_erddap_site 
    ON chl_monthly_erddap(site);
CREATE INDEX IF NOT EXISTS idx_chl_monthly_erddap_year_month 
    ON chl_monthly_erddap(year_month);

-- コメント
COMMENT ON TABLE chl_monthly_erddap IS 
    'ERDDAP erdSW2018chla8day 月次平均クロロフィルa (SeaWiFS 1997-2002 + MODIS 2002-, 4km解像度)';


-- 2. クロロフィルa気候値（1998-2020基準）
-- 注: SeaWiFSは1997年9月開始のため、1998年から完全年
CREATE TABLE IF NOT EXISTS chl_climatology_erddap (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    mean_chl NUMERIC(8,4),         -- 月別平均クロロフィルa (mg/m³)
    std_dev NUMERIC(8,4),          -- 標準偏差
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site, month)
);

COMMENT ON TABLE chl_climatology_erddap IS 
    'クロロフィルa気候値 (1998-2020基準期間)';


-- 3. RPC関数: 年別平均クロロフィルa取得
CREATE OR REPLACE FUNCTION get_annual_chl_erddap(p_site TEXT DEFAULT NULL)
RETURNS TABLE (
    site TEXT,
    year INTEGER,
    mean_chl NUMERIC,
    anomaly NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.site,
        EXTRACT(YEAR FROM c.year_month)::INTEGER AS year,
        ROUND(AVG(c.chl_a)::NUMERIC, 4) AS mean_chl,
        ROUND(AVG(c.anomaly)::NUMERIC, 4) AS anomaly
    FROM chl_monthly_erddap c
    WHERE (p_site IS NULL OR c.site = p_site)
    GROUP BY c.site, EXTRACT(YEAR FROM c.year_month)
    ORDER BY c.site, year;
END;
$$;


-- 4. RPC関数: クロロフィルa線形トレンド計算
CREATE OR REPLACE FUNCTION calc_chl_trend(
    p_site TEXT,
    p_start_year INTEGER DEFAULT 1998,
    p_end_year INTEGER DEFAULT 2024
)
RETURNS TABLE (
    site TEXT,
    period_start INTEGER,
    period_end INTEGER,
    n_years INTEGER,
    trend_per_decade NUMERIC,
    r_squared NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_n INTEGER;
    v_sum_x NUMERIC;
    v_sum_y NUMERIC;
    v_sum_xy NUMERIC;
    v_sum_xx NUMERIC;
    v_sum_yy NUMERIC;
    v_slope NUMERIC;
    v_r_squared NUMERIC;
BEGIN
    -- 年別平均を計算
    WITH annual AS (
        SELECT 
            EXTRACT(YEAR FROM year_month)::INTEGER AS year,
            AVG(chl_a) AS mean_chl
        FROM chl_monthly_erddap
        WHERE chl_monthly_erddap.site = p_site
          AND EXTRACT(YEAR FROM year_month) >= p_start_year
          AND EXTRACT(YEAR FROM year_month) <= p_end_year
        GROUP BY EXTRACT(YEAR FROM year_month)
    ),
    stats AS (
        SELECT 
            COUNT(*)::INTEGER AS n,
            SUM(year) AS sum_x,
            SUM(mean_chl) AS sum_y,
            SUM(year * mean_chl) AS sum_xy,
            SUM(year * year) AS sum_xx,
            SUM(mean_chl * mean_chl) AS sum_yy
        FROM annual
    )
    SELECT 
        n, sum_x, sum_y, sum_xy, sum_xx, sum_yy
    INTO v_n, v_sum_x, v_sum_y, v_sum_xy, v_sum_xx, v_sum_yy
    FROM stats;
    
    -- 線形回帰
    IF v_n > 1 THEN
        v_slope := (v_n * v_sum_xy - v_sum_x * v_sum_y) / 
                   (v_n * v_sum_xx - v_sum_x * v_sum_x);
        
        -- R^2 計算
        v_r_squared := POWER(
            (v_n * v_sum_xy - v_sum_x * v_sum_y) /
            SQRT((v_n * v_sum_xx - v_sum_x * v_sum_x) * 
                 (v_n * v_sum_yy - v_sum_y * v_sum_y)),
            2
        );
    ELSE
        v_slope := NULL;
        v_r_squared := NULL;
    END IF;
    
    RETURN QUERY SELECT 
        p_site,
        p_start_year,
        p_end_year,
        v_n,
        ROUND(v_slope * 10, 4),  -- mg/m³ per decade
        ROUND(v_r_squared, 3);
END;
$$;


-- 使用例:
-- SELECT * FROM get_annual_chl_erddap('sekisei');
-- SELECT * FROM calc_chl_trend('sekisei', 1998, 2024);
