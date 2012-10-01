import logging
from scipy.spatial import KDTree, cKDTree
from numpy import max, min, linspace, reshape, array, transpose, zeros
from numpy.linalg import norm
from pandac.PandaModules import GeomVertexFormat, GeomVertexData
from pandac.PandaModules import GeomNode, Geom, GeomTriangles, GeomVertexWriter, GeomPoints
from pandac.PandaModules import RenderModeAttrib, CullFaceAttrib
from reader import openOff
from min_squares import MinSquares
from marching_cube import MarchingCubeNode
from halfedge import HalfEdgeMesh
from optimizer import HalfEdgeMeshOptimizer

class ImplicitSurface(object):
    def __init__(self, points, normals):
        self._log               = logging.getLogger('ImplicitSurface')
        self.points             = points
        self.normals            = normals
        self.tree               = cKDTree(self.points)

        # choose distance threshold and eps depending on bbox diameter
        min_point, max_point    = self.get_bounding_box()
        self.box_diag           = float(norm(max_point - min_point))
        self.distance_threshold = 1 # initialized when needed
        self.eps                = 1.0 # initialized when needed
        self.center             = min_point + 0.5 * (max_point - min_point)

        self.square_solver      = None # initialized when needed

        # cache mls results
        self.mls_subdivisions   = None
        self.mls_distances      = []
        self.mls_points         = []
        self.mls_degree         = None
        self.mls_radius         = None

        self.cube_node          = None

    @classmethod
    def from_file(cls, filename, invert_normals=False):
        logging.getLogger('SurfaceFactory').info(u"Reading surface from '%s'..." % filename)
        vertices = []
        normals = []
        for vertex, normal in openOff(filename).iter_vertices_and_normals():
            vertices.append(vertex)
            normals.append(normal)
        vertices = array(vertices)
        normals = array(normals)
        # scale points
        scale_factor = 1.0/norm(max(vertices, 0) - min(vertices, 0))
        vertices *= scale_factor
        # invert normals?
        if invert_normals:
            normals *= -1
        return cls(points=vertices, normals=normals)

    def get_bounding_box(self, expansion_factor=0.2):
        """Returns the minumum and maximum corners of the bounding box.

        :Parameters:
            expansion_factor : float
                The factor by which to enlarge the bounding box.

        :return: (min_point, max_point)
        """
        min_point = min(self.points, 0)
        max_point = max(self.points, 0)
        diff = max_point - min_point
        min_point -= diff*expansion_factor
        max_point += diff*expansion_factor
        return (min_point, max_point)

    def get_parameter_grid(self, subdivisions, degree, radius):
        self.calculate_mls_values(subdivisions, degree, radius)
        if self.mls_subdivisions:
            self._log.debug(u"Calculating colors...")
            colors = zeros(((subdivisions+2)**3,), dtype='4f')
            max_abs_distance = max([abs(min(self.mls_distances)), abs(max(self.mls_distances))])
            for index, distance in enumerate(self.mls_distances):
                if distance < 0:
                    colors[index] = (0.0, 0.0, 1.0, 0.0)
                else:
                    colors[index] = (0.0, 1.0, 0.0, 0.0)
                colors[index] *= (1.0 - abs(float(distance)/max_abs_distance))**4
            colors[:,3] = 1.0
        else:
            self._log.debug(u"Using plain colors...")
            colors = None
        return PointCloudNode(
                name   = 'parameter grid',
                points = [(x,y,z) for x,y,z in self.iter_regular_xyz_grid_points(subdivisions)],
                color  = (0.0,1.0,0.0,0.6),
                colors = colors)

    def get_original_point_cloud(self):
        return PointCloudNode(
                name   = 'point cloud',
                points = self.points,
                color  = (1.0, 1.0, 1.0, 1.0))

    def calculate_mls_values(self, subdivisions, degree, radius):
        if self.mls_subdivisions != subdivisions or self.mls_degree != degree:
            self._log.debug(u"Calculating mls grid values...")

            self.mls_subdivisions = subdivisions
            self.mls_degree = degree
            self.mls_radius = radius
            self.mls_distances = zeros(((subdivisions+2)**3,), dtype='f')
            self.mls_points = zeros(((subdivisions+2)**3,), dtype='3f')

            self.eps = self.box_diag / 100 #((subdivisions or 10) * 10.0)
            self._log.debug("Using radius %f, eps %f..." % (self.mls_radius, self.eps))
            self.square_solver = MinSquares(self)

            for index, point in enumerate(self.iter_regular_xyz_grid_points(subdivisions)):
                distance = self.square_solver.get_point(point, degree)
                self.mls_distances[index] = distance
                self.mls_points[index] = point
        else:
            self._log.debug(u"Using cached mls grid values...")

    def query_distance(self, point):
        return self.square_solver.get_point(point, self.mls_degree)

    def query_normal(self, point):
        return self.square_solver.get_normal(point, self.mls_degree)

    def get_implicit_surface(self, subdivisions, degree, radius):
		if self.cube_node is None:
			self.calculate_mls_values(subdivisions, degree, radius)
			self.cube_node = MarchingCubeNode(
					name    = "implicit_surface",
					surface = self,
					color   = (1.0, 0.0, 0.0, 1.0),
					wireframe = False)
		return self.cube_node

    def get_halfedge_mesh(self, optimization_choice, value):
        if self.cube_node:
            halfedge_mesh = HalfEdgeMesh.from_triangles(self.cube_node)
            optimizer = HalfEdgeMeshOptimizer(halfedge_mesh, self)
            if optimization_choice == 0:
                optimizer.optimize_by_faces(value)
            elif optimization_choice == 1:
                optimizer.optimize_by_improvement(value)
            return halfedge_mesh.get_node("HalfEdge Mesh", color=array([1.0, 0.5, 0.0, 1.0]))
        else:
            return None

    def iter_regular_xyz_grid_points(self, subdivisions):
        min_point, max_point = self.get_bounding_box()
        for x in linspace(min_point[0], max_point[0], subdivisions+2):
            for y in linspace(min_point[1], max_point[1], subdivisions+2):
                for z in linspace(min_point[2], max_point[2], subdivisions+2):
                #self._log.debug(u"Yielding (%f, %f)..." % (x, y))
                    yield (x, y, z)

