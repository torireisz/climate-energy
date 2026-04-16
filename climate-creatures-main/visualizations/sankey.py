import pandas as pd
import numpy as np
import plotly.graph_objects as go

def make_sankey(data_path="../final_dataset.csv", states=None, sector="all", season="all"):
    #load data into a dataframe
    df = pd.read_csv(data_path)

    df["month"] = pd.to_numeric(df["month"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["HDD"] = pd.to_numeric(df["HDD"], errors="coerce")
    df["CDD"] = pd.to_numeric(df["CDD"], errors="coerce")
    df["TAVG"] = pd.to_numeric(df["TAVG"], errors="coerce")

    if "state_name" not in df.columns and "state" in df.columns:
        df["state_name"] = df["state"]

    df["sector"] = df["sector"].astype(str).str.strip().str.lower()

    def month_to_season(month):
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        return "fall"

    df["season"] = df["month"].apply(month_to_season)

    if states:
        df = df[df["state_name"].isin(states)]

    if sector != "all":
        df = df[df["sector"] == sector]

    if season != "all":
        df = df[df["season"] == season]

    def classify_weather_stress(row):
        '''
        This function creates three classifications for weather stress based on HDD and CDD
        values.

        args:
            row - a row of the dataframe containing "HDD" and "CDD" columns
        returns:
            A string indicating the weather stress category
        '''
        hdd = row["HDD"]
        cdd = row["CDD"]

        if hdd >= 400:
            return "High Heating Stress"
        elif cdd >= 60:
            return "High Cooling Stress"
        else:
            return "Moderate / Mild"

    #applies the above function to each row in the dataframe to create a new column
    # "weather_stress", which contains the respective weather stress classifications
    df["weather_stress"] = df.apply(classify_weather_stress, axis=1)

    #creates a new column "demand_level" in the dataframe by categorizing the "sales" column
    # into three quartiles (low, medium, high) using pd.qcut
    df["demand_level"] = pd.qcut(
        df["sales"],
        q=3,
        labels=["Low Demand", "Medium Demand", "High Demand"],
        duplicates="drop")

    #creates a list of individual values for the 4 aspects of the Sankey diagram
    states_list = df["state_name"].unique().tolist()
    weather_categories = df["weather_stress"].unique().tolist()
    sectors = df["sector"].unique().tolist()
    demand_levels = ["Low Demand", "Medium Demand", "High Demand"]

    #combines the 4 aspects lists into a single list "all_nodes" and creates a dictionary
    # "node_dict" that maps each unique value to its corresponding index in the "all_nodes" list.
    all_nodes = states_list + weather_categories + sectors + demand_levels
    node_dict = {name: i for i, name in enumerate(all_nodes)}

    #creates the first link between state name and weather stress by grouping the dataframe
    # by "state_name" and "weather_stress",
    links_1 = (
        df.groupby(["state_name", "weather_stress"])
        .agg(count=("sales", "size"), avg_sales=("sales", "mean"), avg_temp=("TAVG", "mean"))
        .reset_index())

    #creates the second link between weather stress and sector by grouping the dataframe by
    # "weather_stress" and "sector"
    links_2 = (
        df.groupby(["weather_stress", "sector"])
        .agg(count=("sales", "size"),avg_sales=("sales", "mean"),avg_temp=("TAVG", "mean"))
          .reset_index())

    #creates the third link between sector and demand level by grouping the dataframe by "sector"
    # and "demand_level"
    links_3 = (
        df.groupby(["sector", "demand_level"], observed=False)
        .agg(count=("sales", "size"), avg_sales=("sales", "mean"),avg_temp=("TAVG", "mean"))
        .reset_index())

    #initializes 4 empty lists to store indices for the Sankey diagram
    source = []
    target = []
    value = []
    customdata = []

    #iterates through links_1 as individual rows and appends the corresponding source,
    # target, value, and customdata to the respective lists
    for _, row in links_1.iterrows():
        source.append(node_dict[row["state_name"]])
        target.append(node_dict[row["weather_stress"]])
        value.append(row["count"])
        customdata.append([
            row["avg_sales"],
            row["avg_temp"],
            row["count"]])

    #iterates through links_2 as individual rows and appends the corresponding source,
    # target, value, and customdata to the respective lists
    for _, row in links_2.iterrows():
        source.append(node_dict[row["weather_stress"]])
        target.append(node_dict[row["sector"]])
        value.append(row["count"])
        customdata.append([
            row["avg_sales"],
            row["avg_temp"],
            row["count"]])

    #iterates through links_3 as individual rows and appends the corresponding source,
    # target, value, and customdata to the respective lists
    for _, row in links_3.iterrows():
        source.append(node_dict[row["sector"]])
        target.append(node_dict[str(row["demand_level"])])
        value.append(row["count"])
        customdata.append([
            row["avg_sales"],
            row["avg_temp"],
            row["count"]])

    #converts customdata list into a numpy array so it is more easily used in the Sankey diagram
    customdata = np.array(customdata)

    #creates the Sankey diagram figure
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=18,
            line=dict(color="black", width=0.5),
            label=all_nodes),
        link=dict(
            source=source,
            target=target,
            value=value,
            customdata=customdata,
            hovertemplate=(
                "Flow count: %{value}<br>"
                "Avg sales: %{customdata[0]:.2f}<br>"
                "Avg temperature: %{customdata[1]:.2f}°C<br>"
                "<extra></extra>")))])

    #adds title and formatting to the Sankey diagram
    fig.update_layout(
        title_text="State → Weather Stress Category → Sector → Energy Demand Level",
        font_size=12,
        width=1200,
        height=700,
        paper_bgcolor="#f7f5f2")

    return fig