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

from compute_fft import fourierTransformInterferogram
import config as cfg
import generate_data


interferogram_data = [[], []]
fft_data = [[], []]
block_generation = False

class InterferogramDynamicCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.parent_window = parent_window

        self.fig = Figure(**kwargs)

        self.ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 0), colspan=2, fig=self.fig)
        self.zoomed_ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 2), fig=self.fig)
        self.zoomed_ax.set_yticklabels([])

        self.ax.set_xlabel("Position du miroir[µm]")
        self.zoomed_ax.set_xlabel("Position du miroir[µm]")
        self.ax.set_ylabel("Voltage normalisé [-]")

        self.line = Line2D([], [], color='#008080', ls='-')
        self.ax.add_line(self.line)
        self.line_copy = Line2D([], [], color='#008080', ls='-', markersize=3, marker='o')
        self.zoomed_ax.add_line(self.line_copy)

        self.ax.set_ylim(-1, 1)
        self.zoomed_ax.set_ylim(-1, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100)
        self.fig.suptitle("Interférogramme")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def new_frame_seq(self):
        return iter(range(10))

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

    def _draw_frame(self, framedata):
        global interferogram_data
        self.line.set_data(interferogram_data)
        self.line_copy.set_data(interferogram_data)
        self._drawn_artists = [self.line, self.line_copy]

    def _init_draw(self):
        lines = [self.line, self.line_copy]
        for l in lines:
            l.set_data([], [])

    def rescale_axis(self, limits, zoomed_limits):
        self.ax.set_xlim(*limits)
        self.zoomed_ax.set_xlim(*zoomed_limits)

class FFTDynamicCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.fig = Figure(**kwargs)

        self.ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 0), colspan=2, fig=self.fig)
        self.zoomed_ax = matplotlib.pyplot.subplot2grid((1, 3), (0, 2), fig=self.fig)
        self.zoomed_ax.set_yticklabels([])

        self.ax.set_xlabel("Longueur d'onde [nm]")
        self.zoomed_ax.set_xlabel("Longueur d'onde [nm]")
        self.ax.set_ylabel("Intensité")

        self.line = Line2D([], [], color='#008080', ls='-')
        self.ax.add_line(self.line)
        self.line_copy = Line2D([], [], color='#008080', ls='-', markersize=3, marker='o')
        self.zoomed_ax.add_line(self.line_copy)

        self.ax.set_ylim(0, 1)
        self.zoomed_ax.set_ylim(0, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100)
        self.fig.suptitle("Transformée de Fourier")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.25)

    def new_frame_seq(self):
        return iter(range(10))

    def compute_fft(self):
        global fft_data, block_generation
        if block_generation:
            return

        w, f, s = fourierTransformInterferogram(*interferogram_data)
        fft_data = w*1000, abs(s)

    def _draw_frame(self, framedata, force_regenerate=False):
        global fft_data

        self.line.set_data(fft_data)
        self.line_copy.set_data(fft_data)

        max_frequency = max(fft_data[0][~numpy.isinf(fft_data[0])])
        max_intensity = max(fft_data[1][~numpy.isinf(fft_data[0]) & ~numpy.isinf(fft_data[1])])*1.05
        self.ax.set_ylim(0, max_intensity)
        self.zoomed_ax.set_ylim(0, max_intensity)
        self._drawn_artists = [self.line, self.line_copy]

    def _init_draw(self):
        lines = [self.line, self.line_copy]
        for l in lines:
            l.set_data([], [])

    def rescale_axis(self, limits, zoomed_limits):
        self.ax.set_xlim(*limits)
        self.zoomed_ax.set_xlim(*zoomed_limits)

