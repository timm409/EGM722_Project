from shapely.geometry import shape, mapping
import fiona


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


study_area = 'C:/Users/Raph Martin/Documents/project/data_files/vector/travel_time.shp'
erase_mask = 'C:/Users/Raph Martin/Documents/project/data_files/vector/erase_mask.shp'
new_land = 'C:/Users/Raph Martin/Documents/project/data_files/vector/new_land.shp'

erase_shp(study_area, erase_mask, new_land, "EPSG:27700")
