# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets


class HorizontalParameterSlider(QtWidgets.QHBoxLayout):
    def __init__(self, parent_window, parameter_key, *args):
        super(QtWidgets.QHBoxLayout, self).__init__(*args)

        self.parent_window = parent_window
        self.key = parameter_key
        self.scale = 1
        self.base = 1

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(parent_window.readSliderValues)
        self.slider.valueChanged.connect(self.updateSliderLabel)
        self.slider.valueChanged.connect(parent_window.updateFigures)

        self.label = QtWidgets.QLabel()

        self.addWidget(self.label)
        self.addWidget(self.slider)

    def changeSliderRange(self, slider_config):
        self.unit = slider_config[self.key]["unit"]

        self.slider.setValue(slider_config[self.key]["initial"])
        self.slider.setMinimum(slider_config[self.key]["minimum"])
        self.slider.setMaximum(slider_config[self.key]["maximum"])
        self.slider.setSingleStep(slider_config[self.key]["step"])
        self.scale = slider_config[self.key]["scale"]

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText("{} [{}]: {}".format(self.key, self.unit, value/self.scale))

class HorizontalLogarithmicParameterSlider(HorizontalParameterSlider):
    def changeSliderRange(self, slider_config):
        super().changeSliderRange(slider_config)
        self.base = slider_config[self.key]["base"]

    def updateSliderLabel(self):
        value = self.slider.value()
        self.label.setText("{} [{}]: {}".format(self.key, self.unit, int(self.base**(value/self.scale))))
