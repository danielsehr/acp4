import geopandas as gpd
from shapely import Point

from rasterio.mask import mask

from typing import Any


def create_weatherstation_points(
    points: list[tuple] | tuple[tuple]
    ) -> gpd.GeoDataFrame:

    points_gdf = gpd.GeoDataFrame(
    [
        {
            "name": name,
            "geometry" : Point(lon, lat)
        } 
        for name, lon, lat in points
    ],
    crs="EPSG:4326",
    )
    
    return points_gdf


def expand_bbox(
    gdf: gpd.GeoDataFrame,
    extent: float,
) -> tuple[float, float, float, float]:
    
    gdf = gdf.to_crs("25832")
    
    centroid = gdf.geometry.centroid
    
    return (
        centroid.x.iloc[0] - extent,
        centroid.y.iloc[0] - extent,
        centroid.x.iloc[0] + extent,
        centroid.y.iloc[0] + extent,
    )
    

