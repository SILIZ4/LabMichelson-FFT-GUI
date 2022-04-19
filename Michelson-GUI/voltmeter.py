import numpy as np


class Voltmeter:
    def __init__(self, usb_port):
        self.t = 0.05
        pass


    def read(self):
        self.t += 0.05
        return np.sin(self.t)
