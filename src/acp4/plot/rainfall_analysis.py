import numpy as np
import pandas as pd
from dataclasses import fields

import calendar
import statsmodels.formula.api as smf

import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib.axes import Axes
from matplotlib.patches import Patch

from acp4.io.io import Data
from acp4.processing.process_data import calc_trend_metrics
from acp4.plot.utils import mapping, months_abbreviations, seasons, season_colors


def print_annual_mean_precip_sum(
    data: dict
    ) -> None:
    
    print("Average precip sum 2016-2020:\n")
    
    for key, df in data.items():
        print(key) 
        print("Mean: ", 
            (
                df.loc[df.index != 2015]['sum']
                .mean()
                .round(2)
            )
        )
        print("Std: ", 
            (
                df.loc[df.index != 2015]["sum"]
                .std()
                .round(2))
            )
        print("-----------------")
        

def plot_annual_precip_sum(
    df: pd.DataFrame | pd.Series,
    ax: Axes,
    location: str
    ) -> None:

    ax.bar(
        df.index,
        df["sum"],
        yerr=df["std"],
        capsize=3,
        alpha=0.8,
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Mean precipitation [mm]")
    ax.set_title(mapping[location])
    ax.grid(
        axis="y",
        alpha=0.3,
    )


def plot_all_annual_precip_sum(data: dict) -> figure:
    
    fig, axs = plt.subplots(figsize=(9, 7), nrows=3)
    
    for ax, (key, df) in zip(axs, data.items()):
        plot_annual_precip_sum(df=df, ax=ax, location = key)
    
    plt.suptitle("Mean annually precipitation sum, period: 2009 - 2020")
    
    fig.tight_layout()
    plt.show()
    
    return fig


def plot_camels_annual_precip_sum(df: pd.Series) -> figure:
    
    df = df.reset_index()
    
    model = smf.ols(
        formula=f"sum ~ date",
        data=df,
    )

    result = model.fit()
    trend = result.predict(df)

    metrics = calc_trend_metrics(df=df["sum"])


    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        df["date"],
        df["sum"],
        )

    ax.plot(
        df["date"],
        trend,
        linestyle="--",
        color="red",
        label=(
            f"slope = {result.params['date']:.3f}\n"
            f"R² = {result.rsquared:.3f}\n"
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
    ax.set_ylabel("Mean annual precipitation sum [mm]")
    ax.set_title("Mean annual precipitation sums, CAMELS-DE")
    ax.grid(axis="y", alpha=0.3)

    ax.legend()

    plt.tight_layout()
    plt.show()
    
    return fig


def plot_monthly_precip_sum(
    df: pd.DataFrame | pd.Series,
    ax: Axes,
    location: str
    ) -> None:

    df.boxplot(
        column="precipitation",
        by="month",
        ax=ax,
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly precipitation [mm]")

    ax.set_xticklabels(
        [calendar.month_abbr[i] for i in range(1, 13)]
    )

    # Add jittered observations
    for month in range(1, 13):
        values = df.loc[
            df["month"] == month,
            "precipitation",
        ]

        x = np.random.normal(
            loc=month,
            scale=0.08,
            size=len(values),
        )

        ax.scatter(
            x,
            values,
            s=12,
            alpha=0.6,
        )

    ax.set_title(mapping[location])
    
    
def plot_all_monthly_precip_sum(data: dict) -> figure:
    fig, axs = plt.subplots(figsize=(9, 7), nrows=3, sharey=True)
        
    for ax, (key, df) in zip(axs, data.items()):
        plot_monthly_precip_sum(df=df, ax=ax, location = key)
    
    plt.suptitle("Monthly precipitation sum, period: 2009 - 2020")
    
    fig.tight_layout()
    plt.show()
    
    return fig
    

def plot_extreme_rainfall_events(
    df: pd.Series,
    ax: Axes,
    location: str
    ) -> None:
    
    p99 = df.quantile(0.99)

    colors = df.gt(p99).map({
        True: "red",
        False: "steelblue",
    })

    ax.bar(
        df.index,
        df,
        color=colors,
    )

    ax.axhline(
        p99,
        linestyle="--",
        label=f"99th percentile = {p99:.2f}",
    )

    ax.set_title(mapping[location])
    ax.set_ylabel("Precipitation [mm]")
    ax.legend()


def plot_all_extreme_rainfall_events(data: Data) -> figure:
    
    fig, axs = plt.subplots(figsize=(12, 7), nrows=3, sharex=False, sharey=True)
    
    plot_fields = [
        field for field in fields(data)
        if field.name != "discharge"
    ]

    for ax, field in zip(axs, plot_fields):
        
        if field.name == "discharge":
            continue
        
        df = getattr(data, field.name)
        
        plot_extreme_rainfall_events(
            df=df["precipitation_mean"], 
            ax=ax, 
            location = field.name
        )
    
    fig.tight_layout()
    plt.show()
    
    return fig


def plot_extreme_precip_events_monthly(df: pd.DataFrame) -> figure:

    months = range(1, 13)
    bar_colors = [
        season_colors[seasons[month]]
        for month in months
    ]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        list(months),
        df["count"].reindex(months, fill_value=0),
        color=bar_colors,
    )

    ax.set_xticks(list(months))
    ax.set_xticklabels(months_abbreviations)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of extreme days")
    ax.set_title("Monthly precipitation extremes (> 99th percentile), CAMELS-DE")
    ax.grid(axis="y", alpha=0.3)

    legend_handles = [
        Patch(color=color, label=season)
        for season, color in season_colors.items()
    ]
    
    ax.legend(handles=legend_handles, title="Season")

    fig.tight_layout()
    
    return fig