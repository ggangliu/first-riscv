#####################################
# ALU testbench
####################################
from amaranth.sim import Simulator, Delay, Settle, Tick
import sys, os
sys.path.append(os.getcwd()+"/../")

from src.isa import *
from src.alu import *

# Keep track of test pass / fail rates.
p = 0
f = 0
# Perform an individual ALU unit test.
def alu_ut( alu, a, b, fn, expected ):
  global p, f
  # Set A, B, F.
  yield alu.a.eq( a )
  yield alu.b.eq( b )
  yield alu.f.eq( fn )
  # Wait a clock tick.
  yield Tick()
  # Done. Check the result after combinatorial logic settles.
  yield Settle()
  actual = yield alu.y
  if hexs( expected ) != hexs( actual ):
    f += 1
    print( "\033[31mFAIL:\033[0m %s %s %s = %s (got: %s)"
           %( hexs( a ), ALU_STRS[ fn ], hexs( b ),
              hexs( expected ), hexs( actual ) ) )
  else:
    p += 1
    print( "\033[32mPASS:\033[0m %s %s %s = %s"
           %( hexs( a ), ALU_STRS[ fn ],
              hexs( b ), hexs( expected ) ) )

# Top-level ALU test method.
def alu_test( alu ):
  # Let signals settle after reset.
  yield Settle()

  # Print a test header.
  print( "--- ALU Tests ---" )

  # Test the bitwise 'AND' operation.
  print( "AND (&) tests:" )
  yield from alu_ut( alu, 0xCCCCCCCC, 0xCCCC0000, ALU_AND, 0xCCCC0000 )
  yield from alu_ut( alu, 0x00000000, 0x00000000, ALU_AND, 0x00000000 )
  yield from alu_ut( alu, 0xFFFFFFFF, 0xFFFFFFFF, ALU_AND, 0xFFFFFFFF )
  yield from alu_ut( alu, 0x00000000, 0xFFFFFFFF, ALU_AND, 0x00000000 )
  yield from alu_ut( alu, 0xFFFFFFFF, 0x00000000, ALU_AND, 0x00000000 )

  # Test the bitwise 'OR' operation.
  print( "OR  (|) tests:" )
  yield from alu_ut( alu, 0xCCCCCCCC, 0xCCCC0000, ALU_OR, 0xCCCCCCCC )
  yield from alu_ut( alu, 0x00000000, 0x00000000, ALU_OR, 0x00000000 )
  yield from alu_ut( alu, 0xFFFFFFFF, 0xFFFFFFFF, ALU_OR, 0xFFFFFFFF )
  yield from alu_ut( alu, 0x00000000, 0xFFFFFFFF, ALU_OR, 0xFFFFFFFF )
  yield from alu_ut( alu, 0xFFFFFFFF, 0x00000000, ALU_OR, 0xFFFFFFFF )

  # Test the bitwise 'XOR' operation.
  print( "XOR (^) tests:" )
  yield from alu_ut( alu, 0xCCCCCCCC, 0xCCCC0000, ALU_XOR, 0x0000CCCC )
  yield from alu_ut( alu, 0x00000000, 0x00000000, ALU_XOR, 0x00000000 )
  yield from alu_ut( alu, 0xFFFFFFFF, 0xFFFFFFFF, ALU_XOR, 0x00000000 )
  yield from alu_ut( alu, 0x00000000, 0xFFFFFFFF, ALU_XOR, 0xFFFFFFFF )
  yield from alu_ut( alu, 0xFFFFFFFF, 0x00000000, ALU_XOR, 0xFFFFFFFF )

  # Test the addition operation.
  print( "ADD (+) tests:" )
  yield from alu_ut( alu, 0, 0, ALU_ADD, 0 )
  yield from alu_ut( alu, 0, 1, ALU_ADD, 1 )
  yield from alu_ut( alu, 1, 0, ALU_ADD, 1 )
  yield from alu_ut( alu, 0xFFFFFFFF, 1, ALU_ADD, 0 )
  yield from alu_ut( alu, 29, 71, ALU_ADD, 100 )
  yield from alu_ut( alu, 0x80000000, 0x80000000, ALU_ADD, 0 )
  yield from alu_ut( alu, 0x7FFFFFFF, 0x7FFFFFFF, ALU_ADD, 0xFFFFFFFE )

  # Test the subtraction operation.
  print( "SUB (-) tests:" )
  yield from alu_ut( alu, 0, 0, ALU_SUB, 0 )
  yield from alu_ut( alu, 0, 1, ALU_SUB, -1 )
  yield from alu_ut( alu, 1, 0, ALU_SUB, 1 )
  yield from alu_ut( alu, -1, 1, ALU_SUB, -2 )
  yield from alu_ut( alu, 1, -1, ALU_SUB, 2 )
  yield from alu_ut( alu, 29, 71, ALU_SUB, -42 )
  yield from alu_ut( alu, 0x80000000, 1, ALU_SUB, 0x7FFFFFFF )
  yield from alu_ut( alu, 0x7FFFFFFF, -1, ALU_SUB, 0x80000000 )

  # Test the signed '<' comparison operation.
  print( "SLT (signed <) tests:" )
  yield from alu_ut( alu, 0, 0, ALU_SLT, 0 )
  yield from alu_ut( alu, 1, 0, ALU_SLT, 0 )
  yield from alu_ut( alu, 0, 1, ALU_SLT, 1 )
  yield from alu_ut( alu, -1, 0, ALU_SLT, 1 )
  yield from alu_ut( alu, -42, -10, ALU_SLT, 1 )
  yield from alu_ut( alu, -10, -42, ALU_SLT, 0 )

  # Test the unsigned '<' comparison operation.
  print( "SLTU (unsigned <) tests:" )
  yield from alu_ut( alu, 0, 0, ALU_SLTU, 0 )
  yield from alu_ut( alu, 1, 0, ALU_SLTU, 0 )
  yield from alu_ut( alu, 0, 1, ALU_SLTU, 1 )
  yield from alu_ut( alu, -1, 0, ALU_SLTU, 0 )
  yield from alu_ut( alu, -42, -10, ALU_SLTU, 1 )
  yield from alu_ut( alu, -10, -42, ALU_SLTU, 0 )
  yield from alu_ut( alu, -42, 42, ALU_SLTU, 0 )

  # Test the shift right operation.
  print ( "SRL (>>) tests:" )
  yield from alu_ut( alu, 0x00000001, 0, ALU_SRL, 0x00000001 )
  yield from alu_ut( alu, 0x00000001, 1, ALU_SRL, 0x00000000 )
  yield from alu_ut( alu, 0x00000011, 1, ALU_SRL, 0x00000008 )
  yield from alu_ut( alu, 0x00000010, 1, ALU_SRL, 0x00000008 )
  yield from alu_ut( alu, 0x80000000, 1, ALU_SRL, 0x40000000 )
  yield from alu_ut( alu, 0x80000000, 4, ALU_SRL, 0x08000000 )

  # Test the shift right with sign extension operation.
  print ( "SRA (>> + sign extend) tests:" )
  yield from alu_ut( alu, 0x00000001, 0, ALU_SRA, 0x00000001 )
  yield from alu_ut( alu, 0x00000001, 1, ALU_SRA, 0x00000000 )
  yield from alu_ut( alu, 0x00000011, 1, ALU_SRA, 0x00000008 )
  yield from alu_ut( alu, 0x00000010, 1, ALU_SRA, 0x00000008 )
  yield from alu_ut( alu, 0x80000000, 1, ALU_SRA, 0xC0000000 )
  yield from alu_ut( alu, 0x80000000, 4, ALU_SRA, 0xF8000000 )

  # Done.
  yield Tick()
  print( "ALU Tests: %d Passed, %d Failed"%( p, f ) )

# 'main' method to run a basic testbench.
if __name__ == "__main__":
  # Instantiate an ALU module.
  dut = ALU()
  def proc():
    yield from alu_test( dut )
  
  # Run the tests.
  sim = Simulator(dut)
  sim.add_clock( 1e-6 )
  sim.add_sync_process( proc )
  with sim.write_vcd("alu.vcd"):
    sim.run()

