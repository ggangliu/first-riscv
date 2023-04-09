from amaranth import *
from amaranth.back import *
from amaranth_soc.wishbone import *
from amaranth_soc.memory import *

import sys
sys.path.append("..")

from src.isa import *
from src.ram import *

#############################################################
# "RISC-V Memories" module.                                 #
# This directs memory accesses to the appropriate submodule #
# based on the memory space defined by the 3 MSbits.        #
# (None of this is actually part of the RISC-V spec)        #
# Current memory spaces:                                    #
# *  0x0------- = ROM                                       #
# *  0x2------- = RAM                                       #
# *  0x4------- = Peripherals                               #
#############################################################

class RV_Memory( Elaboratable ):
  def __init__( self, rom_module, ram_words ):
    # Memory multiplexers.
    # Data bus multiplexer.
    self.data_mux = Decoder( addr_width = 32,
                         data_width = 32,
                         alignment = 0 )
    # Instruction bus multiplexer.
    self.inst_mux = Decoder( addr_width = 32,
                         data_width = 32,
                         alignment = 0 )

    # Add ROM and RAM buses to the data multiplexer.
    self.rom = rom_module
    self.ram = RAM( ram_words )
    self.rom_data = self.rom.new_bus()
    self.ram_data = self.ram.new_bus()
    self.data_mux.add( self.rom_data,    addr = 0x00000000 )
    self.data_mux.add( self.ram_data,    addr = 0x20000000 )
    # (Later, when we write peripherals, they'll be added to the data bus here)

    # Add ROM and RAM buses to the instruction multiplexer.
    self.rom_inst = self.rom.new_bus()
    self.ram_inst = self.ram.new_bus()
    self.inst_mux.add( self.rom_inst,    addr = 0x00000000 )
    self.inst_mux.add( self.ram_inst,    addr = 0x20000000 )
    # (No peripherals on the instruction bus)

  def elaborate( self, platform ):
    m = Module()
    # Register the multiplexers, peripherals, and memory submodules.
    m.submodules.data_mux     = self.data_mux
    m.submodules.inst_mux     = self.inst_mux
    m.submodules.rom          = self.rom
    m.submodules.ram          = self.ram

    # Currently, all bus cycles are single-transaction.
    # So set the 'strobe' signals equal to the 'cycle' ones.
    m.d.comb += [
      self.data_mux.bus.stb.eq( self.data_mux.bus.cyc ),
      self.inst_mux.bus.stb.eq( self.inst_mux.bus.cyc )
    ]

    return m
