# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class FloatTextBox(QtWidgets.QLineEdit):
    def __init__(self, editable=True, minimum=1, maximum=100, decimals=2, default="", *args):
        super(QtWidgets.QLineEdit, self).__init__(*args)

        self.setText(default)
        self.setMaximumWidth(100)
        validator = QtGui.QDoubleValidator(decimals=decimals, notation=0)
        validator.setRange(minimum, maximum)
        self.setValidator(validator)
        self.setMinimumHeight(15)

        self.setReadOnly(not editable)


class FloatWithUnitLayout(QtWidgets.QHBoxLayout):
    def __init__(self, unit, minimum=1, maximum=100, decimals=2, editable=True, default="", *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.float_textbox = FloatTextBox(editable, minimum, maximum, decimals, default)
        self.addWidget(self.append_widget(self.float_textbox))
        self.addWidget(self.append_widget(QtWidgets.QLabel(unit)))


    def text(self):
        return self.float_textbox.text()


    def setText(self, *args):
        return self.float_textbox.setText(*args)


    def append_widget(self, widget):
        self.widgets_to_disable.append(widget)
        return widget
