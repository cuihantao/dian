import unittest
import logging

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class TestPJM5Bus(unittest.TestCase):
    def test_pjm5bus(self):
        exec(open("pjm5bus.py").read())
