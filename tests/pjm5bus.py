import numpy as np  # NOQA
import sympy as smp  # NOQA
from dian.system import System
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

system = System()

system.bus.add_element(idx=0, name="Bus 1", Vn=110)
system.bus.add_element(idx=1, name="Bus 2", Vn=110)
system.bus.add_element(idx=2, name="Bus 3", Vn=110)
system.bus.add_element(idx=3, name="Bus 4", Vn=110)
system.bus.add_element(idx=4, name="Bus 5", Vn=110)

system.pq.add_element(idx=0, name="PQ 1", bus=1, p=3, q=0.9861)
system.pq.add_element(idx=1, name="PQ 2", bus=2, p=3, q=0.9861)
system.pq.add_element(idx=2, name="PQ 3", bus=3, p=4, q=1.3147)

system.line.add_element(idx=0, name="Line 1-2", bus1=0, bus2=1, r=0.00281, x=0.0281, b=0.00712)
system.line.add_element(idx=1, name="Line 1-4", bus1=0, bus2=3, r=0.00304, x=0.0304, b=0.00658)
system.line.add_element(idx=2, name="Line 1-5", bus1=0, bus2=4, r=0.00064, x=0.0064, b=0.03126)
system.line.add_element(idx=3, name="Line 2-3", bus1=1, bus2=2, r=0.00108, x=0.0108, b=0.01852)
system.line.add_element(idx=4, name="Line 3-4", bus1=2, bus2=3, r=0.00297, x=0.0297, b=0.00674)
system.line.add_element(idx=5, name="Line 4-5", bus1=3, bus2=4, r=0.00297, x=0.0297, b=0.00674)

system.pv.add_element(idx=0, name="PV 1", bus=0, p0=0.4, v0=1)
system.pv.add_element(idx=1, name="PV 2", bus=1, p0=1.7, v0=1)
system.pv.add_element(idx=2, name="PV 3", bus=2, p0=3.2349, v0=1)
system.pv.add_element(idx=3, name="PV 5", bus=4, p0=4.6651, v0=1)

system.slack.add_element(idx=0, name="Slack 1", bus=3, v0=1, a0=0)

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

logger.info(f'\nNumber of equations: {len(system.dae.g)}, Number of variables: {len(system.dae.y)}')
jac = smp.SparseMatrix(system.dae.g).jacobian(system.dae.y)
logger.info(jac)
