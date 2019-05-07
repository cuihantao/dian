import unittest
from dian.devices.bus import Bus


class TestInitData(unittest.TestCase):

    def setUp(self) -> None:
        self.bus = Bus()
        self.bus.n = 10

    def test_init_data(self):
        self.bus._init_data()
