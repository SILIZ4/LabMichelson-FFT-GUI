import sys
import matplotlib
import numpy
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import TimedAnimation
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class AnimatedCanvas(FigureCanvasQTAgg, TimedAnimation):
    def __init__(self, parent_window, **kwargs):
        self.previous_parameters = parent_window.fft_parameters.copy()
        self.parent_window = parent_window

        self.fig = Figure(**kwargs)
        ax = self.fig.add_subplot(111)

        ax.set_xlabel('x axis')
        ax.set_ylabel('y axis')
        self.line = Line2D([], [], color='#008080', ls='-', marker='o')
        ax.add_line(self.line)
        ax.set_xlim(-100, 100)
        ax.set_ylim(0, 50)

        FigureCanvasQTAgg.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100, blit=True)

        self.data = [[], []]

    def new_frame_seq(self):
        return iter(range(10))

    def _draw_frame(self, framedata):

        if self.previous_parameters != self.parent_window.fft_parameters:
            self.data = numpy.random.rand(5)*100-50, numpy.random.rand(5)*50

            self.previous_parameters = self.parent_window.fft_parameters.copy()

        self.line.set_data(self.data)
        self._drawn_artists = [self.line]

    def _init_draw(self):
        lines = [self.line]
        for l in lines:
            l.set_data([], [])

class HorizontalParameterSlider(QtWidgets.QHBoxLayout):
    def __init__(self, parent_window, parameter_key, minValue=0, maxValue=10, step=1, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.parent_window = parent_window
        self.key = parameter_key

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(parent_window.fft_parameters[self.key])
        self.slider.setMinimum(minValue)
        self.slider.setMaximum(maxValue)
        self.slider.setSingleStep(step)
        self.slider.valueChanged.connect(self.updateSliderLabel)

        self.label = QtWidgets.QLabel()
        self.label.setText(self.key+": "+str(minValue))

        self.addWidget(self.label)
        self.addWidget(self.slider)

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText(self.key+": "+str(value))
        self.parent_window.fft_parameters[self.key] = value


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)
        self.fft_parameters = {"Step": 0, "Interval": 10, "Noise": 1}

        self.step_slider = HorizontalParameterSlider(self, "Step")
        self.interval_slider = HorizontalParameterSlider(self, "Interval")
        self.noise_slider = HorizontalParameterSlider(self, "Noise")

        self.canvas = AnimatedCanvas(self, figsize=(5, 4), dpi=100)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.canvas)
        self.mainLayout.addLayout(self.step_slider)
        self.mainLayout.addLayout(self.interval_slider)
        self.mainLayout.addLayout(self.noise_slider)

        self.setLayout(self.mainLayout)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
