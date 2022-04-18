from matplotlib import rcParams
from matplotlib import use as mpl_use

mpl_use('Qt5Agg')


# Matplotlib figures configuration
darkblack = "#1a1a1a"
midblack ="#3d3d3d"
lightgray = "#ababab"

rcParams["axes.labelsize"] = 9
rcParams["axes.facecolor"] = "white"
rcParams["axes.grid"] = False
rcParams["axes.edgecolor"] = lightgray

rcParams["xtick.labelsize"] = 8
rcParams["ytick.labelsize"] = 8
rcParams["xtick.color"] = midblack
rcParams["ytick.color"] = midblack

rcParams["legend.edgecolor"] = "white"
rcParams["legend.fontsize"] = 10
rcParams["text.color"] = darkblack
