from halfedge import Vertex, Halfedge, Face

class EdgeOperation(object):
    __slots__ = ["edge", "surface", "improvement"]

    def __init__(self, edge, surface,  optimizer):
        self.edge        = edge
        self.surface     = surface
        self.optimizer = optimizer
        self.improvement = self.calculate_improvement()

    def calculate_improvement(self):
        """needs to be overridden in subclasses."""
        return 0

    def perform(self, halfedge_mesh):
        """needs to be overridden in subclasses."""
        pass

    def _get_edge_distance(self, edge):
        return self.surface.query_distance(edge.origin.coordinates) + self.surface.query_distance(edge.next.origin.coordinates)

    def _get_edge_distances(self, edges):
        return max([ self._get_edge_distance(edge) for edge in edges ])

    def __cmp__(self, other):
        return other.improvement - self.improvement 

    def __unicode__(self):
        return self.__str__()

    @classmethod
    def is_suitable(cls, edge):
        """needs to be overridden in subclasses."""
        return False

class EdgeFlipOperation(EdgeOperation):
    def calculate_improvement(self):
        faces = self.edge.get_faces()
        original_vertices = self.edge.get_vertices()
        original_distance = self._get_edge_distance(self.edge)
        other_vertices = list(set(self.edge.face.get_vertices()) ^ set(self.edge.opposite.face.get_vertices()))
        new_edge = Halfedge(other_vertices[0], other_vertices[1].edge, None, None)
        new_distance = self._get_edge_distance(new_edge)
        return abs(original_distance) / (abs(new_distance) or 0.0000000001)

    def perform(self, halfedge_mesh):
        #collect data
        opposite_halfedge = self.edge.opposite
        face1 = self.edge.face
        face2 = opposite_halfedge.face
        node1_to_update = self.edge.origin
        node2_to_update = opposite_halfedge.origin
        node1_new_edge = opposite_halfedge.next
        node2_new_edge = self.edge.next
        new_edges_face1 = [self.edge,  self.edge.next,  opposite_halfedge.next.next]
        new_edges_face2 = [opposite_halfedge,  opposite_halfedge.next,  self.edge.next.next]
        edges_to_update = [self.edge.next,  opposite_halfedge.next.next,  opposite_halfedge.next,  self.edge.next.next]
        halfedge1_new_origin = self.edge.next.next.origin
        halfedge2_new_origin = opposite_halfedge.next.next.origin
        
        #update half edge data structure
        self.edge.origin = halfedge1_new_origin
        opposite_halfedge.origin = halfedge2_new_origin
        for i in range(3):
            new_edges_face1[i].next = new_edges_face1[i+1] if i < 2 else new_edges_face1[0]
            new_edges_face1[i].face = face1
            new_edges_face2[i].next = new_edges_face2[i+1] if i < 2 else new_edges_face2[0]
            new_edges_face2[i].face = face2
        face1.edge = self.edge
        face2.edge = opposite_halfedge
        node1_to_update.edge = node1_new_edge
        node2_to_update.edge = node2_new_edge
        
        # update heap
        #self.optimizer.update_by_edge(edges_to_update)
        self.optimizer.delete_by_edge(edges_to_update)

    @classmethod
    def is_suitable(cls, edge):
        return not edge.opposite is None

	def __str__(self):
		return "<EdgeFlipOperation edge=%s improvement=%d>" % (self.edge, self.improvement)

