import pandas as pd
from pandas.api.types import (
    is_string_dtype,
    is_integer_dtype,
    is_numeric_dtype
)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FINAL_PATH = BASE_DIR / "final_dataset.csv"

# valid values for checks
VALID_STATES = {"CT", "ME", "MA", "NH", "RI", "VT"}
VALID_SECTORS = {"residential", "commercial"}

# load merged dataset
def load_merged_data():
    return pd.read_csv(FINAL_PATH)

# check that all states are valid New England states
def test_states_are_valid_new_england_states():
    df = load_merged_data()
    assert set(df["state"].unique()).issubset(VALID_STATES)

# check year range is within project scope
def test_years_are_between_2014_and_2024():
    df = load_merged_data()
    assert df["year"].between(2014, 2024).all()

# check month values are valid (1–12)
def test_months_are_between_1_and_12():
    df = load_merged_data()
    assert df["month"].between(1, 12).all()

# check sector values are only residential or commercial
def test_sector_contains_only_valid_values():
    df = load_merged_data()
    assert set(df["sector"].dropna().str.lower().unique()).issubset(VALID_SECTORS)

# check derived weather values are nonnegative
def test_hdd_and_cdd_are_nonnegative():
    df = load_merged_data()
    assert (df["HDD"] >= 0).all()
    assert (df["CDD"] >= 0).all()

# check data types
def test_state_column_is_string():
    df = load_merged_data()
    assert is_string_dtype(df["state"])


def test_year_and_month_are_integer():
    df = load_merged_data()
    assert is_integer_dtype(df["year"])
    assert is_integer_dtype(df["month"])

# check numeric columns
def test_numeric_columns_are_numeric():
    df = load_merged_data()

    numeric_cols = [
        "sales", "TMAX", "TMIN", "TAVG",
        "HDD", "CDD", "population", "per_capita_income"
    ]

    for col in numeric_cols:
        assert is_numeric_dtype(df[col]), f"{col} is not numeric"
