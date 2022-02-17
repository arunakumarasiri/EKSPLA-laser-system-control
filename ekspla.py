from sqlite3 import Timestamp
from typing import Any
from serial import Serial

# TODO Logging of instrument registers using logstart/logget
# TODO Figure out a better way to remove \r\n\x03 when converting to string
# TODO Look into always flushing buffer and drop the flush calls

class Instrument:
    def __init__(self, serial_port: str = "COM3"):
        self._ser = Serial(baudrate=19200)
        self._ser.port = serial_port

    def connect(self):
        self._ser.open()

        # Communication Test
        self._ser.write(b"\r")
        self._ser.flush()
        assert self._ser.read_until(b"\x03").startswith(b"Remote control over RS232")
        # return self._ser.read_until(b"\x03").startswith(b"Remote control over RS232")

    def disconnect(self):
        self._ser.close() 

    def device_id(self):
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        self._ser.write(b"/id()\r")
        self._ser.flush()
        return self._ser.read_until(b"\x03")[:-3].decode('latin-1')

# Timestamp test ########################################################

    def timestamp(self):
        if not self._ser.is_open:
         raise Exception("connect to the instrument first")

        self._ser.write(b"/timestamp\r")
        self._ser.flush()
        return self._ser.read_until(b"\x03")[:-3].decode('latin-1')

# '''Error: (-1) 2nd and 3rd arguments are missing (/timestamp/???/???)
###########################################################################

    def register_list(self):
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        self._ser.write(b"/list()\r")
        self._ser.flush()
        # TODO Marshall the data into something more useful than a string
        return self._ser.read_until(b"\x03")[:-3].decode('latin-1')

    def register_read(self, module_name: str, id: int, register_name: str):
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        cmd = f'/{module_name}/{id}/{register_name}\r'
        self._ser.write(cmd.encode())
        self._ser.flush()
        return self._ser.read_until(b'\x03')[:-3].decode('latin-1')

    def register_write(
        self, module_name: str, id: int, register_name: str, value: Any, nvram: bool = False
    ):
        # XXX If any can be anything, need to pay attention...
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        cmd = f'/{module_name}/{id}/{register_name}/{value}'
        if nvram:
            cmd += "/NV"
        cmd += "\r"

        self._ser.write(cmd.encode())
        self._ser.flush()

        if (msg := self._ser.read_until(b'\x03')) != b"\r\n\x03":
            # TODO Better formatting
            raise Exception(msg[3:-3].decode("latin-1"))


instr = Instrument()
instr.connect()

# print(instr.device_id())
print(instr.device_id())

# Turning laser on
instr.register_write("SY3PL50M", 32, "State", "ON")
instr.register_write("SY3PL50M", 32, "Energy level", "Maximum")
instr.register_write("PMTC0000", 1, "PMT HV power supply", "ON")
# instr.register_write("SY3PL50M", 32, "Start->Lasing delay", "5")

# Just reading the values for tests
assert instr.register_read("SY3PL50M", 32, "State") == "ON"
assert instr.register_read("SY3PL50M", 32, "Energy level") == "Maximum"
assert instr.register_read("PMTC0000", 1, "PMT HV power supply") == "ON"

# Getting outputs

print( instr.register_read("SY3PL50M", 32, "State"))
# print(instr.timestamp())
# print(instr.connect())
# print(instr.register_list())

import time
time.sleep(5)

# Turning laser off
instr.register_write("PMTC0000", 1, "PMT HV power supply", "OFF")
instr.register_write("SY3PL50M", 32, "Energy level", "OFF")
instr.register_write("SY3PL50M", 32, "State", "OFF")

# Just reading the values for tests
assert instr.register_read("SY3PL50M", 32, "State") == "OFF"
assert instr.register_read("SY3PL50M", 32, "Energy level") == "OFF"
assert instr.register_read("PMTC0000", 1, "PMT HV power supply") == "OFF"

instr.disconnect()

# CheckPolarizationSelector.vi/SetSFGPolarization





