import unittest

from numpy import array
from min_squares import *
from surface import *

class CatTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)
        self.square_solver = self.surface.square_solver
        self.faildifference_value = 0.05
        self.faildifference_normal = 0.05

    def test_kdtree(self):
        point1 = self.square_solver.pointlist[0]
        point2 = self.square_solver.pointlist[365]
        self.failUnless(self.square_solver.selectPoints(point1, 1) == (0.0, 0))
        self.failUnless(self.square_solver.selectPoints(point2, 1) == (0.0, 365))
        
    def test_solver_degree_1(self):
        point1 = array([0, 0, 0])
        normal1 = array([-0.112399, 0.0705785, 0.991153])
        point2 = array([-10, 19, -900])
        normal2 = array([-0.281896, 0.862049, 0.421197])
        point3 = array([248, -502, -964])
        normal3 = array([0.86795, -0.398594, -0.296286])
        z1,n1 = self.square_solver.solveEquations(point1, 1)
        z2,n2 = self.square_solver.solveEquations(point2, 1)
        z3,n3 = self.square_solver.solveEquations(point3, 1)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(abs(normal1 - n1)[0] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[1] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[2] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[0] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[1] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[2] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[0] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[1] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[2] < self.faildifference_normal)
    
    def test_solver_degree_2(self):
        point1 = array([0, 0, 0])
        normal1 = array([-0.112399, 0.0705785, 0.991153])
        point2 = array([-10, 19, -900])
        normal2 = array([-0.281896, 0.862049, 0.421197])
        point3 = array([248, -502, -964])
        normal3 = array([0.86795, -0.398594, -0.296286])
        z1,n1 = self.square_solver.solveEquations(point1, 2)
        z2,n2 = self.square_solver.solveEquations(point2, 2)
        z3,n3 = self.square_solver.solveEquations(point3, 2)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(abs(normal1 - n1)[0] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[1] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[2] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[0] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[1] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[2] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[0] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[1] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[2] < self.faildifference_normal)
        
    def test_solver_degree_3(self):
        point1 = array([0, 0, 0])
        normal1 = array([-0.112399, 0.0705785, 0.991153])
        point2 = array([-10, 19, -900])
        normal2 = array([-0.281896, 0.862049, 0.421197])
        point3 = array([248, -502, -964])
        normal3 = array([0.86795, -0.398594, -0.296286])
        z1,n1 = self.square_solver.solveEquations(point1, 3)
        z2,n2 = self.square_solver.solveEquations(point2, 3)
        z3,n3 = self.square_solver.solveEquations(point3, 3)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(abs(normal1 - n1)[0] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[1] < self.faildifference_normal)
        self.failUnless(abs(normal1 - n1)[2] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[0] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[1] < self.faildifference_normal)
        self.failUnless(abs(normal2 - n2)[2] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[0] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[1] < self.faildifference_normal)
        self.failUnless(abs(normal3 - n3)[2] < self.faildifference_normal)
    
    
        
        
