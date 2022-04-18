# -*- coding: utf-8 -*-
import sys, os
import matplotlib
import numpy
import subprocess
import datetime
from math import ceil
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets, QtGui

from matplotlib import patches, path, pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import config


class RealValuesTextBox(QtWidgets.QLineEdit):
    def __init__(self, editable=True, minimum=1, maximum=100, decimals=2, *args):
        super(QtWidgets.QLineEdit, self).__init__(*args)

        self.setMaximumWidth(100)
        validator = QtGui.QDoubleValidator(decimals=decimals, notation=0)
        validator.setRange(minimum, maximum)
        self.setValidator(validator)
        self.setMinimumHeight(15)

        self.setReadOnly(not editable)


class RealValuesTextBoxLayout(QtWidgets.QHBoxLayout):
    def __init__(self, unit, minimum=1, maximum=100, editable=True, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets = []
        self.addWidget(self.append_widget(RealValuesTextBox(editable, minimum, maximum)))
        self.addWidget(self.append_widget(QtWidgets.QLabel(unit)))

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets = []
        cols = [QtWidgets.QVBoxLayout() for i in range(5)]

        for i, col in enumerate(cols):
            label = ""
            if i == 1:
                label = "Vis"
            elif i == 3:
                label = "Miroir"
            label = QtWidgets.QLabel(label)
            label.setAlignment(QtCore.Qt.AlignCenter)
            col.addWidget(label)

        for i, name in enumerate(["Position absolue:", "Position relative:"]):
            cols[0].addWidget(QtWidgets.QLabel(name), 1)
            cols[1].addWidget(RealValuesTextBox(editable=False), 2)
            cols[2].addWidget(QtWidgets.QLabel("µm"))
            cols[3].addWidget(RealValuesTextBox(editable=False), 2)
            cols[4].addWidget(QtWidgets.QLabel("µm"))

        cols[0].addWidget(QtWidgets.QLabel("Facteur de calibration:"), 1)
        cols[1].addWidget(self.append_widget(RealValuesTextBox(editable=True)), 2)
        cols[2].addWidget(QtWidgets.QLabel(""))
        cols[3].addWidget(QtWidgets.QLabel(""), 2)
        cols[4].addWidget(QtWidgets.QLabel(""))

        for col in cols:
            self.addLayout(col)

        self.addWidget(self.append_widget(QtWidgets.QPushButton("Remettre position relative à 0")))

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget


class ExperimentalSetupConfiguration(QtWidgets.QVBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets = []

        radio_buttons_layout = QtWidgets.QVBoxLayout()
        radio_buttons_layout.addWidget(self.append_widget(QtWidgets.QRadioButton("Avancer")))
        radio_buttons_layout.addWidget(self.append_widget(QtWidgets.QRadioButton("Reculer")))
        radio_buttons_layout.addItem(QtWidgets.QSpacerItem(1, 10))

        self.optimize_checkbox = QtWidgets.QCheckBox("Optimiser le moyennage")
        self.optimize_checkbox.stateChanged.connect(self.toggleAverageTextBoxVisibility)
        radio_buttons_layout.addWidget(self.append_widget(self.optimize_checkbox))

        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.addWidget(QtWidgets.QLabel("Longueur d'un déplacement"))
        labels_layout.addWidget(QtWidgets.QLabel("Délai entre chaque déplacement"))
        labels_layout.addItem(QtWidgets.QSpacerItem(1, 10))
        labels_layout.addWidget(QtWidgets.QLabel("Nombre de mesures par donnée"))

        text_box_layout = QtWidgets.QVBoxLayout()
        text_box_layout.addLayout(self.append_layouts_widgets(RealValuesTextBoxLayout("µm")))
        text_box_layout.addLayout(self.append_layouts_widgets(RealValuesTextBoxLayout("ms")))
        text_box_layout.addItem(QtWidgets.QSpacerItem(1, 10))
        self.average_number_textbox = RealValuesTextBox(True, 0, 10, 0)
        text_box_layout.addWidget(self.append_widget(self.average_number_textbox), 2)

        move_controls = QtWidgets.QHBoxLayout()
        move_controls.addLayout(radio_buttons_layout, 1)
        move_controls.addLayout(labels_layout)
        move_controls.addLayout(text_box_layout, 1)


        self.addLayout(move_controls)

    def toggleAverageTextBoxVisibility(self):
        self.average_number_textbox.setEnabled(not self.optimize_checkbox.isChecked())

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget

    def append_layouts_widgets(self, layout):
        self.widgets += layout.widgets
        return layout


class DataCollection(QtWidgets.QVBoxLayout):
    def __init__(self, window_parent, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets = []

        self.addWidget(InterferogramDynamicCanvas())

        button_layout = QtWidgets.QHBoxLayout()
        self.collect_data_button = QtWidgets.QPushButton("Acquérir des données")
        self.collect_data_button.pressed.connect(window_parent.enable_all_widgets_toggle)
        self.collect_data_button.pressed.connect(self.change_text)
        self.collecting_data = False
        button_layout.addWidget(self.collect_data_button)

        save_button = QtWidgets.QPushButton("Enregistrer sous")
        save_button.pressed.connect(self.save_data)
        self.widgets.append(save_button)
        button_layout.addWidget(save_button)
        button_layout.setSpacing(20)

        self.addLayout(button_layout)

    def save_data(self, directory='', forOpen=True, fmt='', isFolder=False):
        self.file_path = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                caption="Choisissez un emplacement pour les données", directory=os.getcwd())

    def change_text(self):
        self.collecting_data = not self.collecting_data
        if self.collecting_data:
            text = "Arrêter l'acquisition"
        else:
            text = "Acquérir des données"
        self.collect_data_button.setText(text)


class InterferogramDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, **kwargs):

        self.fig = Figure(**kwargs)

        self.ax = matplotlib.pyplot.subplot2grid((1, 12), (0, 0), colspan=11, fig=self.fig)
        self.ax.set_xlabel("Position du miroir[µm]")
        self.ax.set_ylabel("Voltage [-]")

        self.voltmeter_ax = matplotlib.pyplot.subplot2grid((1, 12), (0, 11), fig=self.fig)
        self.voltmeter_ax.set_ylim(0, 1)
        self.voltmeter_ax.yaxis.tick_right()
        self.voltmeter_ax.get_xaxis().set_visible(False)

        self.voltmeter = Voltmeter(0.2)
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


class Voltmeter:
    def __init__(self, value=0, maximum=1):
        self.value = value
        self.max = maximum
        self.vertices = numpy.array([[0, 0], [1, 0], [1, value], [0, value], [0, 0]])
        self.code = numpy.array([path.Path.MOVETO] + [path.Path.LINETO]*3 + [path.Path.CLOSEPOLY])

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


class LineSeparator(QtWidgets.QFrame):
    def __init__(self, *args):
        super(QtWidgets.QFrame, self).__init__(*args)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        self.widgets = []
        self.widgets_active = True

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.append_layous_widgets(ExperimentalSetupInformation()))
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(self.append_layous_widgets(ExperimentalSetupConfiguration()))
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(self.append_layous_widgets(DataCollection(self)))

        self.setLayout(self.main_layout)
        self.setWindowTitle("Interface de contrôle du montage de Michelson")

    def append_layous_widgets(self, layout):
        self.widgets += layout.widgets
        return layout

    def enable_all_widgets_toggle(self):
        self.widgets_active = not self.widgets_active
        for widget in self.widgets:
            widget.setEnabled(self.widgets_active)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
