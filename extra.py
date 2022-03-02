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