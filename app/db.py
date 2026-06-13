import os
from decimal import Decimal
from datetime import date, datetime

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def json_safe_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def json_safe_row(row: dict):
    return {key: json_safe_value(value) for key, value in row.items()}


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Add it to your .env file.")

    return psycopg.connect(DATABASE_URL)


def fetch_all(query: str, params: tuple = ()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)

            if cur.description is None:
                return []

            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                json_safe_row(dict(zip(columns, row)))
                for row in rows
            ]


def execute(query: str, params: tuple = ()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)

        conn.commit()