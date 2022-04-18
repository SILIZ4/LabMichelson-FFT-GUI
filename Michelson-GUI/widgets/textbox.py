# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class FloatTextBox(QtWidgets.QLineEdit):
    def __init__(self, editable=True, minimum=1, maximum=100, decimals=2, *args):
        super(QtWidgets.QLineEdit, self).__init__(*args)

        self.setMaximumWidth(100)
        validator = QtGui.QDoubleValidator(decimals=decimals, notation=0)
        validator.setRange(minimum, maximum)
        self.setValidator(validator)
        self.setMinimumHeight(15)

        self.setReadOnly(not editable)


class FloatWithUnitLayout(QtWidgets.QHBoxLayout):
    def __init__(self, unit, minimum=1, maximum=100, editable=True, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets = []
        self.addWidget(self.append_widget(FloatTextBox(editable, minimum, maximum)))
        self.addWidget(self.append_widget(QtWidgets.QLabel(unit)))

    def append_widget(self, widget):
        self.widgets.append(widget)
        return widget
