import unittest
import logging


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class TestPJM5Bus(unittest.TestCase):
    def test_simple3bus(self):
        exec(open("simple3bus.py").read())
