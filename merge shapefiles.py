import pandas as pd
import geopandas as gpd

# Open the shapefiles for infrastructure
roads = gpd.read_file('data_files/roads.shp')
rivers = gpd.read_file('data_files/rivers.shp')
buildings = gpd.read_file('data_files/buildings.shp')

# buildings_buf.to_file('buildings_buf.shp', driver='ESRI Shapefile')

# Merge infrastructure data
inf_merge = gpd.GeoDataFrame(pd.concat([roads, rivers, buildings]))

# 25m buffer of infrastructure
inf_buf = inf_merge.buffer(25)


