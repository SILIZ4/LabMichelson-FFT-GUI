from struct import pack, unpack
import time
from warnings import warn

import serial


# Properties must be integers.
jog_settings = {
            "jog mode"    : 0x0002,  # move with steps
            "acceleration": 5,       # mm/s^2
            "min velocity": 0,       # always set to 0
            "max velocity": 0.1,     # mm/s
            "stop mode"   : 0x0002   # smooth stop
        }


class MotorTest:
    def __init__(self, *args):
        self.position = 0
        self.step = 0
        self._reference_point = 0


    def set_step_size(self, size):
        self.step = size


    def set_reference_point(self):
        self._reference_point = self.position


    def get_absolute_position(self):
        return self.position


    def get_relative_position(self):
        return self.position - self._reference_point


    def jog(self, forward):
        self.position += self.step if forward else -self.step


class Motor:
    """
    Object that sends to and receive data from a ThorLabs' motor.

    ThorLabs uses its own messaging protocol called APT. Thorlabs documentation is found here https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf
    This manual also present the available instructions for each type of motor and describes how they behave.
    Here, this docstring explains in summary how APT is used.

    Messages are a sequence of bits of varying length. They are sent via the "write" method of the "serial" object
    connected to the given motor USB port. They are created using Python's "struct.pack" function. The first argument
    of this function contains a format string in which each character represent the type of parameter in the sequence:
        'B': 8 bits;
        'H': 16-bit unsigned integer;
        'I': 32-bit signed integer.
    The complete list can be found at https://docs.python.org/3/library/struct.html. Because motors read little-endian
    values, the character '<' must be added in the format string.

    Ex: To send a message containing a 16-bit unsigned integer followed by a byte (8 bits), the format string is "<HB":
            struct.pack("<HB", ...)

    Types used in messages are described at page 39 of ThorLabs' documentation (as of Issue 30). The second argument
    of "struck.pack" is the list of values to store in the sequence (using the types of the format string).

    In the APT protocol, every message must start the ID of the instruction, a 16-bit unsigned integer ("H"). The
    other bits are optional: they depend on the instruction asked (read the instruction's description in the manual).

    The motors represents positions in their intrinsic integer unit which this class calls MU. The Motor class provides
    the conversion factors for each unit used.
    """

    unit_conversion = {
                # "ZST225B": { "MU/mm": 2008645.63, "MU/(mm/s)": 107824097.5, "MU/(mm/s^2)": 22097.3} Incorrect factor?
                # These values were calibrated manually
                "ZST225B": { "MU/um": 2008645.63/0.26886/1e3, "MU/(mm/s)": 107824097.5, "MU/(mm/s^2)": 22097.3}
            }

    def __init__(self, usb_port_location, motor_name):
        # Command Protol PDF can be found https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf

        self.unit_conversions = self.unit_conversion[motor_name]

        # Port Settings
        baud_rate = 115200
        data_bits = 8
        stop_bits = 1
        parity = serial.PARITY_NONE

        self.channel = 1 # Channel is always 1 for a K Cube/T Cube
        self.source = 0x01 # Source Byte
        self.destination = 0x50 # Destination byte; 0x50 for T Cube/K Cube, USB controllers

        self.communicator = serial.Serial(port=usb_port_location, baudrate=baud_rate, bytesize=data_bits,
                                            parity=parity, stopbits=stop_bits, timeout=0.1)

        # Get hardware info; MGMSG_HW_REQ_INFO; may be required by a K Cube to allow confirmation Rx messages
        self.communicator.write(pack('<HBBBB', 0x0005, 0x00, 0x00, 0x50, 0x01))
        self.flush()

        self.enable_stage()
        self.home()

        self.set_reference_point()


    def enable_stage(self):
        # Enable Stage; MGMSG_MOD_SET_CHANENABLESTATE
        self.communicator.write(pack('<HBBBB', 0x0210, self.channel, 0x01, self.destination, self.source))
        self._ensure_motor_received_instruction()
        self.flush()


    def disable_stage(self):
        # Disable Stage; MGMSG_MOD_SET_CHANENABLESTATE
        self.communicator.write(pack('<HBBBB', 0x0210, self.channel, 0x02, self.destination, self.source))
        self._ensure_motor_received_instruction()
        self.flush()


    def get_absolute_position(self):
        # Request Position; MGMSG_MOT_REQ_POSCOUNTER
        self.communicator.write(pack('<HBBBB', 0x0411, self.channel, 0x00, self.destination, self.source))

        # Read back position returned by the cube; Rx message MGMSG_MOT_GET_POSCOUNTER
        header, chan_dent, position_in_mu = unpack('<6sHI', self.communicator.read(12))
        return self.convert_MU_to_position(position_in_mu)


    def get_relative_position(self):
        return self.get_absolute_position() - self._reference_point


    def set_reference_point(self):
        self._reference_point = self.get_absolute_position()


    def set_reference_point_to(self, value):
        self._reference_point = value


    def home(self):
        # Home Stage; MGMSG_MOT_MOVE_HOME
        self.communicator.write(pack('<HBBBB', 0x0443, self.channel, 0x00, self.destination, self.source))

        # Wait until stage homed; MGMSG_MOT_MOVE_HOMED
        Rx = ''
        Homed = pack('<H',0x0444)
        while Rx != Homed:
            Rx = self.communicator.read(2)
        self.flush()


    def set_step_size(self, step_size):
        # Set job params; MGMSG_MOT_SET_JOGPARAMS
        self.communicator.write(pack('<HBBBBHHIIIIH', 0x0416, 0x16, 0x00, self.destination|0x80, self.source, self.channel,
                        jog_settings["jog mode"],
                        self.convert_position_to_MU(step_size),
                        self.convert_velocity_to_MU(jog_settings["min velocity"]),
                        self.convert_acceleration_to_MU(jog_settings["acceleration"]),
                        self.convert_velocity_to_MU(jog_settings["max velocity"]),
                        jog_settings["stop mode"]))
        self._ensure_motor_received_instruction()


    def jog(self, forward):
        # Do a jog; MGMSG_MOT_MOVE_JOG
        direction = 0x01 if forward else 0x02
        self.communicator.write(pack('<HBBBB', 0x046A, self.channel, direction, self.destination, self.source))
        self._ensure_motor_received_instruction()
        self.wait_until_move_completed()


    def move_to(self, position, relative=False):
        if relative:
            # Move to relative position; MGMSG_MOT_MOVE_RELATIVE (long version)
            self.communicator.write(pack('<HBBBBHI', 0x0448, 0x06, 0x00, self.destination|0x80, self.source, self.channel,
                              self.convert_position_to_MU(position)))
        else:
            # Move to absolute position; MGMSG_MOT_MOVE_ABSOLUTE (long version)
            self.communicator.write(pack('<HBBBBHI', 0x0453, 0x06, 0x00, self.destination|0x80, self.source, self.channel,
                              self.convert_position_to_MU(position)))

        self._ensure_motor_received_instruction()
        self.wait_until_move_completed()


    def wait_until_move_completed(self):
        Rx = ''
        Moved = pack('<H',0x0464)
        while Rx != Moved:
            # Check if moving; MGMSG_MOT_MOVE_COMPLETED
            Rx = self.communicator.read(2)
            time.sleep(0.1)


    def stop(self):
        # Stop any movement; MGMSG_MOT_MOVE_STOP
        self.communicator.write(pack('<HBBBB',0x0465, 0x02, self.channel, self.destination, self.source))


    def flush(self):
        self.communicator.flushInput()
        self.communicator.flushOutput()


    def convert_position_to_MU(self, position):
        """ position in um """
        return int(round(self.unit_conversions["MU/um"]*position))


    def convert_MU_to_position(self, position):
        """ position in um """
        return position/self.unit_conversions["MU/um"]


    def convert_velocity_to_MU(self, velocity):
        """ velocity in mm/s^2 """
        return int(round(self.unit_conversions["MU/(mm/s)"]*velocity))


    def convert_acceleration_to_MU(self, acceleration):
        """ acceleration in mm/s^2 """
        return int(round(self.unit_conversions["MU/(mm/s^2)"]*acceleration))


    def _ensure_motor_received_instruction(self):
        time.sleep(0.1)
