import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from fiona.crs import from_epsg


def c_point(coordinates, location, epsg, output):
    """
    Create point
    :param coordinates: coordinates of the point (units must be same as epsg)
    :param location: string name of the point
    :param epsg: coordinate system
    :param output: location on drive to save .shp
    :return: saves point.shp to drive
    """
    # Create empty gpd GeoDataFrame
    newdata = gpd.GeoDataFrame()
    # Create a new column called geometry
    newdata['geometry'] = None
    # Create a shapely point from the coordinates
    p_stat = Point(coordinates)
    # Insert point into geometry
    newdata.loc[0, 'geometry'] = p_stat
    # Add column called location and insert data
    newdata.loc[0, 'location'] = location
    # Set the GeoDataFrame coordinate system
    newdata.crs = from_epsg(epsg)
    # Write data to output path
    return newdata.to_file(output)


# Create point for Stevens Croft power station
pwr_stn = c_point((312130.15, 585253.25), 'Stevens Croft', 27700, "data_files/pwr_stn.shp")
