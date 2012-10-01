import unittest

from surface import Surface

class Franke4TestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/franke4.off"
        self.surface = Surface.from_file(self.model_filename)

    def test_bezier_plane(self):
        self.surface.get_bezier_interpolated_surface(2,2)
        #self.surface.get_bezier_interpolated_surface(10,2)
        #self.surface.get_mls_interpolated_surface(100)
