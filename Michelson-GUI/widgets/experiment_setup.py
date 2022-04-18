from PyQt5 import QtCore, QtWidgets, QtGui

from .textbox import FloatWithUnitLayout, FloatTextBox


class ExperimentalSetupInformation(QtWidgets.QHBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets = []
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

        for i, name in enumerate(["Position absolue:", "Position relative:"]):
            cols[0].addWidget(QtWidgets.QLabel(name), 1)
            cols[1].addWidget(FloatTextBox(editable=False), 2)
            cols[2].addWidget(QtWidgets.QLabel("µm"))
            cols[3].addWidget(FloatTextBox(editable=False), 2)
            cols[4].addWidget(QtWidgets.QLabel("µm"))

        cols[0].addWidget(QtWidgets.QLabel("Facteur de calibration:"), 1)
        cols[1].addWidget(self.append_widget(FloatTextBox(editable=True)), 2)
        cols[2].addWidget(QtWidgets.QLabel(""))
        cols[3].addWidget(QtWidgets.QLabel(""), 2)
        cols[4].addWidget(QtWidgets.QLabel(""))

        for col in cols:
            self.addLayout(col)

        self.addWidget(self.append_widget(QtWidgets.QPushButton("Remettre position relative à 0")))

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget


class ExperimentalSetupConfiguration(QtWidgets.QVBoxLayout):
    def __init__(self, *args):
        super(QtWidgets.QVBoxLayout, self).__init__(*args)

        self.widgets = []

        radio_buttons_layout = QtWidgets.QVBoxLayout()
        radio_buttons_layout.addWidget(self.append_widget(QtWidgets.QRadioButton("Avancer")))
        radio_buttons_layout.addWidget(self.append_widget(QtWidgets.QRadioButton("Reculer")))
        radio_buttons_layout.addItem(QtWidgets.QSpacerItem(1, 10))

        self.optimize_checkbox = QtWidgets.QCheckBox("Optimiser le moyennage")
        self.optimize_checkbox.stateChanged.connect(self.toggleAverageTextBoxVisibility)
        radio_buttons_layout.addWidget(self.append_widget(self.optimize_checkbox))

        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.addWidget(QtWidgets.QLabel("Longueur d'un déplacement"))
        labels_layout.addWidget(QtWidgets.QLabel("Délai entre chaque déplacement"))
        labels_layout.addItem(QtWidgets.QSpacerItem(1, 10))
        labels_layout.addWidget(QtWidgets.QLabel("Nombre de mesures par donnée"))

        text_box_layout = QtWidgets.QVBoxLayout()
        text_box_layout.addLayout(self.append_layouts_widgets(FloatWithUnitLayout("µm")))
        text_box_layout.addLayout(self.append_layouts_widgets(FloatWithUnitLayout("ms")))
        text_box_layout.addItem(QtWidgets.QSpacerItem(1, 10))
        self.average_number_textbox = FloatTextBox(True, 0, 10, 0)
        text_box_layout.addWidget(self.append_widget(self.average_number_textbox), 2)

        move_controls = QtWidgets.QHBoxLayout()
        move_controls.addLayout(radio_buttons_layout, 1)
        move_controls.addLayout(labels_layout)
        move_controls.addLayout(text_box_layout, 1)


        self.addLayout(move_controls)

    def toggleAverageTextBoxVisibility(self):
        self.average_number_textbox.setEnabled(not self.optimize_checkbox.isChecked())

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget

    def append_layouts_widgets(self, layout):
        self.widgets += layout.widgets
        return layout

