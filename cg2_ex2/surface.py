import logging
from scipy.spatial import KDTree
from numpy import max, min, linspace, reshape, array, transpose
from pandac.PandaModules import GeomVertexFormat, GeomVertexData
from pandac.PandaModules import GeomNode, Geom, GeomTriangles, GeomVertexWriter, GeomPoints
from pandac.PandaModules import RenderModeAttrib, CullFaceAttrib
from reader import openOff
from min_squares import MinSquares
from casteljau import Casteljau

class Surface(object):
    def __init__(self, points):
        self._log = logging.getLogger('Surface')
        self.mapping = {}
        for point in points:
            self.mapping[point[0:2]] = point[2]
        self.points = self.mapping.keys()
        self.tree = KDTree(self.points)
        self.square_solver = MinSquares(self)
        # cache mls results
        self.mls_subdivisions = None
        self.mls_points = None

    @classmethod
    def from_file(cls, filename):
        logging.getLogger('SurfaceFactory').info(u"Reading surface from '%s'..." % filename)
        return cls(openOff(filename).iter_vertices())

    def get_parameter_plane(self, subdivisions):
        return SurfaceNode(
                name   = 'parameter plane',
                width  = subdivisions+2,
                height = subdivisions+2,
                points = [(x,y,0) for x,y in self.iter_regular_xy_grid_points(subdivisions)],
                color  = (1.0,1.0,1.0,0.9),
                wireframe = True)

    def get_original_point_cloud(self):
        return PointCloudNode(
                name   = 'point cloud',
                points = self.mapping,
                color  = (1.0, 1.0, 1.0, 0.9))

    def get_mls_interpolated_surface(self, subdivisions):
        if self.mls_subdivisions != subdivisions:
            points_normals = [(x,y) + self.square_solver.solveEquations((x,y)) for x,y in self.iter_regular_xy_grid_points(subdivisions)]
            self.mls_points = [(x,y,z) for x,y,z,n in points_normals]
            self.mls_normals = [n for x,y,z,n in points_normals]
            self.mls_subdivisions = subdivisions
        return SurfaceNode(
                name   = 'mls surface',
                width  = subdivisions+2,
                height = subdivisions+2,
                points = self.mls_points,
                normals= self.mls_normals,
                color  = (1.0,0.0,0.0,0.9))

    def get_bezier_interpolated_surface(self, mls_subdivisions, bezier_factor):
        self._log.debug(u"Creating surface using grid %d and bezier factor %d" % (mls_subdivisions, bezier_factor))
        if self.mls_subdivisions != mls_subdivisions:
            self.get_mls_interpolated_surface(mls_subdivisions)

        value_matrix = transpose(reshape(array(self.mls_points)[:,2], (mls_subdivisions+2, mls_subdivisions+2)), (1,0))
        casteljau = Casteljau(value_matrix)
        points_normals = [(x,y) + casteljau.evaluate_point((x,y)) for x,y in self.iter_regular_xy_grid_points(mls_subdivisions*bezier_factor)]
        return SurfaceNode(
                name   = 'bezier surface',
                width  = mls_subdivisions*bezier_factor+2,
                height = mls_subdivisions*bezier_factor+2,
                points = [(x,y,z) for x,y,z,n in points_normals],
                normals= [n for x,y,z,n in points_normals],
                color  = (0.0,1.0,0.0,0.5))

    def iter_regular_xy_grid_points(self, subdivisions):
        min_point = min(self.points, 0)
        max_point = max(self.points, 0)

        for x in linspace(min_point[0], max_point[0], subdivisions+2):
            for y in linspace(min_point[1], max_point[1], subdivisions+2):
                #self._log.debug(u"Yielding (%f, %f)..." % (x, y))
                yield (x, y)

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
    def __init__(self, name, points, color=(1.0,1.0,1.0,1.0)):
        GeomNode.__init__(self, name)
        self._points = points
        self._color = color

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

        for point, value in self._points.iteritems():
            vertex.addData3f(point[0], point[1], value)
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

