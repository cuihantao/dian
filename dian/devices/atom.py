"""Atomic classes to build up a device"""
import numpy as np  # NOQA
import sympy as smp  # NOQA
from collections.abc import Iterable  # NOQA


class DataArray(object):
    """Abstract DataArray class for any atomic types"""
    def __init__(self, n: int):
        self.n = n


class Param(object):
    """
    Class for a parameter
    """
    def __init__(self, name: str, host: str):
        self.name = name
        self.host = host
        self.n = 0

        # an array holding parameter values
        self._values_raw = np.array([])

        # a list holding all symbols
        self._symbols = []

        # an array holding parameter values in per unit
        self._values_pu = np.array([])

        # properties

        # key parameter is usually `idx`
        self.is_key = False

        # internal parameter
        self.is_int = False

        # computed internal parameter
        self.is_computed = False

        # external parameter
        self.is_ext = False

        # externally computed parameter
        self.is_ext_computed = False

        # mandatory parameter
        self.is_mandatory = False

        # non computational parameter such as names
        self.is_non_computational = False

        # user defined parameter. Need to supply a function to compute the parameter
        self.is_user_def = False

        # a list of references to the parameters this one depends on
        self._accessor = []

    def insert(self, value_new):
        """
        Insert a value to this parameter

        Parameters
        ----------
        value_new
            Raw value of the new element to insert. It can be a single or array-like

        Returns
        -------
        None
        """
        self._values_raw = np.append(self._values_raw, value_new)

    def initialize(self):
        """
        Initialize the storage for `self._values_raw`, `self._symbols`, and `self._values_pu`

        Returns
        -------
        None
        """
        self._values = np.ndarray([])


class Variable(object):
    pass
