#!/usr/bin/env python3

import gdal
import fiona
import ogr
import pandas as pd
import geopandas as gpd
import numpy as np
from osgeo import osr
from shapely.geometry import Point, shape, mapping
from fiona.crs import from_epsg
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches


"""
This code is for finding suitable land for biomass planting
functions: line 18 - 140
analysis: line 144 - 231
mapping: line 234 - 
"""


def raster_shp_clip(ras_in, shp_in, ras_out):
    """
    Clip raster to shapefile
    :param ras_in: raster input path
    :param shp_in: shapefile input path
    :param ras_out: clipped raster output path
    """
    return gdal.Warp(ras_out, ras_in, cutlineDSName=shp_in, cropToCutline=True)


def create_slp_asp(dem_in, slp_out, asp_out):
    """
    Create a slope and aspect raster from DEM
    :param dem_in: DEM input path
    :param slp_out: slope raster output path
    :param asp_out: aspect raster output path
    """
    # Open the DEM
    gdal.Open(dem_in)
    # Create slope raster
    gdal.DEMProcessing(slp_out, dem_in, "slope", computeEdges=True)
    # Create aspect raster
    gdal.DEMProcessing(asp_out, dem_in, "aspect", computeEdges=True)
    # Close the DEM
    dem_in = None


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


def polygon_raster(raster, polygon_shp):
    """
    Converts raster file to a polygon shapefile
    :param raster: input raster path
    :param polygon_shp: output shapefile path
    """
    # Open raster file
    src_ds = gdal.Open(raster)
    # Get raster band 1
    srcband = src_ds.GetRasterBand(1)
    # Get the spatial reference
    srs = osr.SpatialReference()
    # Get spatial projection
    srs.ImportFromWkt(src_ds.GetProjection())
    # Define output datasource
    dst_layername = polygon_shp
    # Get driver for ESRI shapefile
    drv = ogr.GetDriverByName("ESRI Shapefile")
    # Create a shapefile for datasource
    dst_ds = drv.CreateDataSource(dst_layername + ".shp")
    # Create a layer and set srs
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
    # Polygonize the data and save to file
    gdal.Polygonize(srcband, srcband, dst_layer, -1, [], callback=None)


def merge_shp(shp_out):
    """
    merge shapefiles
    :param shp_out: list of shapefile paths
    :return: merged shapefile
    """
    return gpd.GeoDataFrame(pd.concat(shp_out))


def unite_shp(shp_df, crs1):
    """
    dissolves shapefile
    :param shp_df: input shapefile
    :param crs1: set crs of the new dataframe
    :return: Get gpd GeoDataFrame, set CRS and amend geometry with union
    """
    # Union the objects
    shp_u = shp_df.unary_union
    return gpd.GeoDataFrame(crs=crs1, geometry=[shp_u])


def multi2single(gpdf):
    """
    multipart to singlepart
    :param gpdf: polygon gpd GeoDataFrame path
    :return: exploded polygon
    """
    # Input is polygon
    gpdf_singlepoly = gpdf[gpdf.geometry.type == 'Polygon']
    # Output is multi polygon
    gpdf_multipoly = gpdf[gpdf.geometry.type == 'MultiPolygon']

    for i, row in gpdf_multipoly.iterrows():
        series_geometries = pd.Series(row.geometry)
        df = pd.concat([gpd.GeoDataFrame(row, crs=gpdf_multipoly.crs).T]*len(series_geometries), ignore_index=True)
        df['geometry'] = series_geometries
        gpdf_singlepoly = pd.concat([gpdf_singlepoly, df])

    gpdf_singlepoly.reset_index(inplace=True, drop=True)
    return gpdf_singlepoly


def erase_shp(big_shp, small_shp, path_out, crs1):
    """
    Erase part of a shapefile using another shapefile and write to output
    :param big_shp: input path of shapefile
    :param small_shp: input path of template shapefile
    :param path_out: output path of shapefile
    :param crs1: crs of dataset
    """
    # Open the shapefiles
    big = fiona.open(big_shp)
    small = fiona.open(small_shp)
    # Cycle through the attribute
    pol_big = big.next()
    pol_small = small.next()
    # Define variables as shape and difference between geometries
    a = shape(pol_big['geometry'])
    b = shape(pol_small['geometry'])
    c = a.difference(b)
    # Set the schema
    source_schema = {'geometry': 'Polygon'}
    # With the output open, write the mapping of the variable c
    with fiona.open(path_out, 'w', 'ESRI Shapefile', schema=source_schema, crs=crs1) as out:
        out.write({
            'geometry': mapping(c)
        })


