from amaranth import Module
from amaranth.sim import Simulator, Delay, Settle
from your_module import YourModule

if __name__ == "__main__":
    m = Module()
    m.submodules.yourmodule = yourmodule = YourModule()

    sim = Simulator(m)
	sim.add_clock(1e-6, domain="fast_clock")
	sim.add_clock(0.91e-6, domain="faster_clock")

    def process():
        # To be defined
		yield x.eq(0)
		yield Delay(1e-6)
		yield y.eq(0xff)
		yield Settle()
		got = yield yourmodel.sum
		want = yield (x+y)[:8]
		if got != want:
			print("xx")

    def process_sync():
        # To be defined
		yield x.eq(0)
		yield Delay(1e-6)
		yield y.eq(0xff)
		yield Settle()
		got = yield yourmodel.sum
		want = yield (x+y)[:8]
		if got != want:
			print("xx")
    
	sim.add_process(process) # or sim.add_sync_process(process), see below
    sim.add_sync_process(process_sync, domain="name1")

    with sim.write_vcd("test.vcd", "test.gtkw", traces=yourmodule.ports()):
        sim.run()
