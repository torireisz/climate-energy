# Climate & Electricity Demand Dashboard

## Overview

This project explores how electricity demand changes across New England states in response to weather conditions and socioeconomic factors from 2014–2024.

The dashboard combines:

* Monthly electricity demand data by state and sector
* Weather metrics including average temperature, Heating Degree Days (HDD), and Cooling Degree Days (CDD)
* Socioeconomic variables such as population and per-capita income

The interactive dashboard includes:

* Ridgeline plot comparing residential and commercial demand distributions
* Box plot showing variation in demand by state and sector
* Animated correlation heatmap across years
* Sankey diagram tracing relationships between weather conditions and demand
* Numeric indicator cards summarizing key trends

---

# Project Structure

```text
climate-creatures/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── final_dataset.csv
├── correlation_heatmap_animation.mp4
├── README.md
│
├── visualizations/
│   ├── joyplot.py
│   ├── boxplot.py
│   ├── sankey.py
│   └── heatmap.py
│
├── data_acquisition/
│   ├── fetch_noaa.py
│   └── fetch_eia.py
│
├── data_cleaning/
│   ├── clean_noaa.py
│   ├── clean_eia.py
│   └── clean_bea.py
│
├── cleaned_data/
├── raw_fetched_data/
└── pytest_suite/
```

---

# Running the Dashboard Locally

## 1. Clone or Download the Project

Place all project files in the same folder.

## 2. Create and Activate a Python Environment

```bash
python -m venv ds
```

### Windows

```bash
ds\Scripts\activate
```

### Mac/Linux

