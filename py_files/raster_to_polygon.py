import gdal
import pandas as pd
import geopandas as gpd
import ogr
from osgeo import osr


def unite_shp(shp_df, crs1, output):
    """
    dissolves shapefile
    :param shp_df: input shapefile
    :param crs1: set crs of the new dataframe
    :param output: path for writing output
    :return: write data to output path
    """
    # Union the objects
    shp_u = shp_df.unary_union
    # Create gpd GeoDataFrame, set CRS and add geometry column
    newdata = gpd.GeoDataFrame(crs=crs1, geometry=[shp_u])
    # Write output to file
    return newdata.to_file(output)

def polygon_raster(raster, polygon_shp):
    """
    Converts raster file to a polygon shapefile
    :param raster: input raster path
    :param polygon_shp: output shapefile path
    """
    # Open raster file
    src_ds = gdal.Open(raster)
    # Get raster band 1
    srcband = src_ds.GetRasterBand(1)
    # Get the spatial reference
    srs = osr.SpatialReference()
    # Get spatial projection
    srs.ImportFromWkt(src_ds.GetProjection())
    # Define output datasource
    dst_layername = polygon_shp
    # Get driver for ESRI shapefile
    drv = ogr.GetDriverByName("ESRI Shapefile")
    # Create a shapefile for datasource
    dst_ds = drv.CreateDataSource(dst_layername + ".shp")
    # Create a layer and set srs
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
    # Polygonize the data and save to file
    gdal.Polygonize(srcband, srcband, dst_layer, -1, [], callback=None)

# Merge shp data
def merge_shp(shp_out):
    return gpd.GeoDataFrame(pd.concat(shp_out))


aspect_reclass_nw = "data_files/raster/aspect_reclass_nw.tif"
aspect_vec_nw = "data_files/vector/aspect_vec_nw"

polygon_raster(aspect_reclass_nw, aspect_vec_nw)

aspect_reclass_ne = "data_files/raster/aspect_reclass_ne.tif"
aspect_vec_ne = "data_files/vector/aspect_vec_ne"

polygon_raster(aspect_reclass_ne, aspect_vec_ne)

slope_reclass = "data_files/raster/slope_reclass.tif"
slope_vec = "data_files/vector/slope_vec"

polygon_raster(slope_reclass, slope_vec)

# Open the shapefiles from dem
aspect_vec_nw = gpd.read_file('data_files/vector/aspect_vec_nw.shp')
aspect_vec_ne = gpd.read_file('data_files/vector/aspect_vec_ne.shp')
slope_vec = gpd.read_file('data_files/vector/slope_vec.shp')

# buildings_buf.to_file('buildings_buf.shp', driver='ESRI Shapefile')
steep_north = [aspect_vec_nw, aspect_vec_ne, slope_vec]

steep_north_merged = merge_shp(steep_north)

steep_north_dissolved = "data_files/vector/steep_north_dissolved.shp"

unite_shp(steep_north_merged, "EPSG:27700", steep_north_dissolved)