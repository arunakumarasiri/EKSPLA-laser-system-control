from sqlite3 import Timestamp
from typing import Any
from serial import Serial
import time
from pandas import *

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

time.sleep(10)
# print(instr.timestamp())
# print(instr.connect())
# print(instr.register_list())

def polarization(pol):
    if pol == "ppp":
        instr.register_write("SM5-SF", 57, "Target position", "54700.000000")
        instr.register_write("SM5-HW2", 59, "Target position", "20000.000000")
        time.sleep(5)
        instr.register_write("SM5-V", 58, "Target position", "11200.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)
        instr.register_write("SM5-M4", 50, "Target position", "-12000.000000")
        instr.register_write("SM5-M6", 51, "Target position", "42000.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)
    if pol == "ssp":    
        instr.register_write("SM5-SF", 57, "Target position", "111500.000000")
        instr.register_write("SM5-HW2", 59, "Target position", "50000.000000")
        time.sleep(5)
        instr.register_write("SM5-V", 58, "Target position", "40000.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)
        instr.register_write("SM5-M4", 50, "Target position", "-12000.000000")
        instr.register_write("SM5-M6", 51, "Target position", "42000.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)
    if pol == "sps": 
        instr.register_write("SM5-SF", 57, "Target position", "111500.000000")
        instr.register_write("SM5-HW2", 59, "Target position", "50000.000000")
        time.sleep(5)
        instr.register_write("SM5-V", 58, "Target position", "11200.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)
        instr.register_write("SM5-M4", 50, "Target position", "-120000.000000")
        instr.register_write("SM5-M6", 51, "Target position", "113500.000000")
        instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
        time.sleep(5)

# Set PMT sensitivity

instr.register_write("PMTC0000", 1, "Set PMT cathode voltage", "500.000000")

######## Set SFG polarization ########   -- to S

instr.register_write("SM5-SF", 57, "Target position", "111500.000000")
instr.register_write("SM5-HW2", 59, "Target position", "50000.000000")
time.sleep(5)

######## Set SFG polarization ########   -- to P  

instr.register_write("SM5-SF", 57, "Target position", "54700.000000")
instr.register_write("SM5-HW2", 59, "Target position", "20000.000000")
time.sleep(5)


######## Set VIS polarization ######## -- to P

instr.register_write("SM5-V", 58, "Target position", "11200.000000")
instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
time.sleep(5)

######## Set VIS polarization ######## -- to S

instr.register_write("SM5-V", 58, "Target position", "40000.000000")
instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
time.sleep(5)

######## Set IR polarization ######## -- to S

instr.register_write("SM5-M4", 50, "Target position", "-120000.000000")
instr.register_write("SM5-M6", 51, "Target position", "113500.000000")
instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
time.sleep(5)

######## Set IR polarization ######## -- to P 

instr.register_write("SM5-M4", 50, "Target position", "-12000.000000")
instr.register_write("SM5-M6", 51, "Target position", "42000.000000")
instr.register_write("SM5-HM2", 47, "Target position", "-31.000000E+3")
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