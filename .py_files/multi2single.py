import geopandas as gp
import pandas as pd

gsa_other = gp.read_file("data_files/vector/gsa_other.shp")


def multi2single(gpdf):
    gpdf_singlepoly = gpdf[gpdf.geometry.type == 'Polygon']
    gpdf_multipoly = gpdf[gpdf.geometry.type == 'MultiPolygon']

    for i, row in gpdf_multipoly.iterrows():
        series_geometries = pd.Series(row.geometry)
        df = pd.concat([gp.GeoDataFrame(row, crs=gpdf_multipoly.crs).T]*len(series_geometries), ignore_index=True)
        df['geometry'] = series_geometries
        gpdf_singlepoly = pd.concat([gpdf_singlepoly, df])

    gpdf_singlepoly.reset_index(inplace=True, drop=True)
    return gpdf_singlepoly


multi2single(gsa_other).to_file('data_files/vector/gsa_explode.shp', driver='ESRI Shapefile')
