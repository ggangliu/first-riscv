from amaranth import *
from src.isa import *

v_filename = "alu.v"
#######################################
# ALU module
######################################

class ALU(Elaboratable):
	def __init__(self):
		self.f3  = Signal(4,  reset=0b0000)
		self.rs1 = Signal(32, reset=0x00000000)
		self.rs2 = Signal(32, reset=0x00000000)
		self.rd  = Signal(32, reset=0x00000000) 
		
	def elaborate(self, platform):
		m = Module()

		if platform is None:
			ta = Signal()
			m.d.sync += ta.eq(~ta)

		with m.Switch(self.f3[:3]):
			with m.Case(ALU_ADD):
				m.d.comb += self.rd.eq(self.rs1.as_signed() + Mux(self.f3[3], (~self.rs2+1).as_signed(), self.rs2.as_signed()))

		return m
