import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy

from PyQt5 import QtCore, QtWidgets

import sys
sys.path.append("../")
from compute_fft import fourierTransformInterferogram
import generate_data


interferogram_data = [[], []]
fft_data = [[], []]
fft_axis_k = []
fft_axis_frequencies = []
block_generation = False

teal = "#008080"
zoomed_color = "#1a1a1a"

class InterferogramDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, parent_window, **kwargs):
        self.parent_window = parent_window

        self.fig = Figure(**kwargs)

        self.ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 0), colspan=2, fig=self.fig)
        self.zoomed_ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 2), fig=self.fig)
        self.zoomed_ax.set_yticklabels([])

        self.ax.set_xlabel("Position du miroir[µm]")
        self.ax.set_ylabel("Voltage normalisé [-]")
        self.zoomed_ax.set_xlabel("Position du miroir[µm]")

        self.rectangle = Rectangle((0,0), width=1, height=2,
                alpha=1, fill=False, ec=zoomed_color, lw=2, ls='--', zorder=4)
        for child in self.zoomed_ax.get_children():
            if isinstance(child, matplotlib.spines.Spine):
                child.set_color(zoomed_color)
                child.set_linewidth(1.5)
        self.ax.add_patch(self.rectangle)

        self.line = Line2D([], [], color=teal, ls='-')
        self.ax.add_line(self.line)
        self.line_copy = Line2D([], [], color=teal, ls='-', markersize=3, marker='o')
        self.zoomed_ax.add_line(self.line_copy)

        self.ax.set_ylim(-1, 1)
        self.zoomed_ax.set_ylim(-1, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.fig.suptitle("Interférogramme")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def generate_data(self):
        global block_generation
        if block_generation:
            return

        current_interferogram_parameters = self.parent_window.interferogram_parameters

        generation_parameters = (0, current_interferogram_parameters["Plage"], 
                current_interferogram_parameters["Pas"], 
                current_interferogram_parameters["SNR"]/100  # Noise is in %
                )

        global interferogram_data
        if self.parent_window.source == "HeNe":
            interferogram_data = generate_data.generateHeNeInterferogram(*generation_parameters)
        elif self.parent_window.source == "WhiteLight":
            interferogram_data = generate_data.generateWhiteLightInterferogram(*generation_parameters)
        else:
            raise ValueError("Unknown source type to generate data")

        interferogram_data = interferogram_data[0], interferogram_data[1]/max(interferogram_data[1])

    def draw_frame(self):
        global interferogram_data
        self.line.set_data(interferogram_data)
        self.line_copy.set_data(interferogram_data)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def rescale_axis(self, limits, zoomed_limits):
        self.rectangle.set_xy((zoomed_limits[0], -1))
        self.rectangle.set_width(zoomed_limits[1]-zoomed_limits[0])
        self.ax.set_xlim(*limits)
        self.zoomed_ax.set_xlim(*zoomed_limits)

class FFTDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, parent_window, **kwargs):
        self.xaxis_type = "wavelengths"


        self.fig = Figure(**kwargs)

        self.ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 0), colspan=2, fig=self.fig)
        self.zoomed_ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 2), fig=self.fig)
        self.zoomed_ax.set_yticklabels([])

        self.ax.set_xlabel("Longueur d'onde [nm]")
        self.zoomed_ax.set_xlabel("Longueur d'onde [nm]")
        self.ax.set_ylabel("Intensité")

        self.rectangle = Rectangle((0,0), width=1, height=1,
                alpha=1, fill=False, ec=zoomed_color, lw=2, ls='--', zorder=4)
        for child in self.zoomed_ax.get_children():
            if isinstance(child, matplotlib.spines.Spine):
                child.set_color(zoomed_color)
                child.set_linewidth(1.5)
        self.ax.add_patch(self.rectangle)

        self.line = Line2D([], [], color=teal, ls='-')
        self.ax.add_line(self.line)
        self.line_copy = Line2D([], [], color=teal, ls='-', markersize=3, marker='o')
        self.zoomed_ax.add_line(self.line_copy)

        self.ax.set_ylim(0, 1)
        self.zoomed_ax.set_ylim(0, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.fig.suptitle("Transformée de Fourier")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def compute_fft(self):
        global fft_data, block_generation
        if block_generation:
            return

        w, f, s = fourierTransformInterferogram(*interferogram_data)
        if self.xaxis_type == "wavelengths":
            fft_data = [w*1000, abs(s)]
        elif self.xaxis_type == "frequencies":
            fft_data = [f, abs(s)]

    def toggle_xaxis_type(self):
        if self.xaxis_type == "wavelengths":
            self.xaxis_type = "frequencies"
            self.ax.set_xlabel("Fréquences")
            self.zoomed_ax.set_xlabel("Fréquences")

        elif self.xaxis_type == "frequencies":
            self.xaxis_type = "wavelengths"
            self.ax.set_xlabel("Longueurs d'onde [nm]")
            self.zoomed_ax.set_xlabel("Longueurs d'onde [nm]")

        self.compute_fft()

    def draw_frame(self):
        global fft_data, block_generation
        if block_generation:
            return

        self.line.set_data(fft_data)
        self.line_copy.set_data(fft_data)

        max_frequency = max(fft_data[0][~numpy.isinf(fft_data[0])])
        max_intensity = max(fft_data[1][~numpy.isinf(fft_data[0]) & ~numpy.isinf(fft_data[1])])*1.05
        self.ax.set_ylim(0, max_intensity)
        self.zoomed_ax.set_ylim(0, max_intensity)
        self.rectangle.set_height(max_intensity)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def rescale_axis(self, limits, zoomed_limits):
        self.rectangle.set_xy((zoomed_limits[0], -1))
        self.rectangle.set_width(zoomed_limits[1]-zoomed_limits[0])
        self.ax.set_xlim(*limits)
        self.zoomed_ax.set_xlim(*zoomed_limits)
