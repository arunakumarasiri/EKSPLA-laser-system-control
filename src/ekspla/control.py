import csv
import re
from collections import defaultdict
from ctypes import byref, c_double, c_int, create_string_buffer, pointer
from enum import Flag, IntEnum, auto
from pathlib import Path
from shutil import copy

from .lib import LibRmtCtrl


class ConnectionType(IntEnum):
    DIRECT = 0
    RS232 = 1
    LAN = 2


class RegisterStatus(Flag):
    WRITABLE = auto()
    NONVOLATILE = auto()


# TODO Docstring
# TODO Dynamic resize by doubling the size on BufferError
# TODO Improve raised ValueError by adding info on valid range/values
# TODO Adding useful dunder methods like __enter__/__exit__, __repr__, etc.
class RemoteControl:
    def __init__(self, con_type: ConnectionType, port_num: int | None = None):
        self._lib = LibRmtCtrl()
        self._con_type = ConnectionType(con_type)

        # CAN over TCP
        if self._con_type == ConnectionType.LAN:
            raise NotImplementedError("LAN not implemented in the Python wrapper")

        # USBCAN over FTDI
        if self._con_type == ConnectionType.DIRECT:
            self._port_num = 0  # XXX
            return

        # COM port CAN
        if not isinstance(port_num, int):
            raise TypeError(
                f"COM port number must be an int, not {type(port_num).__name__}"
            )
        if port_num < 1:
            raise ValueError("COM port number must be greater than 0")
        self._port_num = port_num

    def _parse_types(self):
        types = defaultdict(lambda: defaultdict(lambda: float))
        with open(Path.cwd() / "REMOTECONTROL.csv", encoding="latin-1") as file:
            for line in csv.reader(file.readlines()[2:-1], delimiter=";"):
                device_id = int(line[1].lstrip("$"), 16)
                device, register = f"{line[0].rstrip()}:{device_id}", line[11]

                if line[4].startswith("str"):
                    types[device][register] = str
                elif re.match("(?:u|s)\d+", line[4]):
                    types[device][register] = int
        return types

    def connect(self):
        # XXX Hack to load the correct DLL
        vendor_dir = Path(__file__).parents[2] / "vendor"
        if self._con_type == ConnectionType.DIRECT:
            copy(vendor_dir / "usbcand.dll", Path.cwd())
        elif self._con_type == ConnectionType.RS232:
            copy(vendor_dir / "canrs232.dll", Path.cwd())
        elif self._con_type == ConnectionType.LAN:
            copy(vendor_dir / "cantcp.dll", Path.cwd())

        self._lib.rcConnect(self._con_type, self._port_num)
        self._reg_types = self._parse_types()

    def disconnect(self):
        self._lib.rcDisconnect()

    def devices(self):
        # Rounded minimum of 11 bytes to the next power of 2
        buffer = create_string_buffer(16)

        self._lib.rcGetFirstDeviceName(buffer, len(buffer))
        names: list[str] = [buffer.value.decode("latin-1")]
        while self._lib.rcGetNextDeviceName(buffer, len(buffer)) is None:
            names.append(buffer.value.decode("latin-1"))

        return names

    def registers(self, device: str):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        device = device.encode("latin-1")

        # Rounded minimum of 46 bytes to the next power of 2
        buffer = create_string_buffer(64)

        self._lib.rcGetFirstRegisterName(device, buffer, len(buffer))
        names: list[str] = [buffer.value.decode("latin-1")]
        while self._lib.rcGetNextRegisterName(buffer, len(buffer)) is None:
            names.append(buffer.value.decode("latin-1"))

        return names

    def register_status(self, device: str, register: str):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")
        device, register = device.encode("latin-1"), register.encode("latin-1")

        status = RegisterStatus(0)

        writeable = c_int()
        self._lib.rcIsRegisterWriteable(device, register, byref(writeable))
        if writeable:
            status |= RegisterStatus.WRITABLE

        nonvolatile = writeable
        self._lib.rcIsRegisterNV(device, register, byref(nonvolatile))
        if nonvolatile:
            status |= RegisterStatus.NONVOLATILE

        return status

    def register_enum(self, device: str, register: str):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")
        device, register = device.encode("latin-1"), register.encode("latin-1")

        # Rounded minimum of 17 bytes to the next power of 2
        # XXX Doesn't seem to return an error code if buffer is too small
        buffer = create_string_buffer(32)

        if (
            self._lib.rcGetRegFirstEnumValue(device, register, buffer, len(buffer))
            is not None
        ):
            return None

        values: list[str] = [buffer.value.decode("latin-1")]
        while (
            self._lib.rcGetRegNextEnumValue(device, register, buffer, len(buffer))
            is None
        ):
            values.append(buffer.value.decode("latin-1"))

        return values

    def register_range(
        self, device: str, register: str
    ) -> tuple[int, int] | tuple[float, float]:
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")

        reg_type: int | float | str = self._reg_types[device][register]
        if reg_type is str:
            return None

        device, register = device.encode("latin-1"), register.encode("latin-1")

        limit = c_double()

        self._lib.rcGetRegMinVal(device, register, byref(limit))
        lo = limit.value

        self._lib.rcGetRegMaxVal(device, register, byref(limit))
        hi = limit.value

        return reg_type(lo), reg_type(hi)

    def register_format(self, device: str, register: str):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")
        device, register = device.encode("latin-1"), register.encode("latin-1")

        # Rounded minimum of 78 bytes to the next power of 2
        # XXX Doesn't seem to return an error code if buffer is too small
        buffer = create_string_buffer(128)

        self._lib.rcGetRegFmtString(device, register, buffer, len(buffer))

        format: str = buffer.value.decode("latin-1")
        if format[0] == "[" and format[-1] == "]":
            return None
        return format

    def register_get(
        self,
        device: str,
        register: str,
        timestamp=False,
        timeout: int | None = None,
    ) -> tuple[int, int] | tuple[int, float] | tuple[int, str]:
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")

        reg_type: int | float | str = self._reg_types[device][register]

        device, register = device.encode("latin-1"), register.encode("latin-1")
        timestamp = pointer(c_int()) if timestamp else None
        timeout = -1 if timeout is None else timeout

        if reg_type is str:
            # TODO Choose a more appropriate buffer size
            buffer = create_string_buffer(512)

            self._lib.rcGetRegAsString(
                device, register, buffer, len(buffer), timeout, timestamp
            )

            if timestamp:
                return timestamp.contents.value, buffer.value.decode("latin-1")
            return buffer.value.decode("latin-1")

        value = c_double()

        self._lib.rcGetRegAsDouble(device, register, byref(value), timeout, timestamp)

        if timestamp:
            return timestamp.contents.value, reg_type(value.value)
        return reg_type(value.value)

    def register_set(
        self,
        device: str,
        register: str,
        value: int | float | str,
        nonvolatile=False,
    ):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")

        device, register = device.encode("latin-1"), register.encode("latin-1")

        if isinstance(value, str):
            fn = (
                self._lib.rcSetRegNVFromString
                if nonvolatile
                else self._lib.rcSetRegFromString
            )
            fn(device, register, value.encode("latin-1"))
            return

        fn = (
            self._lib.rcSetRegNVFromDouble
            if nonvolatile
            else self._lib.rcSetRegFromDouble
        )
        fn(device, register, float(value))

    def register_log(
        self,
        device: str,
        register: str,
        size=128,  # XXX
        timestamp=True,
    ):
        if not isinstance(device, str):
            raise TypeError("Device name must be a str")
        if not isinstance(register, str):
            raise TypeError("Register name must be a str")

        # TODO Adding rcGetRegFromLogAsString based on reg_type
        reg_type: int | float | str = self._reg_types[device][register]

        device, register = device.encode("latin-1"), register.encode("latin-1")
        timestamp = pointer(c_int()) if timestamp else None

        value = c_double()

        self._lib.rcLogRegStart(device, register, size)
        try:
            while True:
                if (
                    self._lib.rcGetRegFromLogAsDouble(
                        device, register, byref(value), timestamp
                    )
                    is None
                ):
                    if timestamp:
                        yield timestamp.contents.value, reg_type(value.value)
                    else:
                        yield reg_type(value.value)
        # TODO Deal with exceptions
        except (StopIteration, GeneratorExit):
            pass
        finally:
            self._lib.rcLogRegStop(device, register)
