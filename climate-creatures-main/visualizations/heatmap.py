import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# load merged data
df = pd.read_csv("../final_dataset.csv")

# columns for correlation
corr_cols = ["sales", "TAVG", "HDD", "CDD", "population", "per_capita_income"]
col_labels = ["sales", "TAVG", "HDD", "CDD", "population", "per capita\n income"]

# make sure they are numeric
for col in corr_cols + ["year"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# keep only needed columns
corr_df = df[["year"] + corr_cols].dropna()

all_years = []
all_matrices = []

# make one correlation matrix per year
for year in sorted(corr_df["year"].unique()):
    year_df = corr_df[corr_df["year"] == year]
    corr_matrix = year_df[corr_cols].corr().to_numpy(dtype=float)

    all_years.append(int(year))
    all_matrices.append(corr_matrix)


def update(frame, im, text_objs, matrices, years, labels, fig):
    """Update the heatmap and title for the current year."""
    current_matrix = matrices[frame]
    im.set_data(current_matrix)

    # update title with year
    plt.title(f"Yearly Correlation Between Weather, Socioeconomic Factors, and Demand ({years[frame]})")

    # update cell text
    for i in range(len(labels)):
        for j in range(len(labels)):
            text_objs[i][j].set_text(f"{current_matrix[i, j]:.2f}")

    return [im] + [text for row in text_objs for text in row]


def animate_corr_heatmap():
    """Create and save animated heatmap of yearly correlations."""
    fig, ax = plt.subplots(figsize=(10, 8))

    first_matrix = all_matrices[0]

    from matplotlib.colors import LinearSegmentedColormap

    custom_scale = [
        [0.00, "#2b6f77"],  # deeper blue-green
        [0.18, "#5e9d96"],
        [0.35, "#a8c9b3"],
        [0.47, "#d8ddd9"],
        [0.50, "#cfc7cc"],
        [0.53, "#e5c8d8"],
        [0.65, "#cf94b6"],
        [0.82, "#b65b92"],
        [1.00, "#7a2f68"]  # darker purple-magenta
    ]

    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_corr",
        [(pos, color) for pos, color in custom_scale]
    )

    im = ax.imshow(
        first_matrix,
        cmap=custom_cmap,
        vmin=-1,
        vmax=1,
        aspect="auto"
    )

    ax.set_xticks(range(len(corr_cols)))
    ax.set_xticklabels(col_labels)

    ax.set_yticks(range(len(corr_cols)))
    ax.set_yticklabels(col_labels)

    ax.set_xlabel("Variable")
    ax.set_ylabel("Variable")
    ax.set_title(f"Yearly Correlation Between Weather, Socioeconomic Factors, and Demand ({all_years[0]})")

    # add text labels inside cells
    text_objs = []
    for i in range(len(corr_cols)):
        row = []
        for j in range(len(corr_cols)):
            txt = ax.text(j, i, f"{first_matrix[i, j]:.2f}",
                          ha="center", va="center", color="black")
            row.append(txt)
        text_objs.append(row)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Correlation")

    anim = FuncAnimation(
        fig,
        update,
        frames=len(all_matrices),
        fargs=(im, text_objs, all_matrices, all_years, corr_cols, fig),
        interval=1000,
        repeat=False
    )

    anim.save("../correlation_heatmap_animation.mp4", fps=1)

def main():
    animate_corr_heatmap()


if __name__ == "__main__":
    main()
