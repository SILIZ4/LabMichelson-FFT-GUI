import sys
import matplotlib
import numpy
from math import ceil
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets, QtGui

from matplotlib import pyplot
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

        self.addWidget(RealValuesTextBox(editable, minimum, maximum))
        self.addWidget(QtWidgets.QLabel(unit))


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

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
        cols[1].addWidget(RealValuesTextBox(editable=True), 2)
        cols[2].addWidget(QtWidgets.QLabel(""))
        cols[3].addWidget(QtWidgets.QLabel(""), 2)
        cols[4].addWidget(QtWidgets.QLabel(""))

        for col in cols:
            self.addLayout(col)

        self.addWidget(QtWidgets.QPushButton("Remettre position relative à 0"))


class ExperimentalSetupConfiguration(QtWidgets.QVBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        radio_buttons_layout = QtWidgets.QVBoxLayout()
        radio_buttons_layout.addWidget(QtWidgets.QRadioButton("Avancer"))
        radio_buttons_layout.addWidget(QtWidgets.QRadioButton("Reculer"))
        radio_buttons_layout.addWidget(QtWidgets.QCheckBox("Optimiser le moyennage"))

        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.addWidget(QtWidgets.QLabel("Longueur d'un déplacement"))
        labels_layout.addWidget(QtWidgets.QLabel("Délai entre chaque déplacement"))
        labels_layout.addWidget(QtWidgets.QLabel("Nombre de mesures par donnée"))

        text_box_layout = QtWidgets.QVBoxLayout()
        text_box_layout.addLayout(RealValuesTextBoxLayout("µm"))
        text_box_layout.addLayout(RealValuesTextBoxLayout("s"))
        text_box_layout.addWidget(RealValuesTextBox(True, 0, 10, 0), 2)

        move_controls = QtWidgets.QHBoxLayout()
        move_controls.addLayout(radio_buttons_layout, 1)
        move_controls.addLayout(labels_layout)
        move_controls.addLayout(text_box_layout, 1)


        self.addLayout(move_controls)


class DataCollection(QtWidgets.QVBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.addWidget(InterferogramDynamicCanvas())
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(QtWidgets.QPushButton("Acquérir des données"))
        button_layout.addWidget(QtWidgets.QPushButton("Enregistrer"))
        button_layout.setSpacing(20)
        self.addLayout(button_layout)

class InterferogramDynamicCanvas(FigureCanvasQTAgg):
    def __init__(self, **kwargs):

        self.fig = Figure(**kwargs)

        self.ax = self.fig.subplots()
        self.ax.set_xlabel("Position du miroir[µm]")
        self.ax.set_ylabel("Voltage [-]")

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


class LineSeparator(QtWidgets.QFrame):
    def __init__(self, *args):
        super(QtWidgets.QFrame, self).__init__(*args)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(ExperimentalSetupInformation())
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(ExperimentalSetupConfiguration())
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(DataCollection())

        self.setLayout(self.main_layout)
        self.setWindowTitle("Interface de contrôle du montage de Michelson")


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