```bash
source ds/bin/activate
```

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```

## 4. Run the Dashboard

```bash
panel serve app.py --address=0.0.0.0 --port=5006
```

Then open the dashboard in your browser:

```text
http://localhost:5006/app
```

To stop the dashboard, press:

```text
Ctrl + C
```

---

# Running with Docker

## Build the Docker Image

```bash
docker build -t climate-dashboard .
```

## Run the Container

```bash
docker run -p 5006:5006 climate-dashboard
```

Then open:

```text
http://localhost:5006/app
```

If you make changes to the code, rebuild the image:

```bash
docker build -t climate-dashboard .
```

---

# Usage

The dashboard contains five tabs.

## Ridgeline Overview

* Compare residential vs. commercial demand distributions
* Filter by state and weather condition:

  * All
  * High HDD
  * High CDD
  * Mild

## Box Plot

* Compare demand variability by state and sector
* Filter by:

  * State
  * Sector
  * Season
  * Metric (sales, sales per capita, sales anomaly)

## Animated Heatmap

* Shows how correlations between variables change over time
* Correlations are shown between:

  * Sales
  * Temperature
  * HDD / CDD
  * Population
  * Income

## Sankey Diagram

* Shows how observations flow from:

  * State
  * Weather condition
  * Sector
  * Demand level

## Numeric Metrics

* Displays summary indicators including:

  * Overall average monthly demand
  * Average residential demand
  * Average commercial demand
  * Average demand during high-HDD months
  * Average demand during high-CDD months

---

# Architecture

The project is organized into separate layers so that data acquisition, cleaning, visualization, and interface logic remain independent.

## Data Acquisition Layer

Located in:

```text
data_acquisition/
```

Responsible for downloading raw datasets from external sources:

* NOAA weather data
* EIA electricity demand data

Files:

* `fetch_noaa.py`
* `fetch_eia.py`

Output is stored in:

```text
raw_fetched_data/
```

---

## Data Cleaning Layer

Located in:

```text
data_cleaning/
```

Responsible for:

* Converting raw data into a consistent format
* Aggregating to state-year-month level
* Creating HDD and CDD metrics
* Removing missing or duplicate values

Files:

* `clean_noaa.py`
* `clean_eia.py`
* `clean_bea.py`

Output is stored in:

```text
cleaned_data/
```

---

## Merge Layer

The file:

```text
merge.py
```

Combines the cleaned NOAA, EIA, and BEA datasets into a single final dataset.

The merged dataset is:

```text
final_dataset.csv
```

Each row represents a unique:

* State
* Year
* Month
* Sector

with weather, socioeconomic, and demand variables included.

---

## Visualization Layer

Located in:

```text
visualizations/
```

Each visualization is implemented in its own file:

* `joyplot.py` → Ridgeline plot
* `boxplot.py` → Box plot
* `sankey.py` → Sankey diagram
* `heatmap.py` → Correlation heatmap animation

This modular structure makes it easy to edit or debug one visualization without changing the others.

---

## User Interface Layer

The main interface is built in:

```text
app.py
```

`app.py`:

* Loads the final dataset
* Creates widgets and controls
* Connects widgets to visualization callbacks
* Organizes the dashboard into tabs using Panel

The dashboard uses:

* `Panel` for layout and widgets
* `Plotly` for interactive plots
* `Matplotlib` and `JoyPy` for the ridgeline plot

---

# Dependencies

Main packages used:

* Panel
* Pandas
* Plotly
* Matplotlib
* NumPy
* JoyPy

These are listed in `requirements.txt`.

---

# Notes

* The animated heatmap uses the pre-generated file:

```text
correlation_heatmap_animation.mp4
```

* The dashboard requires:

```text
final_dataset.csv
```

Both files must remain in the same directory as `app.py`.

* The app should be run using:

```bash
panel serve app.py
```

rather than:

```bash
python app.py
```

# Data Cleaning & Quality Overview

## Running the Pipeline
- Run data acquisition
  > `python data_acquisition/fetch_noaa.py`
  > `python data_acquisition/fetch_eia.py`
- Run data cleaning
  > `python data_cleaning/clean_bea.py`
  > `python data_cleaning/clean_noaa.py`
  > `python data_cleaning/clean_eia.py`
- Merge datasets
  > `merge.py`
- Run validation
  > `pytest_suite` files

## Data Cleaning Decisions

### BEA
The BEA dataset was processed in two stages: aggregation and cleaning. Since the raw data included all U.S. states, it was first filtered to only include the six New England states. During this step, minor cleaning was applied, such as removing asterisks and extra whitespace from state names. The dataset was then restricted to the years 2014–2024, and only the relevant variables (population and per capita income) were retained.
The data was reshaped from wide to long format and then pivoted so these variables became separate columns, improving readability and usability. In the cleaning phase, missing values were checked, and data types were standardized: state names and years were converted to strings, while population and per capita income were converted to integers. A second missing value check ensured no errors were introduced during type conversion, and any remaining incomplete rows were removed. Finally, state names were converted to their standard abbreviations.

### NOAA
The NOAA dataset was already relatively clean, so the main focus was on standardizing and restructuring the data. Only the necessary columns (`date`, `datatype`, `station`, `value`, `state_abbr`) were retained. The `date` column was converted to datetime format, and `value` was converted to numeric. Text fields like `datatype` and `state_abbr` were standardized for consistency.
The dataset was filtered to include only `TMAX` and `TMIN`, since these are sufficient to derive temperature-based metrics. The data was then pivoted from long to wide format so that `TMAX` and `TMIN` became separate columns for each station-date observation. This enabled the calculation of derived features such as `TAVG`, `HDD`, and `CDD`. Finally, the data was aggregated from daily station-level observations to monthly state-level averages.

### EIA
The EIA dataset cleaning focused on consistency and merge-readiness. Rows missing key fields (`period`, `state`, `sector`, or `sales`) were removed, along with duplicate rows. The period column was converted to datetime format, and `sales` was converted to numeric for analysis. Additional columns for `year` and `month` were created to support aggregation and merging. Formatting was standardized by converting state values to uppercase and sector values to lowercase.

## Data Quality Issues
### BEA
The BEA dataset contained several formatting and structural issues. Many values included extraneous characters such as asterisks, parentheses, extra whitespace, and quotation marks, which required cleaning. The dataset was also structured in an unconventional way, where each state had multiple rows representing a single set of variables. This required reshaping using key columns like `GeoName` and `TypeCode`.
Another key limitation is that BEA data is available only at a yearly level, while the other datasets are monthly. To align datasets during merging, yearly values were repeated across all months within each year.

### NOAA
The NOAA dataset was generally high quality, with little to no missing or duplicate values in key columns (`date`, `datatype`, `station`, `value`, `state_abbr`). However, there are some structural limitations. Station converage is uneven across states.  Rhode Island has only 13 unique stations, while Maine has 85. Another issue to take into consideration is that not every station-date has both temperature measures. After checking station-date combinations, 891 observations were missing `TMAX` and 1,802 were missing `TMIN`, which matters because derived metrics like `TAVG`, `HDD`, and `CDD` depend on having both values. This was handled during aggregation, where mean calculations ignore missing values, allowing incomplete observations to still contribute.

### EIA
The main issue of the EIA dataset is that it is only available at the state level, not a more detailed city or county level. There were also some missing values and inconsistencies in formatting that had to be cleaned. Additionally, sector labels and data types needed to be standardized before the dataset could be used.
