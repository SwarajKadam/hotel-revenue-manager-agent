from app.db import execute

migration_sql = """
CREATE TABLE IF NOT EXISTS rate_plan_lookup (
    rate_plan_code TEXT PRIMARY KEY,
    rate_plan_name TEXT,
    rate_plan_group TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS macro_group_history (
    market_code TEXT NOT NULL,
    macro_group TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    PRIMARY KEY (market_code, effective_from)
);

CREATE TABLE IF NOT EXISTS dataset_verification (
    id SERIAL PRIMARY KEY,
    dataset_revision TEXT,
    total_stay_rows INTEGER,
    total_reservations INTEGER,
    posted_otb_total_revenue NUMERIC,
    posted_otb_room_revenue NUMERIC,
    reservation_stay_status_sha256 TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE reservations_hackathon
ADD COLUMN IF NOT EXISTS financial_status TEXT;

ALTER TABLE reservations_hackathon
ADD COLUMN IF NOT EXISTS property_date DATE;
"""

execute(migration_sql)

print("Schema update applied successfully.")