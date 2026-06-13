CREATE TABLE IF NOT EXISTS room_type_lookup (
    space_type TEXT PRIMARY KEY,
    room_class TEXT,
    display_name TEXT,
    number_of_rooms INTEGER
);

CREATE TABLE IF NOT EXISTS market_code_lookup (
    market_code TEXT PRIMARY KEY,
    market_name TEXT,
    macro_group TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS channel_code_lookup (
    channel_code TEXT PRIMARY KEY,
    channel_name TEXT,
    channel_group TEXT
);

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

CREATE TABLE IF NOT EXISTS reservations_hackathon (
    reservation_stay_id BIGINT PRIMARY KEY,
    reservation_id TEXT NOT NULL,
    arrival_date DATE,
    departure_date DATE,
    stay_date DATE NOT NULL,
    reservation_status TEXT,
    financial_status TEXT,
    property_date DATE,
    create_datetime TIMESTAMPTZ,
    cancellation_datetime TIMESTAMPTZ,
    guest_country TEXT,
    is_block BOOLEAN,
    is_walk_in BOOLEAN,
    number_of_spaces INTEGER,
    space_type TEXT REFERENCES room_type_lookup(space_type),
    market_code TEXT REFERENCES market_code_lookup(market_code),
    channel_code TEXT REFERENCES channel_code_lookup(channel_code),
    source_name TEXT,
    rate_plan_code TEXT REFERENCES rate_plan_lookup(rate_plan_code),
    daily_room_revenue_before_tax NUMERIC,
    daily_total_revenue_before_tax NUMERIC,
    nights INTEGER,
    adr_room NUMERIC,
    lead_time INTEGER,
    company_name TEXT,
    travel_agent_name TEXT
);