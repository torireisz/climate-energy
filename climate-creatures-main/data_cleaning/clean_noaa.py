"""
Clean raw NOAA weather data and aggregate it to monthly, state-level data.
Input:
    ..raw_fetched_data/raw_noaa.csv
Output:
    ..processed_data/cleaned_noaa.csv
"""

import pandas as pd

PATH_TO_FILE = "../raw_fetched_data/raw_noaa.csv"
OUTPUT_PATH = "../cleaned_data/cleaned_noaa.csv"
BASE_TEMP_C = 18    # Base temperature in Celsius for calculating HDD and CDD (65F = 18C)
# comfortable indoor temperature where you don’t need heating or cooling, established by NOAA.

def load_data():
    """Load raw NOAA data"""
    df = pd.read_csv(PATH_TO_FILE)
    print(f"Loaded data with shape {df.shape}")
    return df


def clean_data(df):
    """
    Basic cleaning:
    - keep needed columns
    - drop duplicates
    - handle missing values
    - parse date
    - keep only TMAX/TMIN
    """
    df_clean = df.copy()

    # keep only columns we need
    df_clean = df_clean[["date", "datatype", "station", "value", "state_abbr"]]

    # remove duplicates
    print(f"Number of duplicates: {df_clean.duplicated().sum()}")
    df_clean = df_clean.drop_duplicates()

    # drop missing critical values
    df_clean = df_clean.dropna(subset=["date", "datatype", "station", "value", "state_abbr"])

    # clean text columns
    df_clean["datatype"] = df_clean["datatype"].str.strip().str.upper()
    df_clean["station"] = df_clean["station"].str.strip()
    df_clean["state_abbr"] = df_clean["state_abbr"].str.strip().str.upper()

    # keep only TMAX and TMIN
    df_clean = df_clean[df_clean["datatype"].isin(["TMAX", "TMIN"])]

    # convert date and value
    df_clean["date"] = pd.to_datetime(df_clean["date"])
    df_clean["value"] = pd.to_numeric(df_clean["value"], errors="coerce")

    # drop rows where value became invalid
    df_clean = df_clean.dropna(subset=["value"])

    # add time columns
    df_clean["year"] = df_clean["date"].dt.year
    df_clean["month"] = df_clean["date"].dt.month
    df_clean["day"] = df_clean["date"].dt.day

    print(f"Cleaned data shape: {df_clean.shape}")
    return df_clean

def pivot_weather(df):
    """
    Pivot NOAA long format into wide format so TMAX and TMIN are columns
    """
    df_pivot = df.pivot_table(
        index=["station", "state_abbr", "date", "year", "month", "day"],
        columns="datatype",
        values="value",
        aggfunc="mean"
    ).reset_index()

    df_pivot.columns.name = None
    print(f"Pivoted data shape: {df_pivot.shape}")
    return df_pivot


def add_weather_features(df):
    """
    - TAVG
    - HDD
    - CDD
    """
    df_features = df.copy()

    # Any value below 0 is replaced with 0, and everything else stays the same.
    df_features["TAVG"] = (df_features["TMAX"] + df_features["TMIN"]) / 2
    df_features["HDD"] = (BASE_TEMP_C - df_features["TAVG"]).clip(lower=0)
    df_features["CDD"] = (df_features["TAVG"] - BASE_TEMP_C).clip(lower=0)

    return df_features

def aggregate_station_month(df):
    """
    Aggregate daily station data to monthly station data
    """
    df_station = df.groupby(
        ["station", "state_abbr", "year", "month"],
        as_index=False
    ).agg({
        "TMAX": "mean",
        "TMIN": "mean",
        "TAVG": "mean",
        "HDD": "sum",
        "CDD": "sum"
    })

    print(f"Station-month shape: {df_station.shape}")
    return df_station


def aggregate_state(df):
    """
    Aggregate station-month data to monthly state-level data

    Temperature variables -> mean across stations
    HDD/CDD -> mean across stations
    """
    df_state = df.groupby(
        ["state_abbr", "year", "month"],
        as_index=False
    ).agg({
        "TMAX": "mean",
        "TMIN": "mean",
        "TAVG": "mean",
        "HDD": "mean",
        "CDD": "mean"
    })

    print(f"State-month shape: {df_state.shape}")
    return df_state

if __name__ == "__main__":
    df = load_data()
    df = clean_data(df)
    df = pivot_weather(df)
    df = add_weather_features(df)
    df = aggregate_station_month(df)
    df = aggregate_state(df)
    df = df.sort_values(["state_abbr", "year", "month"]).reset_index(drop=True)

    df.to_csv(OUTPUT_PATH, index=False)
    print(df.head())
