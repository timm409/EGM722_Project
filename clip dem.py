import gdal

dem = "data_files/raster/dem_25m.tif"
travel_time = "data_files/vector/travel_time.shp"
dem_clip = "data_files/raster/dem_clip.tif"


def raster_shp_clip(ras_in, shp_in, ras_out):
    return gdal.Warp(ras_out, ras_in, cutlineDSName=shp_in, cropToCutline=True)


raster_shp_clip(dem, travel_time, dem_clip)
