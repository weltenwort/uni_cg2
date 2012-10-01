from OpenGL.GL import *
from OpenGL.GLUT import *

from cg2kit import *

class PointCloudGeom(TriMeshGeom):
    def drawGL(self):
        print("foo")
        glBegin(GL_POINTS)
        for vertex in self.verts:
            glVertex3fv(tuple(vertex))
        glEnd()


class PointCloud(WorldObject):
    def __init__(self,
                 name     = "PointCloud",
                 dynamics = True,
                 static   = False,
                 verts    = [],
                 faces    = [],
                 **params):
        WorldObject.__init__(self, name=name, **params)

        self.geom = PointCloudGeom()

        self.dynamics_slot = BoolSlot(dynamics)
        self.static_slot = BoolSlot(static)
        self.addSlot("dynamics", self.dynamics_slot)
        self.addSlot("static", self.static_slot)

        tm = self.geom
        
        if len(verts)>0:
            tm.verts.resize(len(verts))
            i = 0
            for v in verts:
                tm.verts.setValue(i, v)
                i+=1

        if len(faces)>0:
            tm.faces.resize(len(faces))
            i = 0
            for f in faces:
                tm.faces.setValue(i, f)
                i+=1
        
    exec slotPropertyCode("static")
    exec slotPropertyCode("dynamics")
