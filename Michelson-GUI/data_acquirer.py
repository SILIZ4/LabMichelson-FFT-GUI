import time

import config


class DataAcquirer:
    """
    Acquires data by moving the motor and reading voltage

    Parameters required by the "acquire" method are:
     - "measure number"
     - "step size"
     - "delay"
    """
    def __init__(self, motor, voltmeter, get_acquirer_parameters_function):
        self._motor = motor
        self._voltmeter = voltmeter
        self._get_parameters = get_acquirer_parameters_function
        self._is_acquiring = False

        self.clear()


    def clear(self):
        self._voltages = []
        self._positions = []

    def acquire(self):
        """ Infinite loop that must be ran in a thread to be stopped via "stop". """
        if self._is_acquiring:
            return
        self._is_acquiring = True

        parameters = self._get_parameters()
        self._motor.set_step_size(parameters["step size"])
        measure_number = int(parameters["measure number"])

        while self._is_acquiring:
            self._motor.jog()
            self._positions.append( self._motor.get_current_position() )

            voltage_sum = 0
            for i in range(measure_number):
                voltage_sum += self._voltmeter.read()
                time.sleep(parameters["delay"]/1000)

            self._voltages.append(voltage_sum/measure_number)

    def stop(self):
        self._is_acquiring = False

    def is_acquiring(self):
        return self._is_acquiring

    def get_data(self):
        return {
                "positions": self._positions,
                "voltages": self._voltages
            }
