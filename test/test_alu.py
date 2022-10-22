#####################################
# ALU testbench
####################################
from amaranth.sim import Simulator 
import sys, os
sys.path.append(os.getcwd()+"/../")

from src.isa import *
from src.alu import *

p = 0
f = 0
def alu_ut(dut, rs1, rs2, f3, expected):
	global p, f
	yield dut.rs1.eq(rs1)
	yield dut.rs2.eq(rs2)
	yield dut.f3.eq(f3)

	yield #Tick()

	actual = yield dut.rd
	if hexs(expected) != hexs(actual):
		f += 1
		print("\033[31mFAIL:\033[0m %s %s %s = %s (got: %s)" % (hexs(rs1), ALU_STRS[f3], hexs(rs2), hexs(expected), hexs(actual)))
	else:
		p += 1
		print( "\033[32mPASS:\033[0m %s %s %s = %s" % (hexs(rs1), ALU_STRS[f3], hexs(rs2), hexs(expected)))

def alu_test(alu):
	yield #Settle()
	print("---ALU Tests---")

	print("ADD (+) tests:")
	yield from alu_ut(alu, 0, 0, ALU_ADD, 0)
	yield from alu_ut(alu, 0, 1, ALU_ADD, 1)
	yield from alu_ut(alu, 1, 0, ALU_ADD, 1)
	yield from alu_ut(alu, 0xFFFFFFFF, 1, ALU_ADD, 0)
	yield from alu_ut(alu, 29, 71, ALU_ADD, 100)
	yield from alu_ut(alu, 0x80000000, 0x80000000, ALU_ADD, 0)
	yield from alu_ut(alu, 0x7FFFFFFF, 0x7FFFFFFF, ALU_ADD, 0xFFFFFFFE)

	yield #Tick()
	print("ALU Tests: %d Passed, %d Failed" % (p, f))


if __name__ == "__main__":
	alu = ALU()

	def proc():
		yield from alu_test(alu)

	sim = Simulator(alu)
	sim.add_clock(1e-6)
	sim.add_sync_process(proc)
	with sim.write_vcd("test_alu.vcd"):
		sim.run()

