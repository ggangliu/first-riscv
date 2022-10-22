#############################################################
# RISC-V RV32I
#############################################################
from amaranth import *

v_filename = "isa.v"

# Instruction field definition

#Opcode
OP_LUI = 0b0110011

#func3
F_ADD = 0b000

#func7
FF_ADD = 0b0000000

#CSR


#ALU operation definition
ALU_ADD = 0b0000
ALU_SUB = 0b0000

ALU_STRS = {ALU_ADD:"+", ALU_SUB:"-"}

class UpCounter(Elaboratable):
	def __init__(self, limit):
		self.limit = limit

		# Ports
		self.en  = Signal()
		self.ovf = Signal()

		# State
		self.count = Signal(16)

	def elaborate(self, platform):
		m = Module()
		m.d.comb += self.ovf.eq(self.count == self.limit)
		with m.If(self.en):
			with m.If(self.ovf):
				m.d.sync += self.count.eq(0)
			with m.Else():
				m.d.sync += self.count.eq(self.count + 1)

		return m

def little_end(v):
    return (((v&0x000000ff)<<24) |
            ((v&0x0000ff00)<<8)  |
            ((v&0x00ff0000)>>8)  |
            ((v&0xff000000)>>24) ) 

def hexs(h):
  if h >= 0:
    return "0x%08X"%(h)
  else:
    return "0x%08X"%((h + (1 << 32)) % (1 << 32))

# R-type operation Rc = Ra ? Rb
def rv32i_r(opcode, f3, f7, rd, rs1, rs2):
    return little_end((opcode&0x7f)      | 
                      ((rd&0x1f) << 7)   | 
                      ((f3&0x07) << 12)  | 
                      ((rs1&0x1f) << 15) | 
                      ((rs2&0x1f) << 20) | 
                      ((f7&0x7c) << 25))



def rom_img(arr):
	a = []
	for i in arr:
		if type(i) == tuple:
			for j in i:
				a.append(j)
		else:
			a.append(i)
	return a

def ram_img(arr):
	a = []
	for i in arr:
		a.append(i)
	return a

