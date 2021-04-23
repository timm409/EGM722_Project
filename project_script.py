import gdal
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from fiona.crs import from_epsg


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
roads = gpd.read_file('data_files/vector/roads.shp')
rivers = gpd.read_file('data_files/vector/rivers.shp')
buildings = gpd.read_file('data_files/vector/buildings.shp')

# Define infra as the infrastructure list
infra = [roads, rivers, buildings]

# Merge the infrastructure shapefiles and define
inf_merge = merge_shp(infra)

# 25m buffer of infrastructure
inf_buf = inf_merge.buffer(25)

# Save infrastructure buffer to file
inf_buf.to_file('data_files/vector/inf_buf.shp', driver='ESRI Shapefile')

# Read multipart polygon output
gsa_other = gpd.read_file("data_files/vector/gsa_other.shp")

# Explode the shapefile from multipart to singlepart and write to file
multi2single(gsa_other).to_file('data_files/vector/gsa_explode.shp', driver='ESRI Shapefile')

# Create point for Stevens Croft power station and write to file
pwr_stn = c_point((312130.15, 585253.25), 'Stevens Croft', 27700, "data_files/vector/pwr_stn.shp")
