import gdal
import numpy as np
import rasterio


def calculate_slope(dem):
    gdal.DEMProcessing('slope.tif', dem, 'slope')
    with gdal.Open('slope.tif') as dataset:
        dem_slope = dataset.read(1)
    return dem_slope


def calculate_aspect(dem):
    gdal.DEMProcessing('aspect.tif', dem, 'aspect')
    with gdal.Open('aspect.tif') as dataset:
        dem_aspect = dataset.read(1)
    return dem_aspect


slope = calculate_slope('C:/Users/Raph Martin/Documents/project/data_files/dem_200m.tif')
aspect = calculate_aspect('C:/Users/Raph Martin/Documents/project/data_files/dem_200m.tif')

print(type(slope))
print(slope.dtype)
print(slope.shape)
