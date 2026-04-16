from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

NOAA_PATH = BASE_DIR / "cleaned_data" / "cleaned_noaa.csv"
EIA_PATH = BASE_DIR / "cleaned_data" / "cleaned_eia_data.csv"
BEA_PATH = BASE_DIR / "cleaned_data" / "clean_bea.csv"

noaa = pd.read_csv(NOAA_PATH)
eia = pd.read_csv(EIA_PATH)
bea = pd.read_csv(BEA_PATH)

datasets = {
    "NOAA": noaa,
    "EIA": eia,
    "BEA": bea
}


def test_datasets_not_empty():
    for name, df in datasets.items():
        assert df is not None, f"{name} dataset failed to load"
        assert len(df) > 0, f"{name} dataset is empty"


def test_required_columns():
    required_columns = {
        "NOAA": ["state_abbr", "year", "month"],
        "EIA": ["state", "year", "month", "sectorid", "sales"],
        "BEA": ["GeoName", "Year"]
    }

    for name, df in datasets.items():
        for col in required_columns[name]:
            assert col in df.columns, f"{col} missing from {name} dataset"