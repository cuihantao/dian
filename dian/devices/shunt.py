from .devicebase import DeviceBase


class Shunt(DeviceBase):
    """Class for static shunt
    """

    def __init__(self, system):
        super(Shunt, self).__init__(system)
        self._param_int.extend(['bus', 'Sn', 'Vn', 'g', 'b'])
        self._param_int_non_computational.extend(['bus'])
        self._param_int_mandatory.extend(['bus'])
        self._param_int_default.update({'Sn': 100,
                                        'Vn': 110,
                                        'g': 0,
                                        'b': 0
                                        })

        self._foreign_keys.update({'bus': 'Bus'})

        self._algeb_ext.update({'a': ['bus', 'a'], 'v': ['bus', 'v']})

        self._gcall_ext.update({'a': 'pd',
                                'v': 'qd'})

        self._var_int_computed.update({'pd': ['u * g * v**2 ', 'vectorized'],
                                       'qd': ['- u * b * v**2', 'vectorized']}
                                      )
