from osgeo import gdal 
import numpy as np


def readraster(filename):
    """
    Read raster and extract transformation, projection and z values
    :param filename: path for input raster
    :return: transformation, projection and z values
    """
    # Open the raster
    filehandle = gdal.Open(filename)
    # Get raster band 1
    band1 = filehandle.GetRasterBand(1)
    # Get transformation
    geotransform = filehandle.GetGeoTransform()
    # Get projection
    geoproj = filehandle.GetProjection()
    # Read raster band 1 as array and define as z
    z = band1.ReadAsArray()
    return geotransform, geoproj, z


def writeraster(filename, geotransform, geoprojection, data):
    """
    Writes reclassified raster to file
    :param filename: input path
    :param geotransform: transformation of new data
    :param geoprojection: projection of new data
    :param data: data input values
    """
    # Create grid
    (x, y) = data.shape
    # Get GeoTiff driver
    driver = gdal.GetDriverByName('GTiff')
    # Set data type to 32 bit float
    dst_datatype = gdal.GDT_Float32
    # Create raster file
    dst_ds = driver.Create(filename, y, x, 1, dst_datatype)
    # Get raster band 1 and write as array
    dst_ds.GetRasterBand(1).WriteArray(data)
    # Set transformation
    dst_ds.SetGeoTransform(geotransform)
    # Set projection
    dst_ds.SetProjection(geoprojection)
    # Set no data values to -9999
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)


slope = "data_files/raster/slope.tif"
slope_reclass = "data_files/raster/slope_reclass.tif"

[geotransform, geoproj, z] = readraster(slope)
z[z <= 11.3] = np.nan
z[z > 11.3] = 1

writeraster(slope_reclass, geotransform, geoproj, z)

aspect = "data_files/raster/aspect.tif"
aspect_reclass_nw = "data_files/raster/aspect_reclass_nw.tif"

[geotransform, geoproj, z] = readraster(aspect)
z[z <= 315] = np.nan
z[z > 315] = 1

writeraster(aspect_reclass_nw, geotransform, geoproj, z)

aspect_reclass_ne = "data_files/raster/aspect_reclass_ne.tif"

[geotransform, geoproj, z] = readraster(aspect)
z[z >= 45] = np.nan
z[z < 1] = np.nan
z[z < 45] = 1

writeraster(aspect_reclass_ne, geotransform, geoproj, z)
