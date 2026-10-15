import pandas as pd


def calculate_aet(
    discharge: pd.Series,
    precipitation: pd.Series,
    pet: pd.Series,
    ) -> None:
    
    
    df = pd.concat(
        objs=[
            discharge,
            precipitation,
            pet,
        ],
        axis=1,
        join="inner"
    )

    df = (
        df
        .groupby(df.index.year)
        .agg(
            discharge_sum=("discharge_spec_obs", "sum"),
            precipitation_sum=("precipitation_mean", "sum"),
            pet_simulated_sum=("pet_hargreaves", "sum"),
        )
        .round(3)
    )


    df["AET"] = (df["precipitation_sum"] - df["discharge_sum"]).round(2)

    print("Annual mean: ")
    print(df)
    print("-----------------------------------------------\n")
    print("Long-term annual mean:")
    print(df.mean().round(2))
