#!/usr/bin/python
import unittest

names = [
    "tests.test_kd_tree.CowTestCase",
    ]

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromNames(names)
    unittest.TextTestRunner(verbosity=2).run(suite)

