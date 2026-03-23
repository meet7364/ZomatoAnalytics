"""
Zomato Bangalore — Data Cleaning Script
========================================
Reads the raw Kaggle dataset, applies cleaning transformations,
and saves a clean CSV ready for PostgreSQL loading.

Usage:
    uv run python src/clean.py
"""

from pathlib import Path

import pandas as pd


# ── Paths ────────────────────────────────────────────────────────
RAW_PATH: Path = Path("data/raw/zomato.csv")
CLEAN_PATH: Path = Path("data/processed/zomato_clean.csv")


def load_raw(path: Path) -> pd.DataFrame:
    """Load the raw Zomato CSV."""
    return pd.read_csv(path)


def clean_rate(series: pd.Series) -> pd.Series:
    """
    Extract the numeric rating from strings like '4.1/5'.
    Handles 'NEW', '-', NaN → pd.NA.
    """
    cleaned = series.astype(str).str.strip()
    # Replace known non-numeric sentinels with NA
    cleaned = cleaned.replace(["NEW", "-", "nan", "None", "", "/5"], pd.NA)
    # Extract the number before '/5'
    cleaned = cleaned.str.replace(r"\s*/\s*5$", "", regex=True)
    # Convert to numeric — anything remaining non-numeric becomes NA
    return pd.to_numeric(cleaned, errors="coerce")


def clean_cost(series: pd.Series) -> pd.Series:
    """
    Clean approx cost: remove commas, convert to integer.
    Non-numeric values → pd.NA.
    """
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return numeric.astype("Int64")  # nullable integer


def clean_boolean(series: pd.Series) -> pd.Series:
    """Map 'Yes' → True, 'No' → False."""
    return series.map({"Yes": True, "No": False})


def clean_votes(series: pd.Series) -> pd.Series:
    """Convert votes to nullable integer."""
    return pd.to_numeric(series, errors="coerce").astype("Int64")


# ── Column renaming map ─────────────────────────────────────────
RENAME_MAP: dict[str, str] = {
    "approx_cost(for two people)": "approx_cost",
    "listed_in(type)": "listed_type",
    "listed_in(city)": "listed_city",
    "rest_type": "restaurant_type",
}

# Columns to keep (drop url, address, phone, dish_liked, reviews_list, menu_item)
KEEP_COLUMNS: list[str] = [
    "name",
    "online_order",
    "book_table",
    "rate",
    "votes",
    "location",
    "restaurant_type",
    "cuisines",
    "approx_cost",
    "listed_type",
    "listed_city",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning transformations and return a clean DataFrame."""
    raw_rows = len(df)
    print(f"Raw rows loaded: {raw_rows:,}")

    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()
    print(f"After dedup:     {len(df):,}  (dropped {raw_rows - len(df):,} duplicates)")

    # 2. Rename columns
    df = df.rename(columns=RENAME_MAP)

    # 3. Clean individual columns
    df["rate"] = clean_rate(df["rate"])
    df["approx_cost"] = clean_cost(df["approx_cost"])
    df["votes"] = clean_votes(df["votes"])
    df["online_order"] = clean_boolean(df["online_order"])
    df["book_table"] = clean_boolean(df["book_table"])

    # 4. Strip whitespace from text columns
    for col in ["name", "location", "restaurant_type", "cuisines", "listed_type", "listed_city"]:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["nan", "None", ""], pd.NA)

    # 5. Drop rows where name or location is null
    before = len(df)
    df = df.dropna(subset=["name", "location"])
    print(f"After null drop:  {len(df):,}  (dropped {before - len(df):,} with null name/location)")

    # 6. Keep only relevant columns
    df = df[KEEP_COLUMNS]

    return df


def print_summary(df: pd.DataFrame) -> None:
    """Print a cleaning summary report."""
    print("\n" + "=" * 55)
    print("  CLEANING SUMMARY")
    print("=" * 55)
    print(f"  Final rows:    {len(df):,}")
    print(f"  Final columns: {len(df.columns)}")
    print(f"\n  Null counts per column:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        pct = null_count / len(df) * 100
        print(f"    {col:<20s} {null_count:>6,}  ({pct:.1f}%)")
    print("=" * 55)


def main() -> None:
    """Entry point: load → clean → save."""
    df_raw = load_raw(RAW_PATH)
    df_clean = clean_data(df_raw)

    # Ensure output directory exists
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"\n✅ Saved cleaned data to {CLEAN_PATH}")
    print_summary(df_clean)


if __name__ == "__main__":
    main()
