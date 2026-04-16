import pandas as pd
# load raw EIA dataset
df = pd.read_csv("../raw_fetched_data/all_new_england_eia_data_2014_2024.csv")

# preview data structure
print(df.head())
print(df.info())

# check for missing values
print("Missing values:")
print(df.isnull().sum())

# drop rows missing important columns
df = df.dropna(subset=["period", "stateid", "sectorName", "sales"])

# check and remove duplicates
print("Duplicate rows:", df.duplicated().sum())
df = df.drop_duplicates()

# convert columns to correct data types
df["period"] = pd.to_datetime(df["period"])
df["sales"] = pd.to_numeric(df["sales"])

# extract year and month for merging 
df["year"] = df["period"].dt.year
df["month"] = df["period"].dt.month

df = df.rename(columns={
    "stateid": "state",
    "stateDescription": "state_name",
    "sectorName": "sector",
    "sales-units": "sales_units"
})

df["state"] = df["state"].str.upper()
df["sector"] = df["sector"].str.lower()

print(df.head())
print(df.info())

# save cleaned dataset
df.to_csv("../cleaned_data/cleaned_eia.csv", index=False)
