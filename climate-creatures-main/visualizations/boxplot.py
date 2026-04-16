import pandas as pd
import plotly.express as px

def make_boxplot(data_path="../final_dataset.csv", states=None, sector="all", season="all", y_metric="sales"):
    # load merged data
    df = pd.read_csv(data_path)

    # make sure sales is numeric
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["month"] = pd.to_numeric(df["month"], errors="coerce")

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
    df["sales_per_capita"] = df["sales"] / df["population"]
    df["sales_anomaly"] = df["sales"] - df.groupby(["state_name", "sector"])["sales"].transform("mean")

    if states:
        df = df[df["state_name"].isin(states)]

    if sector != "all":
        df = df[df["sector"] == sector]

    if season != "all":
        df = df[df["season"] == season]

    # drop missing values needed for the plot
    box_df = df.dropna(subset=["state_name", "sector", y_metric])

    # create box plot
    fig = px.box(
        box_df,
        x="sector",
        y=y_metric,
        color="sector",
        color_discrete_map={
            "residential": "#c47da3",  # pink-purple from your scale
            "commercial": "#5e9d96"  # teal-green from your scale
        },
        facet_col="state_name",
        facet_col_wrap=3,
        title="Sector-wise Energy Demand Variation by State",
        labels={
            "sector": "Sector",
            y_metric: y_metric.replace("_", " ").title()
        }
    )

    fig.update_layout(
        showlegend=False,
        title_x=0.5,
        height=760,
        paper_bgcolor="#f7f5f2",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=70, b=20)
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    return fig
