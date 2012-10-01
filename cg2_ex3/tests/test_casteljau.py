import unittest

from numpy import ones, array
from surface import *
from casteljau import *

class GivenMatrixTestCase(unittest.TestCase):
    def setUp(self):
        row1 = [1,2,3,4]
        row2 = [2,3,4,5]
        row3 = [3,4,5,6]
        row4 = [4,5,6,7]
        self.matrix = array([row1, row2, row3, row4])
        self.casteljau = Casteljau(self.matrix)
        
    def test_point_evaluation(self):
        point = array([0.5, 0.5])
        value = 4
        vector = [-4, -4, 1]
        result, normal = self.casteljau.evaluate_point(point)
        self.failUnless(result == value)
        self.failUnless(normal[0] == vector[0] and normal[1] == vector[1] and normal[2] == vector[2])
        
        
        
