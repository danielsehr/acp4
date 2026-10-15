import pandas as pd
from dataclasses import fields

from acp4.processing.process_data import Data


def agg_annually_sum(df: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    
    months_per_year = (
        df
        .groupby(df.index.year)
        .apply(lambda x: x.index.month.nunique())
    )
    
    complete_years = months_per_year[months_per_year == 12].index
    
    df = df[df.index.year.isin(complete_years)]
    
    return(
        (df
         .groupby([df.index.year])
         .agg(["sum", "std"])
         .round(2)
        )
    )


def agg_all_annually_sum(data: Data) -> dict:
    result = {}
    
    for field in fields(data):
        if field.name == "discharge":
            continue
        
        df = getattr(data, field.name)
        
        df_aggregated = agg_annually_sum(df=df["precipitation_mean"])

        result[field.name] = df_aggregated
    
    return(result)
    

def agg_monthly_precip_sum(df: pd.DataFrame) -> pd.DataFrame:
    
    df = (
        df
        .groupby(df.index.to_period("M"))
        .sum()
        .rename("precipitation")
        .to_frame()
    )

    df["month"] = df.index.month
    
    return(df)


def agg_all_monthly_precip_sum(data: Data) -> dict:
    result = {}
        
    for field in fields(data):
        if field.name == "discharge":
            continue
        
        df = getattr(data, field.name)
        
        df_aggregated = agg_monthly_precip_sum(df=df["precipitation_mean"])
        
        result[field.name] = df_aggregated
            
    return(result)        


def count_extreme_precip_events_monthly(df: pd.Series) -> pd.DataFrame:
    df = df.dropna()

    threshold = df.quantile(0.99)
    df = df[df > threshold]

    monthly_counts = (
        df
        .groupby(df.index.month)
        .size()
        .reindex(range(1, 13), fill_value=0)
        .rename("count")
        .to_frame()
    )

    monthly_counts.index.name = "month"

    return monthly_counts
