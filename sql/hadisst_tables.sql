-- HadISST 長期データ用テーブル
-- 実行: Supabase Dashboard > SQL Editor

-- 1. 月次SST（1981年〜）
CREATE TABLE IF NOT EXISTS sst_monthly_hadisst (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    year_month DATE NOT NULL,      -- 月初日（例: 1981-01-01）
    sst NUMERIC(6,3),              -- 月平均SST (℃)
    anomaly NUMERIC(5,3),          -- 気候値からの偏差 (℃)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site, year_month)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_sst_monthly_hadisst_site 
    ON sst_monthly_hadisst(site);
CREATE INDEX IF NOT EXISTS idx_sst_monthly_hadisst_year_month 
    ON sst_monthly_hadisst(year_month);

-- コメント
COMMENT ON TABLE sst_monthly_hadisst IS 
    'HadISST 1.1 月次平均SST (Met Office Hadley Centre, 1°×1°解像度)';


-- 2. 気候値（1981-2010基準）
CREATE TABLE IF NOT EXISTS sst_climatology_hadisst (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    mean_sst NUMERIC(6,3),         -- 月別平均SST (℃)
    std_dev NUMERIC(5,3),          -- 標準偏差
    mmm_sst NUMERIC(6,3),          -- Maximum Monthly Mean (最暖月平均)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site, month)
);

COMMENT ON TABLE sst_climatology_hadisst IS 
    'HadISST気候値 (1981-2010基準期間)';


-- 3. 10年トレンド（キャッシュ用）
CREATE TABLE IF NOT EXISTS decadal_trend (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    variable TEXT NOT NULL,        -- 'sst' | 'chl_a'
    period_start INTEGER NOT NULL, -- 開始年
    period_end INTEGER NOT NULL,   -- 終了年
    trend_per_decade NUMERIC(5,3), -- 変化率 (℃/10年)
    r_squared NUMERIC(4,3),        -- 決定係数
    p_value NUMERIC(8,6),          -- p値
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site, variable, period_start, period_end)
);

COMMENT ON TABLE decadal_trend IS 
    '長期トレンド計算結果のキャッシュ';


-- 4. RPC関数: 年別平均SST取得
CREATE OR REPLACE FUNCTION get_annual_sst_hadisst(p_site TEXT DEFAULT NULL)
RETURNS TABLE (
    site TEXT,
    year INTEGER,
    mean_sst NUMERIC,
    anomaly NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.site,
        EXTRACT(YEAR FROM s.year_month)::INTEGER AS year,
        ROUND(AVG(s.sst)::NUMERIC, 2) AS mean_sst,
        ROUND(AVG(s.anomaly)::NUMERIC, 2) AS anomaly
    FROM sst_monthly_hadisst s
    WHERE (p_site IS NULL OR s.site = p_site)
    GROUP BY s.site, EXTRACT(YEAR FROM s.year_month)
    ORDER BY s.site, year;
END;
$$;


-- 5. RPC関数: 線形トレンド計算
CREATE OR REPLACE FUNCTION calc_sst_trend(
    p_site TEXT,
    p_start_year INTEGER DEFAULT 1981,
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
            AVG(sst) AS mean_sst
        FROM sst_monthly_hadisst
        WHERE sst_monthly_hadisst.site = p_site
          AND EXTRACT(YEAR FROM year_month) >= p_start_year
          AND EXTRACT(YEAR FROM year_month) <= p_end_year
        GROUP BY EXTRACT(YEAR FROM year_month)
    ),
    stats AS (
        SELECT 
            COUNT(*)::INTEGER AS n,
            SUM(year) AS sum_x,
            SUM(mean_sst) AS sum_y,
            SUM(year * mean_sst) AS sum_xy,
            SUM(year * year) AS sum_xx,
            SUM(mean_sst * mean_sst) AS sum_yy
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
        ROUND(v_slope * 10, 3),  -- ℃/decade
        ROUND(v_r_squared, 3);
END;
$$;


-- 使用例:
-- SELECT * FROM get_annual_sst_hadisst('kushimoto');
-- SELECT * FROM calc_sst_trend('kushimoto', 1981, 2024);
-- SELECT * FROM calc_sst_trend('sekisei', 1981, 2024);
