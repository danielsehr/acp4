from pathlib import Path
import numpy as np
import pandas as pd

import calendar
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import cmcrameri.cm as cmc

from acp4.processing.process_data import calc_trend_metrics
from acp4.plot.utils import months_abbreviations, seasons, season_colors


def plot_annual_discharge_sum(
    df: pd.DataFrame | pd.Series,
    ) -> plt.figure:

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        df.index,
        df["sum"],
        yerr=df["std"],
        capsize=3,
    )

    ax.set_ylabel("Mean annual specific discharge sum [mm]")
    ax.set_title("Mean annual specific discharge sums, CAMELS-DE")
    ax.grid(
        axis="y",
        alpha=0.3,
    )

    return fig


def print_mean_high_low_discharge(df: pd.DataFrame) -> None:
    
    for col in df.columns.to_list():
        print(col)
        
        print(f"Mean daily flow: {df[col].mean().round(3)}")
        print(f"Min daily flow: {df[col].min()}")
        print(f"Max daily flow: {df[col].max()}")

        print("-----------------------------")


def plot_monthly_discharge_mean(
    df: pd.DataFrame | pd.Series,
    ) -> figure:
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.boxplot(
        [
            df.loc[df["month"] == month, "spec_discharge"]
            for month in range(1, 13)
        ],
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly specific discharge mean [mm/d]")
    
    ax.set_xticks(
        range(1, 13),
        [calendar.month_abbr[i] for i in range(1, 13)],
    )

    # Add jittered observations
    all_x = []
    all_values = []
    all_years = []
    
    for month in range(1, 13):

        values = df.loc[
            df["month"] == month,
            "spec_discharge",
        ]
        
        years = df.loc[
            df["month"] == month,
            "year"
        ]

        x = np.random.normal(
            loc=month,
            scale=0.1,
            size=len(values),
        )
        
        all_x.extend(x)
        all_values.extend(values)
        all_years.extend(years)
    
    scatter = ax.scatter(
        all_x,
        all_values,
        s=12,
        alpha=0.6,
        c=all_years,
        cmap=cmc.roma_r, 
    )

    ax.set_title("Monthly specific discharge mean, CAMELS-DE")
    
    fig.colorbar(scatter, ax=ax, label="Year")
    
    fig.tight_layout()
    plt.show()
    
    return fig


def count_extreme_discharge_events_monthly(df: pd.Series) -> pd.DataFrame:
    df = df.dropna()
    
    annual = (
        df
        .groupby(df.index.year)
        .agg(max="max")
    )

    annual["max_date"] = df.groupby(df.index.year).idxmax()

    annual = annual[["max_date", "max"]]
    annual["month"] = annual["max_date"].dt.month
    annual = annual[["month", "max"]]
    
    annual = (
        annual
        .groupby("month")
        .count()
    )

    return annual


def plot_extreme_discharge_events_monthly(df: pd.DataFrame) -> plt.Figure:

    bar_colors = [
        season_colors[seasons[month]]
        for month in df.index
    ]

    fig, ax = plt.subplots()

    ax.bar(
        df.index,
        df["max"],
        color=bar_colors,
    )

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months_abbreviations)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of events")
    ax.set_title("Number of annual maximum discharge events by month, CAMELS-DE")
    ax.grid(axis="y", alpha=0.3)

    legend_handles = [
        Patch(color=color, label=season)
        for season, color in season_colors.items()
    ]

    ax.legend(handles=legend_handles, title="Season")

    return fig


def plot_annual_max_flow_days(
    df: pd.Series,
    max_flows: pd.Series
    ) -> figure:
    
    
    fig, ax = plt.subplots(figsize=(12, 7))

    max_flows_ts = df.loc[df.isin(max_flows)]

    ax.plot(
        df.index,
        df,
        color="steelblue",
    )

    ax.scatter(
        max_flows_ts.index,
        max_flows_ts,
        color="red",
        zorder=3,
    )


    ax.set_ylabel("Specific discharge [mm]")

    fig.tight_layout()
    plt.show()
    
    return(fig)
    

def plot_rating_curve(df: pd.DataFrame) -> plt.figure:
    df["year"] = [p.year for p in df.index]

    fig, ax = plt.subplots()

    sc = ax.scatter(
        df["water_level_obs"],
        df["discharge_spec_obs"],
        c=df["year"],
        s=1
    )
    
    cbar = plt.colorbar(sc)
    cbar.ax.set_title("Year")

    ax.set_xlabel("Observed daily water level [cm]")
    ax.set_ylabel("Observed volumetric discharge [m3 s-1]")
    ax.set_title("Stage-discharge curve,\n Klingbach catchment: DEB10810, Herxheim")
    
    plt.tight_layout()
    plt.show()

    return fig


