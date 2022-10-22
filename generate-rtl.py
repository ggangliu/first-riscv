from amaranth.back import verilog

import src.isa as isa
import src.alu as alu 

output_dir = "rtl/"

top = isa.UpCounter(25)
with open(output_dir+isa.v_filename, "w") as f:
	f.write(verilog.convert(top, ports=[top.en, top.ovf]))

top = alu.ALU()
with open(output_dir+alu.v_filename, "w") as f:
	f.write(verilog.convert(top, ports=[top.rs1, top.rs2, top.f3, top.rd]))
