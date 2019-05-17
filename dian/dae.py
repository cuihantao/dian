import numpy as np
import scipy as sp

import sympy as smp  # NOQA

from sympy import lambdify, Matrix
from scipy.optimize import newton_krylov  # NOQA

from typing import Iterable
from collections import OrderedDict


class DAE(object):
    """Differential algebraic equation class that implements the equations provided by devices
    """
    def __init__(self, system):
        self.system = system

        # variable symbols
        self.x = []
        self.y = []

        # variable numeric values
        self.x_num = []
        self.y_num = []

        # location of variable symbols (device, var_name, int)
        self._x = []
        self._y = []

        # equation symbols
        self.f = []
        self.g = []

        # equation numeric values
        self.f_num = []
        self.g_num = []

        # TODO: location of equations that modified the corresponding equation
        self._f = []
        self._g = []

        self.fx = []
        self.fy = []
        self.gx = []
        self.gy = []

        # function calls lambdified from `self.g` and `self.f`
        self.g_func = None
        self.f_func = None

        self.m = 0
        self.n = 0

    def new_idx(self, device, var_type, var_name: Iterable, group_by_element=True):
        assert var_type in ('x', 'y')

        n_element = device.n
        out = OrderedDict()
        for var in var_name:
            out[var] = np.ndarray((n_element, ), dtype=int)

        if group_by_element is False:
            # Group by variable
            for var in var_name:
                if var_type == 'y':
                    self._y.extend([(device.classname.lower(), var, i) for i in range(n_element)])
                    self.y.extend([device.__dict__[var][i] for i in range(n_element)])
                    out[var] = np.arange(self.m, self.m + n_element)
                    self.m = self.m + n_element
                elif var_type == 'x':
                    self._x.extend([(device.classname.lower(), var, i) for i in range(n_element)])
                    self.x.extend([device.__dict__[var][i] for i in range(n_element)])
                    out[var] = np.arange(self.n, self.n + n_element)
                    self.n = self.n + n_element

        else:
            # group by element
            for idx in range(n_element):

                if var_type == 'y':
                    self._y.extend([device.classname.lower(), var, idx] for var in var_name)
                    self.y.extend([device.__dict__[var][idx] for var in var_name])
                    for var in var_name:
                        out[var][idx] = self.m
                        self.m = self.m + 1
                elif var_type == 'x':
                    self._x.extend([device.classname.lower(), var, idx] for var in var_name)
                    self.x.extend([device.__dict__[var][idx] for var in var_name])
                    for var in var_name:
                        out[var][idx] = self.n
                        self.n = self.n + 1

        return out

    def initialize_xyfg_empty(self):
        """
        Initialize x, y, f, g as empty lists based on sizes defined in `self.m` and `self.n`

        Returns
        -------

        """
        # self.x = [0] * self.n
        self.f = [0] * self.n

        self.x_num = np.zeros((self.n, ))
        self.f_num = np.zeros((self.n, ))

        # self.y = [0] * self.m
        self.g = [0] * self.m

        self.y_num = np.zeros((self.m, ))
        self.g_num = np.zeros((self.m, ))

    @property
    def y_pairs(self):
        """
        Return a list of (symbol, numeric value) pairs for algebraic variables

        Returns
        -------

        """
        return [(x, y) for x, y in zip(self.y, self.y_num.tolist())]

    @property
    def y_pairs_dict(self):
        return {x: y for x, y in zip(self.y, self.y_num.tolist())}

    def summary(self):
        """
        Print a summary of the this class

        Returns
        -------

        """
        out = ''
        out += '\n--> DAE summary:'
        out += f'dae.m = {self.m}, N algeb eqs: {len(self.g)} ' + (u'\u2713' if self.m == len(self.g) else
                                                                   u'\u2717')
        out += f'dae.n = {self.n}, N state eqs: {len(self.f)} ' + (u'\u2713' if self.n == len(self.f) else
                                                                   u'\u2717')
        out += f'dae.y_num = {self.y_num}'
        out += f'dae.x_num = {self.x_num}'

    def lambdify_algebs(self):
        """Convert algebraic equations in `self.g` to lambdified function calls and store in `self.g_func`.

        The lambdified function takes an argument of variable arrays.

        Returns
        -------
        None
        """
        self.g_func = lambdify((self.y, ), self.g)

    def solve_algebs(self, method='newton_krylov'):
        """
        Solve the algebraic equations numerically

        Returns
        -------
        None
        """
        if self.g_func is None:
            self.lambdify_algebs()

        # NOTE: not all methods converge.
        #       Not working: newton, anderson
        #       working: newton_krylov
        return sp.optimize.__dict__[method](self.g_func, self.y_num)

    def make_gy(self):
        """
        Generate the Jacobian matrix dg/dy

        Returns
        -------
        None
        """
        return Matrix(self.g).jacobian(self.y)
