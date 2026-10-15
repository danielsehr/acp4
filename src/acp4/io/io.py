from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

import rasterio
from rasterio.windows import from_bounds

from dataclasses import dataclass, fields
from typing import Any

from acp4.config.config import Config

config = Config()


@dataclass
class Data:
    discharge: pd.DataFrame
    camel: pd.DataFrame
    agro_herxheimweyher: pd.DataFrame
    agro_steinweiler: pd.DataFrame


def filter_camel_for_gauge_id(
    timeseries_dir: str | Path,
    gauge_id: str
    ):
    
    return [
        p 
        for p in Path(timeseries_dir).rglob("*.csv") 
        if gauge_id in p.stem.split("_")[4]
    ][0]


def read_camel_data(
    timeseries_dir: str | Path,
    gauge_id: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    filepath = filter_camel_for_gauge_id(
        timeseries_dir=timeseries_dir,
        gauge_id=gauge_id
    )
    
    df = pd.read_csv(
        filepath_or_buffer=filepath, 
        sep=",", 
        decimal="."
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    
    
    discharge_cols = ['discharge_vol_obs', 'discharge_spec_obs', 'water_level_obs']
    
    if all(col in df.columns for col in discharge_cols):
        df_discharge = df[discharge_cols]
        df_camel = df.drop(columns = discharge_cols)
    
        return df_discharge, df_camel
    
    return df


def read_agro_data(timeseries_dir: str) -> dict:
    csv_paths = [p for p in Path(timeseries_dir).rglob("*.csv") if "concat" in str(p)]

    agro_dict = {}

    for path in csv_paths:
        file_name = path.stem
        
        df = pd.read_csv(
            filepath_or_buffer=path, 
            sep=";", 
            decimal=",",
            na_values=["-"]
            )
        
        df = df.rename(columns={"Tag": "Date"})
        
        df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
        df = df.set_index("Date")
        
        df = df[~df.index.duplicated(keep="first")].sort_index()
        
        for col in df.columns.to_list():
            # Convert string "-" for missing value into proper NA
            df[col] = df[col].replace("-", pd.NA)

            # Replace decimal "," to "." for whatever reason the decimal arg did not work for the 2008 series
            df[col] = (
                df[col]
                .astype("string")
                .str.replace(",", ".", regex=False)
            )
            
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Convert Wh / m2 -> W / m2 to align with CAMELS dataset
        df["SUM_GS200"] = df["SUM_GS200"] / 24
                
        agro_dict[file_name] = df
    
    return agro_dict


def read_catchment(
    filepath: str | Path,
    gauge_id: str
    ) -> gpd.GeoDataFrame:

    gdf = gpd.read_file(filename=filepath)
    gdf = gdf[gdf["gauge_id"] == gauge_id]
    
    return gdf


def read_gauge_station(
    filepath: str | Path,
    gauge_id: str
    ) -> gpd.GeoDataFrame:
    
    gdf = gpd.read_file(filename=filepath)
    gdf = gdf[gdf["gauge_id"] == gauge_id]
    
    return gdf


def read_landuse_csv(
    filepath: str | Path,
    gauge_id: str = config.gauge_id
    ) -> pd.DataFrame:
    
    df = pd.read_csv(filepath_or_buffer=filepath)
    df = df[df["gauge_id"] == gauge_id]
    
    return df


def read_dem_window(
    filepath: str | Path,
    bbox: tuple[float, float, float, float],
    ) -> tuple[np.ndarray, Any, Any]:
    
    with rasterio.open(filepath) as src:
        dem_crs = src.crs
        minx, miny, maxx, maxy = bbox

        window = from_bounds(
            minx,
            miny,
            maxx,
            maxy,
            transform=src.transform,
        )

        dem = src.read(1, window=window, masked=True)
        transform = src.window_transform(window)
        
        return dem, transform, dem_crs
