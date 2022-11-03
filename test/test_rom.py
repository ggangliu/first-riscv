#####################################
# ALU testbench
####################################
from amaranth.sim import Simulator, Tick, Settle
import sys, os
sys.path.append(os.getcwd()+"/../")

from src.isa import *
from src.rom import *

p = 0
f = 0
def rom_ut(dut, address, expected):
    global p, f
    yield dut.arb.bus.adr.eq(address)
    yield Tick()
    yield Settle()

    actual = yield dut.arb.bus.dat_r
    if hexs(expected) != hexs(actual):
        f += 1
        print("\033[31mFAIL:\033[0m %s (got: %s)" % (hexs(expected), hexs(actual)))
    else:
        p += 1
        print( "\033[32mPASS:\033[0m %s = %s" % (hexs(expected), hexs(actual)))

def rom_test(dut):
    yield Settle()
    print("---ROM Tests---")
    yield dut.arb.bus.cyc.eq(1)
    yield from rom_ut(dut, 0x0, 0x01234567)
    yield from rom_ut(dut, 0x0, 0x89abcdef)
    yield from rom_ut(dut, 0x0, 0x42424242)
    yield from rom_ut(dut, 0x0, 0xdeadbeef)

    yield Tick()
    print("ROM Tests: %d Passed, %d Failed" % (p, f))


if __name__ == "__main__":
    dut = ROM([0x01234567, 0x89ABCDEF, 0x42424242, 0xDEADBEEF])
	
    def proc():
        yield from rom_test(dut)
	
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    with sim.write_vcd("rom.vcd"):
        sim.run()

