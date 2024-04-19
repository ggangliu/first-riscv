# LLVM first-riscv

## 添加first-riscv后端

为first-riscv添加专用后端

## 添加自定义指令

对自定义指令的支持有三种形式：

1. 直接编写汇编代码
2. 在C/C++程序中使用Intrinsic函数
   1. [RISC-V Vector Intrinsics](https://github.com/riscv/rvv-intrinsic-doc)
3. 通过优化技术将C/C++程序自动转换成向量指令
