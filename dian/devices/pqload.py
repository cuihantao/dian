from .devicebase import DeviceBase


class PQ(DeviceBase):
    """Class for static PQ load
    """

    def __init__(self, system):
        super(PQ, self).__init__(system)
        self._param_int.extend(['bus', 'p', 'q', 'Sn', 'Vn', 'vmax', 'vmin'])
        self._param_int_non_computational = ['bus']

        self._foreign_keys.update({'bus': 'Bus'})

        self._algeb_ext.update({'a': ['bus', 'a'], 'v': ['bus', 'v']})
        self._gcall_ext.update({'a': 'p',
                                'v': 'q'})
