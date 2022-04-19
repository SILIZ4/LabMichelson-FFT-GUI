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
        self._callbacks = []
        self._is_acquiring = False

        self.clear()


    def add_callback(self, callback):
        self._callbacks.append(callback)


    def clear(self):
        self._voltages = []
        self._positions = []


    def acquire(self):
        """ Infinite loop that must be ran in a thread to be stopped via "stop". """
        if self._is_acquiring:
            return
        self._is_acquiring = True

        parameters = self._get_parameters()
        data = None

        self._motor.set_step_size(parameters["step size"])
        measure_number = int(parameters["measure number"])
        delay = parameters["delay"]/1000
        move_forward = bool(parameters["forward"])

        acquire_data = measure_number > 0

        while self._is_acquiring:
            if acquire_data:
                self._positions.append( self._motor.get_current_position() )
                self._voltages.append(self._measure_average_voltage(measure_number, delay))

                data = self.get_data()
            else:
                data = {"positions": [self._motor.get_current_position()], "voltages": [self._voltmeter.read()]}

            for callback in self._callbacks:
                callback(data, acquire_data)
            self._motor.jog(move_forward)


    def stop(self):
        self._is_acquiring = False


    def is_acquiring(self):
        return self._is_acquiring


    def get_data(self):
        return {
                "positions": self._positions,
                "voltages": self._voltages
            }


    def _measure_average_voltage(self, measure_number, delay):
        voltage_sum = 0
        for i in range(measure_number):
            voltage_sum += self._voltmeter.read()
            time.sleep(delay)
        return voltage_sum/measure_number
