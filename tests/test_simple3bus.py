import unittest
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class TestSimple3Bus(unittest.TestCase):
    def test_simple3bus(self):
        cwd = os.getcwd()
        if 'tests' not in cwd:
            cwd = os.path.join(cwd, 'tests')
        test_case = os.path.join(cwd, "simple3bus.py")
        exec(open(test_case).read())
