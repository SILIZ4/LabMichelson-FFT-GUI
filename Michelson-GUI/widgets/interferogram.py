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

        self._ax_absolute = pyplot.subplot2grid((1, 12), (0, 0), colspan=11, fig=self.fig)
        self._ax_relative = self._ax_absolute.twiny()  # Contains invisible line that shows relative positions

        self._voltage_absolute = Line2D([], [], color='#008080', ls='-', marker=".", clip_on=True)
        self._ax_absolute.add_line(self._voltage_absolute)
        self._position_cursor = self._ax_absolute.axvline(0, color=matplotlib_config.midblack, ls="--", lw=2)

        self._ax_absolute.set_xlabel("Position absolue [µm]")
        self._ax_absolute.set_ylabel("Voltage [-]")
        self._ax_absolute.set_ylim(-1, 1)

        self._voltage_relative = Line2D([], [], ls='')
        self._ax_relative.add_line(self._voltage_relative)
        self._ax_relative.set_xlabel("Position relative [µm]")

        self._voltmeter_ax = pyplot.subplot2grid((1, 12), (0, 11), fig=self.fig)
        self._voltmeter_ax.set_ylim(0, 1)
        self._voltmeter_ax.yaxis.tick_right()
        self._voltmeter_ax.get_xaxis().set_visible(False)

        self._voltmeter_screen = VoltmeterScreen(0.2)
        for p in self._voltmeter_screen.get_patches():
            self._voltmeter_ax.add_patch(p)

        self.fig.tight_layout()
        FigureCanvasQTAgg.__init__(self, self.fig)


    def update_voltmeter(self):
        self._voltmeter_screen.update(self._voltmeter.read())
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def draw_frame(self, data, acquiring):
        if data is None:
            return

        absolute_positions = data["absolute positions"]
        relative_positions = data["relative positions"]
        voltages = data["voltages"]

        self._voltmeter_screen.update(voltages[-1])
        self._position_cursor.set_xdata(absolute_positions[-1]) # line plotted on absolute axis

        if acquiring:
            self._voltage_absolute.set_data([absolute_positions, voltages])
            self._voltage_relative.set_data([relative_positions, voltages])

            self._rescale_xaxis(self._ax_absolute, absolute_positions)
            self._rescale_xaxis(self._ax_relative, relative_positions)

        else: # Display motor position on figure if no data collected
            self._rescale_xaxis_if_out_of_range(self._ax_absolute, absolute_positions[-1])
            self._rescale_xaxis_if_out_of_range(self._ax_relative, relative_positions[-1])

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    @staticmethod
    def _rescale_xaxis(ax, data):
        min_value, max_value = min(data), max(data)

        if min_value != max_value:
            ax.set_xlim((min_value, max_value))


    @staticmethod
    def _rescale_xaxis_if_out_of_range(ax, point):
        xlim = ax.get_xlim()
        min_value = min([xlim[0], point])
        max_value = max([xlim[1], point])

        if min_value != max_value:
            ax.set_xlim((min_value, max_value))


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
