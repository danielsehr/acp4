from pathlib import Path
import pandas as pd
from dataclasses import fields
from typing import NamedTuple
import pymannkendall as mk

from acp4.config.config import Config
from acp4.io.io import Data

config = Config()


paths = [
    config.agrometeo_herxheimweyher_dir,
    config.agrometeo_steinweiler_dir
]

agro_column_mapping = {
    "AVG_TA200": "temperature_mean",
    "MIN_TA200min": "temperature_min",
    "MAX_TA200max": "temperature_max",
    "SUM_NN050": "precipitation_mean",
    "AVG_RH200": "humidity_mean",
    "SUM_GS200": "radiation_global_mean",
    "SUM_PEN": "potential_evapotranspiration",
}


class TrendMetrics(NamedTuple):
    mk_orig: object
    sens_slope: object | None
    
    
def calc_trend_metrics(df: pd.Series) -> TrendMetrics:

    # Mann-Kendall-Test
    mk_orig_results = mk.original_test(x_old=df, alpha=0.05)
    mk_hamed_rao_results = mk.hamed_rao_modification_test(x_old=df, alpha=0.05)


    # Theil-Sen's Slope Estimator
    if mk_orig_results.h and mk_hamed_rao_results.h:
        sens_slope = mk.sens_slope(df)

        # Needs to_numpy due to bug in source code. -> Need to open an issue or PR on github
        seasonal_sens_slope = mk.seasonal_sens_slope(df.to_numpy())
    
    else:
        sens_slope = None
        seasonal_sens_slope = None
    
    return(
        TrendMetrics(
            mk_orig=mk_orig_results,
            # mk_hamed_rao=mk_hamed_rao_results,
            sens_slope=sens_slope,
            # seasonal_sens_slope=seasonal_sens_slope
        )
    )


def concat_agrometeo_data(
    paths: list[str] | list[Path] = paths
    ) -> None:
    
    for path in paths:
        files = sorted(list(Path(path).glob("*.csv")))
        
        output_dir = Path(path)
        output_path = output_dir / f"{output_dir.stem}_concat.csv"

        df = pd.concat(
            [pd.read_csv(file, sep=";", decimal=",") for file in files],
            axis=0
        )

        df.to_csv(
            output_path, 
            sep=";", 
            index=False
        )


def rename_agro_data(
    data: dict, 
    mapping: dict = agro_column_mapping
    ) -> dict:
    
    for key, df in data.items():
        df = df.rename(columns=mapping)
        
        df = df.drop(columns = [
            "AVG_TA020", 
            # "MIN_TA200min",
            # "MAX_TA200max",
            "MAX_TA020max",
            "MIN_TA020min",
        ])
        
        data[key] = df

    return data


def intersect_columns(data: Data) -> Data:

    common_columns = None

    for field in fields(data):
        df = getattr(data, field.name)
        
        if field.name == "discharge":
            continue
        
        if common_columns is None:
            common_columns = df.columns
        else:
            common_columns = common_columns.intersection(df.columns)
    

    for field in fields(data):
        df = getattr(data, field.name)
        
        if field.name == "discharge":
            continue
        
        setattr(
            data,
            field.name,
            df.loc[:, common_columns]
        )

    return data
    

def intersect_datetime(data: Data) -> Data:

    for field in fields(data):
        df = getattr(data, field.name)
        df = df.sort_index()

        df = df[~df.index.duplicated(keep="first")].sort_index()
        
        setattr(data, field.name, df)
        
    start = max(
        getattr(data, field.name).index.min()
        for field in fields(data)
    )
    
    end = min(
        getattr(data, field.name).index.max()
        for field in fields(data)
    )
    
    
    return Data(
        **{
            field.name: getattr(data, field.name).loc[start:end]
            for field in fields(data)
        }
    )


def align_climate_timeseries(data: Data) -> Data:
    
    data = intersect_columns(data=data)
    data = intersect_datetime(data=data)
    
    return data