class EdgeCollapseOperation(EdgeOperation):
    def calculate_improvement(self):
        original_vertices = self.edge.get_vertices()
        other_edges = list((set(original_vertices[0].get_edges()) | set(original_vertices[1].get_edges())) - set([self.edge,]))
        other_vertices = set()
        for edge in other_edges:
            other_vertices.update(edge.get_vertices())
        other_vertices -= set(original_vertices)
        new_vertex_coords, new_vertex_normal = self._create_new_vertex(original_vertices)
        new_vertex = Vertex(new_vertex_coords, new_vertex_normal, None)
        new_edges = []
        for vertex in other_vertices:
            temp_edge = Halfedge(vertex, None, None, None)
            new_edges.append(Halfedge(new_vertex, temp_edge, None, None))

        old_distance = self._get_edge_distances(other_edges)
        new_distance = self._get_edge_distances(new_edges)
        return abs(old_distance) / (abs(new_distance) or 0.0000000001)

    def _create_new_vertex(self, original_vertices):
        v1, v2 = original_vertices
        new_vertex_coords = v1.coordinates + 0.5 * (v2.coordinates - v2.coordinates)
        new_vertex_normal = self.surface.query_normal(new_vertex_coords)
        new_vertex_coords -= self.surface.query_distance(new_vertex_coords) * new_vertex_normal
        return (new_vertex_coords, new_vertex_normal)

    def perform(self, halfedge_mesh):
        # collect data
        main_vertices = self.edge.get_vertices()
        
        edges = [
                self.edge,
                self.edge.opposite,
                self.edge.next,
                self.edge.next.next,
                self.edge.opposite.next,
                self.edge.opposite.next.next]

        edge_opposites = [ edge.opposite for edge in edges ]
        other_edges = [ edge for edge in main_vertices[1].get_edges() if not edge in edges ]

        faces_to_delete = [self.edge.face, self.edge.opposite.face]
        edges_to_delete = edges

        # update data
        # update vertices
        if main_vertices[0].edge in edges_to_delete:
            main_vertices[0].edge = main_vertices[0].edge.next.next.opposite
            #main_vertices[0].edge = edges[2] if edges[2].origin is main_vertices[0] else edges[5]
        new_coords, new_normal = self._create_new_vertex(main_vertices)
        main_vertices[0].coordinates = new_coords
        main_vertices[1].normal = new_normal
        
        # fuse edges
        if not edge_opposites[2] is None:
            edge_opposites[2].opposite = edge_opposites[3]
        if not edge_opposites[3] is None:
            edge_opposites[3].opposite = edge_opposites[2]
        if not edge_opposites[4] is None:
            edge_opposites[4].opposite = edge_opposites[5]
        if not edge_opposites[5] is None:
            edge_opposites[5].opposite = edge_opposites[4]
        # update edges
        for edge in other_edges:
            if edge.origin is main_vertices[1]:
                edge.origin = main_vertices[0]

        # delete edges
        for edge in edges_to_delete:
            try:
                halfedge_mesh.halfedges.remove(edge)
            except:
                pass
        self.optimizer.delete_by_edge(edges_to_delete)
        for face in faces_to_delete:
            halfedge_mesh.faces.remove(face)
        halfedge_mesh.vertices.remove(main_vertices[1])

        #self.optimizer.update_by_edge(other_edges)
        self.optimizer.delete_by_edge(other_edges)

    @classmethod
    def is_suitable(cls, edge):
        main_vertices = edge.get_vertices()
        border_edges = [ edge for edge in main_vertices[1].get_edges() if edge.opposite is None ] + [ edge for edge in main_vertices[0].get_edges() if edge.opposite is None ]
        return len(border_edges) == 0

	def __str__(self):
		return "<EdgeCollapseOperation edge=%s improvement=%d>" % (self.edge, self.improvement)

