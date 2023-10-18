# firstRISCV
Try to implement a RISC-V CPU for learning RISC-V architecture and microarchitecture by Python language 

## RISCV core

CPU Core design logic
![CPU uarch](/docs/images/first-riscv-cpu-arch.png)

## ROM
The bootloader program is stored in ROM, and which is the first program to run on CPU. So here will need ROM
CPU的bootloader程序将存储在ROM中，也是CPU启动后运行的第一个程序，因此这里需要添加ROM的支持

## RAM
Program also need RAM to store heap and stack
由于程序运行过程中需要堆栈，因此RAM也是必不可少的部件

## SPI Flash
External flash is used to store applicaton program
用外部SPI Flash来存储应用程序

## Peripherals
1. Used to connect to UART, and support input and output
2. Used to control exteral LED
3. 用于连接UART串口，从而支持串口输出/输入
4. 用于控制外接LED，进行外部LED的点亮

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
Storing FPGA related source code which is converted by Python code
用于存放将risc-v实现运行在fpga上的相关代码

## generate-rtl.py
This script is used to generate RTL code based on Python code, and will output it in rtl folder
该脚本用于生成rtl代码，输出到rtl目录

## rtl
Storing the generated verilog code
用于存放生成的verilog代码

## software
Storing software code
用于存放软件代码

## src
Python source code which implemente the first rsic-v
实现risc-v架构的Python源代码

## test
Used to test and verify the Python code in the 'src' folder, and generate waveform file
用于测试验证src中的python实现，并生成波形文件

# Amaranth tutorial
[https://amaranth-lang.org/docs/amaranth/latest](https://amaranth-lang.org/docs/amaranth/latest)
