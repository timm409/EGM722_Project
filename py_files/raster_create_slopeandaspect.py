import gdal

dem_clip = "data_files/raster/dem_clip.tif"
slope = "data_files/raster/slope1.tif"
aspect = "data_files/raster/aspect1.tif"


def create_slp_asp(dem, slp_out, asp_out):
    gdal.Open(dem)
    gdal.DEMProcessing(slp_out, dem, "slope", computeEdges=True)
    gdal.DEMProcessing(asp_out, dem, "aspect", computeEdges=True)
    dem = None


create_slp_asp(dem_clip, slope, aspect)
