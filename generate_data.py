import numpy as np
from numpy.random import *
from numpy.fft import *
import matplotlib.pyplot as plt

""" Ce script genere des donnees telles qu'obtenues avec un interferometre
de Michelson dans le but d'etudier la transformée de Fourier et de comprendre 
comment la resolution spectrale est déterminée.
"""


def generateHeNeInterferogram(xMin, xMax, N, noise):
	""" Genere un tableau de N valeurs equidistantes enntre xMin et xMax.
	Ensuite, genere un tableau de N valeurs qui representent un interferogramme
	d'un laser He-Ne a 0.6328 microns. On ajoute du bruit pour rendre le tout
	plus realiste.
	"""
	dx = (xMax - xMin)/N
	x = np.linspace(xMin, xMax, N)
	noise = random(N)*noise
	y = 1+np.cos(2 * np.pi / 0.6328 * x)+noise
	return x,y


def generateWhiteLightInterferogram(xMin, xMax, N, noise):
	""" Genere un tableau de N valeurs equidistantes enntre xMin et xMax.
	Ensuite, genere un tableau de N valeurs qui representent un interferogramme
	d'une source blanche visible. On ajoute du bruit pour rendre le tout
	plus realiste.
	"""
	dx = (xMax - xMin)/N
	x = np.linspace(xMin, xMax, N)
	noise = random(N)*noise
	k1 = 1/0.4
	k2 = 1/0.8
	y = 1+np.exp(-x*x/4)*(np.sin(2 * np.pi * (k1+k2)*x/2)/x * np.sin(2 * np.pi * (k1-k2)*x/2)+ noise)
	return x,y
