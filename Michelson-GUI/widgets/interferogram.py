import numpy as np
from matplotlib import patches, pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import matplotlib_config


class InterferogramDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, voltmeter, **kwargs):

        self._voltmeter = voltmeter

        self.fig = Figure(**kwargs)

        self._ax = pyplot.subplot2grid((1, 12), (0, 0), colspan=11, fig=self.fig)
        self._ax.set_xlabel("Position du miroir[µm]")
        self._ax.set_ylabel("Voltage [-]")

        self._voltmeter_ax = pyplot.subplot2grid((1, 12), (0, 11), fig=self.fig)
        self._voltmeter_ax.set_ylim(0, 1)
        self._voltmeter_ax.yaxis.tick_right()
        self._voltmeter_ax.get_xaxis().set_visible(False)

        self._voltmeter_screen = VoltmeterScreen(0.2)
        for p in self._voltmeter_screen.get_patches():
            self._voltmeter_ax.add_patch(p)


        self._line = Line2D([], [], color='#008080', ls='-', marker=".", clip_on=True)
        self._ax.add_line(self._line)

        self._ax.set_ylim(-1, 1)

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.fig.suptitle("Interférogramme")
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.85, bottom=0.2)


    def update_voltmeter(self):
        self._voltmeter_screen.update(self._voltmeter.read())
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def draw_frame(self, data):
        if len(data["positions"]) == 0:
            return

        self._voltmeter_screen.update(data["voltages"][-1])
        self._line.set_data([data["positions"], data["voltages"]])
        self._drawn_artists = [self._line]

        position_min, position_max = min(data["positions"]), max(data["positions"])

        if len(data["positions"]) > 1:
            self._ax.set_xlim((position_min, position_max))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class VoltmeterScreen:
    ok_color = "#68b858"
    warning_color = "#F8D839"
    clipping_color = "#C94E4E"

    cursor_width = .02

    def __init__(self, value=0, maximum=1):
        self.warning_threshold = .7*maximum
        self.clipping_threshold = .9*maximum
        self.max = maximum

        self.cursor = patches.Rectangle((0, abs(value)+self.cursor_width/2), 1, self.cursor_width, color=matplotlib_config.midblack)

    def get_patches(self, **kwargs):
        return [
                patches.Rectangle((0, 0), 1, self.warning_threshold, color=self.ok_color),
                patches.Rectangle((0, self.warning_threshold), 1, self.clipping_threshold-self.warning_threshold, color=self.warning_color),
                patches.Rectangle((0, self.clipping_threshold), 1, self.max-self.warning_threshold, color=self.clipping_color),
                self.cursor
            ]

    def update(self, value):
        self.cursor.set_xy((0, abs(value)+self.cursor_width/2))
