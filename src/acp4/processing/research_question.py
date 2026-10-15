import pandas as pd


def create_correlations(
    precipitation: pd.Series,
    discharge: pd.Series,
    max_lag: int = 10,
    ) -> pd.Series:
    
    precipitation.dropna(inplace=True)
    discharge.dropna(inplace=True)
    
    correlations = pd.Series({
        lag: precipitation.corr(discharge.shift(-lag))
        for lag in range(max_lag + 1)
    })
    
    return correlations


def create_monthly_cross_correlations(
    precipitation: pd.Series,
    discharge: pd.Series,
    max_lag: int = 10,
    ) -> pd.DataFrame:

    df = pd.concat(
        [
            precipitation.rename("precipitation"),
            discharge.rename("discharge"),
        ],
        axis=1,
    ).sort_index()

    df = df.reindex(
        pd.date_range(df.index.min(), df.index.max(), freq="D")
    )

    results = {}

    for lag in range(max_lag + 1):
        df["discharge_lagged"] = df["discharge"].shift(-lag)

        valid = df.dropna(
            subset=["precipitation", "discharge_lagged"]
        )

        results[lag] = valid.groupby(
            valid.index.month
        ).apply(
            lambda group: group["precipitation"].corr(
                group["discharge_lagged"]
            )
        )

    return (
        pd.DataFrame(results)
        .reindex(range(1, 13))
        .rename_axis("month")
        .rename_axis("lag_days", axis=1)
    )