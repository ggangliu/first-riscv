# alu, ldst, pipeline compose a core 
from amaranth import *
from amaranth.back import *
from amaranth.sim import *
from amaranth.hdl.ast import Past

import os
import sys
import warnings
sys.path.append("..")

from src.alu import *
from src.csr import *
from src.isa import *
from src.spi_flash import *
from src.rom import *
from src.rv_mem import *

# define SP module which works by pipeline
class core( Elaboratable ):
  def __init__( self, rom_module ):
    # 'Reset' signal for clock domains.
    self.clk_rst = Signal( reset = 0b0, reset_less = True )
    # Program Counter register.
    self.pc = Signal( 32, reset = 0x00000000 )
    self.opcode = Signal( 7, reset = 0x00000000 )
    # The main 32 CPU registers.
    self.r  = Memory( width = 32, depth = 32,
                          init = ( 0x00000000 for i in range( 32 ) ) )

    # CPU submodules:
    # Memory access ports for rs1, rs2, and rd.
    self.rs1     = self.r.read_port()
    self.rs2     = self.r.read_port()
    self.rd      = self.r.write_port()
    # The ALU submodule which performs logical operations.
    self.alu    = ALU()
    # CSR 'system registers'.
    self.csr    = CSR()
    # Memory module to hold peripherals and ROM / RAM module(s)
    # (4KB of RAM = 1024 words)
    self.mem    = RV_Memory( rom_module, 1024 )

  # SP object's 'elaborate' method to generate the hardware logic.
  def elaborate( self, platform ):
    # Core SP module.
    m = Module()
    # Register the ALU, CSR, and memory submodules.
    m.submodules.alu = self.alu
    m.submodules.csr = self.csr
    m.submodules.mem = self.mem
    # Register the SP register read/write ports.
    m.submodules.rs1  = self.rs1
    m.submodules.rs2  = self.rs2
    m.submodules.rd   = self.rd

    # Pipeline register
    IF2ID_IR  = Signal(unsigned( 32 ), reset = 0)
    ID2EX  = Signal(unsigned( 32 ), reset = 0)
    EX2MEM = Signal(unsigned( 32 ), reset = 0)
    MEM2WB = Signal(unsigned( 32 ), reset = 0)
    
    
    # Wait-state counter to let internal memories load.
    iws = Signal( 2, reset = 0 )

    # IF
    m.d.sync += [
      self.pc.eq( self.pc + 4 )
    ]
    
    m.d.comb += [
      # Instruction bus address is always set to the program counter.
      self.mem.inst_mux.bus.adr.eq( self.pc ),
      IF2ID_IR = self.mem.inst_mux.bus.dat_r
    ]
    
    # ID
    m.d.sync += [
      self.rs1.addr.eq( IF2ID_IR[ 15 : 20 ] ),  # rs1
      self.rs2.addr.eq( IF2ID_IR[ 20 : 25 ] ),  # rs2
      self.rd.addr.eq( IF2ID_IR[ 7  : 12 ] ),   # rd
      self.opcode.eq( IF2ID_IR[ 0 : 7 ] )       # opcode
    ]
    
    m.d.comb += [
      # Store data and width are always wired the same.
      self.mem.ram.dw.eq( self.mem.inst_mux.bus.dat_r[ 12 : 15 ] ), # funct3
      self.mem.data_mux.bus.dat_w.eq( self.rs2.data ),
      self.mem.inst_mux.bus.cyc.eq( iws == 0 )
    ]
    
    
    
    # EX
    
    
    # MEM
    
    
    # WB

      # Decoder switch case:
      with m.Switch( self.opcode ):    # opcode
        # LUI / AUIPC / R-type / I-type instructions: apply
        # pending CPU register write.
        with m.Case( '0-10-11' ):
          m.d.comb += self.rd.en.eq( self.rd.addr != 0 )
        # JAL / JALR instructions: jump to a new address and place
        # the 'return PC' in the destination register (rc).
        with m.Case( '110-111' ):
          m.d.sync += self.pc.eq(
            Mux( self.mem.inst_mux.bus.dat_r[ 3 ],
                 self.pc + Cat(
                   Repl( 0, 1 ),
                   self.mem.inst_mux.bus.dat_r[ 21: 31 ],
                   self.mem.inst_mux.bus.dat_r[ 20 ],
                   self.mem.inst_mux.bus.dat_r[ 12 : 20 ],
                   Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 12 ) ),
                 self.ra.data + Cat(
                   self.mem.inst_mux.bus.dat_r[ 20 : 32 ],
                   Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 20 ) ) ),
          )
          m.d.comb += self.rd.en.eq( self.rd.addr != 0 )

        # Conditional branch instructions: similar to JAL / JALR,
        # but only take the branch if the condition is met.
        with m.Case( OP_BRANCH ):
          # Check the ALU result. If it is zero, then:
          # a == b for BEQ/BNE, or a >= b for BLT[U]/BGE[U].
          with m.If( ( ( self.alu.y == 0 ) ^
                         self.mem.inst_mux.bus.dat_r[ 12 ] ) !=
                       self.mem.inst_mux.bus.dat_r[ 14 ] ):
            # Branch only if the condition is met.
            m.d.sync += self.pc.eq( self.pc + Cat(
              Repl( 0, 1 ),
              self.mem.inst_mux.bus.dat_r[ 8 : 12 ],
              self.mem.inst_mux.bus.dat_r[ 25 : 31 ],
              self.mem.inst_mux.bus.dat_r[ 7 ],
              Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 20 ) ) )

        # Load / Store instructions: perform memory access
        # through the data bus.
        with m.Case( '0-00011' ):
          # Trigger a trap if the address is mis-aligned.
          # * Byte accesses are never mis-aligned.
          # * Word-aligned accesses are never mis-aligned.
          # * Halfword accesses are only mis-aligned when both of
          #   the address' LSbits are 1s.
          with m.If( ( ( self.mem.data_mux.bus.adr[ :2 ] == 0 ) |
                       ( self.mem.inst_mux.bus.dat_r[ 12 : 14 ] == 0 ) |
                       ( ~( self.mem.data_mux.bus.adr[ 0 ] &
                            self.mem.data_mux.bus.adr[ 1 ] &
                            self.mem.inst_mux.bus.dat_r[ 12 ] ) ) ) == 0 ):
            self.trigger_trap( m,
              Cat( Repl( 0, 1 ),
                   self.mem.inst_mux.bus.dat_r[ 5 ],
                   Repl( 1, 1 ) ),
              Past( self.pc ) )
          with m.Else():
            # Activate the data bus.
            m.d.comb += [
              self.mem.data_mux.bus.cyc.eq( 1 ),
              # Stores only: set the 'write enable' bit.
              self.mem.data_mux.bus.we.eq( self.mem.inst_mux.bus.dat_r[ 5 ] )
            ]
            # Don't proceed until the memory access finishes.
            with m.If( self.mem.data_mux.bus.ack == 0 ):
              m.d.sync += [
                self.pc.eq( self.pc ),
                iws.eq( 2 )
              ]
            # Loads only: write to the CPU register.
            with m.Elif( self.mem.inst_mux.bus.dat_r[ 5 ] == 0 ):
              m.d.comb += self.rc.en.eq( self.rc.addr != 0 )

        # System call instruction: ECALL, EBREAK, MRET,
        # and atomic CSR operations.
        with m.Case( OP_SYSTEM ):
          with m.If( self.mem.inst_mux.bus.dat_r[ 12 : 15 ] == F_TRAPS ):
            with m.Switch( self.mem.inst_mux.bus.dat_r[ 20 : 22 ] ):
              # An 'empty' ECALL instruction should raise an
              # 'environment-call-from-M-mode" exception.
              with m.Case( 0 ):
                self.trigger_trap( m, TRAP_ECALL, Past( self.pc ) )
              # "EBREAK" instruction: enter the interrupt context
              # with 'breakpoint' as the cause of the exception.
              with m.Case( 1 ):
                self.trigger_trap( m, TRAP_BREAK, Past( self.pc ) )
              # 'MRET' jumps to the stored 'pre-trap' PC in the
              # 30 MSbits of the MEPC CSR.
              with m.Case( 2 ):
                m.d.sync += [
                  self.csr.mstatus_mie.eq( 1 ),
                  self.pc.eq( Cat( Repl( 0, 2 ),
                                   self.csr.mepc_mepc ) )
                ]
          # Defer to the CSR module for atomic CSR reads/writes.
          # 'CSRR[WSC]': Write/Set/Clear CSR value from a register.
          # 'CSRR[WSC]I': Write/Set/Clear CSR value from immediate.
          with m.Else():
            m.d.comb += [
              self.rc.data.eq( self.csr.dat_r ),
              self.rc.en.eq( self.rc.addr != 0 ),
              self.csr.we.eq( 1 )
            ]

        # FENCE instruction: clear any I-caches and ensure all
        # memory operations are applied. There is no I-cache,
        # and there is no caching of memory operations.
        # There is also no pipelining. So...this is a nop.
        with m.Case( OP_FENCE ):
          pass

    # 'Always-on' decode/execute logic:
    with m.Switch( self.mem.inst_mux.bus.dat_r[ 0 : 7 ] ):
      # LUI / AUIPC instructions: set destination register to
      # 20 upper bits, +pc for AUIPC.
      with m.Case( '0-10111' ):
        m.d.comb += self.rc.data.eq(
          Mux( self.mem.inst_mux.bus.dat_r[ 5 ], 0, self.pc ) +
          Cat( Repl( 0, 12 ),
               self.mem.inst_mux.bus.dat_r[ 12 : 32 ] ) )

      # JAL / JALR instructions: set destination register to
      # the 'return PC' value.
      with m.Case( '110-111' ):
        m.d.comb += self.rc.data.eq( self.pc + 4 )

      # Conditional branch instructions:
      # set us up the ALU for the condition check.
      with m.Case( OP_BRANCH ):
        # BEQ / BNE: use SUB ALU operation to check equality.
        # BLT / BGE / BLTU / BGEU: use SLT or SLTU ALU operation.
        m.d.comb += [
          self.alu.a.eq( self.ra.data ),
          self.alu.b.eq( self.rb.data ),
          self.alu.f.eq( Mux(
            self.mem.inst_mux.bus.dat_r[ 14 ],
            Cat( self.mem.inst_mux.bus.dat_r[ 13 ], 0b001 ),
            0b1000 ) )
        ]

      # Load instructions: Set the memory address and data register.
      with m.Case( OP_LOAD ):
        m.d.comb += [
          self.mem.data_mux.bus.adr.eq( self.ra.data +
            Cat( self.mem.inst_mux.bus.dat_r[ 20 : 32 ],
                 Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 20 ) ) ),
          self.rc.data.bit_select( 0, 8 ).eq(
            self.mem.data_mux.bus.dat_r[ :8 ] )
        ]
        with m.If( self.mem.inst_mux.bus.dat_r[ 12 ] ):
          m.d.comb += [
            self.rc.data.bit_select( 8, 8 ).eq(
              self.mem.data_mux.bus.dat_r[ 8 : 16 ] ),
            self.rc.data.bit_select( 16, 16 ).eq(
              Repl( ( self.mem.inst_mux.bus.dat_r[ 14 ] == 0 ) &
                    self.mem.data_mux.bus.dat_r[ 15 ], 16 ) )
          ]
        with m.Elif( self.mem.inst_mux.bus.dat_r[ 13 ] ):
          m.d.comb += self.rc.data.bit_select( 8, 24 ).eq(
            self.mem.data_mux.bus.dat_r[ 8 : 32 ] )
        with m.Else():
          m.d.comb += self.rc.data.bit_select( 8, 24 ).eq(
            Repl( ( self.mem.inst_mux.bus.dat_r[ 14 ] == 0 ) &
                  self.mem.data_mux.bus.dat_r[ 7 ], 24 ) )

      # Store instructions: Set the memory address.
      with m.Case( OP_STORE ):
        m.d.comb += self.mem.data_mux.bus.adr.eq( self.ra.data +
          Cat( self.mem.inst_mux.bus.dat_r[ 7 : 12 ],
               self.mem.inst_mux.bus.dat_r[ 25 : 32 ],
               Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 20 ) ) )

      # R-type ALU operation: set inputs for rc = ra ? rb
      with m.Case( OP_REG ):
        # Implement left shifts using the right shift ALU operation.
        with m.If( self.mem.inst_mux.bus.dat_r[ 12 : 15 ] == 0b001 ):
          m.d.comb += [
            self.alu.a.eq( FLIP( self.ra.data ) ),
            self.alu.f.eq( 0b0101 ),
            self.rc.data.eq( FLIP( self.alu.y ) )
          ]
        with m.Else():
          m.d.comb += [
            self.alu.a.eq( self.ra.data ),
            self.alu.f.eq( Cat(
              self.mem.inst_mux.bus.dat_r[ 12 : 15 ],
              self.mem.inst_mux.bus.dat_r[ 30 ] ) ),
            self.rc.data.eq( self.alu.y ),
          ]
        m.d.comb += self.alu.b.eq( self.rb.data )

      # I-type ALU operation: set inputs for rc = ra ? immediate
      with m.Case( OP_IMM ):
        # Shift operations are a bit different from normal I-types.
        # They use 'funct7' bits like R-type operations, and the
        # left shift can be implemented as a right shift to avoid
        # having two barrel shifters in the ALU.
        with m.If( self.mem.inst_mux.bus.dat_r[ 12 : 14 ] == 0b01 ):
          with m.If( self.mem.inst_mux.bus.dat_r[ 14 ] == 0 ):
            m.d.comb += [
              self.alu.a.eq( FLIP( self.ra.data ) ),
              self.alu.f.eq( 0b0101 ),
              self.rc.data.eq( FLIP( self.alu.y ) ),
            ]
          with m.Else():
            m.d.comb += [
              self.alu.a.eq( self.ra.data ),
              self.alu.f.eq( Cat( 0b101, self.mem.inst_mux.bus.dat_r[ 30 ] ) ),
              self.rc.data.eq( self.alu.y ),
            ]
        # Normal I-type operation:
        with m.Else():
          m.d.comb += [
            self.alu.a.eq( self.ra.data ),
            self.alu.f.eq( self.mem.inst_mux.bus.dat_r[ 12 : 15 ] ),
            self.rc.data.eq( self.alu.y ),
          ]
        # Shared I-type logic:
        m.d.comb += self.alu.b.eq( Cat(
          self.mem.inst_mux.bus.dat_r[ 20 : 32 ],
          Repl( self.mem.inst_mux.bus.dat_r[ 31 ], 20 ) ) )

    # End of CPU module definition.
    return m

