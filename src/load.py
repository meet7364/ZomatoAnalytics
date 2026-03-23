"""
Zomato Bangalore — Load to PostgreSQL
======================================
Reads the cleaned CSV and loads it into the ``raw.zomato`` table
on Neon PostgreSQL.  Idempotent (replaces table on each run).

Usage:
    uv run python src/load.py
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


CLEAN_PATH: Path = Path("data/processed/zomato_clean.csv")


def get_engine():
    """Create a SQLAlchemy engine from DATABASE_URL in .env."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not found. Add it to .env")
    return create_engine(url)


def load_to_postgres(df: pd.DataFrame) -> int:
    """
    Load DataFrame into raw.zomato table.

    Returns
    -------
    int
        Number of rows loaded.
    """
    engine = get_engine()

    # Ensure the 'raw' schema exists
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.commit()

    # Write to raw.zomato — replace if already exists
    df.to_sql(
        name="zomato",
        con=engine,
        schema="raw",
        if_exists="replace",
        index=False,
    )

    # Verify row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM raw.zomato"))
        count = result.scalar()

    return count


def main() -> None:
    """Entry point: read cleaned CSV → load to PostgreSQL."""
    print(f"Reading {CLEAN_PATH} ...")
    df = pd.read_csv(CLEAN_PATH)
    print(f"  Rows in CSV: {len(df):,}")

    print("Loading to raw.zomato on PostgreSQL ...")
    count = load_to_postgres(df)
    print(f"\n✅ Loaded {count:,} rows into raw.zomato")


if __name__ == "__main__":
    main()
