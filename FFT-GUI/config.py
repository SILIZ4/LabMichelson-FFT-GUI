from matplotlib import rcParams

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


interferogram_xaxis_limits = {
        "HeNe": [0, 300],
        "WhiteLight": [-50, 50]
    }
zoomed_interferogram_xaxis_limits = {
        "HeNe": [0, 5],
        "WhiteLight": [-3, 3]
    }

fft_xaxis_limits =  {
        "frequencies": {
            "HeNe": [-3, 3],
            "WhiteLight": [-10, 10]
        },
        "wavelengths": {
            "HeNe": [-1000, 1000],
            "WhiteLight": [-2000, 2000]
        }
    }
zoomed_fft_xaxis_limits =  {
        "frequencies": {
            "HeNe": [1, 2],
            "WhiteLight": [1, 10]
        },
        "wavelengths": {
            "HeNe": [620, 650],
            "WhiteLight": [200, 1000]
        }
    }


# The dictionary "sources_sliders" sets up slider of each parameter in the
# interface. The intial value are set at the start of the program and each time
# the source is changed.
#
# The slider widget in Qt uses integers. The parameter "scale" is provided to
# allow the use of real numbers. The sliders values are divided by this scaling
# parameter such that the values displayed and used in the computations are
# real numbers.
# Example: value=5 and scale=100 gives a real value of 5/100=0.05
#
# The signal to noise ratio (SNR) is based on a logarithmic scale. The power
# of the logarithm base is set by the "base" parameter in the SNR configuration.
sources_sliders = {
        "HeNe": {

            "Pas": {
                "unit"   : "µm",
                "initial": 1,
                "minimum": 1,
                "maximum": 40,
                "step"   : 1,
                "scale"  : 100
            },
            "Plage": {
                "unit"   : "µm",
                "initial": 250,
                "minimum": 200,
                "maximum": 300,
                "step"   : 5,
                "scale"  : 1
            },
            "SNR": {
                "unit"   : "-",
                "base"   : 2,

                "initial": 8,
                "minimum": 4,
                "maximum": 14,
                "step"   : 1,
                "scale"  : 1
            }
        }, 
        "WhiteLight": {

            "Pas": {
                "unit"   : "µm",
                "initial": 1,
                "minimum": 1,
                "maximum": 40,
                "step"   : 1,
                "scale"  : 100
            },
            "Plage": {
                "unit"   : "µm",
                "initial": 60,
                "minimum": 10,
                "maximum": 100,
                "step"   : 5,
                "scale"  : 1
            },
            "SNR": {
                "unit"   : "-",
                "base"   : 2,

                "initial": 8,
                "minimum": 4,
                "maximum": 16,
                "step"   : 1,
                "scale"  : 1
            }
        }
    }
