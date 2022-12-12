from amaranth import Elaboratable, Module, Signal
from amaranth.build import Platform
from amaranth import * 


class Adder(Elaboratable):
    def __init__(self):
        self.x = Signal(signed(16))
        self.y = Signal(signed(16))
        self.out = Signal(signed(32))

    def ports(self):
        return [self.x, self.y, self.out]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        return m
