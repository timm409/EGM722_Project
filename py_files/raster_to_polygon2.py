import rasterio

def polygonize_raster(dataset):

    # Read the dataset's valid data mask as a ndarray. Dataset is a rasterio read object open for reading
    mask = dataset.dataset_mask()

    array = dataset.read(1)
    generator = rasterio.features.shapes(source=array, mask=mask, transform=dataset.transform)
    # Extract feature shapes and values from the array
    geom_list = []
    for geom, value in generator:
        # Print GeoJSON shapes to stdout
        geom = shapely.geometry.shape(geom)
        geom_list.append(geom)

    return geom_list