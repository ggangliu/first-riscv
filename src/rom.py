from amaranth import *
from math     import ceil, log2
from amaranth.back import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *

from .isa import *

###############################################
# ROM module
###############################################

class ROM(Elaboratable):
    def __init__(self, data):
        # Data storage
        self.data = Memory(width=32, depth=len(data), init=data)
        self.r = self.data.read_port()
        # Initalize Wishbone bus arbiter
        self.size = len(data) * 4
        self.arb = Arbiter(addr_width=ceil(log2(self.size+1)), data_width=32)
        self.arb.bus.memory_map = MemoryMap(addr_width=self.arb.bus.addr_width, data_width=self.arb.bus.data_width, alignment=0)
	
    def new_bus(self):
        #Initial a new wishbone bus interface
        bus = Interface(addr_width=self.arb.bus.addr_width, data_width=self.arb.bus.data_width)
        bus.memory_map = MemoryMap(addr_width=bus.addr_width, data_width=bus.data_width, alignment=0)
        self.arb.add(bus)

        #DMA support
        return bus

    
    def elaborate(self, platform):
        m = Module()
        m.submodules.arb = self.arb
        m.submodules.r = self.r

        rws = Signal(1, reset=0)
        m.d.sync += [
        	rws.eq(self.arb.bus.cyc), 
            self.arb.bus.ack.eq(self.arb.bus.cyc & rws)
        ]

        m.d.comb += self.r.addr.eq(self.arb.bus.adr >> 2)

        with m.If((self.arb.bus.adr & 0b11) == 0b00):
            m.d.sync += self.arb.bus.dat_r.eq(little_end(self.r.data))
        with m.Else():
            m.d.sync += self.arb.bus.dat_r.eq(little_end(self.r.data << ((self.arb.bus.adr&0b11) << 3)))

        return m

