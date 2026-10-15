import pandas as pd


def agg_annually_discharge(
    df: pd.Series,
    complete_years_only: bool = True,
    ) -> pd.DataFrame | pd.Series:
    
    if complete_years_only:
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
         .agg(["mean", "sum", "max", "std", "count"])
         .round(2)
        )
    )
    
    
def agg_monthly_discharge_mean(df: pd.Series) -> pd.DataFrame:
    
    df = (
        df
        .groupby(df.index.to_period("M"))
        .sum()
        .rename("spec_discharge")
        .to_frame()
    )

    df["month"] = df.index.month
    df["year"] = df.index.year
    
    return(df) 


def subset_high_low_values(df: pd.Series) -> dict[str, pd.Series]:
    p95 = df.quantile(0.95)
    p05 = df.quantile(0.05)

    # print(f"p05: {p05:.2f}")
    # print(f"p95: {p95:.2f}")
    
    return(
        {
            "Q05": df[df < p05],
            "Q95": df[df > p95],
        }
    )


def calc_longterm_runoff_coeff(
    discharge: pd.Series,
    precipitation: pd.Series,
    ) -> None:
    
    discharge_mean = discharge.mean()
    precipitation_mean = precipitation.mean()

    runoff_ratio = (discharge_mean / precipitation_mean).round(3)

    print(f"Long-term runoff ratio: {runoff_ratio}")