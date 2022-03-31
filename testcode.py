from ekspla import *

instr = Instrument()
instr.connect()

# Come from the logs of the manufacturer's software
instr.start_logging("PMTC0000", 1, "Data", 41)
instr.start_logging("PHD1K000", 3, "Data", 51)
instr.start_logging("PHD1K000", 5, "Data", 52)
instr.start_logging("PHD1K000", 48, "Mean", 54)
instr.start_logging("MaxiOPG", 31, "OPO", 55)
instr.start_logging("MaxiOPG", 31, "AgGaS2", 56)

print(instr.register_read("SY3PL50M", 32, "State"))

time.sleep(10)

LaserOn(instr,'TRUE')

# setdetectorSensitivity(instr, 50)
# setAmplification(instr, 50)
# setVisTransmission(instr, 70)
# setpolarization(instr, "ssp")


print(instr.logget("PMTC0000", 1, "Data", 10))
print(instr.logget("PHD1K000", 3, "Data", 5))
print(instr.logget("PHD1K000", 5, "Data", 5))
print(instr.logget("PHD1K000", 48, "Mean", 5))
print(instr.logget("MaxiOPG", 31, "OPO", 5))
print(instr.logget("MaxiOPG", 31, "AgGaS2", 5))

motorcheck(instr, 54700)

LaserOn(instr,'FALSE')


print(instr.register_read("SY3PL50M", 32, "State"))

# First trial

# print(instr.logget("PMTC0000", 1, "Data", 5))
# print(instr.logget("PHD1K000", 3, "Data", 5))
# print(instr.logget("PHD1K000", 5, "Data", 5))
# print(instr.logget("PHD1K000", 48, "Mean", 5))
# print(instr.logget("MaxiOPG", 31, "OPO", 5))
# print(instr.logget("MaxiOPG", 31, "AgGaS2", 5))



instr.disconnect()