# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class FloatTextBox(QtWidgets.QLineEdit):
    def __init__(self, editable=True, minimum=None, maximum=None, decimals=2, default="", *args):
        super(QtWidgets.QLineEdit, self).__init__(*args)

        self.setText(default)
        self.setMaximumWidth(100)

        validator = QtGui.QDoubleValidator(decimals=decimals, notation=0)
        self.minimum = minimum
        self.maximum = maximum

        self.editingFinished.connect(self.validate)
        self.setValidator(validator)
        self.setMinimumHeight(20)

        self.setReadOnly(not editable)


    def validate(self):
        _value = self.text()

        if _value == '':
            self.setText(str(self.minimum))
        else:
            value = float(_value)
            if self.minimum is not None and value < self.minimum:
                self.setText(str(self.minimum))
            if self.maximum is not None and value > self.maximum:
                self.setText(str(self.maximum))


class FloatWithUnitLayout(QtWidgets.QHBoxLayout):
    def __init__(self, unit, editable=True, minimum=None, maximum=None, decimals=2, default="", *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.widgets_to_disable = []
        self.float_textbox = FloatTextBox(editable=editable, minimum=minimum, maximum=maximum,
                                            decimals=decimals, default=default, *args)
        self.addWidget(self.append_widget(self.float_textbox))
        self.addWidget(self.append_widget(QtWidgets.QLabel(unit)))


    def text(self):
        return self.float_textbox.text()


    def setText(self, *args):
        return self.float_textbox.setText(*args)


    def append_widget(self, widget):
        self.widgets_to_disable.append(widget)
        return widget