def plot_annual_temperature_trend(
    df: pd.DataFrame,
    ) -> figure:

    fig, ax = plt.subplots(figsize=(10, 5))

    model = smf.ols(
        formula="temperature_mean ~ date",
        data=df,
    )

    result = model.fit()
    trend = result.predict(df)
    
    metrics = calc_trend_metrics(df=df["temperature_mean"])
    
    ax.plot(
        df["date"],
        df["temperature_mean"],
        marker="o",
        color="red"
    )
    
    ax.plot(
        df["date"],
        trend,
        linestyle="--",
        label=(
            f"slope = {result.params['date']:.3f}\n"
            f"R² = {result.rsquared:.2f}\n"
            + (
                f"Significant: {metrics.mk_orig.h}"
                + (
                    f"\nTheil-Sen slope = {metrics.sens_slope.slope:.3f}"
                    if metrics.sens_slope is not None
                    else ""
                )
            )
        ),
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Mean annual temperature [°C]")
    ax.set_title("Mean annual temperature, CAMELS-DE")
    ax.grid(axis="y", alpha=0.3)

    ax.legend()
    
    fig.tight_layout()
    plt.show()

    return fig


def plot_annual_precip_trend(
    df: pd.DataFrame,
    # ) -> figure:
    ):

    fig, ax = plt.subplots(figsize=(10, 5))

    model = smf.ols(
        formula="precipitation_mean ~ date",
        data=df,
    )

    result = model.fit()
    trend = result.predict(df)
    
    metrics = calc_trend_metrics(df=df["precipitation_mean"])
    
    ax.plot(
        df["date"],
        df["precipitation_mean"],
        marker="o",
    )
    
    ax.plot(
        df["date"],
        trend,
        linestyle="--",
        label=(
            f"slope = {result.params['date']:.3f}\n"
            f"R² = {result.rsquared:.2f}\n"
            + (
                f"Significant: {metrics.mk_orig.h}"
                + (
                    f"\nTheil-Sen slope = {metrics.sens_slope.slope:.3f}"
                    if metrics.sens_slope is not None
                    else ""
                )
            )
        ),
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Annual precipitation sum [mm]")
    ax.set_title("Mean annual precipitation sum")
    ax.grid(axis="y", alpha=0.3)

    ax.legend()
    
    fig.tight_layout()
    plt.show()

    return fig


def plot_discharge_trends(
    df: pd.Series,
    suptitle: str,
    ) -> figure:

    fig, axs = plt.subplots(
        nrows=4,
        sharex=True,
        figsize=(12, 12),
    )
    
    df = df.rename_axis("year").reset_index()

    variables = [
        ("mean", "Value [mm/d]", "Annual mean specific discharge"),
        ("max", "Value [mm/d]", "Annual maximum specific discharge"),
        ("sum", "Value [mm]", "Annual sum specific discharge"),
        ("count", "Number of Observation", "Annual count specific discharge"),
    ]

    for ax, (column, ylab, title) in zip(axs, variables):

        model = smf.ols(
            formula=f"{column} ~ year",
            data=df,
        )

        result = model.fit()
        trend = result.predict(df)

        metrics = calc_trend_metrics(df=df[column])
        
        ax.plot(
            df["year"],
            df[column],
            marker="o",
            label="Observed",
        )

        ax.plot(
            df["year"],
            trend,
            linestyle="--",
            label=(
                f"slope = {result.params['year']:.3f}\n"
                f"R² = {result.rsquared:.2f}\n"
                + (
                    f"Significant: {metrics.mk_orig.h}"
                    + (
                        f"\nTheil-Sen slope = {metrics.sens_slope.slope:.3f}"
                        if metrics.sens_slope is not None
                        else ""
                    )
                )
            ),
        )

        ax.set_ylabel(ylab)
        ax.set_title(title)
        ax.legend()

    plt.suptitle(suptitle)
    plt.tight_layout()
    plt.show()
    
    return fig



def plot_high_low_percentile_flows(
    df: pd.Series,
    ) -> figure:

    p95 = df.quantile(0.95)
    p05 = df.quantile(0.05)

    # Convert datetime index to Matplotlib's numeric date representation
    x = mdates.date2num(df.index)
    y = df.to_numpy()

    # Create line segments between consecutive observations
    points = np.column_stack([x, y])

    segments = np.stack(
        [points[:-1], points[1:]],
        axis=1,
    )

    # Color segments according to flow at their starting observation
    colors = np.where(
        y[:-1] > p95,
        "red",
        np.where(
            y[:-1] < p05,
            "blue",
            "grey",
        ),
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    line = LineCollection(
        segments,
        colors=colors,
        linewidths=1,
    )

    ax.add_collection(line)
    ax.autoscale()

    # Format x-axis as dates
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%Y-%m-%d")
    )

    # Legend proxies
    legend_lines = [
        Line2D(
            [0],
            [0],
            color="red",
            linewidth=2,
            label=f"> 95th percentile ({p95:.2f})",
        ),
        
        Line2D(
            [0],
            [0],
            color="blue",
            linewidth=2,
            label=f"< 5th percentile ({p05:.2f})",
        ),
    ]

    ax.legend(handles=legend_lines)

    ax.set_ylabel("Specific discharge [mm]")

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.show()
    
    return fig
    