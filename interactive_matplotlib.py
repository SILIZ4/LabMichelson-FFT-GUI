import sys
import matplotlib
import numpy
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import TimedAnimation
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class AnimatedCanvas(FigureCanvasQTAgg, TimedAnimation):

    def __init__(self, **kwargs):
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

    def new_frame_seq(self):
        return iter(range(10))

    def _draw_frame(self, framedata):
        self.line.set_data(numpy.random.rand(5)*100-50, numpy.random.rand(5)*50)
        self._drawn_artists = [self.line]

    def _init_draw(self):
        lines = [self.line]
        for l in lines:
            l.set_data([], [])


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = AnimatedCanvas(figsize=(5, 4), dpi=100)
        self.setCentralWidget(self.canvas)



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
