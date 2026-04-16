import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.patches import Patch

def make_joyplot(data_path="../final_dataset.csv", states=None, weather_mode="all"):
    df = pd.read_csv(data_path)

    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["HDD"] = pd.to_numeric(df["HDD"], errors="coerce")
    df["CDD"] = pd.to_numeric(df["CDD"], errors="coerce")

    if "state_name" not in df.columns and "state" in df.columns:
        df["state_name"] = df["state"]

    df["state_name"] = df["state_name"].astype(str)
    df["sector"] = df["sector"].astype(str).str.strip().str.lower()

    # keep only the two sectors you care about
    df = df[df["sector"].isin(["residential", "commercial"])].copy()

    state_order = [
        "Connecticut",
        "Maine",
        "Massachusetts",
        "New Hampshire",
        "Rhode Island",
        "Vermont"
    ]

    df = df[df["state_name"].isin(state_order)].copy()

    if states:
        df = df[df["state_name"].isin(states)]

    # weather thresholds
    hdd_75 = df["HDD"].quantile(0.75)
    cdd_75 = df["CDD"].quantile(0.75)

    if weather_mode == "high_hdd":
        df = df[df["HDD"] >= hdd_75]
    elif weather_mode == "high_cdd":
        df = df[df["CDD"] >= cdd_75]
    elif weather_mode == "mild":
        df = df[(df["HDD"] < hdd_75) & (df["CDD"] < cdd_75)]

    df = df.dropna(subset=["sales", "state_name", "sector"])

    if df.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.text(0.5, 0.5, "No data available for this selection.", ha="center", va="center")
        ax.axis("off")
        return fig

    values = df["sales"].dropna()
    x = np.linspace(values.min(), values.max(), 400)

    fig, ax = plt.subplots(figsize=(10, 6.5))

    colors = {
        "residential": "#c47da3",
        "commercial": "#74a88b"
    }

    plotted_states = []
    states_to_plot = [s for s in state_order if s in df["state_name"].unique()]

    for i, state in enumerate(states_to_plot):
        state_df = df[df["state_name"] == state]

        for sector in ["residential", "commercial"]:
            vals = state_df[state_df["sector"] == sector]["sales"].dropna()

            if len(vals) < 2:
                continue

            kde = gaussian_kde(vals)
            y = kde(x)
            y = y / y.max() * 0.42

            ax.fill_between(
                x, i, i + y,
                color=colors[sector],
                alpha=0.55
            )
            ax.plot(
                x, i + y,
                color=colors[sector],
                linewidth=1.5
            )

        ax.hlines(i, x.min(), x.max(), color="black", linewidth=0.8)
        plotted_states.append((i, state))

    ax.set_yticks([i for i, s in plotted_states])
    ax.set_yticklabels([s for i, s in plotted_states], fontsize=10)

    weather_titles = {
        "all": "All Weather Conditions",
        "high_hdd": "High HDD Months",
        "high_cdd": "High CDD Months",
        "mild": "Mild Months"
    }

    ax.set_title(
        f"Monthly Energy Demand Distribution by State\n{weather_titles.get(weather_mode, weather_mode)}",
        fontsize=13,
        pad=10
    )

    ax.set_xlabel("Monthly Energy Sales", fontsize=11)
    ax.set_ylabel("")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    legend_handles = [
        Patch(facecolor=colors["residential"], edgecolor="black", alpha=0.55, label="Residential"),
        Patch(facecolor=colors["commercial"], edgecolor="black", alpha=0.55, label="Commercial")
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="upper right")

    plt.tight_layout()
    return fig