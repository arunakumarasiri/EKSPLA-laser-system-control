from ctypes import c_int
from enum import IntEnum
from warnings import warn

_sentinel = object()


class CsvError(Exception):
    pass


# TODO Passing device and register names
class RegisterError(Exception):
    pass


class LogError(Exception):
    pass


class RegisterLogError(RegisterError, LogError):
    pass


class RmtCtrlError(IntEnum):
    # fmt: off
    NONE              = 0x00
    NO_MORE_DATA      = 0x01
    NO_CONFIG_FILE    = 0x02
    WRONG_CONFIG_FILE = 0x03
    BUFFER_TOO_SHORT  = 0x04
    NO_SUCH_DEVICE    = 0x05
    NO_SUCH_REGISTER  = 0x06
    CANNOT_CONNECT    = 0x07
    TIMEOUT           = 0x08
    READ_ONLY         = 0x09
    NOT_NONVOLATILE   = 0x0a
    HIGH_LIMIT        = 0x0b
    LOW_LIMIT         = 0x0c
    NO_SUCH_VALUE     = 0x0d
    NOT_LOGGED        = 0x0e
    MEMORY_FULL       = 0x0f
    LOG_EMPTY         = 0x10
    ALREADY_CONNECTED = 0x11
    NOT_YET_CONNECTED = 0x12
    LOG_OVERFLOW      = -0x80000000
    # fmt: on


def _format_value(value: float | bytes):
    if isinstance(value, float):
        return f"{value:g}"
    else:
        return value.decode("latin-1")


def errcheck(result: int, func, arguments: tuple):
    if result == RmtCtrlError.NONE:
        return
    if result == RmtCtrlError.NO_MORE_DATA:
        return _sentinel
    if result == RmtCtrlError.NO_CONFIG_FILE:
        raise FileNotFoundError("No such file in current directory: REMOTECONTROL.csv")
    if result == RmtCtrlError.WRONG_CONFIG_FILE:
        raise CsvError("Failed to parse REMOTECONTROL.csv")
    if result == RmtCtrlError.BUFFER_TOO_SHORT:
        max_len = next(arg.value for arg in arguments if isinstance(arg, c_int))
        raise BufferError(f"Supplied buffer is too small ({max_len} bytes)")
    if result == RmtCtrlError.NO_SUCH_DEVICE:
        dev_name: str = arguments[0].value.decode("latin-1")
        raise ValueError(f'Invalid device name: "{dev_name}"')
    if result == RmtCtrlError.NO_SUCH_REGISTER:
        reg_name: str = arguments[1].value.decode("latin-1")
        raise ValueError(f'Invalid register name: "{reg_name}"')
    if result == RmtCtrlError.CANNOT_CONNECT:
        # Not due to a missing CAN driver DLL since we check for them
        if arguments[0].value == 1:  # RS-232
            port_num: int = arguments[1].value
            raise ConnectionError(
                f"COM port {port_num} is already used by another process"
            )
        raise ConnectionError("Already used by another process")  # XXX LAN
    if result == RmtCtrlError.TIMEOUT:
        timeout: int = arguments[-2].value
        raise TimeoutError(f"Timed out waiting for device answer ({timeout} ms)")
    if result == RmtCtrlError.READ_ONLY:
        raise RegisterError("Register is read-only")
    if result == RmtCtrlError.NOT_NONVOLATILE:
        raise RegisterError("Register is not non-volatile")
    if result == RmtCtrlError.HIGH_LIMIT:
        value = _format_value(arguments[2].value)
        raise ValueError(f"Value ({value}) greater than the maximum value")
    if result == RmtCtrlError.LOW_LIMIT:
        value = _format_value(arguments[2].value)
        raise ValueError(f"Value ({value}) less than the minimum value")
    if result == RmtCtrlError.NO_SUCH_VALUE:
        value = _format_value(arguments[2].value)
        raise ValueError(f"Value ({value}) not in the value list")
    if result == RmtCtrlError.NOT_LOGGED:
        raise RegisterLogError("Register is not being logged")
    if result == RmtCtrlError.MEMORY_FULL:
        raise LogError("Not enough memory to allocate")
    if result == RmtCtrlError.LOG_EMPTY:
        return _sentinel
    if result == RmtCtrlError.ALREADY_CONNECTED:
        raise ConnectionError("Already connected")
    if result == RmtCtrlError.NOT_YET_CONNECTED:
        raise ConnectionError("Not connected")
    if result == RmtCtrlError.LOG_OVERFLOW:
        warn("Log FIFO buffer overflow", stacklevel=2)
        return

    raise Exception(f"Unknown return code: 0x{result:x}")
