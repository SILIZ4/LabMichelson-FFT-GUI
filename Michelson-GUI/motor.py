from struct import pack, unpack
import serial
import time
from warnings import warn


# Properties must be integers.
jog_settings = {
            "jog mode"    : 0x0002,  # move with steps
            "acceleration": 5,       # mm/s^2
            "min velocity": 0,       # always set to 0
            "max velocity": 0.1,     # mm/s
            "stop mode"   : 0x0002   # smooth stop
        }


class Motor:
    """
    Object that sends to and receive data from a ThorLabs' motor.

    ThorLabs uses it's own messaging protocol called APT. This protocol is described here https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf
    This manual also present the available instructions for each type of motor and describes how they behave.
    Here, we explain in summary how it works.

    Messages are a sequence of bits of varying length. They are sent via the "write" method of the "serial" object
    connected to the given motor USB port.

    To create a message, we use Python's "struct.pack" function. The first argument contains a format string in
    which each character represent the type of parameter. "B" stands for 8 bits, "H" for 16-bit unsigned integer
    and "I" for a 32-bit signed integer. Complete list can be found at https://docs.python.org/3/library/struct.html
    Because motors read little-endian values, the character '<' must be added in the format string. If we want
    to send a message containing a 16-bit unsigned integer followed by a byte (8 bits), we use "<HB" as the format
    string:

        struct.pack("<HB", ...)

    Types used in messages are described at page 39 of ThorLabs' documentation (as of Issue 30). The second argument
    of "struck.pack" is the list of values to store in the sequence (using the types of the format string).

    In the APT protocol, every message must start the ID of the instruction, a 16-bit unsigned integer ("H"). The
    other bits are optional: they depend on the instruction asked (read the instruction's description in the manual).

    The motors represents positions in their intrinsic integer unit which we call MU. The motor class provides the
    conversion factors for each unit used.
    """

    unit_conversion = {
                # "ZST225B": { "MU/mm": 2008645.63, "MU/(mm/s)": 107824097.5, "MU/(mm/s^2)": 22097.3} Incorrect factor?
                "ZST225B": { "MU/mm": 2008645.63/0.26886, "MU/(mm/s)": 107824097.5/0.26886, "MU/(mm/s^2)": 22097.3/0.26886}
            }

    def __init__(self, usb_port_location, motor_name):
        # Command Protol PDF can be found https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf

        self.unit_conversions = self.unit_conversion[motor_name]

        # Port Settings
        baud_rate = 115200
        data_bits = 8
        stop_bits = 1
        parity = serial.PARITY_NONE

        self.channel = 1 #Channel is always 1 for a K Cube/T Cube
        self.source = 0x01 #Source Byte
        self.destination = 0x50 #Destination byte; 0x50 for T Cube/K Cube, USB controllers

        self.communicator = serial.Serial(port=usb_port_location, baudrate=baud_rate, bytesize=data_bits, parity=parity, stopbits=stop_bits, timeout=0.1)

        # Get hardware info; MGMSG_HW_REQ_INFO; may be required by a K Cube to allow confirmation Rx messages
        self.communicator.write(pack('<HBBBB', 0x0005, 0x00, 0x00, 0x50, 0x01))
        self.flush()

        self.enable_stage()


    def flush(self):
        self.communicator.flushInput()
        self.communicator.flushOutput()


    def _ensure_motor_received_instruction(self):
        time.sleep(0.1)


    def enable_stage(self):
        # Enable Stage; MGMSG_MOD_SET_CHANENABLESTATE
        self.communicator.write(pack('<HBBBB', 0x0210, self.channel, 0x01, self.destination, self.source))
        self._ensure_motor_received_instruction()


    def disable_stage(self):
        # Disable Stage; MGMSG_MOD_SET_CHANENABLESTATE
        self.communicator.write(pack('<HBBBB', 0x0210, self.channel, 0x02, self.destination, self.source))
        self._ensure_motor_received_instruction()

        self.flush()


    def get_current_position(self, relative=True):
        # Request Position; MGMSG_MOT_REQ_POSCOUNTER
        self.communicator.write(pack('<HBBBB', 0x0411, self.channel, 0x00, self.destination, self.source))

        # Read back position returned by the cube; Rx message MGMSG_MOT_GET_POSCOUNTER
        header, chan_dent, position_in_mu = unpack('<6sHI', self.communicator.read(12))
        return self.convert_MU_to_position(position_in_mu)


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


    def jog(self):
        # Do a jog; MGMSG_MOT_MOVE_JOG
        self.communicator.write(pack('<HBBBB', 0x046A, self.channel, 0x01, self.destination, self.source))
        self._ensure_motor_received_instruction()
        self._wait_until_move_completed()


    def move_to(self, position, relative=True):
        if relative:
            # Move to relative position; MGMSG_MOT_MOVE_RELATIVE (long version)
            self.communicator.write(pack('<HBBBBHI', 0x0448, 0x06, 0x00, self.destination|0x80, self.source, self.channel,
                              self.convert_position_to_MU(position)))
        else:
            # Move to absolute position; MGMSG_MOT_MOVE_ABSOLUTE (long version)
            self.communicator.write(pack('<HBBBBHI', 0x0453, 0x06, 0x00, self.destination|0x80, self.source, self.channel,
                              self.convert_position_to_MU(position)))

        self._ensure_motor_received_instruction()
        self._wait_until_move_completed()


    def _wait_until_move_completed(self):
        Rx = ''
        Moved = pack('<H',0x0464)
        while Rx != Moved:
            # Check if moving; MGMSG_MOT_MOVE_COMPLETED
            Rx = self.communicator.read(2)
            time.sleep(0.1)


    def stop(self):
        # Stop any movement; MGMSG_MOT_MOVE_STOP
        self.communicator.write(pack('<HBBBB',0x0465, 0x02, self.channel, self.destination, self.source))


    def convert_position_to_MU(self, position):
        """ position in mm """
        return int(round(self.unit_conversions["MU/mm"]*position))


    def convert_MU_to_position(self, position):
        """ position in mm """
        return position/self.unit_conversions["MU/mm"]


    def convert_velocity_to_MU(self, velocity):
        """ velocity in mm/s^2 """
        return int(round(self.unit_conversions["MU/(mm/s)"]*velocity))


    def convert_acceleration_to_MU(self, acceleration):
        """ acceleration in mm/s^2 """
        return int(round(self.unit_conversions["MU/(mm/s^2)"]*acceleration))


COM_Port = '/dev/ttyUSB0' # Change to preferred
motor = Motor(COM_Port, "ZST225B")
print("Before moving", motor.get_current_position())
motor.move_to(0)
motor.set_step_size(0.5)
motor.jog()
print("After moving", motor.get_current_position())
motor.disable_stage()
