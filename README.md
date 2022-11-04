# firstRISCV
尝试用Python实现一个RISCV CPU，从而达到学习RISC-V架构及微架构的目的 

## RISCV core
Riscv核的核心逻辑介绍

## ROM
CPU的bootloader程序将存储在ROM中，也是CPU启动后运行的第一个程序，因此这里需要添加ROM的支持

## RAM
由于程序运行过程中需要堆栈，因此RAM也是必不可少的部件

## Peripherals
1. 用于连接UART串口，从而支持串口输出/输入
2. 用于控制外接LED，进行外部LED的点亮

# Folder structure
├── fpga  
│   ├── arty-a7-100.py  
│   └── blinky.py  
├── generate-rtl.py  
├── generate-rtl.sh  
├── README.md  
├── rtl  
│   ├── alu.v  
│   └── isa.v  
├── software  
├── src  
│   ├── alu.py  
│   ├── isa.py  
│   └── rom.py  
└── test  
    ├── test_alu.py  
    ├── test_isa.py  
    └── test_rom.py  

## fpga
用于存放将risc-v实现运行在fpga上的相关代码

## generate-rtl.py
该脚本用于生成rtl代码，输出到rtl目录

## rtl 
用于存放生成的verilog代码

## software  
用于存放软件代码

## src
实现risc-v架构的Python源代码

## test 
用于测试验证src中的python实现，并生成波形文件
