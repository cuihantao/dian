from .devicebase import DeviceBase


class PQ(DeviceBase):
    """Class for static PQ load
    """

    def __init__(self, system):
        super(PQ, self).__init__(system)
        self._param_int.extend(['bus', 'p', 'q', 'Sn', 'Vn', 'vmax', 'vmin'])
        self._param_int_mandatory.extend(['bus'])
        self._param_int_default.update({'p': 0,
                                        'q': 0,
                                        'Sn': 100,
                                        'Vn': 110,
                                        'vmax': 1.1,
                                        'vmin': 0.9
                                        })
        self._param_int_non_computational.extend(['bus'])

        self._foreign_keys.update({'bus': 'Bus'})

        self._algeb_ext.update({'a': ['bus', 'a'], 'v': ['bus', 'v']})
        self._gcall_ext.update({'a': 'p',
                                'v': 'q'})
