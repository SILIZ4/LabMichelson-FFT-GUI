# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from widgets.data_acquisition import DataAcquisitionLayout
from widgets.experiment_setup import ExperimentalSetupInformation, ExperimentalSetupConfiguration


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
        self.main_layout.addLayout(self.append_layouts_widgets(ExperimentalSetupInformation()))
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(self.append_layouts_widgets(ExperimentalSetupConfiguration()))
        self.main_layout.addWidget(LineSeparator())
        self.main_layout.addLayout(self.append_layouts_widgets(DataAcquisitionLayout(self.toggle_widgets)))

        self.setLayout(self.main_layout)
        self.setWindowTitle("Interface de contrôle du montage de Michelson")

    def append_layouts_widgets(self, layout):
        self.widgets += layout.widgets
        return layout

    def toggle_widgets(self):
        self.widgets_active = not self.widgets_active
        for widget in self.widgets:
            widget.setEnabled(self.widgets_active)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
