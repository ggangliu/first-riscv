from amaranth import ClockDomain, Module
from amaranth.cli import main
from amaranth_boards.arty_a7 import ArtyA7_100Platform

from thing_block import ThingBlock

# Usage: python3 elaborate_main.py generate -t [v|il|cc] > thing.[v|il|cc]
# ArtyA7_100Platform

if __name__ == "__main__":
    sync = ClockDomain()

    block = ThingBlock()

    m = Module()
    m.domains += sync
    m.submodules += block

    main(m, ports=[sync.clk, sync.rst], platform=None """ArtyA7_100Platform""")
