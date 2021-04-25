import rasterio
import numpy as np

slope = "data_files/raster/slope.tif"
highslope = "data_files/raster/highslope1.tif"

with rasterio.open(slope) as src:
    # Read as numpy array
    array = src.read()
    profile = src.profile

    # Reclassify
    array[np.where(array >= 11.3)] = np.nan
    array[np.where(array < 11.3)] = 1

with rasterio.open(highslope, 'w', **profile) as dst:
    # Write to disk
    dst.write(array)