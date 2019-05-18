import unittest
import numpy as np
from dian.system import System
from dian.devices.devicebase import DeviceBase


class TestDevice(DeviceBase):
    """Test class for DeviceBase"""
    def __init__(self, system):
        super(TestDevice, self).__init__(system=system)


class TestDeviceBase(unittest.TestCase):
    def setUp(self) -> None:
        self.system = System()

        # instantiate TestDevice
        self.system.testdevice = TestDevice(self.system)
        self.test_device = self.system.testdevice

        # create buses
        self.system.bus.add_element_with_defaults(10)
        self.test_device.add_element_with_defaults(5)

        # link TestDevice to buses
        self.test_device.bus = np.array([0, 2, 4])

    def test_metadata_check(self):
        # check metadata
        self.system.bus.metadata_check()
        self.test_device.metadata_check()

    def test_init_data(self):
        # _init_data for bus and TestDevice
        self.system.bus.init_data()
        self.test_device.init_data()

        self.assertEqual(self.system.bus.n, 10)
