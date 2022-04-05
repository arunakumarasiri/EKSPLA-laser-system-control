from ekspla import ConnectionType, RemoteControl

RS232 = ConnectionType.RS232

# TODO Test the warning and tweak the stacklevel
# TODO Confirm that settings values raise an exception on invalid values/range
# TODO Find out the maximum buffer size for logs

with RemoteControl(RS232, port_num=3) as rc:
    # Turning on the instrument
    rc.register_set("SY3PL50M:32", "State", "ON")
    rc.register_set("SY3PL50M:32", "Energy level", "Maximum")
    rc.register_set("PMTC0000:1", "PMT HV power supply", "ON")

    # Turning off the instrument
    rc.register_set("PMTC0000:1", "PMT HV power supply", "OFF")
    rc.register_set("SY3PL50M:32", "Energy level", "OFF")
    rc.register_set("SY3PL50M:32", "State", "OFF")

    # rc.register_log("PMTC0000:1", "Data", 41)
    # rc.register_log("PHD1K000:3", "Data", 51)
    # rc.register_log("PHD1K000:5", "Data", 52)
    # XXX rc.register_log("PHD1K000:48", "Mean", 54)
    # XXX rc.register_log("MaxiOPG:31", "OPO", 55)
    # XXX rc.register_log("MaxiOPG:31", "AgGaS2", 56)

for values in zip(gen1, gen2, gen3, gen4):
    print(values)

## Turning laser off
# instr.register_write("PMTC0000", 1, "PMT HV power supply", "OFF")
# instr.register_write("SY3PL50M", 32, "Energy level", "OFF")
# instr.register_write("SY3PL50M", 32, "State", "OFF")

instr.disconnect()
