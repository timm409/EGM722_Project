# EGM722: Project

## 1. Getting started

To run the script, you will need to install `git`, `conda` and a python interpreter such as `PyCharm` on your computer. 
Instructions for installing git can be found [here](https://git-scm.com/downloads), instructions for Anaconda can be
found [here](https://docs.anaconda.com/anaconda/install/) and instructions for PyCharm Community Edition 
can be found [here](https://www.jetbrains.com/pycharm/download/#section=windows).

## 2. Download/clone this repository

Once you have these installed, __clone__ this repository to your computer by doing one of the following things:

1. Open GitHub Desktop and select __File__ > __Clone Repository__. Select the __URL__ tab, then enter the URL for this 
   repository.
2. Open __Git Bash__ (from the __Start__ menu), then navigate to your folder for this module.
   Now, execute the following command: `git clone https://github.com/timm409/project`. You should see some messages
   about downloading/unpacking files, and the repository should be set up.
3. You can also clone this repository by clicking the green "clone or download" button above, and select "download ZIP"
   at the bottom of the menu. Once it's downloaded, unzip the file and move on to the next step.

## 3. Create a conda environment

Once you have successfully cloned the repository, you can then create a `conda` environment to work through the exercises.

To do this, use the environment.yml file provided in the repository. If you have Anaconda Navigator installed,
you can do this by selecting __Import__ from the bottom of the __Environments__ panel. 

Otherwise, you can open a command prompt (on Windows, you may need to select an Anaconda command prompt). Navigate
to the folder where you cloned this repository and run the following command:

```
C:\Users\> conda env create -f environment.yml
```

## 4. Start PyCharm

Launch PyCharm and open the python script by navigating to the project folder.