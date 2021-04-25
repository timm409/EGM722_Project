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


poly_clip1 = 'C:/Users/Raph Martin/Documents/project/data_files/vector/poly_clip1.shp'
inf_buf2 = 'C:/Users/Raph Martin/Documents/project/data_files/vector/inf_buf2.shp'
poly_clip2 = 'C:/Users/Raph Martin/Documents/project/data_files/vector/poly_clip2.shp'

erase_shp(poly_clip1, inf_buf2, poly_clip2, "EPSG:27700")
