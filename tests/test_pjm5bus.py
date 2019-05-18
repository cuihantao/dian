import unittest
import logging
import os
logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class TestPJM5Bus(unittest.TestCase):
    def test_pjm5bus(self):
        cwd = os.getcwd()
        if 'tests' not in cwd:
            cwd = os.path.join(cwd, 'tests')
        test_case = os.path.join(cwd, "pjm5bus.py")
        exec(open(test_case).read())
