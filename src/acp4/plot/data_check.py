import math
import pandas as pd
import matplotlib.pyplot as plt

from dataclasses import fields
from acp4.io.io import Data

from acp4.plot.utils import mapping

def plot_flow_precip_temp(data: Data) -> plt.figure:
    fig, axs = plt.subplots(
        nrows=4,
        ncols=1,
        figsize=(12, 8),
        sharex=True,
    )
    
    # --- Discharge ---
    axs[0].plot(
        data.discharge.index,
        data.discharge["discharge_spec_obs"],
        linewidth=0.8,
        color="black"
    )

    axs[0].set_title(mapping["camel"])
    axs[0].set_ylabel("Discharge [m³/s]")
    axs[0].grid(alpha=0.3)


    # --- Temperature and Precipitation ---
    plot_idx = 1

    for field in fields(data):
        if field.name == "discharge":
            continue

        df = getattr(data, field.name)

        ax_temp = axs[plot_idx]
        ax_precip = ax_temp.twinx()

        ax_temp.plot(
            df.index,
            df["temperature_mean"],
            linewidth=0.8,
            color="red",
        )

        ax_temp.set_ylabel("Temperature [°C]")

        ax_precip.bar(
            df.index,
            df["precipitation_mean"],
            width=1.0,
            alpha=0.5,
        )

        ax_precip.set_ylabel("Precipitation [mm]")
        ax_precip.invert_yaxis()

        ax_temp.set_title(mapping[field.name])
        ax_temp.set_xlabel("Date")
        ax_temp.grid(alpha=0.3)

        plot_idx += 1

    fig.tight_layout()

    plt.show()
    
    return fig


def plot_flow_with_na(
    df: pd.DataFrame,
    start: str | None = None,
    end: str | None = None,
    ) -> plt.figure:
    
    if start is not None:
            df = df[df.index >= start]

    if end is not None:
        df = df[df.index < end]


    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        df.index,
        df["discharge_spec_obs"],
        linewidth=1.0,
    )
    
    # Missing observations
    na_mask = df["discharge_spec_obs"].isna()
    
    for date in df.index[na_mask]:
        ax.axvline(
            date,
            color="red",
            alpha=0.5,
            linewidth=1.0,
        )

    ax.set_title("Watershed: DEB10810, Klingbach, Herxheim")
    ax.set_xlabel("Date")
    ax.set_ylabel("Observed catchment-specific discharge [mm/d]")

    ax.grid(
        True,
        alpha=0.3,
        linewidth=0.8,
    )

    fig.tight_layout()
    plt.show()
    
    return fig


def plot_outlier_facets(data: Data) -> None:
    for field in fields(data):
        df = getattr(data, field.name)

        cols = df.columns.to_list()
        
        if len(cols) == 0:
            continue

        ncols = 2
        nrows = math.ceil(len(cols) / ncols)

        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            figsize=(14, 3 * nrows),
            squeeze=False,
        )
        axes = axes.flatten()

        for ax, col in zip(axes, cols):
            ax.plot(
                df.index, 
                df[col], 
                linewidth=0.8, 
            )

            ax.set_title(col)
            # ax.legend()
            ax.grid(alpha=0.3)


        fig.suptitle(f"Visual outlier inspection: {field.name}", fontsize=14)
        fig.tight_layout()
        plt.show()