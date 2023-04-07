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

# Optional: Enable verbose output for debugging.
#os.environ["NMIGEN_verbose"] = "Yes"

# CPU module.
class single_cycle_core( Elaboratable ):
  def __init__( self, rom_module ):
    # CPU signals:
    # 'Reset' signal for clock domains.
    self.clk_rst = Signal( reset = 0b0, reset_less = True )
    # Program Counter register.
    self.pc = Signal( 32, reset = 0x00000000 )
    # The main 32 CPU registers.
    self.register_file      = Memory( width = 32, depth = 32,
                          init = ( 0x00000000 for i in range( 32 ) ) )

    # CPU submodules:
    # Memory access ports for rs1 (ra), rs2 (rb), and rd (rc).
    self.rs1    = self.register_file.read_port()
    self.rs2    = self.register_file.read_port()
    self.rd     = self.register_file.write_port()
    # The ALU submodule which performs logical operations.
    self.alu    = ALU()
    # CSR 'system registers'.
    self.csr    = CSR()
    # Memory module to hold peripherals and ROM / RAM module(s)
    # (4KB of RAM = 1024 words)
    self.mem    = RV_Memory( rom_module, 1024 )

  # Helper method to enter a trap handler: jump to the appropriate
  # address, and set the MCAUSE / MEPC CSRs.
  def trigger_trap( self, m, trap_num, return_pc ):
    m.d.sync += [
      # Set mcause, mepc, interrupt context flag.
      self.csr.mcause_interrupt.eq( 0 ),
      self.csr.mcause_ecode.eq( trap_num ),
      self.csr.mepc_mepc.eq( return_pc.bit_select( 2, 30 ) ),
      # Disable interrupts globally until MRET or CSR write.
      self.csr.mstatus_mie.eq( 0 ),
      # Set the program counter to the interrupt handler address.
      self.pc.eq( Cat( Repl( 0, 2 ),
                     ( self.csr.mtvec_base +
                       Mux( self.csr.mtvec_mode, trap_num, 0 ) ) ) )
    ]

  # CPU object's 'elaborate' method to generate the hardware logic.
  def elaborate( self, platform ):
    # Core CPU module.
    m = Module()
    # Register the ALU, CSR, and memory submodules.
    m.submodules.alu = self.alu
    m.submodules.csr = self.csr
    m.submodules.mem = self.mem
    # Register the CPU register read/write ports.
    m.submodules.ra  = self.rs1
    m.submodules.rb  = self.rs2
    m.submodules.rc  = self.rd

    # Wait-state counter to let internal memories load.
    iws = Signal( 2, reset = 0 )

    self.instruction = Signal( 32, reset = 0 )

    m.d.sync += self.instruction.eq( self.mem.imux.bus.dat_r) 
    # Top-level combinatorial logic.
    m.d.comb += [
      # Set CPU register access addresses.
      self.rs1.addr.eq( self.instruction[ 15 : 20 ] ),
      self.rs2.addr.eq( self.instruction[ 20 : 25 ] ),
      self.rd.addr.eq( self.instruction[ 7  : 12 ] ),
      # self.instructionion bus address is always set to the program counter.
      self.mem.imux.bus.adr.eq( self.pc ),

      # Store data and width are always wired the same.
      self.mem.ram.dw.eq( self.instruction[ 12 : 15 ] ),
      self.mem.dmux.bus.dat_w.eq( self.rs2.data ),
    ]

    # Trigger an 'self.instructionion mis-aligned' trap if necessary. 
    with m.If( self.pc[ :2 ] != 0 ):
      self.trigger_trap( m, TRAP_IMIS, Past( self.pc ) )
    with m.Else():
      # I-bus is active until it completes a transaction.
      m.d.comb += self.mem.imux.bus.cyc.eq( iws == 0 )

    # Wait a cycle after 'ack' to load the appropriate CPU registers.
    with m.If( self.mem.imux.bus.ack ):
      # Increment the wait-state counter.
      # (This also lets the self.instructionion bus' 'cyc' signal fall.)
      m.d.sync += iws.eq( 1 )
      with m.If( iws == 0 ):
        # Increment pared-down 32-bit MINSTRET counter.
        # I'd remove the whole MINSTRET CSR to save space, but the
        # test harnesses depend on it to count instructions.
        # TODO: This is OBO; it'll be 1 before the first retire.
        m.d.sync += self.csr.minstret_instrs.eq(
          self.csr.minstret_instrs + 1 )

    # Execute the current self.instructionion, once it loads.
    with m.If( iws != 0 ):
      # Increment the PC and reset the wait-state unless
      # otherwise specified.
      m.d.sync += [
        self.pc.eq( self.pc + 4 ),
        iws.eq( 0 )
      ]

      # Decoder switch case:
      with m.Switch( self.instruction[ 0 : 7 ] ):
        # LUI / AUIPC / R-type / I-type self.instructionions: apply
        # pending CPU register write.
        with m.Case( '0-10-11' ):
          m.d.comb += self.rd.en.eq( self.rd.addr != 0 )

        # JAL / JALR self.instructionions: jump to a new address and place
        # the 'return PC' in the destination register (rc).
        with m.Case( '110-111' ):
          m.d.sync += self.pc.eq(
            Mux( self.instruction[ 3 ],
                 self.pc + Cat(
                   Repl( 0, 1 ),
                   self.instruction[ 21: 31 ],
                   self.instruction[ 20 ],
                   self.instruction[ 12 : 20 ],
                   Repl( self.instruction[ 31 ], 12 ) ),
                 self.rs1.data + Cat(
                   self.instruction[ 20 : 32 ],
                   Repl( self.instruction[ 31 ], 20 ) ) ),
          )
          m.d.comb += self.rd.en.eq( self.rd.addr != 0 )

        # Conditional branch self.instructionions: similar to JAL / JALR,
        # but only take the branch if the condition is met.
        with m.Case( OP_BRANCH ):
          # Check the ALU result. If it is zero, then:
          # a == b for BEQ/BNE, or a >= b for BLT[U]/BGE[U].
          with m.If( ( ( self.alu.y == 0 ) ^
                         self.instruction[ 12 ] ) !=
                       self.instruction[ 14 ] ):
            # Branch only if the condition is met.
            m.d.sync += self.pc.eq( self.pc + Cat(
              Repl( 0, 1 ),
              self.instruction[ 8 : 12 ],
              self.instruction[ 25 : 31 ],
              self.instruction[ 7 ],
              Repl( self.instruction[ 31 ], 20 ) ) )

        # Load / Store self.instructionions: perform memory access
        # through the data bus.
        with m.Case( '0-00011' ):
          # Trigger a trap if the address is mis-aligned.
          # * Byte accesses are never mis-aligned.
          # * Word-aligned accesses are never mis-aligned.
          # * Halfword accesses are only mis-aligned when both of
          #   the address' LSbits are 1s.
          with m.If( ( ( self.mem.dmux.bus.adr[ :2 ] == 0 ) |
                       ( self.instruction[ 12 : 14 ] == 0 ) |
                       ( ~( self.mem.dmux.bus.adr[ 0 ] &
                            self.mem.dmux.bus.adr[ 1 ] &
                            self.instruction[ 12 ] ) ) ) == 0 ):
            self.trigger_trap( m,
              Cat( Repl( 0, 1 ),
                   self.instruction[ 5 ],
                   Repl( 1, 1 ) ),
              Past( self.pc ) )
          with m.Else():
            # Activate the data bus.
            m.d.comb += [
              self.mem.dmux.bus.cyc.eq( 1 ),
              # Stores only: set the 'write enable' bit.
              self.mem.dmux.bus.we.eq( self.instruction[ 5 ] )
            ]
            # Don't proceed until the memory access finishes.
            with m.If( self.mem.dmux.bus.ack == 0 ):
              m.d.sync += [
                self.pc.eq( self.pc ),
                iws.eq( 2 )
              ]
            # Loads only: write to the CPU register.
            with m.Elif( self.instruction[ 5 ] == 0 ):
              m.d.comb += self.rd.en.eq( self.rd.addr != 0 )

        # System call self.instructionion: ECALL, EBREAK, MRET,
        # and atomic CSR operations.
        with m.Case( OP_SYSTEM ):
          with m.If( self.instruction[ 12 : 15 ] == F_TRAPS ):
            with m.Switch( self.instruction[ 20 : 22 ] ):
              # An 'empty' ECALL self.instructionion should raise an
              # 'environment-call-from-M-mode" exception.
              with m.Case( 0 ):
                self.trigger_trap( m, TRAP_ECALL, Past( self.pc ) )
              # "EBREAK" self.instructionion: enter the interrupt context
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
              self.rd.data.eq( self.csr.dat_r ),
              self.rd.en.eq( self.rd.addr != 0 ),
              self.csr.we.eq( 1 )
            ]

        # FENCE self.instructionion: clear any I-caches and ensure all
        # memory operations are applied. There is no I-cache,
        # and there is no caching of memory operations.
        # There is also no pipelining. So...this is a nop.
        with m.Case( OP_FENCE ):
          pass

    # 'Always-on' decode/execute logic:
    with m.Switch( self.instruction[ 0 : 7 ] ):
      # LUI / AUIPC self.instructionions: set destination register to
      # 20 upper bits, +pc for AUIPC.
      with m.Case( '0-10111' ):
        m.d.comb += self.rd.data.eq(
          Mux( self.instruction[ 5 ], 0, self.pc ) +
          Cat( Repl( 0, 12 ),
               self.instruction[ 12 : 32 ] ) )

      # JAL / JALR self.instructionions: set destination register to
      # the 'return PC' value.
      with m.Case( '110-111' ):
        m.d.comb += self.rd.data.eq( self.pc + 4 )

      # Conditional branch self.instructionions:
      # set us up the ALU for the condition check.
      with m.Case( OP_BRANCH ):
        # BEQ / BNE: use SUB ALU operation to check equality.
        # BLT / BGE / BLTU / BGEU: use SLT or SLTU ALU operation.
        m.d.comb += [
          self.alu.a.eq( self.rs1.data ),
          self.alu.b.eq( self.rs2.data ),
          self.alu.f.eq( Mux(
            self.instruction[ 14 ],
            Cat( self.instruction[ 13 ], 0b001 ),
            0b1000 ) )
        ]

      # Load self.instructionions: Set the memory address and data register.
      with m.Case( OP_LOAD ):
        m.d.comb += [
          self.mem.dmux.bus.adr.eq( self.rs1.data +
            Cat( self.instruction[ 20 : 32 ],
                 Repl( self.instruction[ 31 ], 20 ) ) ),
          self.rd.data.bit_select( 0, 8 ).eq(
            self.mem.dmux.bus.dat_r[ :8 ] )
        ]
        with m.If( self.instruction[ 12 ] ):
          m.d.comb += [
            self.rd.data.bit_select( 8, 8 ).eq(
              self.mem.dmux.bus.dat_r[ 8 : 16 ] ),
            self.rd.data.bit_select( 16, 16 ).eq(
              Repl( ( self.instruction[ 14 ] == 0 ) &
                    self.mem.dmux.bus.dat_r[ 15 ], 16 ) )
          ]
        with m.Elif( self.instruction[ 13 ] ):
          m.d.comb += self.rd.data.bit_select( 8, 24 ).eq(
            self.mem.dmux.bus.dat_r[ 8 : 32 ] )
        with m.Else():
          m.d.comb += self.rd.data.bit_select( 8, 24 ).eq(
            Repl( ( self.instruction[ 14 ] == 0 ) &
                  self.mem.dmux.bus.dat_r[ 7 ], 24 ) )

      # Store self.instructionions: Set the memory address.
      with m.Case( OP_STORE ):
        m.d.comb += self.mem.dmux.bus.adr.eq( self.rs1.data +
          Cat( self.instruction[ 7 : 12 ],
               self.instruction[ 25 : 32 ],
               Repl( self.instruction[ 31 ], 20 ) ) )

      # R-type ALU operation: set inputs for rc = ra ? rb
      with m.Case( OP_REG ):
        # Implement left shifts using the right shift ALU operation.
        with m.If( self.instruction[ 12 : 15 ] == 0b001 ):
          m.d.comb += [
            self.alu.a.eq( FLIP( self.rs1.data ) ),
            self.alu.f.eq( 0b0101 ),
            self.rd.data.eq( FLIP( self.alu.y ) )
          ]
        with m.Else():
          m.d.comb += [
            self.alu.a.eq( self.rs1.data ),
            self.alu.f.eq( Cat(
              self.instruction[ 12 : 15 ],
              self.instruction[ 30 ] ) ),
            self.rd.data.eq( self.alu.y ),
          ]
        m.d.comb += self.alu.b.eq( self.rs2.data )

      # I-type ALU operation: set inputs for rc = ra ? immediate
      with m.Case( OP_IMM ):
        # Shift operations are a bit different from normal I-types.
        # They use 'funct7' bits like R-type operations, and the
        # left shift can be implemented as a right shift to avoid
        # having two barrel shifters in the ALU.
        with m.If( self.instruction[ 12 : 14 ] == 0b01 ):
          with m.If( self.instruction[ 14 ] == 0 ):
            m.d.comb += [
              self.alu.a.eq( FLIP( self.rs1.data ) ),
              self.alu.f.eq( 0b0101 ),
              self.rd.data.eq( FLIP( self.alu.y ) ),
            ]
          with m.Else():
            m.d.comb += [
              self.alu.a.eq( self.rs1.data ),
              self.alu.f.eq( Cat( 0b101, self.instruction[ 30 ] ) ),
              self.rd.data.eq( self.alu.y ),
            ]
        # Normal I-type operation:
        with m.Else():
          m.d.comb += [
            self.alu.a.eq( self.rs1.data ),
            self.alu.f.eq( self.instruction[ 12 : 15 ] ),
            self.rd.data.eq( self.alu.y ),
          ]
        # Shared I-type logic:
        m.d.comb += self.alu.b.eq( Cat(
          self.instruction[ 20 : 32 ],
          Repl( self.instruction[ 31 ], 20 ) ) )

    # End of CPU module definition.
    return m

