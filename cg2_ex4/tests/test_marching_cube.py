import unittest

from numpy import array
from surface import ImplicitSurface
from marching_cube import MarchingCubeNode

class CatTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)

    def test_cube_creation(self):
        for subdivisions in [0, 1, 10]:
            cube_node = self.surface.get_implicit_surface(subdivisions, 1)

