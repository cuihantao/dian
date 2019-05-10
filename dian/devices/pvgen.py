from .devicebase import DeviceBase


class PV(DeviceBase):
    """Class for static PV gen
    """

    def __init__(self, system):
        super(PV, self).__init__(system)
        self._param_int.extend(['bus', 'p', 'v0', 'Sn', 'Vn', 'vmax', 'vmin', 'qmax', 'qmin'])
        self._param_int_non_computational = ['bus']

        self._foreign_keys.update({'bus': 'Bus'})

        self._algeb_ext.update({'a': ['bus', 'a'], 'v': ['bus', 'v']})

        self._algeb_int.extend(['q'])

        self._gcall_int.update({'q': 'v - v0',
                                })
        self._gcall_ext.update({'a': '-p',
                                'v': '-q'})
