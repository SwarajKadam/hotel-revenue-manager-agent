import os
import re
from decimal import Decimal
from typing import Any, Dict, List
from urllib.parse import urljoin
import hashlib

import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
from io import StringIO

from app.db import get_connection, fetch_all

load_dotenv()

BASE_URL = os.getenv("DATA_SITE_URL", "https://otel-hackathon-data-site.vercel.app")


# -----------------------------
# Basic cleaners
# -----------------------------

def clean_col(col: str) -> str:
    return (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def none_if_blank(value):
    if value is None:
        return None

    text = str(value).strip()

    if text in ["", "-", "—", "nan", "None", "null"]:
        return None

    return text


def clean_int(value):
    value = none_if_blank(value)
    if value is None:
        return None
    return int(float(str(value).replace(",", "")))


def clean_decimal(value):
    value = none_if_blank(value)
    if value is None:
        return None

    text = str(value)
    text = text.replace("€", "").replace("$", "").replace(",", "").strip()

    return Decimal(text)


def clean_bool(value):
    value = none_if_blank(value)
    if value is None:
        return False

    return str(value).strip().lower() in ["true", "yes", "1", "y"]


def clean_date(value):
    value = none_if_blank(value)
    if value is None:
        return None

    return pd.to_datetime(value).date()


def clean_datetime(value):
    value = none_if_blank(value)
    if value is None:
        return None

    return pd.to_datetime(value, utc=True).to_pydatetime()


def read_tables_from_page(page: Page) -> List[pd.DataFrame]:
    html = page.content()

    # Pandas needs StringIO here, otherwise it may treat raw HTML as a file path
    tables = pd.read_html(StringIO(html))

    cleaned_tables = []
    for df in tables:
        df.columns = [clean_col(c) for c in df.columns]
        cleaned_tables.append(df)

    return cleaned_tables


# -----------------------------
# Extract reference tables
# -----------------------------

def scrape_reference_tables(page):
    reference_url = urljoin(BASE_URL, "/reference")
    page.goto(reference_url, wait_until="networkidle")

    def click_tab_and_read_table(tab_name: str):
        print(f"Opening reference tab: {tab_name}")

        # Click tab by visible text.
        page.get_by_text(tab_name, exact=True).click()
        page.wait_for_timeout(500)

        tables = read_tables_from_page(page)

        if not tables:
            raise RuntimeError(f"No table found after clicking tab: {tab_name}")

        print(f"{tab_name} tables found: {len(tables)}")
        print(f"{tab_name} columns: {tables[0].columns.tolist()}")

        return tables[0]

    room_types = click_tab_and_read_table("Room types")
    market_codes = click_tab_and_read_table("Markets")
    channel_codes = click_tab_and_read_table("Channels")

    required_room_cols = {"space_type", "room_class", "display_name", "number_of_rooms"}
    required_market_cols = {"market_code", "market_name", "macro_group", "description"}
    required_channel_cols = {"channel_code", "channel_name", "channel_group"}

    if not required_room_cols.issubset(set(room_types.columns)):
        raise RuntimeError(
            f"Room types table has wrong columns: {room_types.columns.tolist()}"
        )

    if not required_market_cols.issubset(set(market_codes.columns)):
        raise RuntimeError(
            f"Markets table has wrong columns: {market_codes.columns.tolist()}"
        )

    if not required_channel_cols.issubset(set(channel_codes.columns)):
        raise RuntimeError(
            f"Channels table has wrong columns: {channel_codes.columns.tolist()}"
        )

    return {
        "room_types": room_types,
        "market_codes": market_codes,
        "channel_codes": channel_codes,
    }


# -----------------------------
# Extract reservation links
# -----------------------------

def get_reservation_links_on_current_page(page: Page) -> List[str]:
    links = page.locator('a[href^="/reservations/R"]').evaluate_all(
        """els => els.map(a => a.getAttribute('href'))"""
    )

    full_links = []
    for href in links:
        full_links.append(urljoin(BASE_URL, href))

    return full_links


def scrape_all_reservation_links(page: Page) -> List[str]:
    print("Scraping reservation links...")

    page.goto(f"{BASE_URL}/reservations", wait_until="networkidle")
    page.wait_for_timeout(1000)

    all_links = []
    seen = set()

    page_number = 1

    while True:
        links = get_reservation_links_on_current_page(page)

        new_count = 0
        for link in links:
            if link not in seen:
                seen.add(link)
                all_links.append(link)
                new_count += 1

        print(f"Page {page_number}: found {len(links)} links, {new_count} new, total {len(all_links)}")

        next_button = page.locator("button", has_text=re.compile(r"next", re.I))

        if next_button.count() == 0:
            print("No next button found. Pagination finished.")
            break

        button = next_button.first

        try:
            if button.is_disabled():
                print("Next button disabled. Pagination finished.")
                break
        except Exception:
            pass

        # Click next page
        button.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        page_number += 1

        # Safety guard
        if page_number > 20:
            raise RuntimeError("Pagination exceeded 20 pages. Something may be wrong.")

    return all_links


# -----------------------------
# Extract reservation detail page
# -----------------------------

def parse_reservation_fields_from_text(body_text: str) -> Dict[str, Any]:
    """
    Detail page text looks like:

    RESERVATION FIELDS
    arrival_date
    2026-08-14
    departure_date
    2026-08-15
    ...
    STAY ROWS · ONE ROW PER NIGHT (1)

    This function reads those key-value pairs.
    """

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]

    try:
        start = lines.index("RESERVATION FIELDS") + 1
    except ValueError:
        raise RuntimeError("Could not find RESERVATION FIELDS section.")

    end = None
    for i, line in enumerate(lines):
        if line.startswith("STAY ROWS"):
            end = i
            break

    if end is None:
        raise RuntimeError("Could not find STAY ROWS section.")

    field_lines = lines[start:end]

    fields = {}

    # field_lines should be alternating key, value
    for i in range(0, len(field_lines), 2):
        if i + 1 >= len(field_lines):
            break

        key = field_lines[i]
        value = field_lines[i + 1]
        fields[key] = value

    return fields


