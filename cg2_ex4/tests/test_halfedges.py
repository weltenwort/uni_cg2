import unittest
from pprint import pprint

from numpy import array, any, all
from surface import ImplicitSurface
from marching_cube import MarchingCubeNode
from halfedge import HalfEdgeMesh
from optimizer import HalfEdgeMeshOptimizer

class CatTestCase(unittest.TestCase):
    def setUp(self):
        self.model_filename = "pointdata/cat.off"
        self.surface = ImplicitSurface.from_file(self.model_filename)
        self.cube_node = self.surface.get_implicit_surface(10, 1, 0.05)

    def test_halfedge(self):
        halfedge_mesh = HalfEdgeMesh.from_triangles(self.cube_node)

        # check edge cycles
        for face in halfedge_mesh.faces:
            e1 = face.edge
            e2 = e1.next
            e3 = e2.next
            self.failUnless(e1.face is face)
            self.failUnless(e2.face is face)
            self.failUnless(e3.face is face)
            self.failUnless(e3.next is e1)

    def test_halfedge_mesh(self):
        halfedge_mesh = HalfEdgeMesh.from_triangles(self.cube_node)
        halfedge_mesh_node = halfedge_mesh.get_node("testnode1")
    
    def test_halfedge_optimizer(self):
        halfedge_mesh = HalfEdgeMesh.from_triangles(self.cube_node)
        optimizer = HalfEdgeMeshOptimizer(halfedge_mesh, self.surface)
        optimizer.optimize_by_faces(0.9)
