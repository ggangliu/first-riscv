from amaranth import *
from src.rom import *

###########################################
# rv32ui BGEU instruction tests:          #
###########################################

# Simulated ROM image:
bgeu_rom = rom_img( [
  0x6F008004, 0x732F2034, 0x930F8000, 0x6308FF03, 
  0x930F9000, 0x6304FF03, 0x930FB000, 0x6300FF03, 
  0x130F0000, 0x63040F00, 0x67000F00, 0x732F2034, 
  0x63540F00, 0x6F004000, 0x93E19153, 0x170F0000, 
  0x23223F7C, 0x6FF09FFF, 0x732540F1, 0x63100500, 
  0x97020000, 0x93820201, 0x73905230, 0x73500018, 
  0x97020000, 0x9382C201, 0x73905230, 0x9302F0FF, 
  0x7390023B, 0x9302F001, 0x7390023A, 0x97020000, 
  0x93828201, 0x73905230, 0x73502030, 0x73503030, 
  0x73504030, 0x93010000, 0x97020000, 0x9382C2F6, 
  0x73905230, 0x13051000, 0x1315F501, 0x634A0500, 
  0x0F00F00F, 0x9308D005, 0x13050000, 0x6F008068, 
  0x93020000, 0x638E0200, 0x73905210, 0xB7B20000, 
  0x93829210, 0x73902230, 0x73232030, 0xE39E62F4, 
  0x73500030, 0x37250000, 0x13050580, 0x73200530, 
  0x97020000, 0x93824201, 0x73901234, 0x732540F1, 
  0x73002030, 0x930F0000, 0x6316F065, 0x17010020, 
  0x130141FF, 0xB7D00000, 0x9380C0CC, 0x930FF0FF, 
  0x13080000, 0x63F60F01, 0xB7200100, 0x9380B03A, 
  0x23201100, 0xB7D10000, 0x9381C1CC, 0x639C3060, 
  0xB7D00000, 0x9380C0CC, 0x130F1000, 0x93071080, 
  0x6376FF00, 0xB7200100, 0x9380B03A, 0x23221100, 
  0xB7210100, 0x9381B13A, 0x6396305E, 0x6F008000, 
  0x6F000002, 0xB7D00000, 0x9380C0CC, 0x930E0000, 
  0x1307F0FF, 0xE3F6EEFE, 0xB7200100, 0x9380B03A, 
  0x23241100, 0xB7210100, 0x9381B13A, 0x639C305A, 
  0xB7D00000, 0x9380C0CC, 0x130EF07F, 0xB7F6FFFF, 
  0x9386C6DC, 0x6376DE00, 0xB7200100, 0x9380B03A, 
  0x23261100, 0xB7210100, 0x9381B13A, 0x63943058, 
  0xB7D00000, 0x9380C0CC, 0x930D0000, 0x37060080, 
  0x63F6CD00, 0xB7200100, 0x9380B03A, 0x23281100, 
  0xB7210100, 0x9381B13A, 0x639E3054, 0x17010020, 
  0x130181F1, 0xB7D00000, 0x9380C0CC, 0x371D0000, 
  0x130D0D80, 0xB7150000, 0x93854523, 0x6376BD00, 
  0xB7200100, 0x9380B03A, 0x23201100, 0xB7210100, 
  0x9381B13A, 0x63903052, 0xB7D00000, 0x9380C0CC, 
  0xB74C6507, 0x938C1C32, 0x1305F0FF, 0x63F6AC00, 
  0xB7200100, 0x9380B03A, 0x23221100, 0xB7210100, 
  0x9381B13A, 0x6398304E, 0x6F008000, 0x6F004002, 
  0xB7D00000, 0x9380C0CC, 0x370C0080, 0x130CFCFF, 
  0x93041000, 0xE3749CFE, 0xB7200100, 0x9380B03A, 
  0x23241100, 0xB7D10000, 0x9381C1CC, 0x639C304A, 
  0xB7D00000, 0x9380C0CC, 0x930B1000, 0x37040080, 
  0x1304F4FF, 0x63F68B00, 0xB7200100, 0x9380B03A, 
  0x23261100, 0xB7210100, 0x9381B13A, 0x63943048, 
  0xB7D00000, 0x9380C0CC, 0x130BF0FF, 0xB7436507, 
  0x93831332, 0x63767B00, 0xB7200100, 0x9380B03A, 
  0x23281100, 0xB7D10000, 0x9381C1CC, 0x639C3044, 
  0x97030020, 0x938383E2, 0xB7D00000, 0x9380C0CC, 
  0xB71A0000, 0x938A4A23, 0x37130000, 0x13030380, 
  0x63F66A00, 0xB7200100, 0x9380B03A, 0x23A01300, 
  0x37D40000, 0x1304C4CC, 0x639E8040, 0xB7D00000, 
  0x9380C0CC, 0x370A0080, 0x93020000, 0x63765A00, 
  0xB7200100, 0x9380B03A, 0x23A21300, 0x37D40000, 
  0x1304C4CC, 0x6398803E, 0x6F008000, 0x6F004002, 
  0xB7D00000, 0x9380C0CC, 0xB7F9FFFF, 0x9389C9DC, 
  0x1302F07F, 0xE3F449FE, 0xB7200100, 0x9380B03A, 
  0x23A41300, 0x37D40000, 0x1304C4CC, 0x639C803A, 
  0xB7D00000, 0x9380C0CC, 0x1309F0FF, 0x9301F0FF, 
  0x63763900, 0xB7200100, 0x9380B03A, 0x23A61300, 
  0x37D40000, 0x1304C4CC, 0x63968038, 0xB7D00000, 
  0x9380C0CC, 0x93081080, 0x13011000, 0x63F62800, 
  0xB7200100, 0x9380B03A, 0x23A81300, 0x37D40000, 
  0x1304C4CC, 0x63908036, 0x97010020, 0x938141D4, 
  0x37D10000, 0x1301C1CC, 0x13080000, 0x93000000, 
  0x63761800, 0x37210100, 0x1301B13A, 0x23A02100, 
  0x37D20000, 0x1302C2CC, 0x63164132, 0xB7D00000, 
  0x9380C0CC, 0x9307F0FF, 0x13000000, 0x63F60700, 
  0xB7200100, 0x9380B03A, 0x23A21100, 0x37D20000, 
  0x1302C2CC, 0x63904030, 0x6F008000, 0x6F000002, 
  0xB7D00000, 0x9380C0CC, 0x13071000, 0x930F1080, 
  0xE376F7FF, 0xB7200100, 0x9380B03A, 0x23A41100, 
  0x37220100, 0x1302B23A, 0x6396402C, 0xB7D00000, 
  0x9380C0CC, 0x93060000, 0x130FF0FF, 0x63F6E601, 
  0xB7200100, 0x9380B03A, 0x23A61100, 0x37220100, 
  0x1302B23A, 0x6390402A, 0xB7D00000, 0x9380C0CC, 
  0x1306F07F, 0xB7FEFFFF, 0x938ECEDC, 0x6376D601, 
  0xB7200100, 0x9380B03A, 0x23A81100, 0x37220100, 
  0x1302B23A, 0x63984026, 0x17010020, 0x130181C6, 
  0xB7D00000, 0x9380C0CC, 0x93050000, 0x370E0080, 
  0x63F6C501, 0xB7200100, 0x9380B03A, 0x23201100, 
  0xB7210100, 0x9381B13A, 0x639E3022, 0xB7D00000, 
  0x9380C0CC, 0x37150000, 0x13050580, 0xB71D0000, 
  0x938D4D23, 0x6376B501, 0xB7200100, 0x9380B03A, 
  0x23221100, 0xB7210100, 0x9381B13A, 0x63943020, 
  0x6F008000, 0x6F004002, 0xB7D00000, 0x9380C0CC, 
  0xB7446507, 0x93841432, 0x130DF0FF, 0xE3F4A4FF, 
  0xB7200100, 0x9380B03A, 0x23241100, 0xB7210100, 
  0x9381B13A, 0x6398301C, 0xB7D00000, 0x9380C0CC, 
  0x37040080, 0x1304F4FF, 0x930C1000, 0x63769401, 
  0xB7200100, 0x9380B03A, 0x23261100, 0xB7D10000, 
  0x9381C1CC, 0x6390301A, 0xB7D00000, 0x9380C0CC, 
  0x93031000, 0x370C0080, 0x130CFCFF, 0x63F68301, 
  0xB7200100, 0x9380B03A, 0x23281100, 0xB7210100, 
  0x9381B13A, 0x63983016, 0x97030020, 0x9383C3B7, 
  0xB7D00000, 0x9380C0CC, 0x1303F0FF, 0xB74B6507, 
  0x938B1B32, 0x63767301, 0xB7200100, 0x9380B03A, 
  0x23A01300, 0x37D40000, 0x1304C4CC, 0x639C8012, 
  0xB7D00000, 0x9380C0CC, 0xB7120000, 0x93824223, 
  0x371B0000, 0x130B0B80, 0x63F66201, 0xB7200100, 
  0x9380B03A, 0x23A21300, 0x37D40000, 0x1304C4CC, 
  0x63928010, 0x6F008000, 0x6F000002, 0xB7D00000, 
  0x9380C0CC, 0x37020080, 0x930A0000, 0xE37652FF, 
  0xB7200100, 0x9380B03A, 0x23A41300, 0x37D40000, 
  0x1304C4CC, 0x6398800C, 0xB7D00000, 0x9380C0CC, 
  0xB7F1FFFF, 0x9381C1DC, 0x130AF07F, 0x63F64101, 
  0xB7200100, 0x9380B03A, 0x23A61300, 0x37D40000, 
  0x1304C4CC, 0x6390800A, 0xB7D00000, 0x9380C0CC, 
  0x1301F0FF, 0x9309F0FF, 0x63763101, 0xB7200100, 
  0x9380B03A, 0x23A81300, 0x37D40000, 0x1304C4CC, 
  0x639A8006, 0x97010020, 0x938141A9, 0x37D10000, 
  0x1301C1CC, 0x93001080, 0x13091000, 0x63F62001, 
  0x37210100, 0x1301B13A, 0x23A02100, 0x37D20000, 
  0x1302C2CC, 0x63104104, 0xB7D00000, 0x9380C0CC, 
  0x13000000, 0x93080000, 0x63761001, 0xB7200100, 
  0x9380B03A, 0x23A21100, 0x37D20000, 0x1302C2CC, 
  0x639A4000, 0x0F00F00F, 0x9308D005, 0x13050000, 
  0x6FF05FFF, 0x0F00F00F, 0x9308D005, 0x37150000, 
  0x1305D5BA, 0x6FF01FFF, 0x731000C0, 0x00000000, 
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
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000, 
  0x00000000, 0x00000000, 0x00000000, 0x00000000
] )

# Simulated initialized RAM image:
bgeu_ram = ram_img( [
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
bgeu_exp = {
  1152: [ { 'r': 17, 'e': 93 }, { 'r': 10, 'e': 0 } ],  'end': 1152
}

# Collected test program definition:
bgeu_test = [ 'BGEU compliance tests', 'cpu_bgeu', bgeu_rom, bgeu_ram, bgeu_exp ]