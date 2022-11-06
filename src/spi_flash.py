from amaranth import *
from math     import ceil, log2
from amaranth.back import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *
from amaranth_boards.resources import *

from .isa import *

class DummyPin():
    def __init__(self, name):
        self.o = Signal(name='%s_o'%name)
        self.i = Signal(name='%s_i'%name)

class DummySPI():
    def __init__(self):
        self.cs = DummyPin('cs')
        self.clk = DummyPin('clk')
        self.mosi = DummyPin('mosi')
        self.miso = DummyPin('miso')

###############################################
# SPI Flash module
###############################################

class SPI_Flash(Elaboratable):
    def __init__(self, data_start, data_end, data):
        # Data storage
        self.dstart = data_start
        self.dend = data_end
        self.dlen = (data_end - data_start) + 1
        self.spio = Signal(32, reset=0x03000000)
        self.dc = Signal(6, reset=0b000000)
        
        if data is not None:
            self.data = Memory(width=32, depth=len(data), init=data)
        else:
            self.data = None
        # Initalize Wishbone bus arbiter
        self.arb = Arbiter(addr_width=ceil(log2(self.dlen+1)), data_width=32)
        self.arb.bus.memory_map = MemoryMap(addr_width=self.arb.bus.addr_width, data_width=self.arb.bus.data_width, alignment=0)
	
    def new_bus(self):
        #Initial a new wishbone bus interface
        bus = Interface(addr_width=self.arb.bus.addr_width, data_width=self.arb.bus.data_width)
        bus.memory_map = MemoryMap(addr_width=bus.addr_width, data_width=bus.data_width, alignment=0)
        self.arb.add(bus)
        return bus

    
    def elaborate(self, platform):
        m = Module()
        m.submodules.arb = self.arb

        if platform is None:
            self.spi = DummySPI()
        else:
            self.spi = platform.request('spi_flash')

        # Clock reset at 0
        m.d.comb += self.spi.clk.o.eq(0)

        with m.FSM() as fsm:
            with m.State("SPI_RESET"):
                m.d.sync += [
                    self.spi.cs.o.eq(1),
                    self.spio.eq(0xAB000000)
                ]
                m.next = "SPI_POWERUP"
            with m.State("SPI_POWERUP"):
                m.d.comb += [
                    self.spi.clk.o.eq(~ClockSignal("sync")),
                    self.spi.mosi.o.eq(self.spio[31])
                ]
                m.d.sync += [
                    self.spio.eq(self.spio << 1),
                    self.dc.eq(self.dc + 1)
                ]
                m.next = "SPI_POWERUP"

                with m.If(self.dc == 30):
                    m.next = "SPI_WAITING"
                with m.Elif(self.dc >= 8):
                    m.d.sync += self.spi.cs.o.eq(0)
            with m.State("SPI_WAITING"):
                m.d.sync += [
                    self.arb.bus.ack.eq(self.arb.bus.cyc & (self.arb.bus.ack & self.arb.bus.stb)),
                    self.spi.cs.o.eq(0)
                ]
                m.next = "SPI_WAITING"
                with m.If((self.arb.bus.cyc == 1) & (self.arb.bus.stb == 1) & (self.arb.bus.ack == 0)):
                    m.d.sync += [
                        self.spi.cs.o.eq(1),
                        self.spio.eq((0x03000000 | ((self.arb.bus.adr + self.dstart) & 0x00FFFFFF))),
                        self.arb.bus.ack.eq(0),
                        self.dc.eq(31)
                    ]
                m.next = "SPI_TX"
            with m.State("SPI_TX"):
                m.d.sync += [
                    self.dc.eq( self.dc - 1 ),
                    self.spio.eq( self.spio << 1 )
                ]
                m.d.comb += [
                    self.spi.clk.o.eq( ~ClockSignal( "sync" ) ),
                    self.spi.mosi.o.eq( self.spio[ 31 ] )
                ]

                with m.If( self.dc == 0 ):
                    m.d.sync += [
                        self.dc.eq(7),
                        self.arb.bus.dat_r.eq(0)
                    ]
                    m.next = "SPI_RX"
                with m.Else():
                    m.next = "SPI_TX"
            with m.State("SPI_RX"):
                # Simulate the 'miso' pin value for tests.
                if platform is None:
                    with m.If( self.dc < 8 ):
                        m.d.comb += self.spi.miso.i.eq( ( self.data[ self.arb.bus.adr >> 2 ] >> ( self.dc + 24 ) ) & 0b1 )
                    with m.Elif( self.dc < 16 ):
                        m.d.comb += self.spi.miso.i.eq( ( self.data[ self.arb.bus.adr >> 2 ] >> ( self.dc + 8 ) ) & 0b1 )
                    with m.Elif( self.dc < 24 ):
                        m.d.comb += self.spi.miso.i.eq( ( self.data[ self.arb.bus.adr >> 2 ] >> ( self.dc - 8 ) ) & 0b1 )
                    with m.Else():
                        m.d.comb += self.spi.miso.i.eq( ( self.data[ self.arb.bus.adr >> 2 ] >> ( self.dc - 24 ) ) & 0b1 )
                m.d.sync += [
                    self.dc.eq( self.dc - 1 ),
                    self.arb.bus.dat_r.bit_select( self.dc, 1 ).eq( self.spi.miso.i )
                ]
                m.d.comb += self.spi.clk.o.eq( ~ClockSignal( "sync" ) )
                # Assert 'ack' signal and move back to 'waiting' state
                # once a whole word of data has been received.
                with m.If( self.dc[ :3 ] == 0 ):
                    with m.If( self.dc[ 3 : 5 ] == 0b11 ):
                        m.d.sync += [
                            self.spi.cs.o.eq( 0 ),
                            self.arb.bus.ack.eq( self.arb.bus.cyc )
                        ]
                        m.next = "SPI_WAITING"
                    with m.Else():
                        m.d.sync += self.dc.eq( self.dc + 15 )
                        m.next = "SPI_RX"
                with m.Else():
                    m.next = "SPI_RX"

        return m
