import unittest

from reader import *

class ReaderTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/cat.off"
        self.reader = openOff(self.model_filename)

    def test_normal_iterator(self):
        vertices, normals = [], []
        for vertex, normal in self.reader.iter_vertices_and_normals():
            self.failUnless(len(vertex) == 3)
            self.failUnless(len(normal) == 3)
            vertices.append(vertex)
            normals.append(normal)
        
        self.failUnless(vertices[0] == (0.0, 0.0, 0.0))
        self.failUnless(normals[0] == (-0.112399, 0.0705785, 0.991153))

        self.failUnless(vertices[-1] == (248.0, -502.0, -964.0))
        self.failUnless(normals[-1] == (0.86795, -0.398594, -0.296286))
