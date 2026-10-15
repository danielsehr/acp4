import pandas as pd


def agg_sum_mean_std(
    df: pd.DataFrame,
    cols: list[str],
    group_by: str
    ) -> pd.DataFrame:
    
    if group_by == "month":
        groups = df.index.month

    elif group_by == "year":
        groups = df.index.year
    
    return (
            df[cols]
            .groupby(groups)
            .agg(["sum", "mean", "std"])
            .round(2)
        )   


def summarize_data(
    df: pd.DataFrame,
    group_by: str
    ) -> pd.DataFrame:
    
    columns = ["temperature_mean", "humidity_mean", "radiation_global_mean", "discharge_spec_obs", "precipitation_mean"]

    available_columns = df.columns.intersection(columns).to_list()
    
    df = agg_sum_mean_std(
        df=df, 
        cols=available_columns, 
        group_by=group_by
    )

    if group_by == "month":
        df.index = pd.to_datetime(df.index, format="%m").strftime("%b")
        
    return df