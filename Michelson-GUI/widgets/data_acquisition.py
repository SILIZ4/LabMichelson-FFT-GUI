import os
import queue
import threading
import json
from PyQt5 import QtCore, QtWidgets, QtGui

import config

from .interferogram import InterferogramDynamicCanvas
from data_acquirer import DataAcquirer


class DataAcquisitionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, motor, voltmeter, get_setup_parameters_function, toggle_widgets_function, toggle_refresh_function, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.update_functions = []
        self.widgets_to_disable = []
        self._acquiring = False
        self._thread = None

        self._interferogram = InterferogramDynamicCanvas(voltmeter)
        self._data_acquirer = DataAcquirer(motor, voltmeter, get_setup_parameters_function, self._interferogram.draw_frame)
        self.update_functions.append(self._interferogram.update_voltmeter)

        self.addWidget(self._interferogram)

        button_layout = QtWidgets.QHBoxLayout()
        self.acquire_data_button = QtWidgets.QPushButton("Acquérir des données")
        self.acquire_data_button.pressed.connect(toggle_refresh_function)
        self.acquire_data_button.pressed.connect(self._toggle_motor_state)
        self.acquire_data_button.pressed.connect(toggle_widgets_function)
        self.acquire_data_button.pressed.connect(self._change_button_text)

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
            file_stream.write(json.dumps(self._data_acquirer.get_data(), indent=4))

    def _toggle_motor_state(self):
        self._acquiring = not self._acquiring

        if self._acquiring:
            if self._thread is None:
                self._thread = threading.Thread(target=self._data_acquirer.acquire)
                self._thread.start()
        else:
            if self._thread is not None:
                self._data_acquirer.stop()
                self._thread.join()
                self._thread = None
            self.save_data(os.path.join(os.path.expanduser("~"), "_tmp_michelson_savedata.json"))

    def _change_button_text(self):
        self.acquire_data_button.setText("Arrêter l'acquisition" if self._acquiring else "Acquérir des données")
