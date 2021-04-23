import gdal

fn_template = "C:/Users/Raph Martin/Documents/project/data_files/dem_200m.tif"
fn_new = "C:/Users/Raph Martin/Documents/project/data_files/new_raster.tif"
fn_dif = "C:/Users/Raph Martin/Documents/project/data_files/dif_raster.tif"

ds_template = gdal.Open(fn_template)

driver_tiff = gdal.GetDriverByName("GTiff")

ds_new = driver_tiff.CreateCopy(fn_new, ds_template, strict=0)
ds_dif = driver_tiff.CreateCopy(fn_dif, ds_template, strict=0)

band_base = ds_template.GetRasterBand(1).ReadAsArray()
band_new = band_base * 1.25
band_dif = band_new - band_base

ds_new.GetRasterBand(1).WriteArray(band_new)
ds_dif.GetRasterBand(1).WriteArray(band_dif)
ds_new.GetRasterBand(1).ComputeStatistics(0)
ds_dif.GetRasterBand(1).ComputeStatistics(0)

ds_template = None
ds_new = None
ds_dif = None