def scrape_reservation_detail(page: Page, reservation_url: str) -> List[Dict[str, Any]]:
    page.goto(reservation_url, wait_until="networkidle")
    page.wait_for_timeout(500)

    body_text = page.locator("body").inner_text()

    reservation_id = reservation_url.rstrip("/").split("/")[-1]

    reservation_fields = parse_reservation_fields_from_text(body_text)
    reservation_fields["reservation_id"] = reservation_id

    tables = read_tables_from_page(page)

    if len(tables) < 1:
        raise RuntimeError(f"No stay table found for {reservation_id}")

    stay_df = tables[0]

    required_cols = {
        "stay_date",
        "daily_room_revenue_before_tax",
        "daily_total_revenue_before_tax",
    }

    if not required_cols.issubset(set(stay_df.columns)):
        print("Columns found:", stay_df.columns.tolist())
        raise RuntimeError(f"Stay table columns not recognised for {reservation_id}")

    records = []

    for night_index, (_, stay_row) in enumerate(stay_df.iterrows(), start=1):
        combined = {}
        combined.update(reservation_fields)
        combined.update(stay_row.to_dict())
        combined["night_index"] = night_index
        records.append(combined)

    return records


# -----------------------------
# Transform lookup tables
# -----------------------------

def transform_room_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = []

    for _, row in df.iterrows():
        rows.append({
            "space_type": str(row["space_type"]).strip(),
            "room_class": str(row["room_class"]).strip(),
            "display_name": str(row["display_name"]).strip(),
            "number_of_rooms": clean_int(row["number_of_rooms"]),
        })

    return rows


