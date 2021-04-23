import pandas as pd
import geopandas as gpd

# Open the shapefiles for infrastructure
roads = gpd.read_file('data_files/vector/roads.shp')
rivers = gpd.read_file('data_files/vector/rivers.shp')
buildings = gpd.read_file('data_files/vector/buildings.shp')

# buildings_buf.to_file('buildings_buf.shp', driver='ESRI Shapefile')
infra = [roads, rivers, buildings]


# Merge infrastructure data
def merge_shp(shp_out):
    return gpd.GeoDataFrame(pd.concat(shp_out))


inf_merge = merge_shp(infra)

# 25m buffer of infrastructure
inf_buf = inf_merge.buffer(25)

inf_buf.to_file('data_files/vector/inf_buf.shp', driver='ESRI Shapefile')