def c_point(coordinates, location, epsg, output):
    """
    Create point
    :param coordinates: coordinates of the point (units must be same as epsg)
    :param location: string name of the point
    :param epsg: coordinate system
    :param output: location on drive to save .shp
    :return: saves point.shp to drive
    """
    # Create empty gpd GeoDataFrame
    newdata = gpd.GeoDataFrame()
    # Create a new column called geometry
    newdata['geometry'] = None
    # Create a shapely point from the coordinates
    p_stat = Point(coordinates)
    # Insert point into geometry
    newdata.loc[0, 'geometry'] = p_stat
    # Add column called location and insert data
    newdata.loc[0, 'location'] = location
    # Set the GeoDataFrame coordinate system
    newdata.crs = from_epsg(epsg)
    # Write data to output path
    return newdata.to_file(output)


# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Circle((0.5, 0.5), 0.25, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


def scale_bar(ax, location=(0.92, 0.9)):
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]

    tmc = ccrs.TransverseMercator(sbllx, sblly)
    x0, x1, y0, y1 = ax.get_extent(tmc)
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx, sbx - 5000], [sby, sby], color='k', linewidth=3, transform=tmc)
    plt.plot([sbx-5000, sbx - 10000], [sby, sby], color='w', linewidth=3, transform=tmc)

    plt.text(sbx, sby-2000, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx-5000, sby-2000, '5 km', transform=tmc, fontsize=8)
    plt.text(sbx-10500, sby-2000, '0 km', transform=tmc, fontsize=8)

"""

#-----------------------------------------------------------------------------------------------------------------------

# Define DEM, travel area shapefile and output for clipped DEM
dem = "data_files/raster/dem_25m.tif"
travel_time = "data_files/vector/travel_time.shp"
dem_clip = "data_files/raster/dem_clip.tif"

# Clip DEM to travel time shapefile
raster_shp_clip(dem, travel_time, dem_clip)

# Define slope and aspect output paths
slope = "data_files/raster/slope.tif"
aspect = "data_files/raster/aspect.tif"

# Create slope and aspect raster files from clipped DEM
create_slp_asp(dem_clip, slope, aspect)

# Reclass slope and aspect to high slope and north facing
slope_reclass = "data_files/raster/slope_reclass.tif"
aspect_reclass_nw = "data_files/raster/aspect_reclass_nw.tif"
aspect_reclass_ne = "data_files/raster/aspect_reclass_ne.tif"

# Reclass values below or equal to 11.3 to nodata
[geotransform, geoproj, z] = readraster(slope)
z[z <= 11.3] = np.nan
z[z > 11.3] = 1
writeraster(slope_reclass, geotransform, geoproj, z)

# Reclass values above or equal to 315 to nodata
[geotransform, geoproj, z] = readraster(aspect)
z[z <= 315] = np.nan
z[z > 315] = 1
writeraster(aspect_reclass_nw, geotransform, geoproj, z)

# Reclass values below or equal to 45 to nodata
[geotransform, geoproj, z] = readraster(aspect)
z[z >= 45] = np.nan
z[z < 0] = np.nan
z[z < 45] = 1
writeraster(aspect_reclass_ne, geotransform, geoproj, z)

# Define the output path for the new shapefiles
aspect_vec_nw = "data_files/vector/aspect_vec_nw"
slope_vec = "data_files/vector/slope_vec"
aspect_vec_ne = "data_files/vector/aspect_vec_ne"

# Convert the rasters to shapefiles
polygon_raster(aspect_reclass_nw, aspect_vec_nw)
polygon_raster(aspect_reclass_ne, aspect_vec_ne)
polygon_raster(slope_reclass, slope_vec)

# Open the converted shapefiles 
aspect_vec_nw = gpd.read_file('data_files/vector/aspect_vec_nw.shp')
aspect_vec_ne = gpd.read_file('data_files/vector/aspect_vec_ne.shp')
slope_vec = gpd.read_file('data_files/vector/slope_vec.shp')

# Merge the shapefiles and dissolve into one shapefile
steep_north = [aspect_vec_nw, aspect_vec_ne, slope_vec]
steep_north_merged = merge_shp(steep_north)
steep_north_dissolved = "data_files/vector/steep_north_dissolved.shp"
unite_shp(steep_north_merged, "EPSG:27700", steep_north_dissolved)

# Output path of erase
poly_clip1 = 'data_files/vector/poly_clip1.shp'

# Erase steep and north facing areas
erase_shp(travel_time, steep_north_dissolved, poly_clip1, "EPSG:27700")

# Open the shapefiles for infrastructure
roads = gpd.read_file('data_files/vector/infrastructure/roads.shp')
rivers = gpd.read_file('data_files/vector/infrastructure/rivers.shp')
buildings = gpd.read_file('data_files/vector/infrastructure/buildings.shp')

# Define infra as the infrastructure list
infra = [roads, rivers, buildings]

# Merge the infrastructure shapefiles and define
inf_merge = merge_shp(infra)

# 25m buffer of infrastructure
inf_buf = inf_merge.geometry.buffer(24)

# Dissolve infrastructure buffer and save to file
inf_buf_dissolved = unite_shp(inf_buf, inf_buf.crs)
inf_buf_dissolved.to_file('data_files/vector/inf_buf_dissolved.shp')

# Outputs for infrastructure erase function
poly_clip2 = 'data_files/vector/poly_clip2.shp'

# Path of dissolved infrastructure buffer
inf_buf_dissolved = 'data_files/vector/inf_buf_dissolved.shp'

# Erase the infrastructure from the polygon
erase_shp(poly_clip1, inf_buf_dissolved, poly_clip2, "EPSG:27700")

# Open the shapefiles for protected areas
ramsar = gpd.read_file('data_files/vector/protected_areas/ramsar.shp')
sssi = gpd.read_file('data_files/vector/protected_areas/sssi.shp')

# Define protected areas as a list
p_areas = [ramsar, sssi]

# Merge the protected areas shapefiles and define
p_areas_merge = merge_shp(p_areas)

# Dissolve protected areas and save to file
p_areas_dissolved = unite_shp(p_areas_merge, p_areas_merge.crs)
p_areas_dissolved.to_file('data_files/vector/p_areas_dissolved.shp')

# Output after erasing protected areas 
poly_clip3 = 'data_files/vector/poly_clip3.shp'

# Path of dissolved protected areas 
p_areas_dissolved = 'data_files/vector/p_areas_dissolved.shp'

# Erase the protected areas from the polygon
erase_shp(poly_clip2, p_areas_dissolved, poly_clip3, "EPSG:27700")

# Read multipart polygon output
poly_clip3 = gpd.read_file("data_files/vector/poly_clip3.shp")

# Explode the shapefile from multipart to singlepart and write to file
multi2single(poly_clip3).to_file('data_files/vector/poly_clip_explode.shp', driver='ESRI Shapefile')

# Read singlepart polygon output
explode = gpd.read_file("data_files/vector/poly_clip_explode.shp")

# Add column named area and calculate geometry
explode["area_km2"] = explode['geometry'].area / 10**6

# Write to a new file
explode.to_file('data_files/vector/data_w_area.shp')

# Read file with area
final_areas = gpd.read_file('data_files/vector/data_w_area.shp')

# Select areas greater than 1km2 and write to a new file
final_areas[final_areas['area_km2'] > 1].to_file('data_files/vector/final_selection.shp')

# Read the final areas file
final_selection = gpd.read_file('data_files/vector/final_selection.shp')
 
# Print result of analysis
print("The total suitable area found is {}km2".format(round(final_selection['area_km2'].sum(), 2)))

#-----------------------------------------------------------------------------------------------------------------------

"""

