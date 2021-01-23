import numpy as np
from numpy.random import *
from numpy.fft import *
import matplotlib.pyplot as plt
from scipy import stats

""" Ce script genere des donnees telles qu'obtenues avec un interferometre
de Michelson dans le but d'etudier la transformée de Fourier et de comprendre 
comment la resolution spectrale est déterminée.
"""


def generateHeNeInterferogram(xMin, xMax, dx, snr):
    """ Genere un tableau de valeurs equidistantes entre xMin et xMax et
    genere un second tableau qui represente un interferogramme d'un laser He-Ne
    a 0.6328 microns. Du bruit est ajouté à partir du rapport signal sur bruit
    snr.
    """
    x = np.arange(xMin, xMax+dx, dx) 
    y = np.cos(2 * np.pi / 0.6328 * x)

    return x, stats.norm.rvs(size=len(y), loc=y, scale=abs(y)/snr)

def generateWhiteLightInterferogram(xMin, xMax, dx, snr):
    """ Genere un tableau de valeurs equidistantes entre xMin et xMax et
    genere un second tableau qui represente un interferogramme d'une source
    blanche visible. Du bruit est ajouté à partir du rapport signal sur bruit
    snr.
    """
    xMid = (xMax-xMin)/2
    x = np.arange(xMin, xMax+dx, dx) - xMin - xMid

    k1 = 1/0.4
    k2 = 1/0.8
    y = 1 + np.exp(-x*x/4)*(np.sin(2*np.pi * (k1+k2)*x/2)/x * np.sin(2 * np.pi * (k1-k2)*x/2))
    y[x==0] = 1

    return x, stats.norm.rvs(size=len(y), loc=y, scale=abs(y)/snr)
