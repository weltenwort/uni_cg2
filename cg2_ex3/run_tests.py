#!/usr/bin/python
import unittest

names = [
    "tests.test_reader.ReaderTestCase",
    "tests.test_implicit_surface.PointCloudTestCase",
    "tests.test_implicit_surface.ColoredGridTestCase",
    "tests.test_min_squares.CatTestCase",
    "tests.test_marching_cube.CatTestCase",
    ]

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    suite = unittest.TestLoader().loadTestsFromNames(names)
    unittest.TextTestRunner(verbosity=2).run(suite)

