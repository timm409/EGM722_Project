import pandas as pd
import geopandas as gpd

# Open the shapefiles for infrastructure
roads = gpd.read_file('C:/Users/Raph Martin/Documents/project/data_files/vector/roads.shp')
rivers = gpd.read_file('C:/Users/Raph Martin/Documents/project/data_files/vector/rivers.shp')
buildings = gpd.read_file('C:/Users/Raph Martin/Documents/project/data_files/vector/buildings.shp')

# buildings_buf.to_file('buildings_buf.shp', driver='ESRI Shapefile')
infra = [roads, rivers, buildings]


# Merge infrastructure data
def merge_shp(shp_out):
    return gpd.GeoDataFrame(pd.concat(shp_out))


def unite_shp(shp_df, crs1, output):
    """
    dissolves shapefile
    :param shp_df: input shapefile
    :param crs1: set crs of the new dataframe
    :param output: path for writing output
    :return: write data to output path
    """
    shp_u = shp_df.unary_union
    newdata = gpd.GeoDataFrame(crs=crs1, geometry=[shp_u])
    return newdata.to_file(output)


inf_merge = merge_shp(infra)

inf_buf = inf_merge.geometry.buffer(25)



# inf_u = inf_buf.unary_union

buf1 = 'C:/Users/Raph Martin/Documents/project/data_files/vector/inf_buf2.shp'

unite_shp(inf_buf, inf_buf.crs, buf1)

# new = gpd.GeoDataFrame(crs=inf_buf.crs, geometry=[inf_u])

# new.to_file(buf1)

# gpd.GeoSeries.to_file(inf_u, buf1, driver='ESRI Shapefile')

# 25m buffer of infrastructure
# inf_buf = gpd.GeoDataFrame(inf_merge.geometry.buffer(25))

# inf_buf['new_column'] = 0

# inf_buf_dissolved = inf_buf.dissolve(by='new_column')

#gpd.overlay(inf_buf, inf_buf, how='union')

# inf_buf_dissolved.to_file('C:/Users/Raph Martin/Documents/project/data_files/vector/inf_buf.shp', driver='ESRI Shapefile')
