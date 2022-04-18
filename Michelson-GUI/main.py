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

        self.widgets_to_disable = []
        self.widgets_active = True

        main_layout = QtWidgets.QVBoxLayout()

        self.setup_information = ExperimentalSetupInformation()
        main_layout.addLayout(self.append_layouts_widgets(self.setup_information))
        main_layout.addWidget(LineSeparator())
        main_layout.addLayout(self.append_layouts_widgets(ExperimentalSetupConfiguration()))
        main_layout.addWidget(LineSeparator())
        main_layout.addLayout(self.append_layouts_widgets(DataAcquisitionLayout(self.setup_information.get_setup_information, self.toggle_widgets)))

        self.setLayout(main_layout)
        self.setWindowTitle("Interface de contrôle du montage de Michelson")

    def append_layouts_widgets(self, layout):
        self.widgets_to_disable += layout.widgets_to_disable
        return layout

    def toggle_widgets(self):
        self.widgets_active = not self.widgets_active

        for widget in self.widgets_to_disable:
            widget.setEnabled(self.widgets_active)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
