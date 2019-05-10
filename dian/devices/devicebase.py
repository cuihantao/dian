from collections import OrderedDict
from collections.abc import Iterable  # NOQA
import sympy as smp
from sympy.tensor.array import MutableDenseNDimArray
import logging
import numpy as np
from dian.utils import non_commutative_sympify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
logger.addHandler(sh)


class DeviceBase(object):
    """
    Base class for devices with universal properties and functions

    """
    def __init__(self, system):

        self.system = system
        self.idx = []

        # options for the whole class
        self._options = OrderedDict()

        # default set of parameters
        self._param_int = ['name', 'u']
        self._param_int_default = {'name': '', 'u': 1}
        self._param_int_non_computational = ['name']

        # computed internal parameters in a list of (parameter, equation)
        self._param_int_computed = OrderedDict()

        # internal parameters that are computed with custom functions
        self._param_int_custom = []

        # external parameters before any computation in tuples (device, original_name, new_name)
        self._param_ext = []  # TODO: method to update external parameters

        # external parameters that are computed by the external device in tuples (device, original name, new_name)
        self._param_ext_computed = []  # TODO: method to update computed external parameters

        # store the idx to internal index mapping
        self._int = OrderedDict()

        # define the parameters of the current model that are referencing the idx of other devices in tuples of
        # (device, parameter)
        self._foreign_keys = OrderedDict()

        # define the internal algebraic variables of the current model
        self._algeb_int = []

        # define the internal algebraic variables that are also interface variables
        self._algeb_intf = []

        # define the external algebraic variables that are interface variables of other devices in tuples
        # (model, algeb_name)
        self._algeb_ext = OrderedDict()

        # computed algebraic variables using either internal or external algebs
        self._var_int_computed = OrderedDict()

        # internal custom computed variables
        self._var_int_custom = OrderedDict()

        # define the internal state variables of the current model
        self._state_int = []

        # define the internal state variables that are also interface variables (UNCOMMON)
        self._state_intf = []

        # define the external state variables that are interface variables of other devices in tuples
        # (model, algeb_name) (UNCOMMON)
        self._state_ext = []

        # define the current status in the work flow
        self._workflow = None

        # equations to be added to the external algebraic equations. Must correspond to `_algeb_ext`
        self._gcall_ext = OrderedDict()
        self._gcall_ext_symbolic_singleton = OrderedDict()
        self._gcall_ext_symbolic = OrderedDict()

        # pairs of singleton variables and symbols, e.g., ('a', a)
        self._symbol_singleton = OrderedDict()

        # internal gcall equations, must equal to the number of `_gcall_int`
        self._gcall_int = OrderedDict()
        self._gcall_int_symbolic_singleton = OrderedDict()
        self._gcall_int_symbolic = OrderedDict()

        # special flags
        self._special_flags = {'no_algeb_ext_check': False,
                               'state_group_by_element': True,
                               'algeb_group_by_element': True,
                               }

        # non-commutative var_int
        self._var_int_non_commutative = OrderedDict()

        # dae address for variable and equations
        self._dae_address = OrderedDict()

    def load_param_from_dataframe(self):
        """
        load parameters of multiple elements from a pandas dataframe

        Returns
        -------
        None

        """
        pass

    def make_gcall_ext_symbolic(self):
        """Generate `self._gcall_ext_symbolic` from `self._gcall_ext`
        """
        # temporary OrderedDict
        _gcall_ext_symbolic = OrderedDict()

        for var, eq in self._gcall_ext.items():
            # convert equation singleton
            equation_singleton = smp.sympify(eq)
            self._gcall_ext_symbolic_singleton[var] = equation_singleton

            # substitute singleton with element variables
            _gcall_ext_symbolic[var] = self._subs_all_vectorized(equation_singleton, return_as=smp.Array)

        self._gcall_ext_symbolic = _gcall_ext_symbolic

    def make_gcall_int_symbolic(self):
        """Generate `self._gcall_int_symbolic` from `self._gcall_int`
        """
        # temporary OrderedDict
        _gcall_int_symbolic = OrderedDict()

        for var, eq in self._gcall_int.items():
            # convert equation singleton
            equation_singleton = smp.sympify(eq)
            self._gcall_int_symbolic_singleton[var] = equation_singleton

            # substitute singleton with element variables
            _gcall_int_symbolic[var] = self._subs_all_vectorized(equation_singleton, return_as=smp.Array)

        self._gcall_int_symbolic = _gcall_int_symbolic

    def _subs_all_vectorized(self, equation_singleton, return_as=list):
        """Substitute symbol singletons with element-wise variable names for the provided expression"""

        free_syms = equation_singleton.free_symbols

        n_element = min([len(self.__dict__[str(x)]) for x in free_syms])

        ret = [0] * n_element
        for i in range(n_element):

            sym_list = []
            for symbol in free_syms:
                sym = str(symbol)

                if len(self.__dict__[sym]) == 0:
                    logger.debug(f'_subs_all skips variable {sym} due to empty length')
                    continue
                sym_list.append((symbol, self.__dict__[sym][i]))

            ret[i] = equation_singleton.subs(sym_list)

        # process return type
        if return_as is list:
            pass
        else:
            ret = return_as(ret)

        return ret

    def _subs_all_singleton(self, equation_singleton, return_as=None):
        """Substitute symbol singletons with symbols expression"""

        free_syms = equation_singleton.free_symbols

        sym_list = []
        for symbol in free_syms:
            sym = str(symbol)
            sym_list.append((symbol, self.__dict__[sym]))

        # use `simultaneous` subs for matrix substitution
        ret = equation_singleton.subs(sym_list, simultaneous=True)

        # process return type
        if return_as is None:
            pass
        else:
            ret = return_as(ret)
        return ret

    def _convert_dict_val_to_Array(self, data):
        """Take an OrderedDict and covert the items from lists to sympy Arrays"""
        for key in data.keys():
            data[key] = smp.Array(data[key])
        return data

    def _convert_list_to_Array(self, data):
        """Take a list and covert it to a sympy Array"""
        return smp.Array(data)

    def load_param_by_row(self, **kwargs):
        """
        Load parameters of a single element (row) from parameter values
        Returns
        -------

        """
        # for key, val in kwargs.items():
        #     if key not in
        pass

    def _init_data(self):
        """Initialize class based on metadata provided in `__init__()`
        """
        # TODO: check for name conflicts

        if self.n == 0:
            return False

        # all computational parameters
        param_int_computational = (set(self._param_int) - set(self._param_int_non_computational))
        if len(param_int_computational) > 0:
            logger.debug(f'{self.__class__.__name__} Param internal computational: ')
            for item in param_int_computational:
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item)
                logger.debug(self.__dict__[item])

        # create placeholders for computed internal parameters
        if len(self._param_int_computed) > 0:
            logger.debug(f'{self.__class__.__name__} Param computed place holder: ')
            for item in self._param_int_computed.keys():
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item)
                logger.debug(self.__dict__[item])

        # create placeholder in `self.__dict__` for custom computed parameters
        if len(self._param_int_custom) > 0:
            logger.debug(f'{self.__class__.__name__} Param custom place holder: ')
            for item in self._param_int_custom:
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item)
                logger.debug(self.__dict__[item])

        # _algeb_int
        if len(self._algeb_int):
            logger.debug(f'{self.__class__.__name__} Internal algeb variables:')
            for item in self._algeb_int:
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item)
                # TODO: register for a variable number in the DAE system
                logger.debug(self.__dict__[item])

        # internal variabled computed
        if len(self._var_int_computed):
            logger.debug(f'{self.__class__.__name__} Algebraic variables computed:')
            for item in self._var_int_computed:
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item, commutative=False)
                logger.debug(self.__dict__[item])

        # _state_int
        if len(self._state_int):
            logger.debug(f'{self.__class__.__name__} Internal state variables:')
            for item in self._state_int:
                self.__dict__[item] = MutableDenseNDimArray(smp.symbols(self.__class__.__name__ +
                                                                        f'_{item}_0:{self.n}'))
                self._symbol_singleton[item] = smp.symbols(item)
                # TODO: register for a variable number in the DAE system
                logger.debug(self.__dict__[item])

    def get_foreign_param(self, update=False):

        pass

    def get_algeb_ext(self):

        if len(self._algeb_ext) > 0:
            logger.debug(f'{self.__class__.__name__} External algebraic variables of device')

            for dest, (fkey, var_name) in self._algeb_ext.items():

                if fkey in self._param_int:  # if fkey is a valid parameter input
                    dev = self._foreign_keys[fkey]
                    int_keys = self._get_int_of_foreign_element(dev, fkey)
                else:  # fkey is a device name instead
                    dev = fkey
                    fkey_values = self.system.__dict__[fkey.lower()].idx
                    int_keys = self.system.__dict__[dev.lower()].idx2int(fkey_values)

                # store indices of this to `{dest}_idx`
                dev_ref = self.system.__dict__[dev.lower()]
                self.__dict__[f'_{dest}_addr'] = dev_ref._dae_address[f'{var_name}'][int_keys]  #
                # deprecated
                self._dae_address[f'{dest}'] = dev_ref._dae_address[f'{var_name}'][int_keys]

                # get external algebraic VARIABLES by accessing
                algeb_symbol_list = self.get_list_of_symbols_from_ext(dev, var_name, int_keys)
                self.__dict__[dest] = smp.Array(algeb_symbol_list)
                self._symbol_singleton[dest] = smp.symbols(var_name)
                logger.debug(self.__dict__[dest])

    def _get_int_of_foreign_element(self, dev, fkey):
        assert dev in self._foreign_keys.values()

        fkey_values = self.__dict__[fkey]
        return self.system.__dict__[dev.lower()].idx2int(fkey_values)

    def get_list_of_symbols_from_ext(self, dev, var_name, int):
        """
        Get a list of symbols from external devices based on the fkey linked to the idx of external devices

        Parameters
        ----------
        dev

        fkey

        Returns
        -------

        """
        dev = dev.lower()
        if isinstance(int, np.ndarray):
            int = int.tolist()
        return [self.system.__dict__[dev].__dict__[var_name][i] for i in int]

    def idx2int(self, idx):
        """
        Convert external indicex `idx` to internal indices
        Returns
        -------

        """
        return np.array([self._int[i] for i in idx])

    def n_elements_with_default_mapping(self, n: int):
        """
        Set the number of elements to n with default {i:i} mapping where i in range(n)
        Parameters
        ----------
        n : int
            The number of elements to add
        Returns
        -------

        """

        assert n >= 0
        self.idx = list(range(n))
        self._int = {i: i for i in self.idx}

    def _init_equation(self):
        """
        Create storage arrays for equations

        Returns
        -------

        """
        for item in (self._algeb_int + self._algeb_intf + self._state_int):
            eq_name = f'_{item}'  # equation names starts with "_" and follows with the corresponding var name
            self.__dict__[eq_name] = MutableDenseNDimArray([0] * self.n)
            logger.debug(self.__dict__[eq_name])

    def _check_number_of_algeb_equations(self):
        """Check the number of algebraic equations so that n_algeb = n_algeb_equations

        """
        if self._special_flags['no_algeb_ext_check'] is False:
            assert len(self._algeb_ext) == len(self._gcall_ext), "{} Number of _algeb_ext does not equal " \
                                                                 "_gcall_ext".format(self.__class__.__name__)
        assert len(self._algeb_int) - len(self._algeb_intf) <= \
            len(self._gcall_int), "{} Too few gcall_int equations".format(self.__class__.__name__)

    def metadata_check(self):
        """Check the metadata and find inconsistency
        """
        self._check_number_of_algeb_equations()

    def _compute_param_int(self):
        """
        Compute internal parameters based on `self._param_int_computed`
        Returns
        -------

        """
        # process internally computed parameters

        if len(self._param_int_computed) > 0:
            logger.debug(f'{self.__class__.__name__} Param computed: ')
            for var, eq in self._param_int_computed.items():
                equation_singleton = smp.sympify(eq)
                self.__dict__[var] = self._subs_all_vectorized(equation_singleton)
                logger.debug(self.__dict__[var])

    def _compute_variable(self):
        """
        Compute variables as defined in `self._var_int_computed`

        Returns
        -------

        """
        if len(self._var_int_computed) > 0:
            logger.debug(f'{self.__class__.__name__} Variables computed: ')
            for var, eq in self._var_int_computed.items():
                compute_type = 'vectorized'
                return_type = None
                # support a list of
                # a) [equation]
                # b) [equation, compute_type]
                # c) [equation, compute_type, return_type]
                if isinstance(eq, list):
                    if len(eq) == 3:
                        eq, compute_type, return_type = eq
                    elif len(eq) == 2:
                        eq, compute_type = eq
                    elif len(eq) == 1:
                        eq = eq[0]
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError

                equation_singleton = non_commutative_sympify(eq)

                # process compute_type
                if compute_type == 'vectorized':
                    self.__dict__[var] = self._subs_all_vectorized(equation_singleton, return_as=smp.Array)
                elif compute_type == 'singleton':
                    self.__dict__[var] = self._subs_all_singleton(equation_singleton)
                else:
                    raise NotImplementedError

                if return_type is not None:
                    self.__dict__[var] = return_type(self.__dict__[var])
                logger.debug(self.__dict__[var])

    def _compute_variable_custom(self):
        """

        Returns
        -------

        """
        pass

    def _compute_param_custom(self):
        """
        Compute custom parameters. To be called at the end of the parameter creation process.

        Parameter initialization:

        _param_int
        _param_ext
        _param_int_computed
        _param_ext_computed
        _param_int_custom

        Returns
        -------

        """
        pass

    @property
    def n(self):
        """
        The count of elements obtained from len(self._idx)

        Returns
        -------
        int
            The count of elements
        """
        return len(self.idx)

    def get_var_address(self):
        """Request address for variables in global DAE
        """

        # state variables
        ret = self.system.dae.new_idx(device=self, var_type='x', var_name=self._state_int,
                                      group_by_element=self._special_flags['state_group_by_element'])

        for key, val in ret.items():
            self.__dict__[f'_{key}_addr'] = val
        self._dae_address.update(ret)

        # algebraic variables
        ret = self.system.dae.new_idx(device=self, var_type='y', var_name=self._algeb_int,
                                      group_by_element=self._special_flags['algeb_group_by_element'])
        for key, val in ret.items():
            self.__dict__[f'_{key}_addr'] = val
        self._dae_address.update(ret)


class DeviceData(object):
    """Class for storing device data"""
    def __init__(self, device: str, param: list, n_element=0):
        self.device = device  # name of the device to which the data belongs
        for item in param:
            self.__dict__[item] = np.ndarray((n_element, ))
