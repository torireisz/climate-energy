import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

'''
Fetching NOAA weather data for New England states from 2014 to 2024, with error handling and retry logic.
https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted
- NOAA API has a limit of 1000 rows per request, so we implement pagination to fetch all data for each state-year combo.

'An access token is required to use the API, and each token will be limited to 
five requests per second and 10,000 requests per day.'

'''

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Read API token from the .env file
TOKEN = os.getenv("NOAA_TOKEN")

HEADERS = {"token": TOKEN}
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

# Map each New England state abbreviation to its NOAA FIPS location ID
STATE_FIPS = {
    "CT": "FIPS:09",
    "ME": "FIPS:23",
    "MA": "FIPS:25",
    "NH": "FIPS:33",
    "RI": "FIPS:44",
    "VT": "FIPS:50"
}

# year range we want to pull weather data for
START_YEAR = 2014
END_YEAR = 2024


def demo_basic_error_handling(response):
    # check for response fail, prints details and retries logic
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Request failed.")
        print(f"Status code: {response.status_code}")
        print("Response text:")
        print(response.text)
        raise e


def request_with_retry(url, params=None, headers=None, max_retries=5, timeout=30):
    # wait time increases with each retry (accounts for rate limits)
    wait = 1

    for attempt in range(1, max_retries + 1):
        try:
            # get request to noaa api with params, headers, and timeout
            response = requests.get(url, params=params, headers=headers, timeout=timeout)

            # retry in case of rate limit (429) or server errors (5xx)
            if response.status_code == 429 or 500 <= response.status_code < 600:
                print(
                    f"Attempt {attempt}/{max_retries} failed with "
                    f"{response.status_code}. Retrying in {wait} sec..."
                )
                print(response.text)
                time.sleep(wait)
                wait *= 2
                continue
            # calling basic error handling in case of bad response (non-2xx)
            demo_basic_error_handling(response)

            # return api response as json if successful
            return response.json()

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # retry in case of network issues or timeouts
            print(
                f"Attempt {attempt}/{max_retries} had a network error: {e}. "
                f"Retrying in {wait} sec..."
            )
            time.sleep(wait)
            wait *= 2
    # just stop if all retries are exhausted, this way you don't risk random missing data
    raise RuntimeError("Max retries exceeded.")


def fetch_weather_for_state_year(state_abbr: str, location_id: str, year: int) -> pd.DataFrame:
    all_rows = [] # all rows for state-year combo
    offset = 1
    limit = 1000

    startdate = f"{year}-01-01"
    enddate = f"{year}-12-31"

    while True:
        # query params for paginated NOAA API req
        params = {
            "datasetid": "GHCND", # this is the daily summaries dataset
            "locationid": location_id, # based on state
            "startdate": startdate,
            "enddate": enddate,
            "datatypeid": "TMAX,TMIN",
            "limit": limit, # per req, fetch 1000 rows (as per noaa documentation, max is 1000)
            "offset": offset, # 1 cause NOAA's pagination is 1-indexed
            "units": "metric"
        }
        # make request with retry logic
        data = request_with_retry(BASE, params=params, headers=HEADERS)

        # extract rows from response
        rows = data.get("results", [])
        if not rows:
            break
        # add state and year to each row for easier merging later
        for row in rows:
            row["state_abbr"] = state_abbr
            row["pull_year"] = year
        # add rows to all_rows for this state-year
        all_rows.extend(rows)

        # pagination metadata to get total count of rows for this query
        resultset = data.get("metadata", {}).get("resultset", {})
        count = resultset.get("count", 0)

        # printing progress to track fetched data
        print(
            f"{state_abbr} {year}: fetched {len(all_rows)} of {count} rows "
            f"(offset={offset})"
        )

        # stop if we've fetched all rows for this state-year combo
        if offset + limit > count:
            break
        # next page offset, and sleep a bit to avoid hitting rate limits
        offset += limit
        time.sleep(0.25)

    return pd.DataFrame(all_rows)


def main():
    # storing all state-year dfs to later concat
    all_frames = []

    # iterating through each state and year, fetching weather data, and appending to all_frames
    for state_abbr, location_id in STATE_FIPS.items():
        for year in range(START_YEAR, END_YEAR + 1):
            print(f"\nFetching weather for {state_abbr}, {year}...")
            year_df = fetch_weather_for_state_year(state_abbr, location_id, year)

            if not year_df.empty:
                all_frames.append(year_df)

    weather = pd.concat(all_frames, ignore_index=True)
    weather.to_csv("../raw_fetched_data/raw_noaa.csv", index=False)

if __name__ == "__main__":
    main()
