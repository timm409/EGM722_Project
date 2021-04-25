import geopandas as gpd
import pandas as pd

test = gpd.read_file("data_files/vector/gsa_explode.shp")

test["area_km2"] = test['geometry'].area / 10**6

test.to_file('data_w_area.shp')

final_areas = gpd.read_file('data_w_area.shp')

final_areas[final_areas['area_km2'] > 1].to_file('final_selection.shp')

final_selection = gpd.read_file('final_selection.shp')

print("The total suitable area found is {}km2".format(round(final_selection['area_km2'].sum(), 2)))
