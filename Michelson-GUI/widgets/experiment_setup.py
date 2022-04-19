from PyQt5 import QtCore, QtWidgets, QtGui

from .textbox import FloatWithUnitLayout, FloatTextBox


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, motor, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.update_functions = []
        self._motor = motor
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

        for name in ["Position absolue:", "Position relative:"]:
            cols[0].addWidget(QtWidgets.QLabel(name), 1)
            cols[1].addWidget(FloatTextBox(editable=False), 2)
            cols[2].addWidget(QtWidgets.QLabel("µm"))
            cols[3].addWidget(FloatTextBox(editable=False), 2)
            cols[4].addWidget(QtWidgets.QLabel("µm"))

        cols[0].addWidget(QtWidgets.QLabel("Facteur de calibration:"), 1)
        cols[1].addWidget(self._append_widget(FloatTextBox(editable=True)), 2)
        cols[2].addWidget(QtWidgets.QLabel(""))
        cols[3].addWidget(QtWidgets.QLabel(""), 2)
        cols[4].addWidget(QtWidgets.QLabel(""))

        for col in cols:
            self.addLayout(col)

        set_relative_position_button = QtWidgets.QPushButton("Remettre position relative à 0")
        set_relative_position_button.pressed.connect(self._set_motor_reference_point)
        self.addWidget(self._append_widget(set_relative_position_button))

    def _set_motor_reference_point(self):
        self._motor.set_reference_point()

    def _append_widget(self, widget):
        self.widgets_to_disable.append(widget)
        return widget


class ExperimentalSetupConfiguration(QtWidgets.QVBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.update_functions = []

        radio_buttons_layout = QtWidgets.QVBoxLayout()
        radio_buttons_layout.addWidget(self._append_widget(QtWidgets.QRadioButton("Avancer")))
        radio_buttons_layout.addWidget(self._append_widget(QtWidgets.QRadioButton("Reculer")))
        radio_buttons_layout.addItem(QtWidgets.QSpacerItem(1, 10))

        self.optimize_checkbox = QtWidgets.QCheckBox("Optimiser le moyennage")
        self.optimize_checkbox.stateChanged.connect(self._toggle_average_textbox)
        radio_buttons_layout.addWidget(self._append_widget(self.optimize_checkbox))

        spacer = QtWidgets.QSpacerItem(1, 10)
        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.addWidget(QtWidgets.QLabel("Taille d'un pas"))
        labels_layout.addWidget(QtWidgets.QLabel("Délai entre chaque pas"))
        labels_layout.addItem(spacer)
        labels_layout.addWidget(QtWidgets.QLabel("Nombre de mesures par pas"))

        self._textboxes_parameters = ["step size", "delay", "measure number"]
        self._textboxes = [
                    FloatWithUnitLayout("µm", default="1"),
                    FloatWithUnitLayout("ms", default="10"),
                    FloatTextBox(editable=True, decimals=0, default="10")
                ]
        text_box_layout = QtWidgets.QVBoxLayout()

        text_box_layout.addLayout(self._append_layouts_widgets(self._textboxes[0]))
        text_box_layout.addLayout(self._append_layouts_widgets(self._textboxes[1]))
        text_box_layout.addItem(spacer)
        text_box_layout.addWidget(self._append_widget(self._textboxes[2]), 2)

        move_controls = QtWidgets.QHBoxLayout()
        move_controls.addLayout(radio_buttons_layout, 1)
        move_controls.addLayout(labels_layout)
        move_controls.addLayout(text_box_layout, 1)


        self.addLayout(move_controls)

    def get_setup_information(self):
        parameters = {}
        for parameter, textbox in zip(self._textboxes_parameters, self._textboxes):
            parameters[parameter] = float(textbox.text())

        return parameters

    def _toggle_average_textbox(self):
        self._textboxes[2].setEnabled(not self.optimize_checkbox.isChecked())

    def _append_widget(self, widget):
        self.widgets_to_disable.append(widget)
        return widget

    def _append_layouts_widgets(self, layout):
        self.widgets_to_disable += layout.widgets_to_disable
        return layout
