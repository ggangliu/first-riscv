from amaranth import Elaboratable


class YourModule(Elaboratable):
    ...
    def ports(self):
        return [self.yourmodule.p1, self.yourmodule.p2, ...]
