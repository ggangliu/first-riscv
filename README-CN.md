# first-riscv
尝试通过Python语言实现一个RISC-V CPU用于学习RISC-V架构和微架构

## RISCV core

CPU核的设计逻辑
![CPU uarch](/docs/images/first-riscv-cpu-arch.png)

## ROM

CPU的bootloader程序将存储在ROM中，也是CPU启动后运行的第一个程序，因此这里需要添加ROM的支持

## RAM

由于程序运行过程中需要堆栈，因此RAM也是必不可少的部件

## SPI Flash

用外部SPI Flash来存储应用程序

## Peripherals

1. 用于连接UART串口，从而支持串口输出/输入
2. 用于控制外接LED，进行外部LED的点亮

# Folder structure

├── docs\
│   └── images\
├── fpga\
├── rtl\
├── src\
│   ├── pipeline\
├── test\
│   ├── hw_tests\
│   │   ├── common\
│   │   ├── led_test\
│   │   └── pwm_test\
│   ├── rv32i_compliance\
│   └── test_rom\
└── tutorial\
    ├── formal_verification\
    └── simulator-framework\

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

# Amaranth tutorial
[https://amaranth-lang.org/docs/amaranth/latest](https://amaranth-lang.org/docs/amaranth/latest)
