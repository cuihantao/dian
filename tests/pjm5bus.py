import numpy as np
import sympy as smp  # NOQA
from dian.system import System
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

system = System()

system.bus.create_n_default_elements(5)
system.pq.create_n_default_elements(3)
system.line.create_n_default_elements(6)
system.pv.create_n_default_elements(4)
system.shunt.create_n_default_elements(0)

system.pq.bus = np.array([1, 2, 3])
system.pv.bus = np.array([0, 1, 2, 4])

system.line.bus1 = np.array([0, 0, 0, 1, 2, 3])
system.line.bus2 = np.array([1, 3, 4, 2, 3, 4])

system.bus.metadata_check()
system.pq.metadata_check()
system.line.metadata_check()
system.pv.metadata_check()

system.bus._init_symbols()
system.pq._init_symbols()
system.line._init_symbols()
system.pv._init_symbols()

system.bus._init_data()
system.pq._init_data()
system.line._init_data()
system.pv._init_data()

system.bus.get_var_address()
system.pq.get_var_address()
system.line.get_var_address()
system.pv.get_var_address()

system.bus.get_algeb_ext()
system.pq.get_algeb_ext()
system.line.get_algeb_ext()
system.pv.get_algeb_ext()

system.bus._init_equation()
system.pq._init_equation()
system.line._init_equation()
system.pv._init_equation()

system.bus._compute_param_int()
system.pq._compute_param_int()
system.line._compute_param_int()
system.pv._compute_param_int()

system.bus._compute_param_custom()
system.pq._compute_param_custom()
system.line._compute_param_custom()
system.pv._compute_param_custom()

system.bus._compute_variable()
system.pq._compute_variable()
system.line._compute_variable()
system.pv._compute_variable()

system.bus.make_gcall_int_symbolic()
system.pq.make_gcall_int_symbolic()
system.line.make_gcall_int_symbolic()
system.pv.make_gcall_int_symbolic()

system.bus.make_gcall_ext_symbolic()
system.pq.make_gcall_ext_symbolic()
system.line.make_gcall_ext_symbolic()
system.pv.make_gcall_ext_symbolic()

system.bus.delayed_symbol_sub_all()
system.pq.delayed_symbol_sub_all()
system.line.delayed_symbol_sub_all()
system.pv.delayed_symbol_sub_all()

system.dae.initialize_xyfg_empty()
system.collect_algeb_int_equations()
system.collect_algeb_ext_equations()
