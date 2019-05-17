import logging
import time
import numpy as np  # NOQA
import sympy as smp  # NOQA
import scipy as sp  # NOQA
from sympy import lambdify, sympify  # NOQA
from scipy.optimize import newton_krylov  # NOQA

from dian.system import System

# set up printing options for `sympy` and `numpy`
smp.init_printing()
np.set_printoptions(suppress=True)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


system = System()

system.bus.add_element(idx=0, name="Bus 1", Vn=110)
system.bus.add_element(idx=1, name="Bus 2", Vn=110)
system.bus.add_element(idx=2, name="Bus 3", Vn=110)

system.pq.add_element(idx=0, name="PQ 1", bus=1, p=3, q=0.9861)
# system.pq.add_element(idx=1, name="PQ 2", bus=2, p=3, q=0.9861)

system.line.add_element(idx=0, name="Line 1-2", bus1=0, bus2=1, r=0.00281, x=0.0281, b=0.00712)
system.line.add_element(idx=3, name="Line 2-3", bus1=1, bus2=2, r=0.00108, x=0.0108, b=0.01852)

system.pv.add_element(idx=0, name="PV 1", bus=0, p0=0.4, v0=1)
# system.pv.add_element(idx=1, name="PV 2", bus=0, p0=1.7, v0=1)
# system.pv.add_element(idx=2, name="PV 3", bus=2, p0=3.2349, v0=1)

system.slack.add_element(idx=0, name="Slack 1", bus=1, v0=1, a0=0)

system.bus.metadata_check()
system.pq.metadata_check()
system.line.metadata_check()
system.pv.metadata_check()
system.slack.metadata_check()

system.bus._init_symbols()
system.pq._init_symbols()
system.line._init_symbols()
system.pv._init_symbols()
system.slack._init_symbols()

system.bus._init_data(subs_param_value=True)
system.pq._init_data(subs_param_value=True)
system.line._init_data(subs_param_value=True)
system.pv._init_data(subs_param_value=True)
system.slack._init_data(subs_param_value=True)

system.bus.get_var_address()
system.pq.get_var_address()
system.line.get_var_address()
system.pv.get_var_address()
system.slack.get_var_address()

system.bus.get_algeb_ext()
system.pq.get_algeb_ext()
system.line.get_algeb_ext()
system.pv.get_algeb_ext()
system.slack.get_algeb_ext()

system.bus._init_equation()
system.pq._init_equation()
system.line._init_equation()
system.pv._init_equation()
system.slack._init_equation()


system.bus._compute_param_int()
system.pq._compute_param_int()
system.line._compute_param_int()
system.pv._compute_param_int()
system.slack._compute_param_int()

system.bus._compute_param_custom()
system.pq._compute_param_custom()
system.line._compute_param_custom()
system.pv._compute_param_custom()
system.slack._compute_param_custom()

system.bus._compute_variable()
system.pq._compute_variable()
system.line._compute_variable()
system.pv._compute_variable()
system.slack._compute_variable()

system.bus.make_gcall_int_symbolic()
system.pq.make_gcall_int_symbolic()
system.line.make_gcall_int_symbolic()
system.pv.make_gcall_int_symbolic()
system.slack.make_gcall_int_symbolic()

system.bus.make_gcall_ext_symbolic()
system.pq.make_gcall_ext_symbolic()
system.line.make_gcall_ext_symbolic()
system.pv.make_gcall_ext_symbolic()
system.slack.make_gcall_ext_symbolic()

system.bus.create_param_symbol_value_pair()
system.pq.create_param_symbol_value_pair()
system.line.create_param_symbol_value_pair()
system.pv.create_param_symbol_value_pair()
system.slack.create_param_symbol_value_pair()

system.bus.subs_param_data()
system.pq.subs_param_data()
system.line.subs_param_data()
system.pv.subs_param_data()
system.slack.subs_param_data()

system.bus.delayed_symbol_sub_all(subs_param_value=True)
system.pq.delayed_symbol_sub_all(subs_param_value=True)
system.line.delayed_symbol_sub_all(subs_param_value=True)
system.pv.delayed_symbol_sub_all(subs_param_value=True)
system.slack.delayed_symbol_sub_all(subs_param_value=True)

system.dae.initialize_xyfg_empty()
system.collect_algeb_int_equations()
system.collect_algeb_ext_equations()

system.bus.compute_and_set_initial_values(subs_param_value=True)
system.pq.compute_and_set_initial_values(subs_param_value=True)
system.line.compute_and_set_initial_values(subs_param_value=True)
system.pv.compute_and_set_initial_values(subs_param_value=True)
system.slack.compute_and_set_initial_values(subs_param_value=True)

system.collect_initial_values()

system.dae.summary()

# NOTE: there was an issue with incorrect initialization of voltage when there is no PV or Slack connection
# TODO: probably allow for setting default/fool-proof initial values when defining the variable

t0 = time.time()
sol = system.dae.solve_algebs(method='newton_krylov')
te = time.time() - t0

print(f'Elapsed time: {te}s')

print('\n--> Power flow results:')
print(f'Voltage phases (deg): {np.degrees(sol[0:system.bus.n])}')
print(f'Voltage magnitudes (pu): {sol[system.bus.n:2*system.bus.n]}')
print(f'Reactive power for pv, slack (pu): {sol[2*system.bus.n:2*system.bus.n + system.pv.n + system.slack.n]}')
print(f'Active power for slack (pu): {sol[2*system.bus.n + system.pv.n + system.slack.n]}')
