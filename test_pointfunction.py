import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from fiona.crs import from_epsg


def c_point(coordinates, location, epsg, output):
    newdata = gpd.GeoDataFrame()
    newdata['geometry'] = None
    p_stat = Point(coordinates)
    newdata.loc[0, 'geometry'] = p_stat
    newdata.loc[0, 'location'] = location
    newdata.crs = from_epsg(epsg)
    outfp = output
    newdata.to_file(outfp)


c_point((312130.15, 585253.25), 'Stevens Croft', 27700, "data_files/power_station_function2")
