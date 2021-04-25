#!/usr/bin/env python3

fileNameIn = "/tmp/geotiff/Global_taxonomic_richness_of_soil_fungi.tif"
fileNameOut = "/tmp/geotiff/Global_taxonomic_richness_of_soil_fungi.tiff"
dst_options = ['COMPRESS=DEFLATE',"PREDICTOR=3","TILED=YES"]
noDataValue = -3.4028234663852886e+38

from osgeo import gdal
import numpy

src_ds = gdal.Open(fileNameIn)
format = "GTiff"
driver = gdal.GetDriverByName(format)
dst_ds = driver.CreateCopy(fileNameOut, src_ds, False ,dst_options)

# Set location
dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
# Set projection
dst_ds.SetProjection(src_ds.GetProjection())
srcband = src_ds.GetRasterBand(1)

dataraster = srcband.ReadAsArray().astype(numpy.float)
#Rplace the nan value with the predefiend noDataValue
dataraster[numpy.isnan(dataraster)]=noDataValue

dst_ds.GetRasterBand(1).WriteArray(dataraster)
dst_ds.GetRasterBand(1).SetNoDataValue(noDataValue)

dst_ds = None