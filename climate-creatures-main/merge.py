"""
merge.py

Merge cleaned NOAA, EIA, and BEA datasets into one final dataset.

Final grain:
one row per state-month-sector

Merge keys:
- NOAA + EIA: state, year, month
- + BEA: state, year
"""

import pandas as pd
from pathlib import Path


NOAA_FILE = Path("cleaned_data/cleaned_noaa.csv")
EIA_FILE = Path("cleaned_data/cleaned_eia_data.csv")
BEA_FILE = Path("cleaned_data/clean_bea.csv")
OUTPUT_FILE = Path("final_dataset.csv")


def load_data():
    """Load cleaned datasets."""
    noaa_df = pd.read_csv(NOAA_FILE)
    eia_df = pd.read_csv(EIA_FILE)
    bea_df = pd.read_csv(BEA_FILE)

    return noaa_df, eia_df, bea_df


def standardize_columns(noaa_df, eia_df, bea_df):
    """Rename columns so merge keys match across datasets."""

    # NOAA: state_abbr -> state
    noaa_df = noaa_df.rename(columns={
        "state_abbr": "state"
    })

    # BEA: GeoName -> state, Year -> year
    bea_df = bea_df.rename(columns={
        "GeoName": "state",
        "Year": "year",
        "Per Capita Income": "per_capita_income",
        "Population": "population"
    })

    # make sure key columns have same types
    noaa_df["state"] = noaa_df["state"].astype(str).str.strip()
    eia_df["state"] = eia_df["state"].astype(str).str.strip()
    bea_df["state"] = bea_df["state"].astype(str).str.strip()

    noaa_df["year"] = noaa_df["year"].astype(int)
    eia_df["year"] = eia_df["year"].astype(int)
    bea_df["year"] = bea_df["year"].astype(int)

    noaa_df["month"] = noaa_df["month"].astype(int)
    eia_df["month"] = eia_df["month"].astype(int)

    return noaa_df, eia_df, bea_df


def merge_noaa_eia(noaa_df, eia_df):
    """
    Merge monthly state-level weather with monthly state-sector electricity data.
    This should create one row per state-month-sector.
    """
    merged_df = pd.merge(
        eia_df,
        noaa_df,
        on=["state", "year", "month"],
        how="left",
        validate="many_to_one"
    )

    return merged_df


def merge_bea(merged_df, bea_df):
    """
    Merge annual BEA socioeconomic data onto monthly dataset by state and year.
    """
    merged_df = pd.merge(
        merged_df,
        bea_df,
        on=["state", "year"],
        how="left",
        validate="many_to_one"
    )

    return merged_df

def save_data(df):
    """Save merged dataset."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved merged dataset to: {OUTPUT_FILE}")


def main():
    noaa_df, eia_df, bea_df = load_data()

    noaa_df, eia_df, bea_df = standardize_columns(noaa_df, eia_df, bea_df)

    merged_df = merge_noaa_eia(noaa_df, eia_df)
    merged_df = merge_bea(merged_df, bea_df)

    save_data(merged_df)


if __name__ == "__main__":
    main()