class EdgeSplitOperation(EdgeOperation):
    def calculate_improvement(self):
        opposite_halfedge = self.edge.opposite
        old_distance = self._get_edge_distance(self.edge) 
        new_coords,  new_normal = self.get_point_location()
        dummy_point = Vertex(new_coords,  new_normal,  None)
        dummy_edge = Halfedge(dummy_point,  None, None,  None)
        new_edge1 = Halfedge(self.edge.origin, dummy_edge, None, None)
        new_edge2 = Halfedge(self.edge.opposite.origin, dummy_edge, None, None)
        new_edge3 = Halfedge(self.edge.next.next.origin, dummy_edge, None, None)
        new_edge4 = Halfedge(self.edge.opposite.next.next.origin, dummy_edge, None, None)
        new_edges = [new_edge1,  new_edge2,  new_edge3,  new_edge4]
        new_distance = self._get_edge_distances(new_edges)
        return abs(old_distance) / (abs(new_distance) or 0.0000000001)

    def perform(self, halfedge_mesh):
        #collect data
        opposite_halfedge = self.edge.opposite
        new_coords,  new_normal = self.get_point_location()
        new_vertex = Vertex(new_coords,  new_normal,  opposite_halfedge)
        edges_to_update = [self.edge.next,  self.edge.next.next,  opposite_halfedge.next,  opposite_halfedge.next.next]
        
        new_edge10 = self.edge
        new_edge11 = opposite_halfedge
        new_edge20 = Halfedge(new_vertex, None, None, None)
        new_edge21 = Halfedge(self.edge.next.origin, None, None, None)
        new_edge30 = Halfedge(new_vertex, None, None, None)
        new_edge31 = Halfedge(self.edge.next.next.origin, None, None, None)
        new_edge40 = Halfedge(new_vertex, None, None, None)
        new_edge41 = Halfedge(opposite_halfedge.next.next.origin, None, None, None)
        
        face1 = self.edge.face
        face2 = opposite_halfedge.face
        face3 = Face(new_edge20)
        face4 = Face(new_edge21)
        new_edges_face1 = [new_edge10,  new_edge30,  self.edge.next.next]
        new_edges_face2 = [new_edge11,  opposite_halfedge.next,  new_edge41]
        new_edges_face3 = [new_edge20,  self.edge.next,  new_edge31]
        new_edges_face4 = [new_edge40,  opposite_halfedge.next.next,  new_edge21]
        
        node1_to_update = self.edge.next.origin
        node1_new_edge = self.edge.next
        
        #update half edge data structure
        new_edge20.opposite = new_edge21
        new_edge21.opposite = new_edge20
        new_edge30.opposite = new_edge31
        new_edge31.opposite = new_edge30
        new_edge40.opposite = new_edge41
        new_edge41.opposite = new_edge40
        
        for i in range(3):
            new_edges_face1[i].next = new_edges_face1[i+1] if i < 2 else new_edges_face1[0]
            new_edges_face1[i].face = face1
            new_edges_face2[i].next = new_edges_face2[i+1] if i < 2 else new_edges_face2[0]
            new_edges_face2[i].face = face2
            new_edges_face3[i].next = new_edges_face3[i+1] if i < 2 else new_edges_face3[0]
            new_edges_face3[i].face = face3
            new_edges_face4[i].next = new_edges_face4[i+1] if i < 2 else new_edges_face4[0]
            new_edges_face4[i].face = face4
            
        node1_to_update.edge = node1_new_edge
        
        halfedge_mesh.vertices.append(new_vertex)
        halfedge_mesh.halfedges.extend([new_edge20,  new_edge21,  new_edge30,  new_edge31,  new_edge40,  new_edge41])
        halfedge_mesh.faces.extend([face3, face4])
        
        # update / delete from heap
        #self.optimizer.update_by_edge(edges_to_update)
        self.optimizer.delete_by_edge(edges_to_update)

    def get_point_location(self):
        temp_coords = 0.5 * self.edge.origin.coordinates + 0.5 * self.edge.opposite.origin.coordinates
        value = self.surface.query_distance(temp_coords)
        normal = self.surface.query_normal(temp_coords)
        return (temp_coords - value * normal,  normal)

    @classmethod
    def is_suitable(cls, edge):
        return not edge.opposite is None

	def __str__(self):
		return "<EdgeSplitOperation edge=%s improvement=%d>" % (self.edge, self.improvement)
