#!/usr/bin/env

import gdal
import fiona
import ogr
import pandas as pd
import geopandas as gpd
from osgeo import osr
from shapely.geometry import Point, shape, mapping
from fiona.crs import from_epsg

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


def merge_shp(shp_out):
    """
    merge shapefiles
    :param shp_out: list of shapefile paths
    :return: merged shapefile
    """
    return gpd.GeoDataFrame(pd.concat(shp_out))


def unite_shp(shp_df, crs1, output):
    """
    dissolves shapefile
    :param shp_df: input shapefile
    :param crs1: set crs of the new dataframe
    :param output: path for writing output
    :return: write data to output path
    """
    # Union the objects
    shp_u = shp_df.unary_union
    # Create gpd GeoDataFrame, set CRS and add geometry column
    newdata = gpd.GeoDataFrame(crs=crs1, geometry=[shp_u])
    # Write output to file
    return newdata.to_file(output)


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

# Open the shapefiles for infrastructure
roads = gpd.read_file('data_files/vector/infrastructure/roads.shp')
rivers = gpd.read_file('data_files/vector/infrastructure/rivers.shp')
buildings = gpd.read_file('data_files/vector/infrastructure/buildings.shp')

# Define infra as the infrastructure list
infra = [roads, rivers, buildings]

# Merge the infrastructure shapefiles and define
inf_merge = merge_shp(infra)

# 25m buffer of infrastructure
inf_buf = inf_merge.geometry.buffer(25)

# Buffer output location
buf1 = 'data_files/vector/inf_buf.shp'

# Dissolve infrastructure buffer and save to file
unite_shp(inf_buf, inf_buf.crs, buf1)

# Define inputs and outputs for erase function
big_poly = 'data_files/vector/big_poly.shp'
inf_buf2 = 'data_files/vector/inf_buf.shp'
poly_clip = 'data_files/vector/poly_clip.shp'

# Erase the infrastructure from the polygon
erase_shp(big_poly, inf_buf2, poly_clip, "EPSG:27700")

# Open the shapefiles for protected areas
ramsar = gpd.read_file('data_files/vector/protected_areas/ramsar.shp')
sssi = gpd.read_file('data_files/vector/protected_areas/sssi.shp')

# Define protected areas as a list
p_areas = [ramsar, sssi]

# Merge the protected areas shapefiles and define
p_areas_merge = merge_shp(p_areas)

# Dissolve output location
p_areas1 = 'data_files/vector/p_areas1.shp'

# Dissolve protected areas and save to file
unite_shp(p_areas_merge, p_areas_merge.crs, p_areas1)

# Erase the infrastructure from the polygon
erase_shp(big_poly, p_areas1, poly_clip, "EPSG:27700")

# Read multipart polygon output
gsa_other = gpd.read_file("data_files/vector/gsa_other.shp")

# Explode the shapefile from multipart to singlepart and write to file
multi2single(gsa_other).to_file('data_files/vector/gsa_explode.shp', driver='ESRI Shapefile')

# Read singlepart polygon output
test = gpd.read_file("data_files/vector/gsa_explode.shp")

# Add column named area and calculate geometry
test["area_km2"] = test['geometry'].area / 10**6

# Write to a new file
test.to_file('data_files/vector/data_w_area.shp')

# Read file with area
final_areas = gpd.read_file('data_files/vector/data_w_area.shp')

# Select areas greater than 1km2 and write to a new file
final_areas[final_areas['area_km2'] > 1].to_file('data_files/vector/final_selection.shp')

# Read the final areas file
final_selection = gpd.read_file('data_files/vector/final_selection.shp')

# Print result of analysis
print("The total suitable area found is {}km2".format(round(final_selection['area_km2'].sum(), 2)))

# Create point for Stevens Croft power station and write to file
pwr_stn = c_point((312130.15, 585253.25), 'Stevens Croft', 27700, "data_files/vector/pwr_stn.shp")

# Create a point for Dumfries
dumfries = c_point((297182.05, 576278.94), 'Dumfries', 27700, "data_files/vector/dumfries.shp")