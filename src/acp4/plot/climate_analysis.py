import seaborn as sns
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib.axes import Axes

from dataclasses import fields

from acp4.io.io import Data
from acp4.processing.process_data import calc_trend_metrics
from acp4.processing.climate_analysis import summarize_data
from acp4.plot.utils import mapping


def print_minmax_month(data: Data) -> None:
    for field in fields(data):
        df = getattr(data, field.name)
        
        if "discharge" in field.name:
            continue
        
        df = summarize_data(df=df, group_by="month")
        
        print(field.name)

        print("Coldest months:")
        print(df["temperature_mean"]["mean"].idxmin())
        
        print("\nHottest months:")
        print(df["temperature_mean"]["mean"].idxmax())
        
        print("---------------------\n")
            
      
def extract_min_max_values(df: pd.DataFrame) -> None:
    for col in df.columns.to_list():
        
        if not "mean" in col[1]:
            continue
        
        col = col[0]
        
        min_idx = df[col].idxmin()["mean"]
        max_idx = df[col].idxmax()["mean"]
        
        print(f"Date: {min_idx}")
        print(f"{col.replace('_mean', '_min')}: {df.loc[min_idx, col]['mean']}")
        print("----------------------------")
        print(f"Date: {max_idx}")
        print(f"{col.replace('_mean', '_max')}: {df.loc[max_idx, col]['mean']}")
        print("============================")   
      
            
def add_pointplot(
    df: pd.DataFrame,
    column_name: str,
    ax: plt.Axes,
    color: str
    ) -> None:
    
    sns.pointplot(
        data=df,
        x=df.index,
        y=df[column_name]["mean"],
        errorbar=None,
        ax=ax,
        color=color
    )

    
def add_errorbar(
    df: pd.DataFrame, 
    column_name: str,
    ax: Axes
    ) -> None:

    ax.errorbar(
        x=range(len(df)),
        y=df[column_name]["mean"],
        yerr=df[column_name]["std"],
        fmt="none",
        capsize=4,
        color="black"
    )


def plot_monthly_temp_hum_rad(
    df: pd.DataFrame,
    name: str,
    ax: Axes,
    ) -> None:

    # Temperature
    add_pointplot(df=df, column_name="temperature_mean", ax=ax, color="red")
    add_errorbar(df=df, column_name="temperature_mean", ax=ax,)

    # Humidity
    add_pointplot(df=df,column_name="humidity_mean",ax=ax,color="blue",)
    add_errorbar(df=df,column_name="humidity_mean",ax=ax,)

    ax.set_xlabel("Month")
    ax.set_ylabel("\nMean montly temperature [°C]  |  humidity [%]")
    ax.set_title(
        f"Station: {name}"
    )

    # Radiation
    ax2 = ax.twinx()

    add_pointplot(df=df,column_name="radiation_global_mean",ax=ax2,color="orange",)

    ax2.set_ylabel("Mean montly global radiation [W/m²]")


def plot_all_monthly_temp_hum_rad(data: Data) -> figure:

    datasets = [
        (field.name, getattr(data, field.name))
        for field in fields(data)
        if "discharge" not in field.name
    ]

    n = len(datasets)

    fig, axes = plt.subplots(
        nrows=1,
        ncols=n,
        figsize=(6 * n, 5),
        squeeze=False,
    )

    axes = axes[0]

    for ax, (name, df) in zip(axes, datasets):

        df_monthly = summarize_data(df=df, group_by="month")

        plot_monthly_temp_hum_rad(
            df=df_monthly,
            name=mapping[name],
            ax=ax
        )

    fig.tight_layout()
    plt.show()
    
    return fig
        

def plot_pet_comparison(
    camel_pet: pd.Series,
    hargreaves_pet: pd.Series,
    ax: Axes
    ) -> None:
    
    ax.scatter(
        camel_pet.index, 
        camel_pet.values, 
        s=1, 
    )
    
    ax.scatter(
        hargreaves_pet.index,
        hargreaves_pet.values,
        s=1,
    )
    
    ax.set_xlabel("Date")
    ax.set_ylabel("PET [mm d⁻¹]")
    ax.grid(alpha=0.3)
    
    
def plot_both_pet_comparison(
    camel_pet: pd.Series,
    herxheimweyher_pet: pd.Series,
    steinweiler_pet: pd.Series,
    ) -> figure:
    
    agrometeo_pets = {
        "Herxheimweyher (Hargreaves)": herxheimweyher_pet,
        "Steinweiler (Hargreaves)": steinweiler_pet,
    }

    fig, axs = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(12, 5),
        sharey=True,
    )

    for ax, (name, pet) in zip(axs, agrometeo_pets.items()):

        ax.scatter(
            camel_pet.index,
            camel_pet.values,
            s=1,
            label="CAMELS-DE",
        )

        ax.scatter(
            pet.index,
            pet.values,
            s=1,
            label=name,
        )

        ax.set_title("Comparison CAMELS-DE PET and Hargreaves PET")
        ax.set_xlabel("Date")
        ax.set_ylabel("PET [mm d⁻¹]")
        ax.grid(alpha=0.3)
        ax.legend()

    fig.tight_layout()
    plt.show()
    
    return fig