# Create point for Stevens Croft power station and write to file
c_point((312130.15, 585253.25), 'Stevens Croft', 27700, "data_files/vector/pwr_stn.shp")
pwr_station_point = gpd.read_file('data_files/vector/pwr_stn.shp')

# Read the travel time and suitable area shapefiles
study_area = gpd.read_file('data_files/vector/travel_time.shp')
suitable_areas = gpd.read_file('data_files/vector/final_selection.shp')

# Convert shapefiles to WGS84/ UTM zone 30N
pwr_station = pwr_station_point.to_crs(epsg=32630)
s_areas = suitable_areas.to_crs(epsg=32630)
study_tm = study_area.to_crs(epsg=32630)

# Set the map crs to UTM zone
mycrs = ccrs.UTM(30)

# Create figure for the map
fig, ax = plt.subplots(1, 1, figsize=(8, 8), subplot_kw=dict(projection=mycrs))

# Plot the polygon data
study_plot = ShapelyFeature(study_tm['geometry'], mycrs, facecolor='w', edgecolor='k', linewidth=0.75)
area_plot = ShapelyFeature(s_areas['geometry'], mycrs, facecolor='g')

# Add study area, suitable land areas and power station to the map
ax.add_feature(study_plot)
ax.add_feature(area_plot)
ax.plot(pwr_station.geometry.x, pwr_station.geometry.y, 'o', color='r', ms=8, label='Stevens Croft', transform=mycrs)

# Set extent of the map to the extent of the travel time/study area
xmin, ymin, xmax, ymax = study_tm.total_bounds
ax.set_extent([xmin, xmax, ymin, ymax], crs=mycrs)

# Colours and labels for legend
colours = ['g', 'r', 'k']
text = ["Suitable Land", "Power Station"]

# Generate handle for legend
area_handle = generate_handles('Suitable Land', ['g'])

# Create legend
ax.legend(area_handle, ['Suitable Land'], fontsize=10, loc='upper right', frameon=True, framealpha=1)

# Add a scale bar
scale_bar(ax)

# Add a north arrow
x, y, arrow_length = 0.05, 0.98, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=2, headwidth=10),
            ha='center', va='center', fontsize=18,
            xycoords=ax.transAxes)

# Add a label for the power station
ax.text(pwr_station.geometry.x, pwr_station.geometry.y+1000, 'Power Station',
        size=8, color='k', ha='center', fontweight='bold',
        path_effects=[pe.withStroke(linewidth=2, foreground="white")])

# Save the figure
fig.savefig('final_map.jpg', dpi=500, bbox_inches='tight')