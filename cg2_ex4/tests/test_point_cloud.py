import unittest

from surface import Surface

class Franke4TestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/franke4.off"
        self.surface = Surface.from_file(self.model_filename)

    def test_point_cloud(self):
        self.surface.get_original_point_cloud()
