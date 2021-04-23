import gdal

slope = gdal.Open("C:/Users/Raph Martin/Documents/project/data_files/slope1.tif")
low_slope = "C:/Users/Raph Martin/Documents/project/data_files/low_slope.tif"

low_slp = gdal_calc(slope