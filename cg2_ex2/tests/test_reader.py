import unittest

from reader import *

class Franke4TestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/franke4.off"
        self.reader = openOff(self.model_filename)
        self.vertex_dict = {}
        for line in self.reader.iter_vertices():
            self.vertex_dict[tuple(line[0:2])] = line[2]

    def test_reader_dict(self):
        key1 = tuple([float(7.826369e-06), float(1.315378e-01)])
        value1 = float(6.897177e-01)
        key2 = tuple([float(5.261817e-01), float(5.359563e-01)])
        value2 = float(8.803976e-02)
        key3 = tuple([float(2.100336e-01), float(3.497096e-02)])
        value3 = float(8.997839e-01)
        
        self.failUnless(key1 in self.vertex_dict)
        self.failUnless(self.vertex_dict[key1] == value1)
        
        self.failUnless(key2 in self.vertex_dict)
        self.failUnless(self.vertex_dict[key2] == value2)
        
        self.failUnless(key3 in self.vertex_dict)
        self.failUnless(self.vertex_dict[key3] == value3)
