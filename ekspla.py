from multiprocessing.sharedctypes import Value
from sqlite3 import Timestamp
from typing import Any
from serial import Serial
import time

# TODO Logging of instrument registers using logstart/logget
# TODO Figure out a better way to remove \r\n\x03 when converting to string
# TODO Look into always flushing buffer and drop the flush calls
# TODO Refactor the code and remove needless duplication
# TODO Dynamic conversion from/to string based on types and metadata from instrument

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

        self._ser.write(b"/timestamp()\r")
        self._ser.flush()
        return self._ser.read_until(b"\x03")[:-3].decode('latin-1')

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

    def start_logging(self, module_name: str, id: int, register_name: str, buffer_size: int):
        if buffer_size <= 0:
            raise ValueError("buffer size must be at least 1 byte")

        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        cmd = f'/{module_name}/{id}/{register_name}/logstart()/{buffer_size}\r'
        self._ser.write(cmd.encode())
        self._ser.flush()

        if (msg := self._ser.read_until(b'\x03')) != b"\r\n\x03":
            # TODO Better formatting
            raise Exception(msg[3:-3].decode("latin-1"))

    def stop_logging(self, module_name: str, id: int, register_name: str):
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        cmd = f'/{module_name}/{id}/{register_name}/logstart()/0\r'
        self._ser.write(cmd.encode())
        self._ser.flush()

        if (msg := self._ser.read_until(b'\x03')) != b"\r\n\x03":
            # TODO Better formatting
            raise Exception(msg[3:-3].decode("latin-1"))

    # TODO Consider streaming data as it is read (usage of generators...)
    # TODO Find a better name
    def logget(self, module_name: str, id: int, register_name: str, num_recs: int):
        if num_recs < 0: # TODO Is 0 a valid value?
            raise ValueError("number of records must be positive")
        
        if not self._ser.is_open:
            raise Exception("connect to the instrument first")

        cmd = f'/{module_name}/{id}/{register_name}/logget()/{num_recs}\r'
        self._ser.write(cmd.encode())
        self._ser.flush()

        # TODO Timestamp should be an int
        # FIXME Peak the message for ''' and raise exception
        # FIXME Deal with errors that can show up later like FIFO overrun
        data = self._ser.read_until(b'\x03').decode('latin-1')
        return list(map(lambda x: x.rsplit(maxsplit=1), data.split('\r\n')))

def setdetectorSensitivity(instr, val): # 1-99

    instr.register_write("PMTC0000", 1, "Set PMT cathode voltage", f"{val}0.000000")

def setVisTransmission(instr, val): # 1-99
    
    instr.register_write("SM5-HM1", 46, "Target position", f"{val}.000000")

def setAmplification(instr, val): # 1-99
    
    instr.register_write("SY3PL50M", 32, "Amplification", f"{val}.000000")

def LaserOn(instr, val):
    # Turning laser on

    if val == 'TRUE':
        instr.register_write("SY3PL50M", 32, "State", "ON")
        instr.register_write("SY3PL50M", 32, "Energy level", "Maximum")
        instr.register_write("PMTC0000", 1, "PMT HV power supply", "ON")
        # instr.register_write("SY3PL50M", 32, "Start->Lasing delay", "5")

        # Just reading the values for tests
        assert instr.register_read("SY3PL50M", 32, "State") == "ON"
        assert instr.register_read("SY3PL50M", 32, "Energy level") == "Maximum"
        assert instr.register_read("PMTC0000", 1, "PMT HV power supply") == "ON"
    if val == 'FALSE':
    # Turning laser off
        instr.register_write("PMTC0000", 1, "PMT HV power supply", "OFF")
        instr.register_write("SY3PL50M", 32, "Energy level", "OFF")
        instr.register_write("SY3PL50M", 32, "State", "OFF")

        # Just reading the values for tests
        assert instr.register_read("SY3PL50M", 32, "State") == "OFF"
        assert instr.register_read("SY3PL50M", 32, "Energy level") == "OFF"
        assert instr.register_read("PMTC0000", 1, "PMT HV power supply") == "OFF"

def setpolarization(instr, pol):
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

def motorcheck(instr, val): # 1-99
    
    instr.register_write("SM5-7", 12, "Target position", f"{val}.000000")
