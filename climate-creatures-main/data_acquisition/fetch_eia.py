import requests
import pandas as pd

# API key for EIA
API_KEY = "Wh8lpBPWgSewNECwtphd6SRyqhwX9rSzw9mQbYeg"

# New England states and sectors 
states = ["CT", "ME", "MA", "NH", "RI", "VT"]
sectors = ["RES", "COM"]

all_dfs = []

# loop through each state and sector to pull data
for state in states:
    for sector in sectors:
        url = (
            f"https://api.eia.gov/v2/electricity/retail-sales/data"
            f"?api_key={API_KEY}"
            f"&frequency=monthly"
            f"&data[0]=sales"
            f"&facets[stateid][]={state}"
            f"&facets[sectorid][]={sector}"
        )
     
        # request data from API
        response = requests.get(url)
        data = response.json()

        # convert to dataframe
        df = pd.DataFrame(data["response"]["data"])
        all_dfs.append(df)

# combine all state/sector data into one dataframe
final_df = pd.concat(all_dfs, ignore_index=True)

# convert period to datetime and filter years (2014–2024)
final_df["period"] = pd.to_datetime(final_df["period"])
final_df = final_df[
    (final_df["period"].dt.year >= 2014) &
    (final_df["period"].dt.year <= 2024)
]

print(final_df.head())
print(final_df.columns)
print(final_df["stateid"].unique())
print(final_df["sectorName"].unique())
print(final_df["period"].min(), final_df["period"].max())

# save raw data
final_df.to_csv("../raw_fetched_data/raw_eia.csv", index=False)