def transform_market_codes(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = []

    for _, row in df.iterrows():
        rows.append({
            "market_code": str(row["market_code"]).strip(),
            "market_name": str(row["market_name"]).strip(),
            "macro_group": str(row["macro_group"]).strip(),
            "description": str(row["description"]).strip(),
        })

    return rows


def transform_channel_codes(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = []

    for _, row in df.iterrows():
        rows.append({
            "channel_code": str(row["channel_code"]).strip(),
            "channel_name": str(row["channel_name"]).strip(),
            "channel_group": str(row["channel_group"]).strip(),
        })

    return rows


# -----------------------------
# Transform reservation stay rows
# -----------------------------

def make_reservation_stay_id(reservation_id: str, night_index: int) -> int:
    """
    Stable BIGINT primary key generated from reservation_id + night_index.

    This works for both normal reservation IDs such as:
    - R0001
    - R0250
    - R5100

    and edge-case IDs such as:
    - RES-EDGE-001
    - RES-ZEPHYR-7F3A
    """
    raw_key = f"{reservation_id}-{night_index}"
    hashed = hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    # First 15 hex characters safely fit inside PostgreSQL BIGINT.
    return int(hashed[:15], 16)


def transform_reservations(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []

    for r in raw_records:
        reservation_id = str(r["reservation_id"]).strip()
        night_index = clean_int(r["night_index"])

        row = {
            "reservation_stay_id": make_reservation_stay_id(reservation_id, night_index),
            "reservation_id": reservation_id,

            "arrival_date": clean_date(r.get("arrival_date")),
            "departure_date": clean_date(r.get("departure_date")),
            "stay_date": clean_date(r.get("stay_date")),

            "reservation_status": str(r.get("reservation_status")).strip(),

            "create_datetime": clean_datetime(r.get("create_datetime")),
            "cancellation_datetime": clean_datetime(r.get("cancellation_datetime")),

            "guest_country": none_if_blank(r.get("guest_country")),
            "is_block": clean_bool(r.get("is_block")),
            "is_walk_in": clean_bool(r.get("is_walk_in")),

            "number_of_spaces": clean_int(r.get("number_of_spaces")),
            "space_type": str(r.get("space_type")).strip(),
            "market_code": str(r.get("market_code")).strip(),
            "channel_code": str(r.get("channel_code")).strip(),

            "source_name": none_if_blank(r.get("source_name")),
            "rate_plan_code": none_if_blank(r.get("rate_plan_code")),

            "daily_room_revenue_before_tax": clean_decimal(r.get("daily_room_revenue_before_tax")),
            "daily_total_revenue_before_tax": clean_decimal(r.get("daily_total_revenue_before_tax")),

            "nights": clean_int(r.get("nights")),
            "adr_room": clean_decimal(r.get("adr_room")),
            "lead_time": clean_int(r.get("lead_time")),

            "company_name": none_if_blank(r.get("company_name")),
            "travel_agent_name": none_if_blank(r.get("travel_agent_name")),
        }

        if row["stay_date"] is None:
            raise RuntimeError(f"Missing stay_date for {reservation_id}")

        rows.append(row)

    return rows


# -----------------------------
# Load
# -----------------------------

def insert_many(sql: str, rows: List[Dict[str, Any]]):
    if not rows:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
        conn.commit()


def truncate_tables():
    print("Truncating existing data...")

    sql = """
    TRUNCATE TABLE
        reservations_hackathon,
        room_type_lookup,
        market_code_lookup,
        channel_code_lookup
    RESTART IDENTITY CASCADE;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def load_room_types(rows: List[Dict[str, Any]]):
    sql = """
    INSERT INTO room_type_lookup
    (space_type, room_class, display_name, number_of_rooms)
    VALUES
    (%(space_type)s, %(room_class)s, %(display_name)s, %(number_of_rooms)s)
    """

    insert_many(sql, rows)


def load_market_codes(rows: List[Dict[str, Any]]):
    sql = """
    INSERT INTO market_code_lookup
    (market_code, market_name, macro_group, description)
    VALUES
    (%(market_code)s, %(market_name)s, %(macro_group)s, %(description)s)
    """

    insert_many(sql, rows)


def load_channel_codes(rows: List[Dict[str, Any]]):
    sql = """
    INSERT INTO channel_code_lookup
    (channel_code, channel_name, channel_group)
    VALUES
    (%(channel_code)s, %(channel_name)s, %(channel_group)s)
    """

    insert_many(sql, rows)


def load_reservations(rows: List[Dict[str, Any]]):
    sql = """
    INSERT INTO reservations_hackathon
    (
        reservation_stay_id,
        reservation_id,
        arrival_date,
        departure_date,
        stay_date,
        reservation_status,
        create_datetime,
        cancellation_datetime,
        guest_country,
        is_block,
        is_walk_in,
        number_of_spaces,
        space_type,
        market_code,
        channel_code,
        source_name,
        rate_plan_code,
        daily_room_revenue_before_tax,
        daily_total_revenue_before_tax,
        nights,
        adr_room,
        lead_time,
        company_name,
        travel_agent_name
    )
    VALUES
    (
        %(reservation_stay_id)s,
        %(reservation_id)s,
        %(arrival_date)s,
        %(departure_date)s,
        %(stay_date)s,
        %(reservation_status)s,
        %(create_datetime)s,
        %(cancellation_datetime)s,
        %(guest_country)s,
        %(is_block)s,
        %(is_walk_in)s,
        %(number_of_spaces)s,
        %(space_type)s,
        %(market_code)s,
        %(channel_code)s,
        %(source_name)s,
        %(rate_plan_code)s,
        %(daily_room_revenue_before_tax)s,
        %(daily_total_revenue_before_tax)s,
        %(nights)s,
        %(adr_room)s,
        %(lead_time)s,
        %(company_name)s,
        %(travel_agent_name)s
    )
    """

    insert_many(sql, rows)


def load_all(
    room_types: List[Dict[str, Any]],
    market_codes: List[Dict[str, Any]],
    channel_codes: List[Dict[str, Any]],
    reservations: List[Dict[str, Any]],
):
    truncate_tables()

    print("Loading room_type_lookup...")
    load_room_types(room_types)

    print("Loading market_code_lookup...")
    load_market_codes(market_codes)

    print("Loading channel_code_lookup...")
    load_channel_codes(channel_codes)

    print("Loading reservations_hackathon...")
    load_reservations(reservations)


# -----------------------------
# Verify
# -----------------------------

def verify_load() -> Dict[str, Any]:
    checks = {}

    queries = {
        "total_stay_rows": "SELECT COUNT(*) AS value FROM reservations_hackathon",
        "total_reservations": "SELECT COUNT(DISTINCT reservation_id) AS value FROM reservations_hackathon",
        "room_type_lookup": "SELECT COUNT(*) AS value FROM room_type_lookup",
        "market_code_lookup": "SELECT COUNT(*) AS value FROM market_code_lookup",
        "channel_code_lookup": "SELECT COUNT(*) AS value FROM channel_code_lookup",
        "duplicate_reservation_stay_ids": """
            SELECT COUNT(*) AS value
            FROM (
                SELECT reservation_stay_id
                FROM reservations_hackathon
                GROUP BY reservation_stay_id
                HAVING COUNT(*) > 1
            ) x
        """,
        "missing_stay_dates": """
            SELECT COUNT(*) AS value
            FROM reservations_hackathon
            WHERE stay_date IS NULL
        """,
        "missing_total_revenue": """
            SELECT COUNT(*) AS value
            FROM reservations_hackathon
            WHERE daily_total_revenue_before_tax IS NULL
        """,
    }

    for name, query in queries.items():
        checks[name] = fetch_all(query)[0]["value"]

    return checks


# -----------------------------
# Run full ETL
# -----------------------------

def run_etl():
    print("Starting ETL...")
    print(f"Base URL: {BASE_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        reference = scrape_reference_tables(page)
        reservation_links = scrape_all_reservation_links(page)

        print(f"\nTotal reservation links found: {len(reservation_links)}")

        raw_reservation_records = []

        for index, link in enumerate(reservation_links, start=1):
            print(f"Scraping detail {index}/{len(reservation_links)}: {link}")
            records = scrape_reservation_detail(page, link)
            raw_reservation_records.extend(records)

        browser.close()

    print(f"\nRaw reservation stay rows scraped: {len(raw_reservation_records)}")

    print("Transforming data...")

    room_types = transform_room_types(reference["room_types"])
    market_codes = transform_market_codes(reference["market_codes"])
    channel_codes = transform_channel_codes(reference["channel_codes"])
    reservations = transform_reservations(raw_reservation_records)

    print(f"Transformed room types: {len(room_types)}")
    print(f"Transformed market codes: {len(market_codes)}")
    print(f"Transformed channel codes: {len(channel_codes)}")
    print(f"Transformed reservation stay rows: {len(reservations)}")

    print("Loading data...")
    load_all(room_types, market_codes, channel_codes, reservations)

    print("Verifying database...")
    checks = verify_load()

    print("\nETL complete.")
    print(checks)

    return checks


if __name__ == "__main__":
    run_etl()