# -*- coding: utf-8 -*-
import sys
from math import ceil
from time import sleep

from PyQt5 import QtCore, QtWidgets

import config as cfg
from widgets.sliders import HorizontalParameterSlider, HorizontalLogarithmicParameterSlider
from widgets.figures import InterferogramDynamicCanvas, FFTDynamicCanvas
import widgets.figures


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        widgets.figures.block_generation = True
        # The order of creation of widgets is important, some values must
        # be initialized before others
        self.step_slider = HorizontalParameterSlider(self, "Pas")
        self.interval_slider = HorizontalParameterSlider(self, "Plage")
        self.noise_slider = HorizontalLogarithmicParameterSlider(self, "SNR")
        self.parameter_sliders = [self.step_slider, self.interval_slider, self.noise_slider]

        self.fft = FFTDynamicCanvas(self, figsize=(8, 6), dpi=100)
        self.interferogram = InterferogramDynamicCanvas(self, figsize=(8, 6), dpi=100)

        self.HeNesource_radio = QtWidgets.QRadioButton("Source HeNe")
        self.HeNesource_radio.toggle()
        self.HeNesource_radio.toggled.connect(self.updateAll)
        self.whitesource_radio = QtWidgets.QRadioButton("Source de lumière blanche")
        self.whitesource_radio.toggled.connect(self.updateAll)
        self.radioLayout = QtWidgets.QHBoxLayout()
        self.radioLayout.addWidget(self.HeNesource_radio)
        self.radioLayout.addWidget(self.whitesource_radio)
        fft_axis_toggle_button = QtWidgets.QPushButton("Longueurs d'onde/Fréquences")
        self.radioLayout.addWidget(fft_axis_toggle_button)

        refresh_data_button = QtWidgets.QPushButton("Générer de nouvelles données")
        refresh_data_button.clicked.connect(self.updateFigures)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.interferogram)
        self.mainLayout.addWidget(self.fft)
        self.mainLayout.addLayout(self.step_slider)
        self.mainLayout.addLayout(self.interval_slider)
        self.mainLayout.addLayout(self.noise_slider)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addLayout(self.radioLayout)
        self.mainLayout.addWidget(refresh_data_button)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("Effets des paramètres de l'interférogramme sur sa transformée de Fourier")

        fft_axis_toggle_button.clicked.connect(self.fft.toggle_xaxis_type)
        fft_axis_toggle_button.clicked.connect(self.updateFiguresAxis)
        fft_axis_toggle_button.clicked.connect(self.fft.draw_frame)


        self.updateSourceUsed()
        self.updateSlidersRanges()
        self.readSliderValues()

        widgets.figures.block_generation = False
        self.updateFigures()

        for slider in self.parameter_sliders:
            slider.updateSliderLabel()

    def updateAll(self):
        self.updateSourceUsed()
        self.updateSlidersRanges()
        self.readSliderValues()
        self.updateFigures()

    def updateSourceUsed(self):
        if self.HeNesource_radio.isChecked():
            self.source = "HeNe"
        elif self.whitesource_radio.isChecked(): 
            self.source = "WhiteLight"
        else:
            raise ValueError("Unhandled error: one of the source type radio button is not handled")

    def updateSlidersRanges(self):
        for slider in self.parameter_sliders:
            slider.changeSliderRange(cfg.sources_sliders[self.source])

    def readSliderValues(self):
        self.interferogram_parameters = {
                "Pas": self.step_slider.slider.value()/self.step_slider.scale,
                "Plage": self.interval_slider.slider.value()/self.interval_slider.scale,
                "SNR": int(self.noise_slider.base**(self.noise_slider.slider.value()/self.noise_slider.scale))
            }

    def updateFigures(self):
        self.interferogram.generate_data()
        self.fft.compute_fft()

        self.updateFiguresAxis()
        self.interferogram.draw_frame()
        self.fft.draw_frame()

    def updateFiguresAxis(self):
        self.interferogram.rescale_axis(cfg.interferogram_xaxis_limits[self.source], 
                cfg.zoomed_interferogram_xaxis_limits[self.source])
        self.fft.rescale_axis(cfg.fft_xaxis_limits[self.fft.xaxis_type][self.source],
                cfg.zoomed_fft_xaxis_limits[self.fft.xaxis_type][self.source])


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
