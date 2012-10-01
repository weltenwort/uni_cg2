import logging

from numpy import array

class FileFormatException(Exception):
    pass

class openOff(object):
    def __init__(self, filename):
        self._filename = filename
        self._log = logging.getLogger('openOff')
    
    def get_vertices(self):
        try:
            f = open(self._filename)
            self._log.debug(u"Opened file '%s' as OFF file." % self._filename)
            vertices = []
            first_line = f.readline()
            if first_line.startswith("OFF"):
                vertice_count, polygon_count, edge_count = [ int(value.strip()) for value in f.readline().split(" ") ]
                for vertex_index in range(vertice_count):
                    vertices.append(array([ float(coord.strip()) for coord in f.readline().split(" ") if coord.strip() != "" ]))
            else:
                raise FileFormatException("The file '%s' is not of the expected format: %s" % (self._filename, first_line))
        finally:
            f.close()
        return vertices

    def iter_vertices(self):
        try:
            f = open(self._filename)
            self._log.debug(u"Opened file '%s' as OFF file." % self._filename)
            first_line = f.readline()
            if first_line.startswith("OFF"):
                vertice_count, polygon_count, edge_count = [ int(value.strip()) for value in f.readline().split(" ") ]
                for vertex_index in range(vertice_count):
                    yield tuple([ float(coord.strip()) for coord in f.readline().split(" ") if coord.strip() != "" ])
            else:
                raise FileFormatException("The file '%s' is not of the expected format: %s" % (self._filename, first_line))
        finally:
            f.close()

