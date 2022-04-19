import numpy as np
from matplotlib import patches, path, pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import matplotlib_config


class InterferogramDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, **kwargs):

        self.fig = Figure(**kwargs)

        self.ax = pyplot.subplot2grid((1, 12), (0, 0), colspan=11, fig=self.fig)
        self.ax.set_xlabel("Position du miroir[µm]")
        self.ax.set_ylabel("Voltage [-]")

        self.voltmeter_ax = pyplot.subplot2grid((1, 12), (0, 11), fig=self.fig)
        self.voltmeter_ax.set_ylim(0, 1)
        self.voltmeter_ax.yaxis.tick_right()
        self.voltmeter_ax.get_xaxis().set_visible(False)

        self.voltmeter = VoltmeterScreen(0.2)
        self.voltmeter_ax.add_artist(self.voltmeter.get_patch())


        self.line = Line2D([], [], color='#008080', ls='-')
        self.ax.add_line(self.line)

        self.ax.set_ylim(-1, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.fig.suptitle("Interférogramme")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.2)


    def _draw_frame(self, framedata):
        global interferogram_data
        self.line.set_data(interferogram_data)
        self._drawn_artists = [self.line]

    def rescale_axis(self, limits, zoomed_limits):
        self.ax.set_xlim(*limits)


class VoltmeterScreen:
    def __init__(self, value=0, maximum=1):
        self.value = value
        self.max = maximum
        self.vertices = np.array([[0, 0], [1, 0], [1, value], [0, value], [0, 0]])
        self.code = np.array([path.Path.MOVETO] + [path.Path.LINETO]*3 + [path.Path.CLOSEPOLY])

        self.cmap = pyplot.get_cmap("hsv")
        self.safe_zone = 0.8
        self.safe_zone_color = self.cmap(0.4)

        self.set_color()

    def get_patch(self, **kwargs):
        _path = path.Path(self.vertices, self.code)
        return patches.PathPatch(_path, color=self.color, **kwargs)

    def update(self, value):
        self.value = value
        self.vertices[2][1] = value
        self.vertices[3][1] = value
        self.set_color()

    def set_color(self):
        if self.value < self.safe_zone:
            self.color = self.safe_zone_color
        else:
            self.color = self.cmap( 0.4 * (1-self.value/self.max) )
