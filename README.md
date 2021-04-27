# Project for EGM722: Site Selection Tool for Identifying Areas for Biomass Production

## 1. Getting started

To run the script, you will need to install `git`, `conda` and a python interpreter such as `PyCharm` on your computer. 
Instructions for installing git can be found [here](https://git-scm.com/downloads), instructions for Anaconda can be
found [here](https://docs.anaconda.com/anaconda/install/) and instructions for PyCharm Community Edition 
can be found [here](https://www.jetbrains.com/pycharm/download/#section=windows).

## 2. Download/clone this repository

Once these are installed, a __clone__ of this repository will need to be created on the computer. This can be done in
the following ways:

1. Open GitHub Desktop and select __File__ > __Clone Repository__. Select the __URL__ tab, then enter the URL for this 
   repository.
2. Open __GitBash__ (from the __Start__ menu) and navigate to the project folder. 
   Execute the command: `git clone https://github.com/timm409/project`.
3. Download the zip file from this web page by clicking the clone/download button.

## 3. Data

The data files provided have been pre-processed to reduce file size. The data was collated from a variety of sources:

1. DEM - [Earth Explorer](https://earthexplorer.usgs.gov/).
2. Travel Time - Created in ArcGIS Pro.
3. Buildings, rivers and roads - [Ordnance Survey](https://osdatahub.os.uk/downloads/open).
4. Protected Areas - [Scottish Natural Heritage](https://gateway.snh.gov.uk/natural-spaces/).


## 4. Create a conda environment

Once you have successfully cloned the repository and checked the data is there, you can then create a `conda` environment 
and run/edit the script. To create a `conda` environment, use the environment.yml file provided in the repository. If you have 
Anaconda Navigator installed, you can do this by selecting __Import__ from the bottom of the __Environments__ panel. 

Otherwise, you can open a command prompt (on Windows, you may need to select an Anaconda command prompt). Navigate (using __cd__)
to the folder where you cloned this repository and run the following command:

```
C:\Users\timm409> conda env create -f environment.yml
```

[GDAL](https://gdal.org/) is mostly used for the raster analysis, whilst [Geopandas](https://geopandas.org/) is mostly used 
for the vector analysis. [Matplotlib](https://matplotlib.org/) is the primary dependency used for the mapping portion. 


## 5. Start PyCharm

Launch `PyCharm` or another IDE and open the python script by navigating to the project folder.