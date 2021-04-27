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
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches

"""
Selection Tool for Identifying Areas of Biomass Production
functions: line 26 - 230
analysis: line 231 - 330
mapping: line 331 - 387
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
    # Open the DEM, create slope raster, aspect raster, close the DEM
    gdal.Open(dem_in)
    gdal.DEMProcessing(slp_out, dem_in, "slope", computeEdges=True)
    gdal.DEMProcessing(asp_out, dem_in, "aspect", computeEdges=True)
    dem_in = None


def readraster(filename):
    """
    Read raster and extract transformation, projection and z values
    Adapted this question: https://gis.stackexchange.com/q/163685
    Answered by SE user RutgerH: https://gis.stackexchange.com/a/163705
    :param filename: path for input raster
    :return: transformation, projection and z values
    """
    # Open the raster, get raster band 1, get transformation, get projection
    filehandle = gdal.Open(filename)
    band1 = filehandle.GetRasterBand(1)
    geotransform = filehandle.GetGeoTransform()
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
    # Create grid, get GeoTiff driver, set data type to 32 bit float
    (x, y) = data.shape
    driver = gdal.GetDriverByName('GTiff')
    dst_datatype = gdal.GDT_Float32
    # Create raster file, get raster band 1 and write as array
    dst_ds = driver.Create(filename, y, x, 1, dst_datatype)
    dst_ds.GetRasterBand(1).WriteArray(data)
    # Set transformation, set projection and set no data values to -9999
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(geoprojection)
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)


def polygon_raster(raster, polygon_shp):
    """
    Converts raster file to a polygon shapefile
    Adapted this question by SE user nmtoken: https://gis.stackexchange.com/q/254410
    :param raster: input raster path
    :param polygon_shp: output shapefile path
    """
    # Open raster file, get raster band 1, get spatial reference and projection
    src_ds = gdal.Open(raster)
    srcband = src_ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(src_ds.GetProjection())
    # Define output datasource, get driver and create a shapefile for datasource
    dst_layername = polygon_shp
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(dst_layername + ".shp")
    # Create a layer, set srs, polygonize the data and save to file
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
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


def erase_shp(big_shp, small_shp, path_out, crs1):
    """
    Erase part of a shapefile using another shapefile and write to output
    Adapted this question by SE user PolyGeo: https://gis.stackexchange.com/q/163040
    :param big_shp: input path of shapefile
    :param small_shp: input path of template shapefile
    :param path_out: output path of shapefile
    :param crs1: crs of dataset
    """
    # Open the shapefiles
    big = fiona.open(big_shp)
    small = fiona.open(small_shp)
    # Cycle through the attribute
    pol_big = next(iter(big))
    pol_small = next(iter(small))
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
    Create point shapefile
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


def generate_handles(labels, colors, edge='k', alpha=1):
    """
    Generate handles for the legend map
    :param labels: name of legend entry
    :param colors: color of legend box
    :param edge: edge colour, default is black
    :param alpha: transparency of legend, default is not transparent
    :return: handles
    """
    # Get the length of the colour list
    lc = len(colors)
    handles = []
    # Create a rectangle for each of the legend entries
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


def scale_bar(ax, location=(0.92, 0.9)):
    """
    Creates a scale bar of length 10km in the upper right corner of the map.
    Adapted this question:https://stackoverflow.com/q/32333870
    Answered by SO user Siyh: https://stackoverflow.com/a/35705477
    :param ax: axes to draw the scale bar
    :param location: the location of the legend on the map
    """
    # Get the limits of the axes in lat long
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    # Project in meters
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(sbllx, sblly)
    # Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(tmc)
    # Turn the specified scale bar location into metres
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]
    # Plot the color bar
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx, sbx - 5000], [sby, sby], color='k', linewidth=3, transform=tmc)
    plt.plot([sbx-5000, sbx - 10000], [sby, sby], color='w', linewidth=3, transform=tmc)
    # Plot the text
    plt.text(sbx, sby-2000, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx-5000, sby-2000, '5 km', transform=tmc, fontsize=8)
    plt.text(sbx-10500, sby-2000, '0 km', transform=tmc, fontsize=8)


# -----------------------------------------------------------------------------------------------------------------------

# Define DEM, travel area shapefile and output for clipped DEM
dem = "data_files/raster/dem_25m.tif"
study_area = "data_files/vector/travel_time.shp"
dem_clip = "data_files/raster/dem_clip.tif"

# Clip DEM to study area shapefile
raster_shp_clip(dem, study_area, dem_clip)

# Create slope and aspect raster files from clipped DEM
slope = "data_files/raster/slope.tif"
aspect = "data_files/raster/aspect.tif"
create_slp_asp(dem_clip, slope, aspect)

# Reclassify slope and aspect to high slope and north facing
high_slope = "data_files/raster/high_slope.tif"
nw_facing = "data_files/raster/nw_facing.tif"
ne_facing = "data_files/raster/ne_facing.tif"

# Reclassify values below or equal to 11.3 to nodata
[geotransform, geoproj, z] = readraster(slope)
z[z <= 11.3] = np.nan
z[z > 11.3] = 1
writeraster(high_slope, geotransform, geoproj, z)

# Reclassify values above or equal to 315 to nodata
[geotransform, geoproj, z] = readraster(aspect)
z[z <= 315] = np.nan
z[z > 315] = 1
writeraster(nw_facing, geotransform, geoproj, z)

# Reclassify values below or equal to 45 to nodata
[geotransform, geoproj, z] = readraster(aspect)
z[z >= 45] = np.nan
z[z < 0] = np.nan
z[z < 45] = 1
writeraster(ne_facing, geotransform, geoproj, z)

# Define the output path for the new shapefiles
slope_vec = "data_files/vector/slope_vec"
nw_facing_vec = "data_files/vector/nw_facing_vec"
ne_facing_vec = "data_files/vector/ne_facing_vec"

# Convert the raster data to shapefiles
polygon_raster(high_slope, slope_vec)
polygon_raster(nw_facing, nw_facing_vec)
polygon_raster(ne_facing, ne_facing_vec)

# Open the shapefiles for land constraints
roads = gpd.read_file('data_files/vector/infrastructure/roads.shp')
rivers = gpd.read_file('data_files/vector/infrastructure/rivers.shp')
buildings = gpd.read_file('data_files/vector/infrastructure/buildings.shp')
l_con = [roads, rivers, buildings]

# Merge the land constraint shapefiles and define
l_con_merge = merge_shp(l_con)

# 24m buffer of land constraints and save to file
l_con_buf = l_con_merge.geometry.buffer(24)
l_con_buf.to_file('data_files/vector/l_con_buf.shp')

# Open the polygons for removing from the study area polygon
nw_facing_vec = gpd.read_file('data_files/vector/nw_facing_vec.shp')
ne_facing_vec = gpd.read_file('data_files/vector/ne_facing_vec.shp')
slope_vec = gpd.read_file('data_files/vector/slope_vec.shp')
l_con = gpd.read_file('data_files/vector/l_con_buf.shp')
ramsar = gpd.read_file('data_files/vector/protected_areas/ramsar.shp')
sssi = gpd.read_file('data_files/vector/protected_areas/sssi.shp')
erase_mask_polygons = [nw_facing_vec, ne_facing_vec, slope_vec, l_con, ramsar, sssi]

# Merge the polygons, dissolve and save to file
erase_mask = merge_shp(erase_mask_polygons)
erase_mask_dissolved = unite_shp(erase_mask, erase_mask.crs)
erase_mask_dissolved.to_file('data_files/vector/erase_mask.shp')

# Input file and output path for the erase function
erase_mask = 'data_files/vector/erase_mask.shp'
new_land = 'data_files/vector/new_land.shp'

# Erase the areas identified as unsuitable from the polygon
erase_shp(study_area, erase_mask, new_land, "EPSG:27700")

# Explode the shapefile from multipart to singlepart and write to file
new_land = gpd.read_file("data_files/vector/new_land.shp")
new_land.geometry.explode().to_file('data_files/vector/new_land_explode.shp', driver='ESRI Shapefile')

# Add column named area, calculate geometry and write to new file
explode = gpd.read_file("data_files/vector/new_land_explode.shp")
explode["area_km2"] = explode['geometry'].area / 10 ** 6
explode.to_file('data_files/vector/land_w_area.shp')

# Select areas greater than 1km2 and write to a new file
land_w_area = gpd.read_file('data_files/vector/land_w_area.shp')
land_w_area[land_w_area['area_km2'] > 1].to_file('data_files/vector/final_selection.shp')

# Print result of analysis
final_selection = gpd.read_file('data_files/vector/final_selection.shp')
print("The total suitable area found is {}km2".format(round(final_selection['area_km2'].sum(), 2)))

# -----------------------------------------------------------------------------------------------------------------------

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
