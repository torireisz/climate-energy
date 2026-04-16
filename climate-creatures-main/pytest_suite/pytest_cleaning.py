"""
Pytest
Cleaning tests for individual datasets
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

NOAA_PATH = BASE_DIR / "cleaned_data" / "cleaned_noaa.csv"
EIA_PATH = BASE_DIR / "cleaned_data" / "cleaned_eia_data.csv"
BEA_PATH = BASE_DIR / "cleaned_data" / "clean_bea.csv"
FINAL_PATH = BASE_DIR / "final_dataset.csv"

# FIXTURES
@pytest.fixture
def noaa_data():
    """Load cleaned NOAA data"""
    return pd.read_csv(NOAA_PATH)


@pytest.fixture
def eia_data():
    """Load cleaned EIA data"""
    return pd.read_csv(EIA_PATH)


@pytest.fixture
def bea_data():
    """Load cleaned BEA data"""
    return pd.read_csv(BEA_PATH)


# DATA CLEANING TESTS

def test_noaa_no_duplicates(noaa_data):
    """NOAA should have no duplicate state-year-month rows."""
    dupes = noaa_data.duplicated(subset=["state_abbr", "year", "month"]).sum()
    assert dupes == 0


def test_eia_no_duplicates(eia_data):
    """EIA should have no duplicate state-year-month-sector rows."""
    dupes = eia_data.duplicated(subset=["state", "year", "month", "sectorid"]).sum()
    assert dupes == 0


def test_bea_no_duplicates(bea_data):
    """BEA should have no duplicate state-year rows."""
    dupes = bea_data.duplicated(subset=["GeoName", "Year"]).sum()
    assert dupes == 0


def test_noaa_missing_values(noaa_data):
    """NOAA merge keys should not have missing values."""
    assert noaa_data["state_abbr"].notna().all()
    assert noaa_data["year"].notna().all()
    assert noaa_data["month"].notna().all()


def test_eia_missing_values(eia_data):
    """EIA merge keys should not have missing values."""
    assert eia_data["state"].notna().all()
    assert eia_data["year"].notna().all()
    assert eia_data["month"].notna().all()
    assert eia_data["sectorid"].notna().all()


def test_bea_missing_values(bea_data):
    """BEA merge keys should not have missing values."""
    assert bea_data["GeoName"].notna().all()
    assert bea_data["Year"].notna().all()


def test_noaa_expected_format(noaa_data):
    """NOAA should be aggregated to state-year-month."""
    counts = noaa_data.groupby(["state_abbr", "year", "month"]).size()
    assert (counts == 1).all()


def test_eia_expected_format(eia_data):
    """EIA should be structured as state-year-month-sector."""
    counts = eia_data.groupby(["state", "year", "month", "sectorid"]).size()
    assert (counts == 1).all()


def test_bea_expected_format(bea_data):
    """BEA should be structured as state-year."""
    counts = bea_data.groupby(["GeoName", "Year"]).size()
    assert (counts == 1).all()
