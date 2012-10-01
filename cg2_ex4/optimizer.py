import logging
from heapq import heapify, heappop, heappush
from profilehooks import profile
from debughelpers import log_exceptions, dump_args
from pprint import pprint

from operations import EdgeFlipOperation, EdgeSplitOperation, EdgeCollapseOperation

class HalfEdgeMeshOptimizer(object):
    known_operations = [EdgeFlipOperation,]

    def __init__(self, halfedge_mesh, surface):
        self._log          = logging.getLogger('Optimizer')
        self.halfedge_mesh = halfedge_mesh
        self.surface       = surface

    def calculate_operations(self):
        known_edges = []
        operations = []
        for operation_cls in self.known_operations:
            for edge in self.halfedge_mesh.halfedges:
                if not edge.opposite in known_edges:
                    known_edges.append(edge)
                    if operation_cls.is_suitable(edge):
                        operations.append(operation_cls(edge, self.surface, self))
        heapify(operations)
        return operations
	
    def optimize_by_faces(self, face_limit):
        self._log.info(u"Starting optimization by face count (%f)..." % face_limit)
        self.known_operations = [EdgeCollapseOperation,]
        self.operations = self.calculate_operations()
        if len(self.operations) > 0:
            face_limit = face_limit * len(self.halfedge_mesh.faces)
            while len(self.operations):
                operation = heappop(self.operations)
                if len(self.halfedge_mesh.faces) > face_limit:
                    self._log.debug(u"Performing %s..." % str(operation))
                    operation.perform(self.halfedge_mesh)
                else:
                    break
        self._log.info(u"Done optimizing, %d faces left." % len(self.halfedge_mesh.faces))
        
    def optimize_by_improvement(self, improvement_limit):
        self._log.info(u"Starting optimization by improvement (%f)..." % improvement_limit)
        self.known_operations = [EdgeFlipOperation, EdgeCollapseOperation]#EdgeSplitOperation, ]
        self.operations = self.calculate_operations()
        if len(self.operations) > 0:
            improvement_limit = improvement_limit * len(self.operations)
            while len(self.operations):
                operation = heappop(self.operations)
                if len(self.operations) > improvement_limit:
                    self._log.debug(u"Performing %s..." % str(operation))
                    operation.perform(self.halfedge_mesh)
                else:
                    break
        self._log.info(u"Done optimizing, %d faces left." % len(self.halfedge_mesh.faces))
        
    def delete_by_edge(self, edges):
        edges += [ edge.opposite for edge in edges ]
        ops = []
        for operation in self.operations:
            if operation.edge in edges:
                ops.append(operation)
        for operation in ops:
            self.operations.remove(operation)
        heapify(self.operations)

    def update_by_edge(self, edges):
        self.delete_by_edge(edges)
        for operation_cls in self.known_operations:
            for edge in edges:
                if operation_cls.is_suitable(edge):
                    heappush(self.operations, operation_cls(edge, self.surface, self))

