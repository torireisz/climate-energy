"""
Pytest
Merge tests for final dataset
"""

import pandas as pd
import pytest

EIA_PATH = "cleaned_data/cleaned_eia_data.csv"
FINAL_PATH = "final_dataset.csv"

# FIXTURES

@pytest.fixture
def eia_data():
    """Load cleaned EIA data"""
    return pd.read_csv(EIA_PATH)


@pytest.fixture
def final_data():
    """Load merged final dataset"""
    return pd.read_csv(FINAL_PATH)

# MERGE TESTS

def test_final_dataset_preserves_eia_rows(eia_data, final_data):
    """
    Final merged dataset should preserve EIA rows
    because EIA is the main dataset.
    """
    assert len(final_data) == len(eia_data)


def test_final_dataset_has_merged_columns(final_data):
    """
    Final dataset should include merged weather and BEA columns.
    """
    assert "TMAX" in final_data.columns
    assert "TMIN" in final_data.columns
    assert "HDD" in final_data.columns
    assert "CDD" in final_data.columns
    assert "population" in final_data.columns
    assert "per_capita_income" in final_data.columns


def test_final_dataset_no_duplicates(final_data):
    """
    Final merged dataset should have one row per
    state-year-month-sector.
    """
    dupes = final_data.duplicated(subset=["state", "year", "month", "sectorid"]).sum()
    assert dupes == 0


if __name__ == "__main__":
    pass
