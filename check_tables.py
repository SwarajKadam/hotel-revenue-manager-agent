from app.db import fetch_all

rows = fetch_all("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
""")

for row in rows:
    print(row["table_name"])