class SurfaceNode(GeomNode):
    def __init__(self, name, width, height, points, normals=[], color=(1.0,1.0,1.0,1.0), wireframe=False):
        GeomNode.__init__(self, name)
        self._width = width
        self._height = height
        assert(len(points) == self._width * self._height)
        if normals:
            assert(len(normals) == self._width * self._height)
        self._points = points
        self._normals = normals
        self._color = color
        self._wireframe = wireframe

        self._create_vertex_data()
        self._create_geom_primitives()
        self._create_geoms()

        # set visualisation parameters
        if self._wireframe:
            self.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2, 1))
        self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

    def _create_vertex_data(self):
        """Creates and fills the vertex data store."""
        format = GeomVertexFormat.getV3n3cp()
        vdata = GeomVertexData('plane', format, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for x in xrange(self._width):
            for y in xrange(self._height):
                cur_index = x * self._height + y
                vertex.addData3f(*self._points[cur_index][0:3])
                if self._normals:
                    normal.addData3f(*self._normals[cur_index])
                else:
                    normal.addData3f(0, 0, 1)
                color.addData4f(*self._color)

        self._vdata = vdata

    def _create_geom_primitives(self):
        """Creates and fill a GeomTriangles with vertex indices."""
        tri = GeomTriangles(Geom.UHDynamic)
        for x in xrange(self._width-1):
            for y in xrange(self._height-1):
                cur_index = x * self._height + y
                tri.addVertex(cur_index)
                tri.addVertex(cur_index+1)
                tri.addVertex(cur_index+self._height)
                tri.addVertex(cur_index+1)
                tri.addVertex(cur_index+self._height)
                tri.addVertex(cur_index+self._height+1)
        tri.closePrimitive()
        self._geom_primitives = [tri, ]

    def _create_geoms(self):
        """Creates a Geom attached to self and adds the current primitives."""
        self._geom = Geom(self._vdata)
        for primitive in self._geom_primitives:
            self._geom.addPrimitive(primitive)
        self.addGeom(self._geom)

class PointCloudNode(GeomNode):
    def __init__(self, name, points, color=(1.0,1.0,1.0,1.0), colors=None):
        GeomNode.__init__(self, name)
        self._points = points
        self._color = color
        self._colors = colors

        self._create_vertex_data()
        self._create_geom_primitives()
        self._create_geoms()

        # set visualisation parameters
        #if self._wireframe:
        #    self.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2, 1))
        #self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))
        self.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2, 0))

    def _create_vertex_data(self):
        """Creates and fills the vertex data store."""
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('cloud', format, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')

        for index, point in enumerate(self._points):
            vertex.addData3f(*point[0:3])
            if self._colors != None:
                color.addData4f(*self._colors[index])
            else:
                color.addData4f(*self._color)

        self._vdata = vdata

    def _create_geom_primitives(self):
        """Creates and fill a GeomTriangles with vertex indices."""
        pts = GeomPoints(Geom.UHDynamic)
        pts.addNextVertices(len(self._points))
        pts.closePrimitive()
        self._geom_primitives = [pts, ]

    def _create_geoms(self):
        """Creates a Geom attached to self and adds the current primitives."""
        self._geom = Geom(self._vdata)
        for primitive in self._geom_primitives:
            self._geom.addPrimitive(primitive)
        self.addGeom(self._geom)

