from .devicebase import DeviceBase
import sympy as smp
import logging

logger = logging.getLogger(__name__)


class Line(DeviceBase):
    """Class for ac transmission lines
    """

    def __init__(self, system):
        super(Line, self).__init__(system)
        self._param_int.extend(['bus1', 'bus2', 'r', 'x', 'g', 'b', 'g1', 'g2', 'b1', 'b2',
                                'Sn', 'Vn1', 'Vn2', 'fn', 'owner', 'tap', 'phi', 'istf', 'xcoord', 'ycoord'
                                ])
        self._param_int_non_computational.extend(['bus1', 'bus2', 'owner', 'xcoord', 'ycoord'])
        self._param_int_mandatory.extend(['bus1', 'bus2'])

        self._param_int_default.update({'owner': 0,
                                        'r': 1e-4,
                                        'x': 1e-2,
                                        'g': 0,
                                        'b': 0,
                                        'g1': 0,
                                        'g2': 0,
                                        'b1': 0,
                                        'b2': 0,
                                        'Sn': 100,
                                        'Vn1': 110,
                                        'Vn2': 110,
                                        'fn': 60,
                                        'tap': 1,
                                        'phi': 0,
                                        'istf': 0,
                                        'xcoord': 0,
                                        'ycoord': 0,
                                        })

        self._foreign_keys.update({'bus1': 'Bus', 'bus2': 'Bus'})

        self._algeb_ext.update({'a1': ['bus1', 'a'], 'v1': ['bus1', 'v'],
                                'a2': ['bus2', 'a'], 'v2': ['bus2', 'v'],
                                'a': ['Bus', 'a'], 'v': ['Bus', 'v']
                                })
        self._var_int_computed.update({'vc': ['v * exp(I * a)', 'vectorized', smp.Matrix],
                                       'Ic': ['Y * vc', 'singleton'],
                                       'Sc': ['vc * conjugate(Ic)', 'vectorized'],
                                       'Pd': ['re(Sc)'],
                                       'Qd': ['im(Sc)']
                                       }
                                      )

        self._special_flags['no_algeb_ext_check'] = True

        self._param_int_computed.update({'g1sh': 'g1 + 0.5 * g',
                                         'g2sh': 'g2 + 0.5 * g',
                                         'b1sh': 'b1 + 0.5 * b',
                                         'b2sh': 'b2 + 0.5 * b',
                                         'y1': 'u * (g1sh + I*b1sh)',
                                         'y2': 'u * (g2sh + I*b2sh)',
                                         'y12': 'u / (r + I*x)',
                                         'm': 'tap * exp(I*phi)',
                                         'm2': 'tap ** 2',
                                         'mconj': 'conjugate(m)',
                                         })
        self._param_int_custom.extend(['Y'])

        self._gcall_ext.update({'a': 'Pd',
                                'v': 'Qd',
                                })

    def compute_param_custom(self):
        """Compute `self.Y` for lines"""
        # Note: this one assumes `self.a1_int` is the indices of `self.a1` in `bus.a`

        dok_y = dict()
        a1_addr = self._dae_address['a1']
        a2_addr = self._dae_address['a2']

        # pylint: disable=maybe-no-member
        for a1, y1, m2, y12 in zip(a1_addr, self.y1, self.m2, self.y12):
            # Need to check if key exist. Otherwise, same multiple `a1` will overwrite the value
            if (a1, a1) not in dok_y.keys():
                dok_y[(a1, a1)] = (y1 + y12) / m2
            else:
                dok_y[(a1, a1)] = dok_y[(a1, a1)] + ((y1 + y12) / m2)

        for a1, a2, y12, mconj in zip(a1_addr, a2_addr, self.y12, self.mconj):
            if (a1, a2) not in dok_y.keys():
                dok_y[(a1, a2)] = -y12 / mconj
            else:
                dok_y[(a1, a2)] = dok_y[(a1, a2)] - y12 / mconj
        for a1, a2, y12, m in zip(a1_addr, a2_addr, self.y12, self.m):
            if (a2, a1) not in dok_y.keys():
                dok_y[(a2, a1)] = - y12 / m
            else:
                dok_y[(a2, a1)] = dok_y[(a2, a1)] - y12 / m
        for a2, y12, y2 in zip(a2_addr, self.y12, self.y2):
            if (a2, a2) not in dok_y.keys():
                dok_y[(a2, a2)] = y12 + y2
            else:
                dok_y[(a2, a2)] = dok_y[(a2, a2)] + (y12 + y2)

        nbus = self.system.bus.n

        self.Y = smp.SparseMatrix(nbus, nbus, dok_y)
        self.Y = smp.Matrix(self.Y)
