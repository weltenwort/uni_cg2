#!/usr/bin/python
import unittest

names = [
    "tests.test_reader.Franke4TestCase",
    "tests.test_min_squares.Franke4TestCase",
    "tests.test_parameter_plane.Franke4TestCase",
    "tests.test_point_cloud.Franke4TestCase",
    "tests.test_mls_surface.Franke4TestCase",
    "tests.test_bezier_surface.Franke4TestCase",
    "tests.test_casteljau.GivenMatrixTestCase",
    ]

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromNames(names)
    unittest.TextTestRunner(verbosity=2).run(suite)

