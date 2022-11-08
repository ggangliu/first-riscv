#############################################################
# RISC-V RV32I
#############################################################
from amaranth import *

v_filename = "isa.v"

#CSR
# Instruction field definitions.
# RV32I opcode definitions:
OP_LUI    = 0b0110111
OP_AUIPC  = 0b0010111
OP_JAL    = 0b1101111
OP_JALR   = 0b1100111
OP_BRANCH = 0b1100011
OP_LOAD   = 0b0000011
OP_STORE  = 0b0100011
OP_REG    = 0b0110011
OP_IMM    = 0b0010011
OP_SYSTEM = 0b1110011
OP_FENCE  = 0b0001111
# RV32I "funct3" bits. These select different functions with
# R-type, I-type, S-type, and B-type instructions.
F_JALR    = 0b000
F_BEQ     = 0b000
F_BNE     = 0b001
F_BLT     = 0b100
F_BGE     = 0b101
F_BLTU    = 0b110
F_BGEU    = 0b111
F_LB      = 0b000
F_LH      = 0b001
F_LW      = 0b010
F_LBU     = 0b100
F_LHU     = 0b101
F_SB      = 0b000
F_SH      = 0b001
F_SW      = 0b010
F_ADDI    = 0b000
F_SLTI    = 0b010
F_SLTIU   = 0b011
F_XORI    = 0b100
F_ORI     = 0b110
F_ANDI    = 0b111
F_SLLI    = 0b001
F_SRLI    = 0b101
F_SRAI    = 0b101
F_ADD     = 0b000
F_SUB     = 0b000
F_SLL     = 0b001
F_SLT     = 0b010
F_SLTU    = 0b011
F_XOR     = 0b100
F_SRL     = 0b101
F_SRA     = 0b101
F_OR      = 0b110
F_AND     = 0b111
# RV32I "funct7" bits. Along with the "funct3" bits, these select
# different functions with R-type instructions.
FF_SLLI   = 0b0000000
FF_SRLI   = 0b0000000
FF_SRAI   = 0b0100000
FF_ADD    = 0b0000000
FF_SUB    = 0b0100000
FF_SLL    = 0b0000000
FF_SLT    = 0b0000000
FF_SLTU   = 0b0000000
FF_XOR    = 0b0000000
FF_SRL    = 0b0000000
FF_SRA    = 0b0100000
FF_OR     = 0b0000000
FF_AND    = 0b0000000
# CSR definitions, for 'ECALL' system instructions.
# Like with other "I-type" instructions, the 'funct3' bits select
# between different types of environment calls.
F_TRAPS  = 0b000
F_CSRRW  = 0b001
F_CSRRS  = 0b010
F_CSRRC  = 0b011
F_CSRRWI = 0b101
F_CSRRSI = 0b110
F_CSRRCI = 0b111
# Definitions for non-CSR 'ECALL' system instructions. These seem to
# use the whole 12-bit immediate to encode their functionality.
IMM_MRET = 0x302
IMM_WFI  = 0x105
# ID numbers for different types of traps (exceptions).
TRAP_IMIS  = 1
TRAP_ILLI  = 2
TRAP_BREAK = 3
TRAP_LMIS  = 4
TRAP_SMIS  = 6
TRAP_ECALL = 11


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

