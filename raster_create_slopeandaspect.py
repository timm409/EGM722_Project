import gdal

dem = gdal.Open("C:/Users/Raph Martin/Documents/project/data_files/dem_200m.tif")
slope1 = "C:/Users/Raph Martin/Documents/project/data_files/slope1.tif"
aspect1 = "C:/Users/Raph Martin/Documents/project/data_files/aspect1.tif"

slp = gdal.DEMProcessing(slope1, dem, "slope", computeEdges=True)

asp = gdal.DEMProcessing(aspect1, dem, "aspect", computeEdges=True)

slope1 = aspect1 = dem = None
