import unittest

from reader import *
from kd_tree import *

class CowTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "data/cow.off"
        self.reader = openOff(self.model_filename)
        self.vertices = self.reader.get_vertices()
        self.tree = KdTree(self.vertices)

    def test_vertex_count(self):
        self.failUnless(self.tree.nodecount == len(self.vertices))

    def test_vertex_iterator(self):
        iter_vertices = list(self.tree.iter_vertices())
        self.failUnlessEqual(len(iter_vertices), len(self.vertices))
