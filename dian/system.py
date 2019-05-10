from .devices.bus import Bus
from .devices.pqload import PQ
from .devices.line import Line
from .devices.pvgen import PV
from .devices.shunt import Shunt
from .dae import DAE


class System(object):
    def __init__(self):
        self.devices = ['bus', 'pq', 'line', 'pv', 'shunt']

        self.bus = Bus(system=self)
        self.pq = PQ(system=self)
        self.line = Line(system=self)
        self.pv = PV(system=self)
        self.shunt = Shunt(system=self)
        self.dae = DAE(system=self)

    def collect_algeb_int_equations(self):
        """Collect algebraic equations defined for device internals"""
        for dev in self.devices:
            dev_ref = self.__dict__[dev]
            algeb_int_list = dev_ref._algeb_int
            dae_addr = dev_ref._dae_address
            gcall_syms = dev_ref._gcall_int_symbolic

            for variable in algeb_int_list:
                if variable not in gcall_syms:
                    print(f'{variable} internal equation not found in device {dev}')
                    continue

                dae_addr_var = dae_addr[variable]
                for idx, addr in enumerate(dae_addr_var):
                    self.dae.g[addr] = self.dae.g[addr] + gcall_syms[variable][idx]
                    # may replace in-place add with assignment

    def collect_algeb_ext_equations(self):
        """Collect algebraic equations defined for external variables"""
        for dev in self.devices:
            dev_ref = self.__dict__[dev]
            algeb_ext_list = dev_ref._algeb_ext.keys()
            dae_addr = dev_ref._dae_address
            gcall_syms = dev_ref._gcall_ext_symbolic

            for variable in algeb_ext_list:
                if variable not in gcall_syms:
                    print(f'{variable} external equation not found in device {dev}')
                    continue

                dae_addr_var = dae_addr[variable]
                for idx, addr in enumerate(dae_addr_var):
                    self.dae.g[addr] = self.dae.g[addr] + gcall_syms[variable][idx]




    def collect_algeb_variables(self):
        pass
