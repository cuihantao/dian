import unittest
import numpy as np

from dian.system import System

import logging


class TestInitData(unittest.TestCase):

    def setUp(self) -> None:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        self.system = System()
        self.system.bus.add_element_with_defaults(10)

        self.system.pq.add_element_with_defaults(5)
        self.system.pq.bus = np.array([0, 2, 4, 6, 8])

    def test_init_data(self):
        self.system.bus._init_data()
        self.system.bus._init_equation()
        self.system.bus.get_var_address()
        self.system.pq.get_algeb_ext()
