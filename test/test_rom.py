#####################################
# ALU testbench
####################################
from amaranth.sim import Simulator, Tick, Settle
import sys, os
sys.path.append("..")

from src.isa import *
from src.rom import *

p = 0
f = 0
def rom_read_ut(rom, address, expected):
    global p, f
    yield rom.arb.bus.adr.eq(address)
    yield Tick()
    yield Tick()
    yield Settle()

    actual = yield rom.arb.bus.dat_r
    if expected != actual:
        f += 1
        print("\033[31mFAIL:\033[0m ROM[0x%08X] = 0x%08X (got: 0x%08X)" % (address, expected, actual))
    else:
        p += 1
        print( "\033[32mPASS:\033[0m ROM[0x%08X] = 0x%08X" % (address, expected))

def rom_test(rom):
    yield Settle()
    print("---ROM Tests---")
    yield rom.arb.bus.cyc.eq(1)
    yield from rom_read_ut(rom, 0x0, little_end(0x01234567))
    yield from rom_read_ut(rom, 0x4, little_end(0x89abcdef))
    yield from rom_read_ut(rom, 0x8, little_end(0x42424242))
    yield from rom_read_ut(rom, 0xc, little_end(0xdeadbeef))

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

