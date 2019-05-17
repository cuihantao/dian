from collections import OrderedDict  # NOQA
import sympy as smp  # NOQA
import numpy as np  # NOQA

from .devicebase import DeviceBase


class Bus(DeviceBase):
    """AC bus topology device

    Defines two interface equations and variables for voltage magnitude and voltage phase
    """
    def __init__(self, system):
        super(Bus, self).__init__(system)
        self._param_int.extend(['Vn', 'voltage', 'angle', 'region', 'area', 'zone', 'intercon', 'owner',
                                'vmax', 'vmin', 'xcoord', 'ycoord'])

        self._param_int_non_computational.extend(['xcoord', 'ycoord', 'area', 'zone', 'intercon', 'owner',
                                                  'region'])

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

        self._foreign_keys.update({'Area': 'area',
                                   'Zone': 'zone',
                                   'Region': 'region',
                                   'Interconn': 'interconn'}
                                  )

        self._algeb_int.extend(['a', 'v'])
        self._algeb_intf.extend(['a', 'v'])

        self._var_value_initial.update({('self', 'v', 'idx', 'set'): '1'})

        self._special_flags.update({'algeb_group_by_element': False})

        # TODO: check the number of equations equal the number of n_algeb - n_algeb_intf

        """
        How to define the hierarchy of devices
        """
