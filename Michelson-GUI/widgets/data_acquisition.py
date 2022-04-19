import os
import queue
import time
import json
from PyQt5 import QtCore, QtWidgets, QtGui

import config

from .interferogram import InterferogramDynamicCanvas


class DataAcquisitionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, motor, voltmeter, data_acquirer, toggle_widgets_function, toggle_refresh_function, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.update_functions = []
        self.widgets_to_disable = []
        self._acquiring = False

        self._interferogram = InterferogramDynamicCanvas(voltmeter)
        self._data_acquirer = data_acquirer
        data_acquirer.add_callback(self._interferogram.draw_frame)
        self.update_functions.append(self._interferogram.update_voltmeter)

        self.addWidget(self._interferogram)

        button_layout = QtWidgets.QHBoxLayout()
        self.acquire_data_button = QtWidgets.QPushButton("Acquérir des données")
        self.acquire_data_button.pressed.connect(self._change_button_text)
        self.acquire_data_button.pressed.connect(toggle_widgets_function)
        self.acquire_data_button.pressed.connect(toggle_refresh_function)
        self.acquire_data_button.pressed.connect(self._toggle_motor_state)  # starts infinite loop, must be called last

        save_button = QtWidgets.QPushButton("Enregistrer sous")
        save_button.pressed.connect(self.open_save_data_dialog)

        button_layout.setSpacing(20)
        button_layout.addWidget(self.acquire_data_button)
        button_layout.addWidget(save_button)
        self.widgets_to_disable.append(save_button)
        self.addLayout(button_layout)


    def open_save_data_dialog(self):
        file_path, extension = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                caption="Choisissez un emplacement pour les données", directory=os.path.expanduser("~"))

        if file_path != "":
            self.save_data(file_path)


    def save_data(self, file_path):
        with open(file_path, "w") as file_stream:
            file_stream.write(json.dumps(self._data_acquirer.get_data()))


    def _toggle_motor_state(self):
        self._acquiring = not self._acquiring

        if self._acquiring:
            self._data_acquirer.acquire()  # infinite loop
        else:
            self._data_acquirer.stop()
            self.save_data(os.path.join(os.path.expanduser("~"), "_tmp_michelson_data.json"))


    def _change_button_text(self):
        self.acquire_data_button.setText("Arrêter l'acquisition" if not self._acquiring else "Acquérir des données")
