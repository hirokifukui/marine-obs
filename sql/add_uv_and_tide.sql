-- UV Index カラムを marine_weather に追加
ALTER TABLE marine_weather ADD COLUMN IF NOT EXISTS uv_index REAL;

-- 潮汐データ用テーブル
CREATE TABLE IF NOT EXISTS tide_extremes (
    id SERIAL PRIMARY KEY,
    location TEXT NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    tide_type TEXT NOT NULL,  -- 'high' or 'low'
    height REAL,              -- 潮位（メートル）
    lat REAL,
    lng REAL,
    station_name TEXT,        -- 最寄り観測点名
    station_distance REAL,    -- 観測点までの距離（km）
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(location, datetime, tide_type)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_tide_extremes_location_datetime 
ON tide_extremes(location, datetime);

-- コメント
COMMENT ON TABLE tide_extremes IS 'Stormglass Tide API からの満潮・干潮データ';
COMMENT ON COLUMN tide_extremes.tide_type IS 'high = 満潮, low = 干潮';
