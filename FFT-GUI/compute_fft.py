from numpy.random import *
from numpy.fft import *


def fourierTransformInterferogram(x,y):
	""" A partir du tableau de valeurs Y correspondant a l'abscisse X, 
	la transformée de Fourier est calculée et l'axes des fréquences (f en 
	µm^-1) et des wavelengths (1/f en microns) est retournée.

	Le spectre est un ensemble de valeurs complexes pour lesquelles l'amplitude
	et la phase sont pertinentes: l'ordre des valeurs commence par la valeur DC (0)
	et monte jusqu'a f_max=1/2/∆x par resolution de ∆f = 1/N/∆x. A partir de la
	(N/2) ieme valeur, la frequence est negative jusqu'a -∆f dans la N-1 case.
	Voir 
	https://github.com/dccote/Enseignement/blob/master/HOWTO/HOWTO-Transformes%20de%20Fourier%20discretes.pdf 
	"""
	spectrum = fft(y)
	dx = x[1]-x[0] # on obtient dx, on suppose equidistant
	N = len(x)     # on obtient N directement des données
	frequencies = fftfreq(N, dx) # Cette fonction est fournie par numpy
	wavelengths = 1/frequencies  # Les fréquences en µm^-1 sont moins utiles que lambda en µm
	return (wavelengths, frequencies, spectrum)
