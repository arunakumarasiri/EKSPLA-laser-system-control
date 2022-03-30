from ctypes import POINTER, WinDLL, c_char_p, c_double, c_int
from os import add_dll_directory, path

from .errors import errcheck

c_int_p = POINTER(c_int)
c_double_p = POINTER(c_double)


class LibRmtCtrl(WinDLL):
    def __init__(self, name: str = "remotecontrol"):
        vendor_dir = path.join(path.dirname(__file__), "..", "..", "vendor")
        with add_dll_directory(vendor_dir):
            super().__init__(name)

        """ Argument types """
        # fmt: off
        # Connection
        self.rcConnect.argtypes = (c_int, c_int)
        self.rcDisconnect.argtypes = ()

        # Devices and registers enumeration
        self.rcGetFirstDeviceName.argtypes = (c_char_p, c_int)
        self.rcGetNextDeviceName.argtypes = (c_char_p, c_int)
        self.rcGetFirstRegisterName.argtypes = (c_char_p, c_char_p, c_int)
        self.rcGetNextRegisterName.argtypes = (c_char_p, c_int)

        # Register classification
        self.rcIsRegisterWriteable.argtypes = (c_char_p, c_char_p, c_int_p)
        self.rcIsRegisterNV.argtypes = (c_char_p, c_char_p, c_int_p)
        self.rcGetRegFirstEnumValue.argtypes = (c_char_p, c_char_p, c_char_p, c_int)
        self.rcGetRegNextEnumValue.argtypes = (c_char_p, c_char_p, c_char_p, c_int)

        # Register access
        self.rcGetRegAsDouble.argtypes = (c_char_p, c_char_p, c_double_p, c_int, c_int_p)
        self.rcSetRegFromDouble.argtypes = (c_char_p, c_char_p, c_double)
        self.rcSetRegFromDoubleA.argtypes = (c_char_p, c_char_p, c_double, c_int)
        self.rcSetRegNVFromDouble.argtypes = (c_char_p, c_char_p, c_double)
        self.rcGetRegAsString.argtypes = (c_char_p, c_char_p, c_char_p, c_int, c_int, c_int_p)
        self.rcSetRegFromString.argtypes = (c_char_p, c_char_p, c_char_p)
        self.rcSetRegFromStringA.argtypes = (c_char_p, c_char_p, c_char_p, c_int)
        self.rcSetRegNVFromString.argtypes = (c_char_p, c_char_p, c_char_p)

        # Register log and access
        self.rcLogRegStart.argtypes = (c_char_p, c_char_p, c_int)
        self.rcLogRegStop.argtypes = (c_char_p, c_char_p)
        self.rcGetRegFromLogAsDouble.argtypes = (c_char_p, c_char_p, c_double_p, c_int_p)
        self.rcGetRegFromLogAsString.argtypes = (c_char_p, c_char_p, c_char_p, c_int, c_int_p)
        # fmt: on

        """ Error checking """
        for attr, value in vars(self).items():
            if attr.startswith("rc"):
                value.errcheck = errcheck
