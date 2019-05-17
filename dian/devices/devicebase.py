import sympy as smp  # NOQA
import numpy as np
import logging
import pprint

from sympy import symbols, MatrixSymbol  # NOQA
from sympy import Array, Matrix, sympify  # NOQA
from collections import OrderedDict
from sympy.tensor.array import MutableDenseNDimArray
from dian.utils import non_commutative_sympify

logger = logging.getLogger(__name__)


class DeviceBase(object):
    """
    Base class for devices with universal properties and functions
    """
    #  {Constant, Symbol {scalar, vector {parameter, variable{internal, external}, matrix}, Anything}

    def __init__(self, system):

        self.system = system
        self.idx = []

        # options for the whole class
        self._options = OrderedDict()

        # parameter data stored in the value of the OrderedDictionary, includes params defined in `_param_int`,
        # `_param_int_computed`, `_param_int_custom`, `_param_ext`, and `_param_ext_computed`
        self._param_data = OrderedDict()

        # key: parameter name, value: (list of symbols, list of values)
        self._param_sym_val_pair = OrderedDict()

        # default set of parameters
        self._param_int = ['name', 'u']
        self._param_int_default = {'name': '', 'u': 1}
        self._param_int_non_computational = ['name']
        self._param_int_mandatory = []

        # computed internal parameters in a list of (parameter, equation)
        self._param_int_computed = OrderedDict()

        # internal parameters that are computed with custom functions
        self._param_int_custom = []

        # external parameters before any computation in tuples (device, original_name, new_name)
        self._param_ext = []  # TODO: may change to OrderedDict; method to update external parameters

        # external parameters that are computed by the external device in tuples (device, original name, new_name)
        self._param_ext_computed = []
        # TODO: may change to OrderedDict, method to update computed external parameters

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

        # initial values of the variables
        # A dictionary with the key being the tuple of destination (device, var_name, fkey, operation),
        #   where `device` is the name of the device or `self,
        #         `var_name` is the variable name
        #         `fkey` is the foreign key indexing into `idx` of the device
        #         `operation` is the type of math operation in ('set', 'add')
        #   and the value being the equation string
        self._var_value_initial = OrderedDict()
        self._var_value_initial_symbolic = OrderedDict()
        self._var_value_initial_numeric = OrderedDict()

        # variable data during iteration
        self._var_data = OrderedDict()

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

        # internal fcall equations
        self._fcall_int = OrderedDict()
        self._fcall_int_symbolic_singleton = OrderedDict()
        self._fcall_int_symbolic = OrderedDict()

        # special flags
        self._special_flags = {'no_algeb_ext_check': False,
                               'state_group_by_element': True,
                               'algeb_group_by_element': True,
                               }

        # non-commutative var_int
        self._var_int_non_commutative = OrderedDict()

        # dae address for variable and equations
        self._dae_address = OrderedDict()

    def meta_summary(self):
        """
        Generate a summary for the metadata of this device class

        Returns
        -------
        None
        """
        pass

    def init_symbols(self, init_type='symbol'):
        """
        Create symbol singletons in the first place for parameters and variables

        Dictionaries:
        - _gcall_int
        - _fcall_int
        - _var_int_computed
        - _var_int_custom
        Lists:
        - _param_int

        Returns
        -------
        None
        """
        assert init_type in ('symbol', 'array')

        meta_lists = ['_param_int', '_algeb_int', '_state_int', '_algeb_ext', '_param_ext']

        meta_dicts = ['_gcall_int', '_fcall_int', '_param_int_computed', '_var_int_computed']

        with_types = ['_var_int_custom']

        for item in meta_lists:
            for symbol_str in self.__dict__[item]:
                if symbol_str in self._symbol_singleton:
                    continue
                if init_type == 'symbol':
                    self._symbol_singleton[symbol_str] = symbols(symbol_str)
                elif init_type == 'array':
                    self._symbol_singleton[symbol_str] = MatrixSymbol(symbol_str, self.n, 1)

        for item in meta_dicts:
            for symbol_str in self.__dict__[item].keys():
                if symbol_str in self._symbol_singleton:
                    continue
                if init_type == 'symbol':
                    self._symbol_singleton[symbol_str] = symbols(symbol_str)
                elif init_type == 'array':
                    self._symbol_singleton[symbol_str] = MatrixSymbol(symbol_str, self.n, 1)

        for item in with_types:
            for symbol_str in self.__dict__[item].keys():
                if symbol_str in self._symbol_singleton:
                    continue
                if init_type == 'symbol':
                    self._symbol_singleton[symbol_str] = symbols(symbol_str, commutative=False)
                elif init_type == 'array':
                    # TODO: this is to be implemented. The matrix size of the custom variable need to be
                    #  specifiable by the device definition
                    # raise NotImplementedError
                    pass
                    # self._symbol_singleton[symbol_str] = MatrixSymbol(symbol_str,)

        logger.debug(f'\n--> {self.__class__.__name__}: Initialized symbols: '
                     f'{pprint.pformat(self._symbol_singleton)}')

    def init_data(self, subs_param_value=False):
        """
        Initialize data members based on metadata provided in `__init__()`

        Returns
        -------

        """
        # TODO: check for name conflicts

        if self.n == 0:
            return False
        logger.debug(f'\n--> {self.classname}: Entering _init_data() with subs_param_value={subs_param_value}')
        # all computational parameters
        param_int_computational = (set(self._param_int) - set(self._param_int_non_computational))
        logger.debug(f'Computational parameters: {param_int_computational}')

        # create empty lists for non_computational params
        # for item in self._param_int_non_computational:
        #     self.__dict__[item] = list()

        for item in param_int_computational:
            logger.debug(f'param_int_computational: {item}, ')
            if subs_param_value is False:
                param_array = self._make_n_symbols(var_name=item, n=self.n)
            else:
                if hasattr(self._param_data[item], 'tolist'):
                    param_array = Array(self._param_data[item].tolist())
                else:
                    param_array = Array(self._param_data[item])
            self.__dict__[item] = param_array
            logger.debug(f'{self.__dict__[item]}')

        # create placeholders for computed internal parameters
        for item in self._param_int_computed.keys():
            self.__dict__[item] = self._make_n_symbols(var_name=item, n=self.n)
            logger.debug(f'param_int_computed placeholders: {item}, {self.__dict__[item]}')

        # internal variabled computed
        for item in self._var_int_computed:
            self.__dict__[item] = self._make_n_symbols(var_name=item, n=self.n)
            logger.debug(f'var_int_computed placeholders: {item}, {self.__dict__[item]}')

        # create placeholder in `self.__dict__` for custom computed parameters
        for item in self._param_int_custom:
            self.__dict__[item] = self._make_n_symbols(var_name=item, n=self.n)

        # make symbols for variables with a dae address
        for item in self.int_dae_var:
            logger.debug(f'Creating variable symbols for {item}')
            self.__dict__[item] = self._make_n_symbols(var_name=item, n=self.n)

        # TODO: consider moving outside this function
        # create empty numpy arrays for `self._var_data`
        for item in (self._state_int + self._algeb_int):
            logger.debug(f'Creating numpy storage for variable {item}')
            self._var_data[item] = np.zeros((self.n, ))

    def init_equation(self):
        """
        Create storage arrays for equations. The equation name starts with an underscore `_` followed by the
        variable name.

        Included equations are defined in `self._algeb_int`, `self._algeb_intf`, and `self._state_int`.

        Returns
        -------
        None
        """
        # NOTE: this function is not being used.

        algeb_state_list = self._algeb_int + self._algeb_intf + self._state_int
        if len(algeb_state_list) == 0:
            return
        logger.debug(f'\n--> {self.__class__.__name__}: Entering _init_equation()')

        for item in (self._algeb_int + self._algeb_intf + self._state_int):
            eq_name = f'_{item}'  # equation names starts with "_" and follows with the corresponding var name
            self.__dict__[eq_name] = MutableDenseNDimArray([0] * self.n)
            logger.debug(self.__dict__[eq_name])

    def create_param_symbol_value_pair(self):
        """
        Create (element parameter symbol, value) pair for each parameter

        Returns
        -------
        None
        """
        param_names = list(set(self._param_int) - set(self._param_int_non_computational))
        param_names += self._param_ext_computed
        param_names += self._param_ext
        param_names += self._param_ext_computed
        param_names += self._param_int_custom

        for p in param_names:
            if p not in self.__dict__:
                logger.debug(f'Field {p} not exist in {self.__class__.__name__}, check param consistency.')
                continue
            if p not in self._param_data:
                logger.debug(f'Param data for <{p}> does not exist in <{self.__class__.__name__}>.')
                continue
            self._param_sym_val_pair[p] = (self.__dict__[p], self._param_data[p])

    def add_element(self, **kwargs):
        """
        Add one element to this device

        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        # process `idx`
        idx = kwargs.pop('idx', None)
        if idx is None:
            idx = self.n
        self._int.update({idx: self.n})
        self.idx.append(idx)

        # grab default values and update with `kwargs`
        param_vals = OrderedDict(self._param_int_default)
        param_vals.update(kwargs)

        for man in self._param_int_mandatory:
            if man not in param_vals.keys():
                logger.error(f'{self.classname}: mandatory param <{man}> missing.')

        for key, val in param_vals.items():
            if key not in self._param_data:  # TODO: check if `key` is a valid parameter
                self._param_data[key] = []  # TODO: consider numpy array instead
            self._param_data[key].append(val)

    def make_gcall_ext_symbolic(self):
        """
        Generate symbolic expressions for algebraic equations, based on `self._gcall_ext`, linked to external
        algebraic variables

        Returns
        -------
        None
        """

        if len(self._gcall_ext) == 0:
            return
        logger.debug(f'\n--> {self.classname} Entering make_gcall_ext_symbolic')
        for var, eq in self._gcall_ext.items():
            equation_singleton = sympify(eq, locals=self._symbol_singleton)
            self._gcall_ext_symbolic_singleton[var] = equation_singleton
            logger.debug(f'Equation: <{eq}>, symbolic: <{equation_singleton}>')

    def make_gcall_int_symbolic(self):
        """
        Generate symbolic expressions for algebraic equations, based on `self._gcall_ext`, linked to internal
        variables

        Returns
        -------
        None
        """

        if len(self._gcall_int) == 0:
            return
        logger.debug(f'\n--> {self.classname} Entering make_gcall_int_symbolic')
        for var, eq in self._gcall_int.items():
            # convert to equation singleton
            equation_singleton = sympify(eq, locals=self._symbol_singleton)
            self._gcall_int_symbolic_singleton[var] = equation_singleton
            logger.debug(f'Equation: <{eq}>, symbolic: <{equation_singleton}>')

    def delayed_symbol_sub_all(self, subs_param_value=False):
        """
        Delayed substitution for symbols. May need to call `self._subs_all_vectorized` and
        `self._subs_all_singleton` respectively for each devices

        Returns
        -------
        None

        """
        self.delayed_symbol_sub(in_dict_name='_gcall_ext_symbolic_singleton', out_dict_name='_gcall_ext_symbolic',
                                subs_type='vectorized', output_type=Array, subs_param_value=subs_param_value)
        self.delayed_symbol_sub(in_dict_name='_gcall_int_symbolic_singleton', out_dict_name='_gcall_int_symbolic',
                                subs_type='vectorized', output_type=Array, subs_param_value=subs_param_value)

    def delayed_symbol_sub(self, in_dict_name: str, out_dict_name: str, subs_type='vectorized', output_type=None,
                           update=False, subs_param_value=False):
        """
        Execute symbolic substitution for a dictionary whose values are symbolic equation singletons

        Parameters
        ----------
        in_dict_name : str
            The name of the dictionary which is a member of this instance with the keys as the equation names
            and values as the symbolic equation singletons

        out_dict_name : str
            The name of a dictionary to which the equations with substituted symbols will be stored

        subs_type : str
            The type of the substitution in `('vectorized', 'singleton')`

        output_type : Type
            The type of the returned vectorized substitution for each equation. Can be returned as a list or
            a sympy.Arrray

        update : bool
            Update the value if the key already exists in the output dictionary

        Returns
        -------
        None
        """
        assert subs_type in ('vectorized', 'singleton')

        singleton_dict = self.__dict__[in_dict_name]
        for var, eq in singleton_dict.items():
            if not update and var in self.__dict__[out_dict_name]:
                continue

            if subs_type == 'vectorized':
                self.__dict__[out_dict_name][var] = \
                    self._subs_all_vectorized(eq, subs_param_value=subs_param_value, return_as=output_type)
            elif subs_type == 'singleton':
                self.__dict__[out_dict_name][var] = \
                    self._subs_all_singleton(eq, subs_param_value=subs_param_value, return_as=output_type)

    def _subs_all_vectorized(self, equation_singleton, subs_param_value=False, return_as=list):
        """Substitute symbol singletons with element-wise variable names for the provided expression"""

        logger.debug(f'{self.classname}: Equation <{equation_singleton}> vectorized substitution:')

        free_syms = equation_singleton.free_symbols

        # skip substitution if the `equation_singleton` contains no `free_symbols`. This happens if equation
        # singleton is a pure numerical value

        if len(free_syms) == 0:
            ret = [equation_singleton] * self.n
        else:
            n_element = min([len(self.__dict__[str(x)]) for x in free_syms])

            ret = [0] * n_element
            for i in range(n_element):

                sym_list = []
                for symbol in free_syms:
                    sym = str(symbol)

                    value_exist = True
                    substitute = None
                    if subs_param_value is True:
                        # param value does not exist. Fall back to symbols
                        if (sym not in self._param_data) or len(self._param_data[sym]) == 0:
                            logger.debug(f'{self.__class__.__name__}: Param data <{sym}> not exist. '
                                         f'Using symbols.')
                            value_exist = False
                        else:
                            substitute = self._param_data[sym][i]

                    if (subs_param_value is False) or (value_exist is False):
                        if len(self.__dict__[sym]) == 0:
                            logger.debug(f'{self.__class__.__name__}: symbol <{sym}> not properly initialized.')
                            raise ValueError
                        else:
                            substitute = self.__dict__[sym][i]

                    sym_list.append((symbol, substitute))

                # TODO:
                #  Issue with Sympy: the `subs` below will convert the new substitute to the type of the old one
                #  E.g., if we are substuting Bus_v_0 (symbol) for v (MatrixSymbol), then Bus_v_0 will be converted
                #  to a MatrixSymbol, which cannot be added to the DAE
                ret[i] = equation_singleton.subs(sym_list)

        # process return type
        if return_as is None:
            pass
        elif return_as is list:
            pass
        else:
            ret = return_as(ret)

        logger.debug(pprint.pformat(ret))
        return ret

    def _subs_all_singleton(self, equation_singleton, subs_param_value=False, return_as=None):
        """Substitute symbol singletons with symbols expression"""

        free_syms = equation_singleton.free_symbols

        sym_list = []
        for symbol in free_syms:
            sym = str(symbol)
            if subs_param_value is False:
                sym_list.append((symbol, self.__dict__[sym]))
            else:
                sym_list.append((symbol, self._param_data[sym]))  # TODO: substituting with a numpy array may
                # cause issue

        # use `simultaneous` subs for matrix substitution
        ret = equation_singleton.subs(sym_list, simultaneous=True)

        # process return type
        if return_as is None:
            pass
        else:
            ret = return_as(ret)
        return ret

    def _make_n_symbols(self, var_name, n, commutative=True, return_as=Array):
        """
        Make an array of n consecutive symbols for the given variable name. The return symbols has the format
        `classname_varname_idx`

        Parameters
        ----------
        var_name : str
            Name of the variable
        n : int
            The number of symbols
        commutative : bool
            If the variables are commutative or not
        return_as : Type
            The return type of the created symbols

        Returns
        -------
        A array of symbols
        """
        symbol_range_str = f'{self.classname}_{var_name}_0:{n}'
        return return_as(symbols(symbol_range_str, commutative=commutative))

    @property
    def int_dae_var(self):
        """
        Return the name list of internal variables which have a dae address, including `_algeb_int`, `_state_int`

        Returns
        -------
        list : a list of the variable names that are registered in the dae
        """
        return self._algeb_int + self._state_int

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

    @property
    def classname(self):
        return self.__class__.__name__

    def get_algeb_ext(self):
        """
        Based on the definition of algebraic variables (defined in `self._algeb_ext` and the associated device,
        retrieve the
        - variable symbol singleton (goes to self._symbol_singleton[dest])
        - the variable list for the respective external elements (goes to `self.{dest}` as a sympy.Array)
        - the variable address in the dae (goes to `self._dae_address[f'{dest'}]`)

        Returns
        -------
        None
        """
        if len(self._algeb_ext) == 0:
            return
        logger.debug(f'\n--> {self.__class__.__name__}: Entering get_algeb_ext()')

        for dest, (fkey, var_name) in self._algeb_ext.items():

            if fkey in self._param_int:  # if fkey is a valid parameter input
                dev = self._foreign_keys[fkey]
                int_keys = self._get_int_of_element(dev, fkey)
            else:  # fkey is a device name instead
                dev = fkey
                fkey_values = self.system.__dict__[fkey.lower()].idx
                int_keys = self.system.__dict__[dev.lower()].idx2int(fkey_values)

            # store dae address
            dev_ref = self.system.__dict__[dev.lower()]
            self._dae_address[f'{dest}'] = dev_ref._dae_address[f'{var_name}'][int_keys]

            # get external algebraic variable symbol array by accessing
            algeb_symbol_list = self.get_list_of_symbols_from_ext(dev, var_name, int_keys)
            self.__dict__[dest] = Array(algeb_symbol_list)

            # store the singleton
            # TODO: should be retrieved. but the retrieved MatrixSymbol may have a
            #  different size
            # self._symbol_singleton[dest] = symbols(var_name)
            # self._symbol_singleton[dest] = dev_ref._symbol_singleton[var_name]
            logger.debug(self.__dict__[dest])

    def _get_int_of_element(self, dev, fkey):
        """
        For device `dev`, get the internal indicex (int) of the elements having `fkey` matching their `idx`

        Parameters
        ----------
        dev : str
            Name of the device
        fkey : np.array
            A list or numpy array as foreign keys indexing into `dev.idx`

        Returns
        -------

        """
        assert dev in self._foreign_keys.values(), f"{self.classname} does not have {fkey} as foreign key"

        fkey_values = self._param_data[fkey]
        # the values of `fkey` is stored in `self._param_data` instead of self.__dict__

        return self.system.__dict__[dev.lower()].idx2int(fkey_values)

    def get_list_of_symbols_from_ext(self, dev, var_name, int_idx):
        """
        Get a list of symbols from external devices based on the fkey linked to the idx of external devices

        Parameters
        ----------
        dev : str
            Name of the device

        var_name : str
            Name of the variable of the device to access

        int_idx
            A list or numpy array of the internal indices of the elements to access

        Returns
        -------

        """
        dev = dev.lower()
        if isinstance(int_idx, np.ndarray):
            int_idx = int_idx.tolist()  # sympy is not aware of numpy.int64; convert to a list of floats
        return [self.system.__dict__[dev].__dict__[var_name][i] for i in int_idx]

    def idx2int(self, idx):
        """
        Convert external indices `idx` to internal indices as stored in `self.int`

        Returns
        -------
        np.ndarray : an array of internal indices
        """
        return np.array([self._int[i] for i in idx])

    def add_element_with_defaults(self, n: int):
        """
        Create `n` elements with the default N-to-N mapping between int and idx. The `idx` and `int` are both
        in range(n).

        Parameters
        ----------
        n : int
            The number of elements to add
        Returns
        -------
        None
        """

        assert n >= 0
        self.idx = list(range(n))
        self._int = {i: i for i in self.idx}

        for p in self._param_int:
            if p in self._param_int_mandatory:
                continue
            self._param_data[p] = [self._param_int_default[p]] * n

    def metadata_check(self):
        """
        Check the metadata and find inconsistency. Contains of subroutines for consistency check.

        Returns
        -------
        None
        """
        self._check_number_of_algeb_equations()

    def _check_number_of_algeb_equations(self):
        """
        Consistency check subroutine: check if the number of equations equal the number of variables.

        Returns
        -------
        None
        """
        if self._special_flags['no_algeb_ext_check'] is False:
            assert len(self._algeb_ext) == len(self._gcall_ext), "{} Number of _algeb_ext does not equal " \
                                                                 "_gcall_ext".format(self.__class__.__name__)
        assert len(self._algeb_int) - len(self._algeb_intf) <= \
            len(self._gcall_int), "{} Too few gcall_int equations".format(self.__class__.__name__)

    def compute_param_int(self, subs_param_value=False):
        """
        Compute internal parameters based on `self._param_int_computed`.

        Returns
        -------
        None
        """
        # process internally computed parameters

        if len(self._param_int_computed) == 0:
            return
        logger.debug(f'\n--> {self.__class__.__name__}: Entering compute_param_int():')
        for var, eq in self._param_int_computed.items():
            equation_singleton = sympify(eq)
            self.__dict__[var] = self._subs_all_vectorized(equation_singleton, subs_param_value=subs_param_value)
            logger.debug(f'variable <{var}>, equation <{eq}>: \n {self.__dict__[var]}')

    def compute_variable(self):
        """
        Compute internal variable symbols as defined in `self._var_int_computed`. Supports a list of
         - [equation]
         - [equation, compute_type]
         - [equation, compute_type, return_type]

        Returns
        -------
        None

        """
        if len(self._var_int_computed) == 0:
            return

        logger.debug(f'\n--> {self.__class__.__name__}: Entering _compute_variable(): ')
        for var, eq in self._var_int_computed.items():
            compute_type = 'vectorized'
            return_type = None
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
                self.__dict__[var] = self._subs_all_vectorized(equation_singleton, return_as=Array)
            elif compute_type == 'singleton':
                self.__dict__[var] = self._subs_all_singleton(equation_singleton)
            else:
                raise NotImplementedError

            if return_type is not None:
                self.__dict__[var] = return_type(self.__dict__[var])

    def compute_variable_custom(self):
        """
        Hook functions to compute custom variables. To be overloaded by devices.

        Returns
        -------
        None
        """
        pass

    def compute_param_custom(self):
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

    def get_var_address(self):
        """
        Request address for variables in global DAE. Stored in `self._dae_address` with the variable name as
        keys and address array as the values.

        Returns
        -------
        None
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

    def is_state(self, var_name):
        """
        Check if a variable `var_name` is a state variable.

        Parameters
        ----------
        var_name : str
            Name of the variable

        Returns
        -------
        bool : True if is a state variable. False otherwise.
        """
        pass

    def is_algeb(self, var_name):
        """
        Check if a variable `var_name` is an algebraic variable.

        Parameters
        ----------
        var_name : str
            Name of the variable

        Returns
        -------
        bool : True if is an algebraic variable. False otherwise.
        """
        pass

    def subs_variable_values(self):
        """
        Substitute variable symbols for values for evaluation

        Returns
        -------

        """
        pass

    def compute_and_set_initial_values(self, subs_param_value=True):
        """
        Compute initial values for variables. Store to `self._var_value_initial_numeric`.

        Returns
        -------
        None
        """
        for keys, eq in self._var_value_initial.items():
            dev, var_name, fkey, operation = keys
            equation_singleton = sympify(eq)
            equation_vec = self._subs_all_vectorized(equation_singleton, subs_param_value=subs_param_value,
                                                     return_as=list)

            # store numeric values
            self._var_value_initial_numeric[keys] = equation_vec

            if dev == 'self':
                dev = self.classname
            if fkey == 'idx':
                element_int = list(self._int.keys())
            else:
                element_int = self._get_int_of_element(dev=dev, fkey=fkey)

            dev_ref = self.system.__dict__[dev.lower()]
            if operation == 'set':
                dev_ref._var_data[var_name][element_int] = equation_vec
                logger.debug(f'Set initial value for {dev}.{var_name}{element_int} = {equation_vec}')
            elif operation == 'add':
                dev_ref._var_data[var_name][element_int] = dev_ref._var_data[var_name][element_int] + equation_vec
                logger.debug(f'Added initial value for {dev}.{var_name}{element_int} += {equation_vec}')


class DeviceData(object):
    """Class for storing device data"""
    def __init__(self, device: str, param: list, n_element=0):
        self.device = device  # name of the device to which the data belongs
        for item in param:
            self.__dict__[item] = np.ndarray((n_element, ))

    def load_param_by_row(self, **kwargs):
        """
        Load parameters of a single element (row) from parameter values
        Returns
        -------

        """
        # for key, val in kwargs.items():
        #     if key not in
        pass

    def load_param_from_dataframe(self):
        """
        load parameters of multiple elements from a pandas.DataFrame

        Returns
        -------
        None

        """

        pass
