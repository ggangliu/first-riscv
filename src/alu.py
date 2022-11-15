from amaranth import *
from .isa import *

v_filename = "alu.v"
#######################################
# ALU module
######################################
class ALU( Elaboratable ):
  def __init__( self ):
    # 'A' and 'B' data inputs.
    self.a = Signal( 32, reset = 0x00000000 )
    self.b = Signal( 32, reset = 0x00000000 )
    # 'F' function select input.
    self.f = Signal( 4,  reset = 0b0000 )
    # 'Y' data output.
    self.y = Signal( 32, reset = 0x00000000 )

  def elaborate( self, platform ):
    # Core ALU module.
    m = Module()

    # Dummy synchronous logic only for simulation.
    if platform is None:
      ta = Signal()
      m.d.sync += ta.eq( ~ta )

    # Perform ALU computations based on the 'function' bits.
    with m.Switch( self.f[ :3 ] ):
      # Y = A AND B
      with m.Case( ALU_AND & 0b111 ):
        m.d.comb += self.y.eq( self.a & self.b )
      # Y = A  OR B
      with m.Case( ALU_OR & 0b111 ):
        m.d.comb += self.y.eq( self.a | self.b )
      # Y = A XOR B
      with m.Case( ALU_XOR & 0b111 ):
        m.d.comb += self.y.eq( self.a ^ self.b )
      # Y = A +/- B
      # Subtraction is implemented as A + (-B).
      with m.Case( ALU_ADD & 0b111 ):
        m.d.comb += self.y.eq(
          self.a.as_signed() + Mux( self.f[ 3 ],
            ( ~self.b + 1 ).as_signed(),
            self.b.as_signed() ) )
      # Y = ( A < B ) (signed)
      with m.Case( ALU_SLT & 0b111 ):
        m.d.comb += self.y.eq( self.a.as_signed() < self.b.as_signed() )
      # Y = ( A <  B ) (unsigned)
      with m.Case( ALU_SLTU & 0b111 ):
        m.d.comb += self.y.eq( self.a < self.b )
      # Note: Shift operations cannot shift more than XLEN (32) bits.
      # Also, left shifts are implemented by flipping the inputs
      # and outputs of a right shift operation in the CPU logic.
      # Y = A >> B
      with m.Case( ALU_SRL & 0b111 ):
        m.d.comb += self.y.eq( Mux( self.f[ 3 ],
          self.a.as_signed() >> ( self.b[ :5 ] ),
          self.a >> ( self.b[ :5 ] ) ) )

    # End of ALU module definition.
    return m

