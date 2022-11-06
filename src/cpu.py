from src.alu import *

class CPU(Elaboratable):
    def __init__( self ):
        # CPU signals:
        # 'Reset' signal for clock domains.
        self.clk_rst = Signal( reset = 0b0, reset_less = True )
        # Program Counter register.
        self.pc = Signal( 32, reset = 0x00000000 )
    
