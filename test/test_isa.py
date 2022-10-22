from amaranth.sim import Simulator

import sys
sys.path.append("..")

from src.isa import * 

dut = UpCounter(25)

def bench():
    # Disabled counter should not overflow.
    yield dut.en.eq(0)
    for _ in range(30):
        yield
        assert not (yield dut.ovf)

    # Once enabled, the counter should overflow in 25 cycles.
    yield dut.en.eq(1)
    for _ in range(25):
        yield
        assert not (yield dut.ovf)

    yield
    assert (yield dut.ovf)

    # The overflow should clear in one cycle.
    yield
    assert not (yield dut.ovf)


sim = Simulator(dut)
sim.add_clock(1e-6) # 1 MHz
sim.add_sync_process(bench)
with sim.write_vcd("test_isa.vcd"):
    sim.run()
