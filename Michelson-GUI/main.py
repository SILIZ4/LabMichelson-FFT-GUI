# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from widgets.data_acquisition import DataAcquisitionLayout
from widgets.experiment_setup import ExperimentalSetupInformation, ExperimentalSetupConfiguration

from motor import MotorTest
from voltmeter import Voltmeter
import config


class LineSeparator(QtWidgets.QFrame):
    def __init__(self, *args):
        super(QtWidgets.QFrame, self).__init__(*args)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        self.widgets_to_disable = []
        self.update_functions = []
        self.widgets_active = True

        self.motor = MotorTest(config.motor_usb_port, config.motor_name)
        self.voltmeter = Voltmeter(config.voltmeter_usb_port)

        main_layout = QtWidgets.QVBoxLayout()

        self.addLayout(main_layout, ExperimentalSetupInformation(self.motor))

        setup_config = ExperimentalSetupConfiguration()
        main_layout.addWidget(LineSeparator())
        self.addLayout(main_layout, setup_config)

        data_acquisition = DataAcquisitionLayout(self.motor, self.voltmeter, setup_config.get_setup_information, self._toggle_widgets, self._toggle_refresh)
        main_layout.addWidget(LineSeparator())
        self.addLayout(main_layout, data_acquisition)

        self.setLayout(main_layout)
        self.setWindowTitle("Interface de contrôle du montage de Michelson")

        self._refreshing_display = True
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self._refresh_display)
        self.update_timer.start()


    def addLayout(self, main_layout, layout, *args):
        main_layout.addLayout(layout, *args)
        self.update_functions += layout.update_functions
        self.widgets_to_disable += layout.widgets_to_disable


    def _toggle_refresh(self):
        if self._refreshing_display:
            self.update_timer.stop()
        else:
            self.update_timer.start()

        self._refreshing_display = not self._refreshing_display


    def _toggle_widgets(self):
        self.widgets_active = not self.widgets_active

        for widget in self.widgets_to_disable:
            widget.setEnabled(self.widgets_active)


    def _refresh_display(self):
        for update in self.update_functions:
            update()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
