from amaranth.asserts import Assert, Assume, Cover
from amaranth.asserts import Past, Rose, Fell, Stable
from amaranth.cli import main_parser, main_runner
from amaranth import Module
from adder import Adder

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.submodules.adder = adder = Adder()

    m.d.comb += Assert(adder.out == (adder.x + adder.y)[:8])

    with m.If(adder.x == (adder.y << 1)):
        m.d.comb += Cover((adder.out > 0x00) & (adder.out < 0x40))

    main_runner(parser, args, m, ports=[] + adder.ports())
