from amaranth import *
from math import ceil, log2 
from amaranth.sim import Simulator, Tick, Settle 
from amaranth.back import *
from amaranth_soc.wishbone import *
from amaranth_soc.memory import *

import os, sys
import warnings
sys.path.append("..")

from src.isa import *

# CSR Addresses for the supported subset of 'Machine-Level ISA' CSRs.
# Machine information registers:
CSRA_MVENDORID  = 0xF11
CSRA_MARCHID    = 0xF12
CSRA_MIMPID     = 0xF13
CSRA_MHARTID    = 0xF14
# Machine trap setup:
CSRA_MSTATUS    = 0x300
CSRA_MISA       = 0x301
CSRA_MIE        = 0x304
CSRA_MTVEC      = 0x305
CSRA_MSTATUSH   = 0x310
# Machine trap handling:
CSRA_MSCRATCH   = 0x340
CSRA_MEPC       = 0x341
CSRA_MCAUSE     = 0x342
CSRA_MTVAL      = 0x343
CSRA_MIP        = 0x344
CSRA_MTINST     = 0x34A
CSRA_MTVAL2     = 0x34B
# Machine counters:
CSRA_MCYCLE           = 0xB00
CSRA_MINSTRET         = 0xB02
# Machine counter setup:
CSRA_MCOUNTINHIBIT    = 0x320

# CSR memory map definitions.
CSRS = {
  'minstret': {
    'c_addr': CSRA_MINSTRET,
    'bits': { 'instrs': [ 0, 15, 'rw', 0 ] }
  },
  'mstatus': {
    'c_addr': CSRA_MSTATUS,
    'bits': {
      'mie':  [ 3,  3,  'rw', 0 ],
      'mpie': [ 7,  7,  'r',  0 ]
     }
  },
  'mcause': {
    'c_addr': CSRA_MCAUSE,
    'bits': {
      'interrupt': [ 31, 31, 'rw', 0 ],
      'ecode':     [ 0, 30,  'rw', 0 ]
    }
  },
  'mtval': {
    'c_addr': CSRA_MTVAL,
    'bits': { 'einfo': [ 0, 31, 'rw', 0 ] }
  },
  'mtvec': {
    'c_addr': CSRA_MTVEC,
    'bits': {
      'mode': [ 0, 0,  'rw', 0 ],
      'base': [ 2, 31, 'rw', 0 ]
    }
  },
  'mepc': {
    'c_addr': CSRA_MEPC,
    'bits': {
      'mepc': [ 2, 31, 'rw', 0 ]
    }
  },
}

#############################################
# 'Control and Status Registers' file.      #
# This contains logic for handling the      #
# 'system' opcode, which is used to         #
# read/write CSRs in the base ISA.          #
# CSR named constants are in `isa.py`.      #
#############################################

# Core "CSR" class, which addresses Control and Status Registers.
class CSR( Elaboratable, Interface ):
  def __init__( self ):
    # CSR function select signal.
    self.f  = Signal( 3,  reset = 0b000 )
    # Actual data to write (depends on write/set/clear function)
    self.wd = Signal( 32, reset = 0x00000000 )
    # Initialize wishbone bus interface.
    Interface.__init__( self, addr_width = 12, data_width = 32 )
    self.memory_map = MemoryMap( addr_width = self.addr_width,
                                 data_width = self.data_width,
                                 alignment = 0 )
    # Initialize required CSR signals and constants.
    for cname, reg in CSRS.items():
      for bname, bits in reg[ 'bits' ].items():
        if 'w' in bits[ 2 ]:
          setattr( self,
                   "%s_%s"%( cname, bname ),
                   Signal( bits[ 1 ] - bits[ 0 ] + 1,
                           name = "%s_%s"%( cname, bname ),
                           reset = bits[ 3 ] ) )
        elif 'r' in bits[ 2 ]:
          setattr( self,
                   "%s_%s"%( cname, bname ),
                   Const( bits[ 3 ] ) )
  
  def elaborate( self, platform ):
    m = Module()

    # Read values default to 0.
    m.d.comb += self.dat_r.eq( 0 )

    with m.Switch( self.adr ):
      # Generate logic for supported CSR reads / writes.
      for cname, reg in CSRS.items():
        with m.Case( reg['c_addr'] ):
          # Assemble the read value from individual bitfields.
          for bname, bits in reg[ 'bits' ].items():
            if 'r' in bits[ 2 ]:
              m.d.comb += self.dat_r \
                .bit_select( bits[ 0 ], bits[ 1 ] - bits[ 0 ] + 1 ) \
                .eq( getattr( self, "%s_%s"%( cname, bname ) ) )
            with m.If( self.we == 1 ):
              # Writes are enabled; set new values on the next tick.
              if 'w' in bits[ 2 ]:
                m.d.sync += getattr( self, "%s_%s"%( cname, bname ) ) \
                  .eq( self.wd[ bits[ 0 ] : ( bits[ 1 ] + 1 ) ] )

    # Process 32-bit CSR write logic.
    with m.If( ( self.f[ :2 ] ) == 0b01 ):
      # 'Write' - set the register to the input value.
      m.d.comb += self.wd.eq( self.dat_w )
    with m.Elif( ( ( self.f[ :2 ] ) == 0b10 ) & ( self.dat_w != 0 ) ):
      # 'Set' - set bits which are set in the input value.
      m.d.comb +=  self.wd.eq( self.dat_w | self.dat_r )
    with m.Elif( ( ( self.f[ :2 ] ) == 0b11 ) & ( self.dat_w != 0 ) ):
      # 'Clear' - reset bits which are set in the input value.
      m.d.comb += self.wd.eq( ~( self.dat_w ) & self.dat_r )
    with m.Else():
      # Read-only operation; set write data to current value.
      m.d.comb += self.wd.eq( self.dat_r )

    return m
