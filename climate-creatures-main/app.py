"""
UI Layer
Climate & Energy Demand Dashboard
"""

import panel as pn
import pandas as pd

from visualizations.joyplot import make_joyplot
from visualizations.boxplot import make_boxplot
from visualizations.sankey import make_sankey

# load panel extensions
pn.extension("plotly")

# CONFIG
DATA_PATH = "final_dataset.csv"
HEATMAP_VIDEO = "correlation_heatmap_animation.mp4"
SIDEBAR_WIDTH = 400
CONTENT_WIDTH = 750
VIDEO_WIDTH = 700
VIDEO_HEIGHT = 480

HEADER_STYLE = "margin: 0 0 8px 0; line-height: 1.2;"
BODY_STYLE = "margin: 0; line-height: 1.45; max-width: 100%;"
SECTION_GAP = 10
TAB_TOP_GAP = 18

# load data once for widget options
df = pd.read_csv(DATA_PATH)

if "state_name" not in df.columns and "state" in df.columns:
    df["state_name"] = df["state"]

df["sector"] = df["sector"].astype(str).str.strip().str.lower()

numeric_cols = ["sales", "HDD", "CDD", "population", "per_capita_income", "year", "month"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

state_order = [
    "Connecticut",
    "Maine",
    "Massachusetts",
    "New Hampshire",
    "Rhode Island",
    "Vermont"
]

available_states = [
    s for s in state_order
    if s in df["state_name"].dropna().unique().tolist()
]


def section_html(title, body, level="h3", width_mode="stretch_width"):
    return pn.pane.HTML(
        f"""
        <div style="max-width: 100%; overflow-wrap: break-word; word-break: break-word;">
            <{level} style="{HEADER_STYLE}">{title}</{level}>
            <p style="{BODY_STYLE}">{body}</p>
        </div>
        """,
        sizing_mode=width_mode
    )


# CALLBACK FUNCTIONS
def get_ridgeline_plot(states, weather_mode):
    fig = make_joyplot(
        data_path=DATA_PATH,
        states=states,
        weather_mode=weather_mode
    )

    return pn.pane.Matplotlib(
        fig,
        tight=True,
        width=CONTENT_WIDTH
    )


def get_box_plot(states, sector, season, y_metric):
    fig = make_boxplot(
        data_path=DATA_PATH,
        states=states,
        sector=sector,
        season=season,
        y_metric=y_metric
    )

    return pn.pane.Plotly(
        fig,
        config={"responsive": True},
        width=CONTENT_WIDTH
    )


def get_sankey_plot(states, sector, season):
    fig = make_sankey(
        data_path=DATA_PATH,
        states=states,
        sector=sector,
        season=season
    )

    return pn.pane.Plotly(
        fig,
        config={"responsive": True},
        width=CONTENT_WIDTH
    )


def get_metrics_panel():
    metrics_df = df.copy()

    if "sales" in metrics_df.columns:
        metrics_df["sales"] = pd.to_numeric(metrics_df["sales"], errors="coerce")
    if "HDD" in metrics_df.columns:
        metrics_df["HDD"] = pd.to_numeric(metrics_df["HDD"], errors="coerce")
    if "CDD" in metrics_df.columns:
        metrics_df["CDD"] = pd.to_numeric(metrics_df["CDD"], errors="coerce")

    residential_mean = metrics_df.loc[
        metrics_df["sector"] == "residential", "sales"
    ].mean()

    commercial_mean = metrics_df.loc[
        metrics_df["sector"] == "commercial", "sales"
    ].mean()

    high_hdd_mean = metrics_df.loc[
        metrics_df["HDD"] > metrics_df["HDD"].median(), "sales"
    ].mean()

    high_cdd_mean = metrics_df.loc[
        metrics_df["CDD"] > metrics_df["CDD"].median(), "sales"
    ].mean()

    overall_mean = metrics_df["sales"].mean()

    def make_number(name, value, color):
        return pn.indicators.Number(
            name=name,
            value=0 if pd.isna(value) else round(value, 2),
            format="{value:,.0f}",
            font_size="34pt",
            title_size="14pt",
            default_color=color
        )

    cards_top = pn.Row(
        make_number("Overall Avg Sales", overall_mean, "#8c5a73"),
        make_number("Residential Avg", residential_mean, "#a8648d"),
        make_number("Commercial Avg", commercial_mean, "#4f7d6a"),
        sizing_mode="stretch_width"
    )

    cards_bottom = pn.Row(
        make_number("High HDD Months", high_hdd_mean, "#5e9d96"),
        make_number("High CDD Months", high_cdd_mean, "#c47da3"),
        pn.Spacer(),
        sizing_mode="stretch_width"
    )

    return pn.Column(
        pn.pane.HTML(
            """
            <div style="font-size: 15px; color: #666; margin: 0 0 10px 0; line-height: 1.45;">
                These indicators summarize how electricity demand changes across sectors and during stronger heating or cooling months.
            </div>
            """,
            width=CONTENT_WIDTH
        ),
        cards_top,
        pn.Spacer(height=18),
        cards_bottom,
        width=CONTENT_WIDTH
    )


def main():

    # RIDGELINE WIDGETS
    ridge_states = pn.widgets.MultiChoice(
        name="States",
        options=available_states,
        value=available_states
    )

    ridge_weather = pn.widgets.RadioButtonGroup(
        name="Weather Filter",
        options={
            "All": "all",
            "High HDD": "high_hdd",
            "High CDD": "high_cdd",
            "Mild": "mild"
        },
        value="all",
        button_type="primary"
    )

    ridge_plot = pn.bind(
        get_ridgeline_plot,
        ridge_states,
        ridge_weather
    )

    ridge_controls = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Ridgeline Controls",
            "Compare residential and commercial monthly energy demand distributions across states under different weather stress conditions."
        ),
        pn.Spacer(height=SECTION_GAP),
        ridge_states,
        ridge_weather,
        sizing_mode="stretch_width"
    )

    ridge_tab = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "High-Level Overview: Ridgeline Plot",
            "This view compares residential and commercial monthly energy demand distributions across New England states under different weather-stress conditions.",
            level="h2",
            width_mode="fixed"
        ),
        pn.Spacer(height=SECTION_GAP),
        ridge_plot,
        width=CONTENT_WIDTH,
        sizing_mode="fixed"
    )

    # ==================================================
    # BOX PLOT WIDGETS
    # ==================================================
    box_states = pn.widgets.MultiChoice(
        name="States",
        options=available_states,
        value=available_states
    )

    box_sector = pn.widgets.Select(
        name="Sector",
        options=["all", "residential", "commercial"],
        value="all"
    )

    box_season = pn.widgets.RadioButtonGroup(
        name="Season",
        options=["all", "winter", "spring", "summer", "fall"],
        value="all",
        button_type="primary"
    )

    box_metric = pn.widgets.Select(
        name="Metric",
        options={
            "Monthly Sales": "sales",
            "Sales per Capita": "sales_per_capita",
            "Sales Anomaly": "sales_anomaly"
        },
        value="sales"
    )

    box_plot = pn.bind(
        get_box_plot,
        box_states,
        box_sector,
        box_season,
        box_metric
    )

    box_controls = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Box Plot Controls",
            "Explore which states and sectors have the greatest variability in monthly electricity demand."
        ),
        pn.Spacer(height=SECTION_GAP),
        box_states,
        box_sector,
        box_season,
        box_metric,
        sizing_mode="stretch_width"
    )

    box_tab = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Detailed Drill-Down: Box Plot",
            "This visualization shows the spread, median, and outliers of energy demand across sectors and states.",
            level="h2",
            width_mode="fixed"
        ),
        pn.Spacer(height=SECTION_GAP),
        box_plot,
        width=CONTENT_WIDTH,
        sizing_mode="fixed"
    )

    # ==================================================
    # HEATMAP TAB
    # ==================================================
    heatmap_video = pn.pane.Video(
        HEATMAP_VIDEO,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
        loop=True,
        autoplay=False
    )

    heatmap_controls = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Animated Heatmap",
            "Watch how the correlations between weather, socioeconomic variables, and electricity demand change from year to year."
        ),
        pn.Spacer(height=6),
        pn.pane.HTML(
            f"""
            <div style="max-width: 100%; overflow-wrap: break-word; word-break: break-word;">
                <p style="{BODY_STYLE}">
                    The animation progresses across the years and shows how relationships between variables strengthen, weaken, or reverse over time.
                </p>
            </div>
            """,
            sizing_mode="stretch_width"
        ),
        sizing_mode="stretch_width"
    )

    heatmap_tab = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Animated Correlation Heatmap",
            "This animation shows the yearly correlation matrix between weather, socioeconomic factors, and electricity demand.",
            level="h2",
            width_mode="fixed"
        ),
        pn.Spacer(height=10),
        heatmap_video,
        width=CONTENT_WIDTH,
        sizing_mode="fixed"
    )

    # ==================================================
    # SANKEY WIDGETS
    # ==================================================
    sankey_states = pn.widgets.MultiChoice(
        name="States",
        options=available_states,
        value=available_states
    )

    sankey_sector = pn.widgets.Select(
        name="Sector",
        options=["all", "residential", "commercial"],
        value="all"
    )

    sankey_season = pn.widgets.RadioButtonGroup(
        name="Season",
        options=["all", "winter", "spring", "summer", "fall"],
        value="all",
        button_type="primary"
    )

    sankey_plot = pn.bind(
        get_sankey_plot,
        sankey_states,
        sankey_sector,
        sankey_season
    )

    sankey_controls = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Sankey Controls",
            "Trace how observations move from state to weather stress, then to sector and final demand level."
        ),
        pn.Spacer(height=SECTION_GAP),
        sankey_states,
        sankey_sector,
        sankey_season,
        sizing_mode="stretch_width"
    )

    sankey_tab = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Interactive Sankey Diagram",
            "This systems-level view shows how weather stress and sector combine to influence energy demand.",
            level="h2",
            width_mode="fixed"
        ),
        pn.Spacer(height=SECTION_GAP),
        sankey_plot,
        width=CONTENT_WIDTH,
        sizing_mode="fixed"
    )

    # ==================================================
    # METRICS TAB
    # ==================================================
    metrics_panel = get_metrics_panel()

    metrics_controls = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Numeric Metrics",
            "These indicators summarize key demand patterns in the dataset and help connect weather stress to electricity demand levels."
        ),
        sizing_mode="stretch_width"
    )

    metrics_tab = pn.Column(
        pn.Spacer(height=TAB_TOP_GAP),
        section_html(
            "Numeric Dashboard Indicators",
            "These summary indicators highlight useful demand patterns tied to the research question, including sector differences and demand under stronger heating or cooling conditions.",
            level="h2",
            width_mode="fixed"
        ),
        pn.Spacer(height=20),
        metrics_panel,
        width=CONTENT_WIDTH,
        sizing_mode="fixed"
    )

    # ==================================================
    # SIDEBAR TABS
    # ==================================================
    sidebar_tabs = pn.Tabs(
        ("Ridgeline", ridge_controls),
        ("Box Plot", box_controls),
        ("Heatmap", heatmap_controls),
        ("Sankey", sankey_controls),
        ("Metrics", metrics_controls),
        dynamic=True
    )

    # ==================================================
    # MAIN TABS
    # ==================================================
    main_tabs = pn.Tabs(
        ("Ridgeline Overview", ridge_tab),
        ("Box Plot", box_tab),
        ("Animated Heatmap", heatmap_tab),
        ("Sankey Flow", sankey_tab),
        ("Metrics", metrics_tab),
        dynamic=True
    )

    # keep sidebar tab synced with selected visualization
    def sync_sidebar(event):
        sidebar_tabs.active = event.new

    main_tabs.param.watch(sync_sidebar, "active")

    # ==================================================
    # TEMPLATE
    # ==================================================
    layout = pn.template.FastListTemplate(
        title="Climate & Energy Demand Dashboard",
        sidebar=[
            pn.pane.HTML(
                f"""
                <div style="max-width: 100%; overflow-wrap: break-word; word-break: break-word;">
                    <h1 style="{HEADER_STYLE}">Explore the Dashboard</h1>
                    <p style="{BODY_STYLE}">
                        Use the controls below for the currently selected visualization.
                    </p>
                </div>
                """,
                sizing_mode="stretch_width"
            ),
            sidebar_tabs
        ],
        main=[
            pn.Column(
                pn.pane.HTML(
                    f"""
                    <div style="max-width: 100%;">
                        <h1 style="{HEADER_STYLE}">Climate and Electricity Demand in New England</h1>
                        <p style="{BODY_STYLE}">
                            This dashboard explores how electricity demand varies across state, sector, season, and weather conditions from 2014–2024.
                        </p>
                    </div>
                    """,
                    width=CONTENT_WIDTH
                ),
                pn.Spacer(height=14),
                main_tabs,
                width=CONTENT_WIDTH,
                sizing_mode="fixed"
            )
        ],
        header_background="#5e9d96",
        accent_base_color="#8c5a73",
        sidebar_width=SIDEBAR_WIDTH,
        theme_toggle=False
    ).servable()

    layout.show()


main()