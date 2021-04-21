import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from fiona.crs import from_epsg

# Create empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()

# Create a new column called 'geometry' in the GeoDataFrame
newdata['geometry'] = None

# Coordinates for the power station
coordinates = [(312130.15, 585253.25)]

# Create a Shapely point from the coordinates
p_stat = Point(coordinates)

# Insert point into geometry
newdata.loc[0, 'geometry'] = p_stat

# Add new column and insert data
newdata.loc[0, 'location'] = 'Stevens Croft'

# Set the GeoDataFrame's coordinate system to British National Grid
newdata.crs = from_epsg(27700)

# Output path for the shapefile
outfp = "data_files/Power_Station.shp"

# Write data to shapefile
newdata.to_file(outfp)
