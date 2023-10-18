from amaranth import *
from src.rom import *

###########################################
# rv32ui SRL instruction tests:           #
###########################################

# Simulated ROM image:
srl_rom = rom_img( [
  0x6F004004, 0x732F2034, 0x930F8000, 0x6308FF03, 
  0x930F9000, 0x6304FF03, 0x930FB000, 0x6300FF03, 
  0x130F0000, 0x63040F00, 0x67000F00, 0x732F2034, 
  0x63540F00, 0x6F004000, 0x93E19153, 0x23203050, 
  0x6FF0DFFF, 0x732540F1, 0x63100500, 0x97020000, 
  0x93820201, 0x73905230, 0x73500018, 0x97020000, 
  0x9382C201, 0x73905230, 0x9302F0FF, 0x7390023B, 
  0x9302F001, 0x7390023A, 0x97020000, 0x93828201, 
  0x73905230, 0x73502030, 0x73503030, 0x73504030, 
  0x93010000, 0x97020000, 0x938202F7, 0x73905230, 
  0x13051000, 0x1315F501, 0x634A0500, 0x0F00F00F, 
  0x9308D005, 0x13050000, 0x6F00003D, 0x93020000, 
  0x638E0200, 0x73905210, 0xB7B20000, 0x93829210, 
  0x73902230, 0x73232030, 0xE39062F6, 0x73500030, 
  0x37250000, 0x13050580, 0x73200530, 0x97020000, 
  0x93824201, 0x73901234, 0x732540F1, 0x73002030, 
  0x930F0000, 0x631AF039, 0x97020020, 0x938282FF, 
  0x930FF0FF, 0x13080000, 0x33D00F01, 0x23A00200, 
  0x13030000, 0x631A6036, 0x130F1000, 0x93070000, 
  0xB350FF00, 0x23A21200, 0x13031000, 0x639E6034, 
  0x930E0000, 0x13071000, 0x33D1EE00, 0x23A42200, 
  0x13030000, 0x63126134, 0x130EF07F, 0x93064000, 
  0xB351DE00, 0x23A63200, 0x1303F007, 0x63966132, 
  0x930D0000, 0x13068000, 0x33D2CD00, 0x23A84200, 
  0x13030000, 0x631A6230, 0x97000020, 0x9380C0F8, 
  0x371D0000, 0x130D0D80, 0x9305F001, 0xB352BD00, 
  0x23A05000, 0x13010000, 0x6398222E, 0xB74C6507, 
  0x938C1C32, 0x13050001, 0x33D3AC00, 0x23A26000, 
  0x13015076, 0x631A232C, 0x370C0080, 0x130CFCFF, 
  0x93041000, 0xB3539C00, 0x23A47000, 0x37010040, 
  0x1301F1FF, 0x639A232A, 0x930B1000, 0x13040000, 
  0x33D48B00, 0x23A68000, 0x13011000, 0x631E2428, 
  0x130BF0FF, 0x93030000, 0xB3547B00, 0x23A89000, 
  0x1301F0FF, 0x63922428, 0x97000020, 0x938000F1, 
  0xB71A0000, 0x938A4A23, 0x13031000, 0x33D56A00, 
  0x23A0A000, 0xB7130000, 0x9383A391, 0x631E7524, 
  0x370A0080, 0x93024000, 0xB3555A00, 0x23A2B000, 
  0xB7030008, 0x63927524, 0xB7F9FFFF, 0x9389C9DC, 
  0x13028000, 0x33D64900, 0x23A4C000, 0xB7030001, 
  0x9383D3FE, 0x63127622, 0x1309F0FF, 0x9301F001, 
  0xB3563900, 0x23A6D000, 0x93031000, 0x63967620, 
  0x93081080, 0x13010001, 0x33D72800, 0x23A8E000, 
  0xB7030100, 0x9383F3FF, 0x6318771E, 0x17010020, 
  0x130101E9, 0x13080000, 0x93001000, 0xB3571800, 
  0x2320F100, 0x93010000, 0x6398371C, 0x9307F0FF, 
  0x13000000, 0x33D80700, 0x23220101, 0x9301F0FF, 
  0x631C381A, 0x13071000, 0x930F0000, 0xB358F701, 
  0x23241101, 0x93011000, 0x6390381A, 0x93060000, 
  0x130F1000, 0x33D9E601, 0x23262101, 0x93010000, 
  0x63143918, 0x1306F07F, 0x930E4000, 0xB359D601, 
  0x23283101, 0x9301F007, 0x63983916, 0x97000020, 
  0x938040E2, 0x93050000, 0x130E8000, 0x33DAC501, 
  0x23A04001, 0x13010000, 0x63182A14, 0x37150000, 
  0x13050580, 0x930DF001, 0xB35AB501, 0x23A25001, 
  0x13010000, 0x639A2A12, 0xB7446507, 0x93841432, 
  0x130D0001, 0x33DBA401, 0x23A46001, 0x13015076, 
  0x631C2B10, 0x37040080, 0x1304F4FF, 0x930C1000, 
  0xB35B9401, 0x23A67001, 0x37010040, 0x1301F1FF, 
  0x639C2B0E, 0x93031000, 0x130C0000, 0x33DC8301, 
  0x23A88001, 0x13011000, 0x63102C0E, 0x97000020, 
  0x938080DA, 0x1303F0FF, 0x930B0000, 0xB35C7301, 
  0x23A09001, 0x9303F0FF, 0x63907C0C, 0xB7120000, 
  0x93824223, 0x130B1000, 0x33DD6201, 0x23A2A001, 
  0xB7130000, 0x9383A391, 0x63107D0A, 0x37020080, 
  0x930A4000, 0xB35D5201, 0x23A4B001, 0xB7030008, 
  0x63947D08, 0xB7F1FFFF, 0x9381C1DC, 0x130A8000, 
  0x33DE4101, 0x23A6C001, 0xB7030001, 0x9383D3FE, 
  0x63147E06, 0x1301F0FF, 0x9309F001, 0xB35E3101, 
  0x23A8D001, 0x93031000, 0x63987E04, 0x17010020, 
  0x1301C1D2, 0x93001080, 0x13090001, 0x33DF2001, 
  0x2320E101, 0xB7010100, 0x9381F1FF, 0x63163F02, 
  0x13000000, 0x93081000, 0xB35F1001, 0x2322F101, 
  0x93010000, 0x639A3F00, 0x0F00F00F, 0x9308D005, 
  0x13050000, 0x6FF05FFF, 0x0F00F00F, 0x9308D005, 
  0x37150000, 0x1305D5BA, 0x6FF01FFF, 0x731000C0, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000
] )

# Simulated initialized RAM image:
srl_ram = ram_img( [
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x80000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000
] )

# Expected 'pass' register values.
srl_exp = {
  768: [ { 'r': 17, 'e': 93 }, { 'r': 10, 'e': 0 } ],  'end': 768
}

# Collected test program definition:
srl_test = [ 'SRL compliance tests', 'cpu_srl', srl_rom, srl_ram, srl_exp ]