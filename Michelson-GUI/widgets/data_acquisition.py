import os
from PyQt5 import QtCore, QtWidgets, QtGui

from motor import Motor
import config
from .interferogram import InterferogramDynamicCanvas


class DataAcquisitionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, get_motor_parameters_function, toggle_widgets_function, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self._motor_moving = False
        #self._motor = Motor(config.usb_port, config.motor_name)
        self.get_motor_parameters = get_motor_parameters_function

        self.addWidget(InterferogramDynamicCanvas())

        button_layout = QtWidgets.QHBoxLayout()
        self.acquire_data_button = QtWidgets.QPushButton("Acquérir des données")
        self.acquire_data_button.pressed.connect(self._toggle_motor_state)
        self.acquire_data_button.pressed.connect(toggle_widgets_function)
        self.acquire_data_button.pressed.connect(self._change_button_text)

        save_button = QtWidgets.QPushButton("Enregistrer sous")
        save_button.pressed.connect(self.save_data)

        button_layout.setSpacing(20)
        button_layout.addWidget(self.acquire_data_button)
        button_layout.addWidget(save_button)
        self.widgets_to_disable.append(save_button)
        self.addLayout(button_layout)

    def save_data(self, directory='', forOpen=True, fmt='', isFolder=False):
        file_path = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                caption="Choisissez un emplacement pour les données", directory=os.path.expanduser("~"))
        print(f"save data into \"{file_path}\"")

    def _toggle_motor_state(self):
        self._motor_moving = not self._motor_moving

        if self._motor_moving:
            print("start motor")
        else:
            print("stop motor")

    def _change_button_text(self):
        self.acquire_data_button.setText("Arrêter l'acquisition" if self._motor_moving else "Acquérir des données")
