import sys
import matplotlib
import numpy
from math import ceil
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import TimedAnimation
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import generate_data
from compute_fft import fourierTransformInterferogram


interferogram_data = [[], []]
fft_data = [[], []]

class InterferogramDynamicCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.previous_parameters = parent_window.fft_parameters.copy()
        self.parent_window = parent_window

        self.fig = Figure(**kwargs)
        ax = self.fig.add_subplot(111)

        ax.set_xlabel("Position")
        ax.set_ylabel("Voltage")
        self.line = Line2D([], [], color='#008080', ls='-', marker='o')
        ax.add_line(self.line)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 3)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100, blit=True)
        self.fig.tight_layout()

        self.generate_data()

    def new_frame_seq(self):
        return iter(range(10))

    def generate_data(self):
        current_fft_parameters = self.parent_window.fft_parameters

        global interferogram_data
        interferogram_data = generate_data.generateHeNeInterferogram(
                0, current_fft_parameters["Interval"], 
                ceil(current_fft_parameters["Interval"]/current_fft_parameters["Step"]),
                current_fft_parameters["Noise"])

        self.parent_window.fft.compute_fft() # Ensures that FFT computed after data generated

    def _draw_frame(self, framedata):
        current_fft_parameters = self.parent_window.fft_parameters

        if self.previous_parameters != current_fft_parameters:
            self.generate_data()
            self.previous_parameters = current_fft_parameters.copy()

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

        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Normalized intensity")
        self.line = Line2D([], [], color='#008080', ls='-', marker='o')
        self.ax.add_line(self.line)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100)
        self.fig.tight_layout()

    def new_frame_seq(self):
        return iter(range(10))

    def compute_fft(self):
        w, f, s = fourierTransformInterferogram(*interferogram_data)

        global fft_data
        fft_data = w, abs(s)
        fft_data = fft_data[0], fft_data[1]/max(fft_data[1])  # Normalize intensity

    def _draw_frame(self, framedata, force_regenerate=False):
        global fft_data
        self.line.set_data(fft_data)

        max_frequency = max(fft_data[0][~numpy.isinf(fft_data[0])])
        self.ax.set_xlim(0, max_frequency)
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

        initial_value = parent_window.fft_parameters[self.key]

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
        self.parent_window.fft_parameters[self.key] = value/self.scale



class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)
        self.fft_parameters = {"Step": 1, "Interval": 100, "Noise": 0}

        self.step_slider = HorizontalParameterSlider(self, "Step", 1, 200, 10, scale=10)
        self.interval_slider = HorizontalParameterSlider(self, "Interval", 50, 100, 5)
        self.noise_slider = HorizontalParameterSlider(self, "Noise", 0, 100, 2, scale=100)

        self.fft = FFTDynamicCanvas(self, figsize=(8, 4), dpi=100)
        self.interferogram = InterferogramDynamicCanvas(self, figsize=(8, 4), dpi=100)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.interferogram)
        self.mainLayout.addWidget(self.fft)
        self.mainLayout.addLayout(self.step_slider)
        self.mainLayout.addLayout(self.interval_slider)
        self.mainLayout.addLayout(self.noise_slider)

        self.setLayout(self.mainLayout)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
