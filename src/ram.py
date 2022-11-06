from amaranth import *
from math import ceil, log2
from amaranth.sim import Simulator, Tick, Settle 
from amaranth.back import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *

import os, sys
sys.path.append("..")

from src.isa import *

###############
# RAM module: #
###############

# Data input width definitions.
RAM_DW_8  = 0
RAM_DW_16 = 1
RAM_DW_32 = 2

class RAM( Elaboratable ):
  def __init__( self, size_words ):
    # Record size.
    self.size = ( size_words * 4 )
    # Width of data input.
    self.dw   = Signal( 3, reset = 0b000 )
    # Data storage.
    self.data = Memory( width = 32, depth = size_words, init = ( 0x000000 for i in range( size_words ) ) )
    # Read and write ports.
    self.r = self.data.read_port()
    self.w = self.data.write_port()

    # Initialize Wishbone bus arbiter.
    self.arb = Arbiter( addr_width = ceil( log2( self.size + 1 ) ),
                        data_width = 32 )
    self.arb.bus.memory_map = MemoryMap(
      addr_width = self.arb.bus.addr_width,
      data_width = self.arb.bus.data_width,
      alignment = 0 )

  def new_bus( self ):
    # Initialize a new Wishbone bus interface.
    bus = Interface( addr_width = self.arb.bus.addr_width,
                     data_width = self.arb.bus.data_width )
    bus.memory_map = MemoryMap( addr_width = bus.addr_width,
                                data_width = bus.data_width,
                                alignment = 0 )
    self.arb.add( bus )
    return bus

  def elaborate( self, platform ):
    # Core RAM module.
    m = Module()
    m.submodules.r = self.r
    m.submodules.w = self.w
    m.submodules.arb = self.arb

    # Ack two cycles after activation, for memory port access and
    # synchronous read-out (to prevent combinatorial loops).
    rws = Signal( 1, reset = 0 )
    m.d.sync += rws.eq( self.arb.bus.cyc )
    m.d.sync += self.arb.bus.ack.eq( self.arb.bus.cyc & rws )
    m.d.comb += [
      # Set the RAM port addresses.
      self.r.addr.eq( self.arb.bus.adr[ 2: ] ),
      self.w.addr.eq( self.arb.bus.adr[ 2: ] ),
      # Set the 'write enable' flag once the reads are valid.
      self.w.en.eq( self.arb.bus.we )
    ]

    # Read / Write logic: synchronous to avoid combinatorial loops.
    m.d.comb += self.w.data.eq( self.r.data )
    with m.Switch( self.arb.bus.adr[ :2 ] ):
      with m.Case( 0b00 ):
        m.d.sync += self.arb.bus.dat_r.eq( self.r.data )
        with m.Switch( self.dw ):
          with m.Case( RAM_DW_8 ):
            m.d.comb += self.w.data.bit_select( 0, 8 ).eq(
              self.arb.bus.dat_w[ :8 ] )
          with m.Case( RAM_DW_16 ):
            m.d.comb += self.w.data.bit_select( 0, 16 ).eq(
              self.arb.bus.dat_w[ :16 ] )
          with m.Case():
            m.d.comb += self.w.data.eq( self.arb.bus.dat_w )
      with m.Case( 0b01 ):
        m.d.sync += self.arb.bus.dat_r.eq( self.r.data[ 8 : 32 ] )
        with m.Switch( self.dw ):
          with m.Case( RAM_DW_8 ):
            m.d.comb += self.w.data.bit_select( 8, 8 ).eq(
              self.arb.bus.dat_w[ :8 ] )
          with m.Case( RAM_DW_16 ):
            m.d.comb += self.w.data.bit_select( 8, 16 ).eq(
              self.arb.bus.dat_w[ :16 ] )
      with m.Case( 0b10 ):
        m.d.sync += self.arb.bus.dat_r.eq( self.r.data[ 16 : 32 ] )
        with m.Switch( self.dw ):
          with m.Case( RAM_DW_8 ):
            m.d.comb += self.w.data.bit_select( 16, 8 ).eq(
              self.arb.bus.dat_w[ :8 ] )
          with m.Case( RAM_DW_16 ):
            m.d.comb += self.w.data.bit_select( 16, 16 ).eq(
              self.arb.bus.dat_w[ :16 ] )
      with m.Case( 0b11 ):
        m.d.sync += self.arb.bus.dat_r.eq( self.r.data[ 24 : 32 ] )
        with m.Switch( self.dw ):
          with m.Case( RAM_DW_8 ):
            m.d.comb += self.w.data.bit_select( 24, 8 ).eq(
              self.arb.bus.dat_w[ :8 ] )

    # End of RAM module definition.
    return m

