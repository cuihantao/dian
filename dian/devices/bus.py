from collections import OrderedDict
import sympy as smp
import numpy as np


class DeviceBase(object):
    """
    Base class for devices with universal properties and functions

    """
    def __init__(self):

        self.n = 0
        self.idx = []

        # default set of parameters
        self._param_int = ['name', 'u']
        self._param_int_default = {'name': '', 'u': 1}
        self._param_int_non_computational = ['name']

        # computed internal parameters in a list of (parameter, equation)
        self._param_int_compute = []

        # external parameters before any computation in tuples (device, original_name, new_name)
        self._param_ext = []  # TODO: method to update external parameters

        # external parameters that are computed by the external device in tuples (device, original name, new_name)
        self._param_ext_computed = [] # TODO: method to update computed external parameters

        # store the idx to internal index mapping
        self._int = OrderedDict()

        # define the parameters of the current model that are referencing the idx of other devices in tuples of
        # (device, parameter)
        self._foreign_keys = []

        # define the internal algebraic variables of the current model
        self._algeb_int = []

        # define the internal algebraic variables that are also interface variables
        self._algeb_intf = []

        # define the external algebraic variables that are interface variables of other devices in tuples
        # (model, algeb_name)
        self._algebs_ext = []

        # define the internal state variables of the current model
        self._state_int = []

        # define the internal state variables that are also interface variables (UNCOMMON)
        self._state_intf = []

        # define the external state variables that are interface variables of other devices in tuples
        # (model, algeb_name) (UNCOMMON)
        self._state_ext = []

    # @property
    # def n(self):
    #     """
    #     The count of elements obtained from len(self._idx)
    #
    #     Returns
    #     -------
    #     int
    #         The count of elements
    #     """
    #     return len(self._int)


class DeviceData(object):
    """Class for storing device data"""
    def __init__(self, device : str, param : list, n_element=0):
        self.device = device  # name of the device to which the data belongs
        for item in param:
            self.__dict__[item] = np.ndarray((n_element, ))


class Bus(DeviceBase):
    """AC bus topology device

    Defines two interface equations and variables for voltage magnitude and voltage phase
    """
    def __init__(self):
        super(Bus, self).__init__()
        self._param_int.extend(['Vn', 'voltage', 'angle', 'region', 'area', 'zone', 'intercon', 'owner',
                                'vmax', 'vmin', 'xcoord', 'ycoord'])

        self._param_int_non_computational.extend(['xcoord', 'ycoord' 'area', 'zone', 'intercon', 'owner'])

        self._param_int_default.update({'Vn': 110,
                                        'voltage': 1.0,
                                        'angle': 0.0,
                                        'region': 0,
                                        'area': 0,
                                        'zone': 0,
                                        'intercon': 0,
                                        'owner': 0,
                                        'vmax': 1.1,
                                        'vmin': 0.9,
                                        'xcoord': 0,
                                        'ycoord': 0,
                                        })

        self._foreign_keys.extend([('area', 'Area'),
                                   ('zone', 'Zone'),
                                   ('region', 'Region'),
                                   ('interconn', 'Interconn')]
                                  )

        self._algeb_int.extend(['theta', 'v'])
        self._algeb_intf.extend(['theta', 'v'])

        # TODO: check the number of equations equal the number of n_algeb - n_algeb_intf

    def load_param_from_dataframe(self):
        """
        load parameters of multiple elements from a pandas dataframe

        Returns
        -------
        None

        """
        pass

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

        for item in (set(self._param_int) - set(self._param_int_non_computational)):
            self.__dict__[item] = smp.Array(smp.symbols(self.__class__.__name__ + f'_{item}_0:{self.n}'))
            print(self.__dict__[item])
        for item in self._algeb_int:
            self.__dict__[item] = smp.Array(smp.symbols(self.__class__.__name__ + f'_{item}_0:{self.n}'))
            print(self.__dict__[item])


"""
How to define the hierarchy of devices
"""