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

CREATE TABLE IF NOT EXISTS reservations_hackathon (
    reservation_stay_id BIGINT PRIMARY KEY,
    reservation_id TEXT NOT NULL,
    arrival_date DATE,
    departure_date DATE,
    stay_date DATE NOT NULL,
    reservation_status TEXT,
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
    rate_plan_code TEXT,
    daily_room_revenue_before_tax NUMERIC,
    daily_total_revenue_before_tax NUMERIC,
    nights INTEGER,
    adr_room NUMERIC,
    lead_time INTEGER,
    company_name TEXT,
    travel_agent_name TEXT
);