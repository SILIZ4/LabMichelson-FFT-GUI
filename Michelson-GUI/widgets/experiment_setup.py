from PyQt5 import QtCore, QtWidgets, QtGui

from .textbox import FloatWithUnitLayout, FloatTextBox

import config


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, motor, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.update_functions = [self._get_and_display_position]
        self._motor = motor
        cols = [QtWidgets.QVBoxLayout() for i in range(4)]

        for i, col in enumerate(cols):
            label = ""
            if i == 1:
                label = "Moteur"
            elif i == 3:
                label = "Miroir"
            label = QtWidgets.QLabel(label)
            label.setAlignment(QtCore.Qt.AlignCenter)
            col.addWidget(label)

        self._relative_motor_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_relative_position()))
        cols[0].addWidget(QtWidgets.QLabel("Position relative:"), 1)
        cols[0].addWidget(QtWidgets.QLabel("Position absolue:"), 1)

        self._absolute_motor_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_absolute_position()))
        cols[1].addLayout(self._relative_motor_position_textbox, 2)
        cols[1].addLayout(self._absolute_motor_position_textbox, 2)

        self._relative_screw_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_relative_position()))
        cols[2].addWidget(QtWidgets.QLabel("Position relative:"), 1)
        cols[2].addWidget(QtWidgets.QLabel("Position absolue:"), 1)

        self._absolute_screw_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_absolute_position()))
        cols[3].addLayout(self._relative_screw_position_textbox, 2)
        cols[3].addLayout(self._absolute_screw_position_textbox, 2)

        cols[0].addWidget(QtWidgets.QLabel("Facteur de calibration:"))
        self._calibration_factor_textbox = FloatTextBox(editable=True, default=str(config.calibration_factor))
        cols[1].addWidget(self._append_widget(self._calibration_factor_textbox))
        for i, col in enumerate(cols):
            if i > 1:
                col.addWidget(QtWidgets.QLabel(""))


        for col in cols:
            self.addLayout(col)

        set_relative_position_button = QtWidgets.QPushButton("Fixer position de référence")
        set_relative_position_button.pressed.connect(self._set_motor_reference_point)
        self.addWidget(self._append_widget(set_relative_position_button))


    def _get_and_display_position(self):
        absolute_position = self._motor.get_absolute_position()
        relative_position = absolute_position - self._motor._reference_point

        self._display_positions(absolute_position, relative_position)


    def display_position(self, data, acquiring_data):
        if data is not None:
            motor_absolute_position = data["absolute positions"][-1]
            motor_relative_position = data["relative positions"][-1]

            self._display_positions(motor_absolute_position, motor_relative_position)


    def _display_positions(self, motor_absolute_position, motor_relative_position):
        calibration = float(self._calibration_factor_textbox.text())

        self._absolute_motor_position_textbox.setText( self.format_position(motor_absolute_position) )
        self._relative_motor_position_textbox.setText( self.format_position(motor_relative_position) )
        self._absolute_screw_position_textbox.setText( self.format_position(motor_absolute_position/calibration) )
        self._relative_screw_position_textbox.setText( self.format_position(motor_relative_position/calibration) )

    def format_position(self, position):
        return str( round(position, 2) )


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
        self._radio_move_forward = QtWidgets.QRadioButton("Avancer")
        self._radio_move_forward.setChecked(True)
        radio_buttons_layout.addWidget(self._append_widget(self._radio_move_forward))
        radio_buttons_layout.addWidget(self._append_widget(QtWidgets.QRadioButton("Reculer")))
        radio_buttons_layout.addItem(QtWidgets.QSpacerItem(1, 10))

        self.optimize_checkbox = QtWidgets.QCheckBox("Optimiser le moyennage")
        self.optimize_checkbox.stateChanged.connect(self._toggle_average_textbox)
        radio_buttons_layout.addWidget(self._append_widget(self.optimize_checkbox))

        spacer = QtWidgets.QSpacerItem(1, 10)
        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.addWidget(QtWidgets.QLabel("Taille des pas"))
        labels_layout.addWidget(QtWidgets.QLabel("Délai entre chaque pas"))
        labels_layout.addItem(spacer)
        labels_layout.addWidget(QtWidgets.QLabel("Mesures par pas"))

        self._textboxes_parameters = ["step size", "delay", "measure number"]
        self._textboxes = [
                    FloatWithUnitLayout("µm", default=str(config.motor_steps["default"]),
                                    minimum=config.motor_steps["min"], maximum=config.motor_steps["max"]),
                    FloatWithUnitLayout("ms", default=str(config.step_delay["default"]),
                                    minimum=config.step_delay["min"], maximum=config.step_delay["max"]),
                    FloatTextBox(editable=True, default="10", decimals=0)
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
        parameters = {"forward": self._radio_move_forward.isChecked()}
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
