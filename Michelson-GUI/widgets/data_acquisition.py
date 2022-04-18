import os
from PyQt5 import QtCore, QtWidgets, QtGui

from .interferogram import InterferogramDynamicCanvas


class DataAcquisitionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, toggle_widgets_function, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets = []

        self.addWidget(InterferogramDynamicCanvas())

        button_layout = QtWidgets.QHBoxLayout()
        self.collect_data_button = QtWidgets.QPushButton("Acquérir des données")
        self.collect_data_button.pressed.connect(toggle_widgets_function)
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
