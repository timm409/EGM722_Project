from osgeo import gdal
from gdalconst import GA_ReadOnly

maskDs = gdal.Open('data_files/raster/highslope3.tif', GA_ReadOnly)# your mask raster
projection=maskDs.GetProjectionRef()
geoTransform = maskDs.GetGeoTransform()
minx = geoTransform[0]
maxy = geoTransform[3]
maxx = minx + geoTransform[1] * maskDs.RasterXSize
miny = maxy + geoTransform[5] * maskDs.RasterYSize


data=gdal.Open('data_files/raster/dem_25m.tif', GA_ReadOnly) #Your data the one you want to clip
output='output.tif' #output file
gdal.Translate(output,data,format='GTiff',projWin=[minx,maxy,maxx,miny],outputSRS=projection) 