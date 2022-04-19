from PyQt5 import QtCore, QtWidgets, QtGui

from .textbox import FloatWithUnitLayout, FloatTextBox


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, motor, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.update_functions = [self._get_and_display_position]
        self._motor = motor
        cols = [QtWidgets.QVBoxLayout() for i in range(2)]

        self._relative_motor_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_relative_position()))
        cols[0].addWidget(QtWidgets.QLabel("Position relative:"), 1)
        cols[0].addWidget(QtWidgets.QLabel("Position absolue:"), 1)

        self._absolute_motor_position_textbox = FloatWithUnitLayout("µm", editable=False, default=str(motor.get_absolute_position()))
        cols[1].addLayout(self._relative_motor_position_textbox, 2)
        cols[1].addLayout(self._absolute_motor_position_textbox, 2)

        for col in cols:
            self.addLayout(col)

        set_relative_position_button = QtWidgets.QPushButton("Fixer position de référence")
        set_relative_position_button.pressed.connect(self._set_motor_reference_point)
        self.addWidget(self._append_widget(set_relative_position_button))


    def _get_and_display_position(self):
        absolute_position = self._motor.get_absolute_position()
        self._absolute_motor_position_textbox.setText(str(absolute_position))
        self._relative_motor_position_textbox.setText(str(absolute_position-self._motor._reference_point))


    def display_position(self, data, acquiring_data):
        if data is not None:
            self._absolute_motor_position_textbox.setText(str(data["absolute positions"][-1]))
            self._relative_motor_position_textbox.setText(str(data["relative positions"][-1]))


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
                    FloatWithUnitLayout("µm", default="1", minimum=0.1, maximum=2),
                    FloatWithUnitLayout("ms", default="10", minimum=1, maximum=50),
                    FloatTextBox(editable=True, default="10", minimum=0, maximum=100, decimals=0)
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