class HorizontalParameterSlider(QtWidgets.QHBoxLayout):
    def __init__(self, parent_window, parameter_key, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.parent_window = parent_window
        self.key = parameter_key
        self.scale = 1
        self.base = 1

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(parent_window.readSliderValues)
        self.slider.valueChanged.connect(self.updateSliderLabel)
        self.slider.valueChanged.connect(parent_window.updateFigures)

        self.label = QtWidgets.QLabel()

        self.addWidget(self.label)
        self.addWidget(self.slider)

    def changeSliderRange(self, slider_config):
        self.unit = slider_config[self.key]["unit"]

        self.slider.setValue(slider_config[self.key]["initial"])
        self.slider.setMinimum(slider_config[self.key]["minimum"])
        self.slider.setMaximum(slider_config[self.key]["maximum"])
        self.slider.setSingleStep(slider_config[self.key]["step"])
        self.scale = slider_config[self.key]["scale"]

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText("{} [{}]: {}".format(self.key, self.unit, value/self.scale))

class HorizontalLogarithmicParameterSlider(HorizontalParameterSlider):
    def changeSliderRange(self, slider_config):
        super().changeSliderRange(slider_config)
        self.base = slider_config[self.key]["base"]

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText("{} [{}]: {}".format(self.key, self.unit, int(self.base**(value/self.scale))))


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        global block_generation
        block_generation = True
        # The order of creation of widgets is important, some values must
        # be initialized before others
        self.step_slider = HorizontalParameterSlider(self, "Pas")
        self.interval_slider = HorizontalParameterSlider(self, "Plage")
        self.noise_slider = HorizontalLogarithmicParameterSlider(self, "SNR")
        self.parameter_sliders = [self.step_slider, self.interval_slider, self.noise_slider]

        self.fft = FFTDynamicCanvas(self, figsize=(8, 6), dpi=100)
        self.interferogram = InterferogramDynamicCanvas(self, figsize=(8, 6), dpi=100)

        self.HeNesource_radio = QtWidgets.QRadioButton("Source HeNe")
        self.HeNesource_radio.toggle()
        self.HeNesource_radio.toggled.connect(self.updateAll)
        self.whitesource_radio = QtWidgets.QRadioButton("Source de lumière blanche")
        self.whitesource_radio.toggled.connect(self.updateAll)
        self.radioLayout = QtWidgets.QHBoxLayout()
        self.radioLayout.addWidget(self.HeNesource_radio)
        self.radioLayout.addWidget(self.whitesource_radio)

        refresh_data_button = QtWidgets.QPushButton("Générer de nouvelles données")
        refresh_data_button.clicked.connect(self.updateFigures)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.interferogram)
        self.mainLayout.addWidget(self.fft)
        self.mainLayout.addLayout(self.step_slider)
        self.mainLayout.addLayout(self.interval_slider)
        self.mainLayout.addLayout(self.noise_slider)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addWidget(refresh_data_button)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("Effets des paramètres de l'interférogramme sur sa transformée de Fourier")


        self.updateSourceUsed()
        self.updateSlidersRanges()
        self.readSliderValues()

        block_generation = False
        self.updateFigures()

        for slider in self.parameter_sliders:
            slider.updateSliderLabel()

    def updateAll(self):
        self.updateSourceUsed()
        self.updateSlidersRanges()
        self.readSliderValues()
        self.updateFigures()

    def updateSourceUsed(self):
        if self.HeNesource_radio.isChecked():
            self.source = "HeNe"
        elif self.whitesource_radio.isChecked(): 
            self.source = "WhiteLight"
        else:
            raise ValueError("Unhandled error: one of the source type radio button is not handled")

    def updateSlidersRanges(self):
        for slider in self.parameter_sliders:
            slider.changeSliderRange(cfg.sources_sliders[self.source])

    def readSliderValues(self):
        self.interferogram_parameters = {
                "Pas": self.step_slider.slider.value()/self.step_slider.scale,
                "Plage": self.interval_slider.slider.value()/self.interval_slider.scale,
                "SNR": int(self.noise_slider.base**(self.noise_slider.slider.value()/self.noise_slider.scale))
            }

    def updateFigures(self):
        self.interferogram.generate_data()
        self.fft.compute_fft()
        self.interferogram.rescale_axis(cfg.interferogram_xaxis_limits[self.source], cfg.zoomed_interferogram_xaxis_limits[self.source])
        self.fft.rescale_axis(cfg.fft_xaxis_limits[self.source], cfg.zoomed_fft_xaxis_limits[self.source])


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
