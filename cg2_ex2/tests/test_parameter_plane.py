import unittest

from surface import Surface

class Franke4TestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/franke4.off"
        self.surface = Surface.from_file(self.model_filename)

    def test_parameter_plane(self):
        self.surface.get_parameter_plane(0)
        self.surface.get_parameter_plane(10)
        self.surface.get_parameter_plane(100)
