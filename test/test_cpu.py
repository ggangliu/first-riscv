from amaranth import *
from math import ceil, log2
from amaranth.sim import * #Simulator, Tick, Settle 
from amaranth.back import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *
from amaranth.hdl.ast import Past, Cat, Repl
from amaranth.hdl.ir import DriverConflict

import os, sys, warnings
sys.path.append("..")

from src.isa import *
from src.cpu import *
from src.rv_mem import *
# Import test programs and expected runtime register values.
from programs import *

##################
# CPU testbench: #
##################
# Keep track of test pass / fail rates.
p = 0
f = 0

# Helper method to check expected CPU register / memory values
# at a specific point during a test program.
def check_vals( expected, ni, cpu ):
  global p, f
  if ni in expected:
    for j in range( len( expected[ ni ] ) ):
      ex = expected[ ni ][ j ]
      # Special case: program counter.
      if ex[ 'r' ] == 'pc':
        cpc = yield cpu.pc
        if hexs( cpc ) == hexs( ex[ 'e' ] ):
          p += 1
          print( "  \033[32mPASS:\033[0m pc  == %s"
                 " after %d operations"
                 %( hexs( ex[ 'e' ] ), ni ) )
        else:
          f += 1
          print( "  \033[31mFAIL:\033[0m pc  == %s"
                 " after %d operations (got: %s)"
                 %( hexs( ex[ 'e' ] ), ni, hexs( cpc ) ) )
      # Special case: RAM data (must be word-aligned).
      elif type( ex[ 'r' ] ) == str and ex[ 'r' ][ 0:3 ] == "RAM":
        rama = int( ex[ 'r' ][ 3: ] )
        if ( rama % 4 ) != 0:
          f += 1
          print( "  \033[31mFAIL:\033[0m RAM == %s @ 0x%08X"
                 " after %d operations (mis-aligned address)"
                 %( hexs( ex[ 'e' ] ), rama, ni ) )
        else:
          cpd = yield cpu.mem.ram.data[ rama // 4 ]
          if hexs( cpd ) == hexs( ex[ 'e' ] ):
            p += 1
            print( "  \033[32mPASS:\033[0m RAM == %s @ 0x%08X"
                   " after %d operations"
                   %( hexs( ex[ 'e' ] ), rama, ni ) )
          else:
            f += 1
            print( "  \033[31mFAIL:\033[0m RAM == %s @ 0x%08X"
                   " after %d operations (got: %s)"
                   %( hexs( ex[ 'e' ] ), rama, ni, hexs( cpd ) ) )
      # Numbered general-purpose registers.
      elif ex[ 'r' ] >= 0 and ex[ 'r' ] < 32:
        cr = yield cpu.r[ ex[ 'r' ] ]
        if hexs( cr ) == hexs( ex[ 'e' ] ):
          p += 1
          print( "  \033[32mPASS:\033[0m r%02d == %s"
                 " after %d operations"
                 %( ex[ 'r' ], hexs( ex[ 'e' ] ), ni ) )
        else:
          f += 1
          print( "  \033[31mFAIL:\033[0m r%02d == %s"
                 " after %d operations (got: %s)"
                 %( ex[ 'r' ], hexs( ex[ 'e' ] ),
                    ni, hexs( cr ) ) )

# Helper method to run a CPU device for a given number of cycles,
# and verify its expected register values over time.
def cpu_run( cpu, expected ):
  global p, f
  # Record how many CPU instructions have been executed.
  ni = -1
  # Watch for timeouts if the CPU gets into a bad state.
  timeout = 0
  instret = 0
  # Let the CPU run for N instructions.
  while ni <= expected[ 'end' ]:
    # Let combinational logic settle before checking values.
    yield Settle()
    timeout = timeout + 1
    # Only check expected values once per instruction.
    ninstret = yield cpu.csr.minstret_instrs
    if ninstret != instret:
      ni += 1
      instret = ninstret
      timeout = 0
      # Check expected values, if any.
      yield from check_vals( expected, ni, cpu )
    elif timeout > 1000:
      f += 1
      print( "\033[31mFAIL: Timeout\033[0m" )
      break
    # Step the simulation.
    yield Tick()

# Helper method to simulate running a CPU with the given ROM image
# for the specified number of CPU cycles. The 'name' field is used
# for printing and generating the waveform filename: "cpu_[name].vcd".
def cpu_sim( test ):
  print( "\033[33mSTART\033[0m running '%s' program:"%test[ 0 ] )
  # Create the CPU device.
  dut = CPU( ROM( test[ 2 ] ) )
  cpu = ResetInserter( dut.clk_rst )( dut )

  # Run the simulation.
  sim_name = "%s.vcd"%test[ 1 ]
  sim = Simulator( cpu )
  def proc():
    # Initialize RAM values.
    for i in range( len( test[ 3 ] ) ):
      yield cpu.mem.ram.data[ i ].eq( LITTLE_END( test[ 3 ][ i ] ) )
      # Run the program and print pass/fail for individual tests.
      yield from cpu_run( cpu, test[ 4 ] )
      print( "\033[35mDONE\033[0m running %s: executed %d instructions"
             %( test[ 0 ], test[ 4 ][ 'end' ] ) )
  sim.add_clock( 1 / 6000000 )
  sim.add_sync_process( proc )
  with sim.write_vcd(sim_name):
    sim.run()

# Helper method to simulate running a CPU from simulated SPI
# Flash which contains a given ROM image.
def cpu_spi_sim( test ):
  print( "\033[33mSTART\033[0m running '%s' program (SPI):"%test[ 0 ] )
  # Create the CPU device.
  sim_spi_off = ( 2 * 1024 * 1024 )
  dut = CPU( SPI_Flash( sim_spi_off, sim_spi_off + 1024, test[ 2 ] ) )
  cpu = ResetInserter( dut.clk_rst )( dut )

  # Run the simulation.
  sim_name = "%s_spi.vcd"%test[ 1 ]
  sim = Simulator( cpu ) 
  def proc():
    for i in range( len( test[ 3 ] ) ):
        yield cpu.mem.ram.data[ i ].eq( test[ 3 ][ i ] )
        yield from cpu_run( cpu, test[ 4 ] )
        print( "\033[35mDONE\033[0m running %s: executed %d instructions"
             %( test[ 0 ], test[ 4 ][ 'end' ] ) )
  sim.add_clock( 1 / 6000000 )
  sim.add_sync_process( proc )
  with sim.write_vcd( sim_name ):
    sim.run()

from test_rom.rv32i_add import *
from test_rom.rv32i_addi import *
from test_rom.rv32i_and import *
from test_rom.rv32i_andi import *
from test_rom.rv32i_auipc import *
from test_rom.rv32i_beq import *
from test_rom.rv32i_bge import *
from test_rom.rv32i_bgeu import *
from test_rom.rv32i_blt import *
from test_rom.rv32i_bltu import *
from test_rom.rv32i_bne import *
from test_rom.rv32i_delay_slots import *
from test_rom.rv32i_ebreak import *
from test_rom.rv32i_ecall import *
from test_rom.rv32i_endianess import *
from test_rom.rv32i_io import *
from test_rom.rv32i_jal import *
from test_rom.rv32i_jalr import *
from test_rom.rv32i_lb import *
from test_rom.rv32i_lbu import *
from test_rom.rv32i_lh import *
from test_rom.rv32i_lhu import *
from test_rom.rv32i_lw import *
from test_rom.rv32i_lui import *
from test_rom.rv32i_nop import *
from test_rom.rv32i_or import *
from test_rom.rv32i_ori import *
from test_rom.rv32i_rf_size import *
from test_rom.rv32i_rf_width import *
from test_rom.rv32i_rf_x0 import *
from test_rom.rv32i_sb import *
from test_rom.rv32i_sh import *
from test_rom.rv32i_sw import *
from test_rom.rv32i_sll import *
from test_rom.rv32i_slli import *
from test_rom.rv32i_slt import *
from test_rom.rv32i_slti import *
from test_rom.rv32i_sltu import *
from test_rom.rv32i_sltiu import *
from test_rom.rv32i_sra import *
from test_rom.rv32i_srai import *
from test_rom.rv32i_srl import *
from test_rom.rv32i_srli import *
from test_rom.rv32i_sub import *
from test_rom.rv32i_xor import *
from test_rom.rv32i_xori import *

# 'main' method to run a basic testbench.
if __name__ == "__main__":
  if ( len( sys.argv ) == 2 ) and ( sys.argv[ 1 ] == '-b' ):
    # Build the application for an iCE40UP5K FPGA.
    # Currently, this is meaningless, because it builds the CPU
    # with a hard-coded 'infinite loop' ROM. But it's a start.
    with warnings.catch_warnings():
      warnings.filterwarnings( "ignore", category = DriverConflict )
      warnings.filterwarnings( "ignore", category = UnusedElaboratable )
      # Build the CPU to read its program from a 2MB offset in SPI Flash.
      prog_start = ( 2 * 1024 * 1024 )
      cpu = CPU( SPI_ROM( prog_start, prog_start * 2, None ) )
      UpduinoPlatform().build( ResetInserter( cpu.clk_rst )( cpu ),
                               do_program = False )
  else:
    # Run testbench simulations.
    with warnings.catch_warnings():
      warnings.filterwarnings( "ignore", category = DriverConflict )

      print( '--- CPU Tests ---' )
      # Simulate the 'infinite loop' ROM to screen for syntax errors.
      cpu_sim( loop_test )
      cpu_spi_sim( loop_test )
      cpu_sim( ram_pc_test )
      cpu_spi_sim( ram_pc_test )
      # Simulate the RV32I compliance tests.
      cpu_sim( add_test )
      """
      cpu_sim( addi_test )
      cpu_sim( and_test )
      cpu_sim( andi_test )
      cpu_sim( auipc_test )
      cpu_sim( beq_test )
      cpu_sim( bge_test )
      cpu_sim( bgeu_test )
      cpu_sim( blt_test )
      cpu_sim( bltu_test )
      cpu_sim( bne_test )
      cpu_sim( delay_slots_test )
      cpu_sim( ebreak_test )
      cpu_sim( ecall_test )
      cpu_sim( endianess_test )
      cpu_sim( io_test )
      cpu_sim( jal_test )
      cpu_sim( jalr_test )
      cpu_sim( lb_test )
      cpu_sim( lbu_test )
      cpu_sim( lh_test )
      cpu_sim( lhu_test )
      cpu_sim( lw_test )
      cpu_sim( lui_test )
      cpu_sim( misalign_jmp_test )
      cpu_sim( misalign_ldst_test )
      cpu_sim( nop_test )
      cpu_sim( or_test )
      cpu_sim( ori_test )
      cpu_sim( rf_size_test )
      cpu_sim( rf_width_test )
      cpu_sim( rf_x0_test )
      cpu_sim( sb_test )
      cpu_sim( sh_test )
      cpu_sim( sw_test )
      cpu_sim( sll_test )
      cpu_sim( slli_test )
      cpu_sim( slt_test )
      cpu_sim( slti_test )
      cpu_sim( sltu_test )
      cpu_sim( sltiu_test )
      cpu_sim( sra_test )
      cpu_sim( srai_test )
      cpu_sim( srl_test )
      cpu_sim( srli_test )
      cpu_sim( sub_test )
      cpu_sim( xor_test )
      cpu_sim( xori_test )
      """
      # Done; print results.
      print(Repl(2, 5))
      print( "CPU Tests: %d Passed, %d Failed"%( p, f ) )
