# firstRISCV
尝试用Python实现一个RISCV CPU，从而达到学习RISCV ISA的目的


## RISCV core
Riscv核的核心逻辑介绍

## ROM
CPU的bootloader程序将存储在ROM中，也是CPU启动后运行的第一个程序，因此这里需要添加ROM的支持

## RAM
由于程序运行过程中需要堆栈，因此RAM也是必不可少的部件

## PIN
1. 用于连接UART串口，从而支持串口输出/输入
2. 用于控制外接LED，进行外部LED的点亮
