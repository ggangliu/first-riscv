#####################################
# ALU testbench
####################################
from amaranth.sim import Simulator, Tick, Settle
import sys, os
sys.path.append("..")

from src.isa import *
from src.spi_flash import *

p = 0
f = 0
def spi_flash_read_ut(name, actual, expected):
    global p, f

    if expected != actual:
        f += 1
        print("\033[31mFAIL:\033[0m %s SPI_FLASH 0x%08X (got: 0x%08X)" % (name, expected, actual))
    else:
        p += 1
        print( "\033[32mPASS:\033[0m %s SPI_FALSH 0x%08X = 0x%08X" % (name, actual, expected))

# Helper method to test reading a byte of SPI data.
def spi_read_word( srom, virt_addr, phys_addr, simword, end_wait ):
    # Set 'address'.
    yield srom.arb.bus.adr.eq(virt_addr)
    # Set 'strobe' and 'cycle' to request a new read.
    yield srom.arb.bus.stb.eq(1)
    yield srom.arb.bus.cyc.eq(1)
    # Wait a tick; the (inverted) CS pin should then be low, and
    # the 'read command' value should be set correctly.
    yield Tick()
    yield Settle()
    csa = yield srom.spi.cs.o
    spcmd = yield srom.spio
    spi_flash_read_ut("CS Low", csa, 1)
    spi_flash_read_ut("SPI Flash Read Cmd Value", spcmd, (phys_addr & 0x00FFFFFF) | 0x03000000)
    # Then the 32-bit read command is sent; two ticks per bit.
    for i in range(32):
        yield Settle()
        dout = yield srom.spi.mosi.o
        spi_flash_read_ut("SPI Flash Read Cmd  [%d]"%i, dout, (spcmd >> ( 31 - i )) & 0b1)
        yield Tick()
    # The following 32 bits should return the word. Simulate
    # the requested word arriving on the MISO pin, MSbit first.
    # (Data starts getting returned on the falling clock edge
    #  immediately following the last rising-edge read.)
    i = 7
    expect = 0
    while i < 32:
        yield Tick()
        yield Settle()
        expect = expect | ( ( 1 << i ) & simword )
        progress = yield srom.arb.bus.dat_r
        spi_flash_read_ut( "SPI Flash Read Word [%d]"%i, progress, expect )
        if ( ( i & 0b111 ) == 0 ):
          i = i + 15
        else:
          i = i - 1
    # Wait one more tick, then the CS signal should be de-asserted.
    yield Tick()
    yield Settle()
    csa = yield srom.spi.cs.o
    spi_flash_read_ut( "CS High (Waiting)", csa, 0 )
    # Done; reset 'strobe' and 'cycle' after N ticks to test
    # delayed reads from the bus.
    for i in range( end_wait ):
        yield Tick()
    yield srom.arb.bus.stb.eq( 0 )
    yield srom.arb.bus.cyc.eq( 0 )
    yield Tick()
    yield Settle()

# Top-level SPI ROM test method.
def spi_flash_test(srom):
    global p, f
    # Let signals settle after reset.
    yield Tick()
    yield Settle()
    # Print a test header.
    print( "--- SPI Flash Tests ---" )
    # Test basic behavior by reading a few consecutive words.
    yield from spi_read_word( srom, 0x00, 0x200000, little_end( 0x89ABCDEF ), 0 )
    yield from spi_read_word( srom, 0x04, 0x200004, little_end( 0x0C0FFEE0 ), 4 )
    # Make sure the CS pin stays de-asserted while waiting.
    for i in range( 4 ):
        yield Tick()
        yield Settle()
        csa = yield srom.spi.cs.o
        spi_flash_read_ut( "CS High (Waiting)", csa, 0 )
    yield from spi_read_word( srom, 0x10, 0x200010, little_end( 0xDEADFACE ), 1 )
    yield from spi_read_word( srom, 0x0C, 0x20000C, little_end( 0xABACADAB ), 1 )
    # Done. Print the number of passed and failed unit tests.
    yield Tick()
    print( "SPI Flash Tests: %d Passed, %d Failed"%( p, f ) )

if __name__ == "__main__":
    # Instantiate a test SPI ROM module.
    off = ( 2 * 1024 * 1024 )
    dut = SPI_Flash(off, off + 1024, [0x89ABCDEF, 0x0C0FFEE0, 0xBABABABA, 0xABACADAB, 0xDEADFACE, 0x12345678, 0x87654321, 0xDEADBEEF, 0xDEADBEEF])

    def proc():
        for i in range(30):
            yield Tick()
        yield from spi_flash_test(dut)
	
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    with sim.write_vcd("spi_flash.vcd"):
        sim.run()

