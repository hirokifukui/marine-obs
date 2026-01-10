-- UV日次データテーブル
CREATE TABLE IF NOT EXISTS uv_daily (
    id SERIAL PRIMARY KEY,
    location TEXT NOT NULL,
    date DATE NOT NULL,
    uv_max REAL,
    sunrise TIMESTAMPTZ,
    sunset TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(location, date)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_uv_daily_location_date ON uv_daily(location, date);

-- 更新日時を自動更新するトリガー
CREATE OR REPLACE FUNCTION update_uv_daily_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_uv_daily_updated_at ON uv_daily;
CREATE TRIGGER trigger_uv_daily_updated_at
    BEFORE UPDATE ON uv_daily
    FOR EACH ROW
    EXECUTE FUNCTION update_uv_daily_updated_at();
