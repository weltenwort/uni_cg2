#!/usr/bin/python
import unittest
import logging
logging.basicConfig(level=logging.DEBUG)

from run_tests import names

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    suite = unittest.TestLoader().loadTestsFromNames(names)
    suite.debug()
    #unittest.TextTestRunner(verbosity=2).debug(suite)

