import logging
from numpy import max, min, linspace, reshape, array, transpose, zeros, where, sum, allclose, fabs, dtype
from numpy.linalg import norm
from pandac.PandaModules import GeomNode, Geom, GeomTriangles, GeomVertexWriter, GeomVertexReader
from pandac.PandaModules import RenderModeAttrib, CullFaceAttrib
from pandac.PandaModules import GeomVertexFormat, GeomVertexData
from profilehooks import profile
from debughelpers import log_exceptions, dump_args

#class DuplicateVertexException(Exception):
#    pass

class Vertex(object):
    __slots__ = ["coordinates", "normal", "edge"]

    def __init__(self, coordinates, normal, edge):
        self.coordinates = coordinates
        self.normal      = normal
        self.edge        = edge

    def iter_edges(self):
        yield self.edge
        if not self.edge.opposite is None:
            edge = self.edge.opposite.next
            while not (edge is self.edge) and not (edge is None):
                yield edge
                if not edge.opposite is None:
                    edge = edge.opposite.next
                else:
                    break

    def get_edges(self):
        return list(self.iter_edges())

    def iter_faces(self):
        for edge in self.iter_edges():
            yield edge.face

    def get_faces(self):
        return list(self.iter_faces())

class Halfedge(object):
    __slots__ = ["origin", "next", "opposite", "face"]

    def __init__(self, origin, next, opposite, face):
        self.origin   = origin
        self.next     = next
        self.opposite = opposite
        self.face     = face

    def iter_vertices(self):
        yield self.origin
        yield self.next.origin

    def get_vertices(self):
        return list(self.iter_vertices())

    def iter_faces(self):
        yield self.face
        if not self.opposite is None:
            yield self.opposite.face

    def get_faces(self):
        return list(self.iter_faces())

class Face(object):
    __slots__ = ["edge", ]

    def __init__(self, edge):
        self.edge = edge

    def iter_edges(self):
        yield self.edge
        edge = self.edge.next
        while not edge is self.edge:
            yield edge
            edge = edge.next

    def get_edges(self):
        return list(self.iter_edges())

    def iter_vertices(self):
        for edge in self.iter_edges():
            yield edge.origin

    def get_vertices(self):
        return list(self.iter_vertices())

class HalfEdgeMesh(object):
    def __init__(self, vertices, halfedges, faces):
        self._log      = logging.getLogger('HalfEdgeMesh')
        self.vertices  = vertices
        self.halfedges = halfedges
        self.faces     = faces

    def get_node(self, name, color=array([1.0, 1.0, 1.0, 1.0]), wireframe=False):
        return HalfEdgeMeshNode(
                name          = name,
                halfedge_mesh = self,
                color         = color,
                wireframe     = wireframe)

    @classmethod
    @profile
    def from_triangles(cls, triangle_geom_node):
        _log               = logging.getLogger('HalfEdgeMesh')
        tri_geom           = triangle_geom_node.getGeom(0) # assume that the triangle list is in the first geom in the node
        tri_primitive      = tri_geom.getPrimitive(0) # assume that the triangle list is the first primitive in the geom
        vdata              = tri_geom.getVertexData()
        vertex_reader      = GeomVertexReader(vdata, 'vertex')
        normal_reader      = GeomVertexReader(vdata, 'normal')
        #halfedges          = zeros((tri_primitive.getNumPrimitives()*3,), dtype=cls.halfedge_dtype)
        #faces              = zeros((tri_primitive.getNumPrimitives()  ,), dtype=cls.face_dtype)
        #temp_vertices      = zeros((vdata.getNumRows(),), dtype=cls.vertex_dtype)
        halfedges          = []
        faces              = []
        vertices           = []
        identity_threshold = 0.00001
        
        _log.debug(u"Creating mesh from %d vertices and %d faces..." % (vdata.getNumRows(), tri_primitive.getNumPrimitives()))

        vertex_count = 0
        vertex_index = 0
        edge_index   = 0
        face_index   = 0
        for triangle_index in range(tri_primitive.getNumPrimitives()):
            # add vertices
            vertex_start = tri_primitive.getPrimitiveStart(triangle_index)
            vertex_end   = tri_primitive.getPrimitiveEnd(triangle_index)
            edge_base    = edge_index
            for prim_vertex_index in range(vertex_start, vertex_end):
                vertex_reader.setRow(prim_vertex_index)
                coordinates = array(vertex_reader.getData3f())
                
                # find duplicate within a threshold
                #same_vertices = [ vertex_index for vertex_index, vertex_data in enumerate(temp_vertices[:vertex_count]) if not any(fabs(vertex_data['coord'] - vertex) > identity_threshold) ]
                vertex = None
                for vertex_data in vertices:
                    if not any(fabs(vertex_data.coordinates - coordinates) > identity_threshold):
                        vertex = vertex_data
                        break;
                if vertex is None:
                    # new vertex
                    normal_reader.setRow(prim_vertex_index)
                    normal = array(normal_reader.getData3f())
                    vertex = Vertex(coordinates, normal, edge_index)
                    vertices.append(vertex)
                    vertex_count += 1

                # add edge
                halfedges.append(Halfedge(vertex, edge_base+(edge_index-edge_base+1)%3, None, None))
                edge_index += 1

            # add face
            face = Face(halfedges[edge_base])
            faces.append(face)
            face_index +=1
            # determine matching face
            for edge_data in halfedges[edge_base:]:
                edge_data.face = face

        _log.debug(u"Found %d unique vertices with %d halfedges and %d faces." % (vertex_count, edge_index, face_index))

        for vertex_data in vertices:
            vertex_data.edge = halfedges[vertex_data.edge]

        # resolve 'next' edges
        for edge_data in halfedges:
            edge_data.next = halfedges[edge_data.next]

        # determine 'opposite' edges
        for edge_data in halfedges:
            if edge_data.opposite == None:
                v1 = edge_data.origin
                v2 = edge_data.next.origin
                for opposite_edge_data in halfedges:
                    if opposite_edge_data.origin == v2 and opposite_edge_data.next.origin == v1:
                        edge_data.opposite = opposite_edge_data
                        opposite_edge_data.opposite = edge_data
                        break

        _log.debug(u"Done creating mesh.")
        return cls(vertices, halfedges, faces)

class HalfEdgeMeshNode(GeomNode):
    def __init__(self, name, halfedge_mesh, color, wireframe=False):
        GeomNode.__init__(self, name)
        self._halfedge_mesh = halfedge_mesh
        self._color         = color
        self._wireframe     = wireframe

        self._create_vertex_data()
        self._create_geoms()

        # set visualisation parameters
        if self._wireframe:
            self.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2, 1))
        self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))


    def _create_vertex_data(self):
        """Creates and fills the vertex data store."""
        format = GeomVertexFormat.getV3n3cp()
        vdata = GeomVertexData('surface', format, Geom.UHDynamic)
        tri = GeomTriangles(Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for triangle in self._halfedge_mesh.faces:
            for v in triangle.iter_vertices():
                vertex.addData3f(*v.coordinates)
                normal.addData3f(*v.normal)
                color.addData4f(*self._color)
                tri.addNextVertices(1)

        self._vdata = vdata
        tri.closePrimitive()
        self._geom_primitives = [tri, ]

    def _create_geoms(self):
        """Creates a Geom attached to self and adds the current primitives."""
        self._geom = Geom(self._vdata)
        for primitive in self._geom_primitives:
            self._geom.addPrimitive(primitive)
        self.addGeom(self._geom)
