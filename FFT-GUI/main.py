import sys
import matplotlib
import numpy
from math import ceil
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib import rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import TimedAnimation
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import generate_data
from compute_fft import fourierTransformInterferogram


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


interferogram_data = [[], []]
fft_data = [[], []]

class InterferogramDynamicCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.previous_parameters = parent_window.interferogram_parameters.copy()
        self.parent_window = parent_window

        self.fig = Figure(**kwargs)
        ax = self.fig.add_subplot(111)

        ax.set_xlabel("Position du miroir[µm]")
        ax.set_ylabel("Voltage [V]")
        self.line = Line2D([], [], color='#008080', ls='-', marker='o')
        ax.add_line(self.line)
        ax.set_xlim(5, 105)
        ax.set_ylim(0, 3)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100)
        self.fig.suptitle("Interférogramme")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def new_frame_seq(self):
        return iter(range(10))

    def generate_data(self):
        current_interferogram_parameters = self.parent_window.interferogram_parameters

        N = ceil(current_interferogram_parameters["Plage"]/current_interferogram_parameters["Pas"])

        generation_parameters = (0, current_interferogram_parameters["Plage"], 
                N, current_interferogram_parameters["%Bruit"])

        global interferogram_data
        if self.parent_window.HeNesource_radio.isChecked():
            interferogram_data = generate_data.generateHeNeInterferogram(*generation_parameters)
        elif self.parent_window.whitesource_radio.isChecked(): 
            interferogram_data = generate_data.generateWhiteLightInterferogram(*generation_parameters)
        else:
            raise ValueError("Unhandled error: one of the source type radio button is not handled")


        self.parent_window.fft.compute_fft() # Ensures that FFT computed after data generated

    def _draw_frame(self, framedata):
        current_interferogram_parameters = self.parent_window.interferogram_parameters

        if self.previous_parameters != current_interferogram_parameters:
            self.generate_data()
            self.previous_parameters = current_interferogram_parameters.copy()

        global interferogram_data
        self.line.set_data(interferogram_data)
        self._drawn_artists = [self.line]

    def _init_draw(self):
        lines = [self.line]
        for l in lines:
            l.set_data([], [])

class FFTDynamicCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.fig = Figure(**kwargs)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel("Longueur d'onde [nm]")
        self.ax.set_ylabel("Intensité")
        self.line = Line2D([], [], color='#008080', ls='-', marker='o')
        self.ax.add_line(self.line)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100)
        self.fig.suptitle("Transformée de Fourier")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def new_frame_seq(self):
        return iter(range(10))

    def compute_fft(self):
        w, f, s = fourierTransformInterferogram(*interferogram_data)

        global fft_data
        fft_data = w*1000, abs(s)


    def _draw_frame(self, framedata, force_regenerate=False):
        global fft_data

        self.line.set_data(fft_data)

        max_frequency = max(fft_data[0][~numpy.isinf(fft_data[0])])
        max_intensity = max(fft_data[1])
        self.ax.set_xlim(-max_frequency, max_frequency)
        self.ax.set_ylim(0, max_intensity)
        self._drawn_artists = [self.line]

    def _init_draw(self):
        lines = [self.line]
        for l in lines:
            l.set_data([], [])

class HorizontalParameterSlider(QtWidgets.QHBoxLayout):
    def __init__(self, parent_window, parameter_key, minValue=0, maxValue=10, step=1, scale=1, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.parent_window = parent_window
        self.key = parameter_key
        self.scale = scale

        initial_value = parent_window.interferogram_parameters[self.key]

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setValue(initial_value*scale)
        self.slider.setMinimum(minValue)
        self.slider.setMaximum(maxValue)
        self.slider.setSingleStep(step)
        self.slider.valueChanged.connect(self.updateSliderLabel)

        self.label = QtWidgets.QLabel()
        self.label.setText(self.key+": "+str(initial_value))

        self.addWidget(self.label)
        self.addWidget(self.slider)

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText(self.key+": "+str(value/self.scale))
        self.parent_window.interferogram_parameters[self.key] = value/self.scale



class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)
        self.interferogram_parameters = {"Pas": 2, "Plage": 200, "%Bruit": 0}

        # The order of creation of widgets is important, some values must
        # be initialized before others
        self.step_slider = HorizontalParameterSlider(self, "Pas", 5, 40, 5, scale=10)
        self.interval_slider = HorizontalParameterSlider(self, "Plage", 200, 300, 5)
        self.noise_slider = HorizontalParameterSlider(self, "%Bruit", 0, 100, 2, scale=100)

        self.fft = FFTDynamicCanvas(self, figsize=(8, 6), dpi=100)
        self.interferogram = InterferogramDynamicCanvas(self, figsize=(8, 6), dpi=100)

        self.HeNesource_radio = QtWidgets.QRadioButton("Source HeNe")
        self.HeNesource_radio.toggled.connect(self.interferogram.generate_data)
        self.HeNesource_radio.toggle()
        self.whitesource_radio = QtWidgets.QRadioButton("Source de lumière blanche")
        self.whitesource_radio.toggled.connect(self.interferogram.generate_data)
        self.radioLayout = QtWidgets.QHBoxLayout()
        self.radioLayout.addWidget(self.HeNesource_radio)
        self.radioLayout.addWidget(self.whitesource_radio)

        refresh_data_button = QtWidgets.QPushButton("Générer de nouvelles données")
        refresh_data_button.clicked.connect(self.interferogram.generate_data)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.interferogram)
        self.mainLayout.addWidget(self.fft)
        self.mainLayout.addLayout(self.step_slider)
        self.mainLayout.addLayout(self.interval_slider)
        self.mainLayout.addLayout(self.noise_slider)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addWidget(refresh_data_button)

        self.interferogram.generate_data()
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Effets des paramètres de l'interférogramme sur sa transformée de Fourier")

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
