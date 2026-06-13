## ETL Verification

The ETL pipeline scrapes the client-rendered reservation portal using Playwright, follows pagination, opens each reservation detail page, extracts per-night stay rows, transforms the data to the required schema, and loads it into Postgres.

Latest verification:

- Total reservations: 250
- Total stay rows: 534
- Room types: 3
- Market codes: 10
- Channel codes: 4
- Duplicate reservation_stay_id values: 0
- Missing stay dates: 0
- Missing revenue rows: 0