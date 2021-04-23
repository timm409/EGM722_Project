import gdal
import ogr
from osgeo import osr

raster = "data_files/raster/dem_clip.tif"
polygon_shp = "data_files/vector/dem_vec"

def polygon_raster(raster, polygon_shp):
    src_ds = gdal.Open(raster)
    srcband = src_ds.GetRasterBand(1)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(src_ds.GetProjection())

    #  create output datasource
    dst_layername = polygon_shp
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(dst_layername + ".shp")
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)

    gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)


polygon_raster(raster, polygon_shp)
