import pandas as pd

df = pd.read_csv("../raw_fetched_data/raw_bea.csv")


df["GeoFIPS"] = df["GeoFIPS"].str.replace('"', '')

new_england_states = [
    "Maine",
    "Massachusetts",
    "New Hampshire",
    "Rhode Island",
    "Connecticut",
    "Vermont"]

df["GeoName"] = df["GeoName"].str.replace(" *", "", regex=False)
df = df[df["GeoName"].isin(new_england_states)]
df = df[df["LineCode"].isin([2, 3])]

years = [str(y) for y in range(2014, 2025)]

df_long = df.melt(
    id_vars=["GeoName", "LineCode"],
    value_vars=years,
    var_name="Year",
    value_name="Value")

df_long["Year"] = df_long["Year"].astype(int)
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

df_final = df_long.pivot_table(
    index=["GeoName", "Year"],
    columns="LineCode",
    values="Value").reset_index()

df_final = df_final.rename(columns={
    2: "Population",
    3: "Per Capita Income"})

print("Missing values:")
print(df_final.isna().sum())

df_final["GeoName"] = df_final["GeoName"].astype(str)
df_final["Year"] = df_final["Year"].astype(str)

df_final["Population"] = pd.to_numeric(df_final["Population"], errors="coerce")
df_final["Per Capita Income"] = pd.to_numeric(df_final["Per Capita Income"], errors="coerce")

print("\nMissing values after conversion:")
print(df_final.isna().sum())

df_final = df_final.dropna(subset=["Population", "Per Capita Income"])

df_final["Population"] = df_final["Population"].astype(int)
df_final["Per Capita Income"] = df_final["Per Capita Income"].astype(int)

state_abbrev = {
    "Maine": "ME",
    "Massachusetts": "MA",
    "New Hampshire": "NH",
    "Rhode Island": "RI",
    "Connecticut": "CT",
    "Vermont": "VT"
}

df_final["GeoName"] = df_final["GeoName"].map(state_abbrev)

df_final.to_csv("../cleaned_data/cleaned_bea.csv", index=False)
