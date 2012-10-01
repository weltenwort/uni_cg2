import unittest

from min_squares import *
from surface import *

class Franke4TestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/franke4.off"
        self.surface = Surface.from_file(self.model_filename)
        self.square_solver = MinSquares(self.surface)
        self.failquotient = 0.01

    def test_kdtree(self):
        point1 = self.square_solver.pointlist[0]
        point2 = self.square_solver.pointlist[999]
        self.failUnless(self.square_solver.selectPoints(point1, 1) == (0.0, 0))
        self.failUnless(self.square_solver.selectPoints(point2, 1) == (0.0, 999))
        
    def test_solver(self):
        point1 = tuple([7.826369e-06, 1.315378e-01])
        value1 = 6.897177e-01
        point2 = tuple([4.160074e-01, 8.363755e-01])
        value2 = -1.411298e-01
        point3 = tuple([2.100336e-01, 3.497096e-02])
        value3 = 8.997839e-01
        z1,n1 = self.square_solver.solveEquations(point1)
        z2,n2 = self.square_solver.solveEquations(point2)
        z3,n3 = self.square_solver.solveEquations(point3)
        
        self.failUnless(abs(1 - (z1 / value1)) < self.failquotient)
        self.failUnless(abs(1 - (z2 / value2)) < self.failquotient)
        self.failUnless(abs(1 - (z3 / value3)) < self.failquotient)
        
