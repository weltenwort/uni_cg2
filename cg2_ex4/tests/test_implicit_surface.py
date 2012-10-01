import unittest


class PointCloudTestCase(unittest.TestCase):
    def setUp(self):
        from surface import ImplicitSurface
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)

    def test_parameter_grid(self):
        self.surface.get_parameter_grid(0)
        self.surface.get_parameter_grid(10)

    def test_point_cloud(self):
        self.surface.get_original_point_cloud()

class ColoredGridTestCase(unittest.TestCase):
    def setUp(self):
        from surface import ImplicitSurface
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)

    def test_colored_grid(self):
        grid = self.surface.get_parameter_grid(4, 1)
        self.failUnless(grid._colors != None and len(grid._colors) > 0 and len(grid._colors) == len(grid._points))
