from matplotlib import rcParams


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


interferogram_xaxis_limits = {
        "HeNe": [0, 300],
        "WhiteLight": [-50, 50]
    }
fft_xaxis_limits =  {
        "HeNe": [-5000, 5000],
        "WhiteLight": [-5000, 5000]
    }


sources_sliders = {
        "HeNe": {

            "Pas": {
                "unit"   : "µm",
                "initial": 20,
                "minimum": 5,
                "maximum": 40,
                "step"   : 5,
                "scale"  : 10
            },
            "Plage": {
                "unit"   : "µm",
                "initial": 250,
                "minimum": 200,
                "maximum": 300,
                "step"   : 5,
                "scale"  : 1
            },
            "Bruit": {
                "unit"   : "%",
                "initial": 5,
                "minimum": 0,
                "maximum": 100,
                "step"   : 1,
                "scale"  : 10
            }
        }, 
        "WhiteLight": {

            "Pas": {
                "unit"   : "µm",
                "initial": 10,
                "minimum": 5,
                "maximum": 20,
                "step"   : 1,
                "scale"  : 10
            },
            "Plage": {
                "unit"   : "µm",
                "initial": 250,
                "minimum": 40,
                "maximum": 100,
                "step"   : 5,
                "scale"  : 1
            },
            "Bruit": {
                "unit"   : "%",
                "initial": 5,
                "minimum": 0,
                "maximum": 100,
                "step"   : 1,
                "scale"  : 10
            }
        }
    }
