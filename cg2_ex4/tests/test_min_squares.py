import unittest

from numpy import array
from numpy.linalg import norm
from min_squares import *
from surface import *

class CatTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)
        self.square_solver = MinSquares(self.surface)
        self.square_solver.radius = 0.05
        self.faildifference_value = 0.005
        self.faildifference_normal = 0.3

    def test_solver_degree_1(self):
        point1 = self.square_solver.pointlist[0]
        normal1 = self.square_solver.normallist[0]
        point2 = self.square_solver.pointlist[183]
        normal2 = self.square_solver.normallist[183]
        point3 = self.square_solver.pointlist[-1]
        normal3 = self.square_solver.normallist[-1]
        z1 = self.square_solver.get_point(point1, 1)
        n1 = self.square_solver.get_normal(point1, 1)
        z2 = self.square_solver.get_point(point2, 1)
        n2 = self.square_solver.get_normal(point2, 1)
        z3 = self.square_solver.get_point(point3, 1)
        n3 = self.square_solver.get_normal(point3, 1)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(norm(normal1 - n1, 2) < self.faildifference_normal)
        self.failUnless(norm(normal2 - n2, 2) < self.faildifference_normal)
        self.failUnless(norm(normal3 - n3, 2) < self.faildifference_normal)
    
    def test_solver_degree_2(self):
        point1 = self.square_solver.pointlist[0]
        normal1 = self.square_solver.normallist[0]
        point2 = self.square_solver.pointlist[183]
        normal2 = self.square_solver.normallist[183]
        point3 = self.square_solver.pointlist[-1]
        normal3 = self.square_solver.normallist[-1]
        z1 = self.square_solver.get_point(point1, 1)
        n1 = self.square_solver.get_normal(point1, 1)
        z2 = self.square_solver.get_point(point2, 1)
        n2 = self.square_solver.get_normal(point2, 1)
        z3 = self.square_solver.get_point(point3, 1)
        n3 = self.square_solver.get_normal(point3, 1)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(norm(normal1 - n1, 2) < self.faildifference_normal)
        self.failUnless(norm(normal2 - n2, 2) < self.faildifference_normal)
        self.failUnless(norm(normal3 - n3, 2) < self.faildifference_normal)
        
    def test_solver_degree_3(self):
        point1 = self.square_solver.pointlist[0]
        normal1 = self.square_solver.normallist[0]
        point2 = self.square_solver.pointlist[183]
        normal2 = self.square_solver.normallist[183]
        point3 = self.square_solver.pointlist[-1]
        normal3 = self.square_solver.normallist[-1]
        z1 = self.square_solver.get_point(point1, 1)
        n1 = self.square_solver.get_normal(point1, 1)
        z2 = self.square_solver.get_point(point2, 1)
        n2 = self.square_solver.get_normal(point2, 1)
        z3 = self.square_solver.get_point(point3, 1)
        n3 = self.square_solver.get_normal(point3, 1)
        
        self.failUnless(z1 < self.faildifference_value)
        self.failUnless(z2 < self.faildifference_value)
        self.failUnless(z3 < self.faildifference_value)
        self.failUnless(norm(normal1 - n1, 2) < self.faildifference_normal)
        self.failUnless(norm(normal2 - n2, 2) < self.faildifference_normal)
        self.failUnless(norm(normal3 - n3, 2) < self.faildifference_normal)
    
    
        
        
