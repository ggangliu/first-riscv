# first-riscv
Try to implement a RISC-V CPU for learning RISC-V architecture and microarchitecture by Python language 

## RISCV core

CPU Core design logic
![CPU uarch](/docs/images/first-riscv-cpu-arch.png)

## ROM

The bootloader program is stored in ROM, and which is the first program to run on CPU. So here will need ROM

## RAM

Program also need RAM to store heap and stack

## SPI Flash

External flash is used to store applicaton program

## Peripherals

1. Used to connect to UART, and support input and output
2. Used to control exteral LED

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

## generate-rtl.py

This script is used to generate RTL code based on Python code, and will output it in rtl folder

## rtl

Storing the generated verilog code

## software

Storing software code

## src

Python source code which implemente the first rsic-v

## test

Used to test and verify the Python code in the 'src' folder, and generate waveform file

# Amaranth tutorial
[https://amaranth-lang.org/docs/amaranth/latest](https://amaranth-lang.org/docs/amaranth/latest)
