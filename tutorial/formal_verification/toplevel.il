attribute \generator "Amaranth"
attribute \amaranth.hierarchy "top.adder"
module \adder
  wire width 1 $empty_module_filler
end
attribute \generator "Amaranth"
attribute \top 1
attribute \amaranth.hierarchy "top"
module \top
  attribute \src "/home/ggangliu/first-riscv/tutorial/formal_verification/adder.py:8"
  wire width 16 input 0 \x
  attribute \src "/home/ggangliu/first-riscv/tutorial/formal_verification/adder.py:9"
  wire width 16 input 1 \y
  attribute \src "/home/ggangliu/first-riscv/tutorial/formal_verification/adder.py:10"
  wire width 32 input 2 \out
  cell \adder \adder
  end
  attribute \src "adder_test.py:14"
  wire width 1 $assert$en
  attribute \src "adder_test.py:14"
  wire width 1 $assert$check
  attribute \src "/home/ggangliu/.local/lib/python3.8/site-packages/amaranth/hdl/ast.py:254"
  wire width 32 $1
  attribute \src "adder_test.py:14"
  wire width 17 $2
  attribute \src "adder_test.py:14"
  wire width 17 $3
  attribute \src "adder_test.py:14"
  cell $add $4
    parameter \A_SIGNED 1
    parameter \A_WIDTH 16
    parameter \B_SIGNED 1
    parameter \B_WIDTH 16
    parameter \Y_WIDTH 17
    connect \A \x
    connect \B \y
    connect \Y $3
  end
  connect $2 $3
  attribute \src "/home/ggangliu/.local/lib/python3.8/site-packages/amaranth/hdl/ast.py:254"
  cell $pos $5
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \Y_WIDTH 32
    connect \A $2 [7:0]
    connect \Y $1
  end
  attribute \src "adder_test.py:14"
  wire width 1 $6
  attribute \src "adder_test.py:14"
  cell $eq $7
    parameter \A_SIGNED 1
    parameter \A_WIDTH 32
    parameter \B_SIGNED 1
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B $1
    connect \Y $6
  end
  attribute \src "adder_test.py:14"
  cell $assert $8
    connect \A $assert$check
    connect \EN $assert$en
  end
  process $group_0
    assign $assert$en 1'0
    assign $assert$check 1'0
    assign $assert$check $6
    assign $assert$en 1'1
    sync init
  end
  attribute \src "adder_test.py:17"
  wire width 1 $cover$en
  attribute \src "adder_test.py:17"
  wire width 1 $cover$check
  attribute \src "adder_test.py:16"
  wire width 17 $9
  attribute \src "adder_test.py:16"
  cell $sshl $10
    parameter \A_SIGNED 1
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 17
    connect \A \y
    connect \B 1'1
    connect \Y $9
  end
  attribute \src "adder_test.py:16"
  wire width 1 $11
  attribute \src "adder_test.py:16"
  cell $eq $12
    parameter \A_SIGNED 1
    parameter \A_WIDTH 16
    parameter \B_SIGNED 1
    parameter \B_WIDTH 17
    parameter \Y_WIDTH 1
    connect \A \x
    connect \B $9
    connect \Y $11
  end
  attribute \src "adder_test.py:17"
  wire width 1 $13
  attribute \src "adder_test.py:17"
  cell $gt $14
    parameter \A_SIGNED 1
    parameter \A_WIDTH 32
    parameter \B_SIGNED 1
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B 32'00000000000000000000000000000000
    connect \Y $13
  end
  attribute \src "adder_test.py:17"
  wire width 1 $15
  attribute \src "adder_test.py:17"
  cell $lt $16
    parameter \A_SIGNED 1
    parameter \A_WIDTH 32
    parameter \B_SIGNED 1
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B 32'00000000000000000000000001000000
    connect \Y $15
  end
  attribute \src "adder_test.py:17"
  wire width 1 $17
  attribute \src "adder_test.py:17"
  cell $and $18
    parameter \A_SIGNED 0
    parameter \A_WIDTH 1
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A $13
    connect \B $15
    connect \Y $17
  end
  attribute \src "adder_test.py:17"
  cell $cover $19
    connect \A $cover$check
    connect \EN $cover$en
  end
  process $group_2
    assign $cover$en 1'0
    assign $cover$check 1'0
    attribute \src "adder_test.py:16"
    switch { $11 }
      attribute \src "adder_test.py:16"
      case 1'1
        assign $cover$check $17
        assign $cover$en 1'1
    end
    sync init
  end
end

