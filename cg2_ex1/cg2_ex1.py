import logging
from Tkinter import *
from OpenGL.GL import *
from cg2kit import *

from reader import openOff
from kd_tree import KdTree

class KdTreeOptionFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master, 
                borderwidth=1,
                relief=GROOVE)
        self._log = logging.getLogger('KdTreeOptions')
        self._model_var = StringVar()
        self._model_var.set("data/cow.off")
        self._tree_min_depth_var = IntVar()
        self._tree_min_depth_var.set(0)
        self._tree_max_depth_var = IntVar()
        self._tree_max_depth_var.set(5)
        self._label = Label(self, text="KD-Tree Options", width=30)
        self._label.grid(row=0, sticky=E+W)
        self._entry_model = Entry(self, textvariable=self._model_var)
        self._entry_model.grid(row=1, sticky=E+W)
        self._button_build = Button(self, text="Build KD-Tree", command=self._build_tree)
        self._button_build.grid(row=2, sticky=E+W)
        self._scale_tree_min_depth = Scale(self, label="Minimum tree depth", variable=self._tree_min_depth_var, from_=0, to=10, orient=HORIZONTAL)
        self._scale_tree_min_depth.grid(row=3, sticky=E+W)
        self._scale_tree_max_depth = Scale(self, label="Maximum tree depth", variable=self._tree_max_depth_var, from_=0, to=10, orient=HORIZONTAL)
        self._scale_tree_max_depth.grid(row=4, sticky=E+W)
        self._button_show = Button(self, text="Show KD-Tree boxes", command=self._build_tree_visualization)
        self._button_show.grid(row=5, sticky=E+W)

        self._tree_boxes = []

    def _build_tree(self):
        # build tree
        self._log.info(u"Building kd-tree...")
        self.tree = KdTree(point_list=openOff(self._model_var.get()).get_vertices())
        self._log.info(u"Building kd-tree done.")
        
        # create vertex visualization
        self._log.info(u"Building kd-tree vizualization...")
        GLTargetDistantLight(
            pos = (0.3, -0.5, 1)
        )
        mat = GLMaterial(
            diffuse = (1, 0, 0)
            )

        vertices = list(self.tree.iter_vertices())
        t_vertices, t_faces = self._generate_trimesh_params(vertices)
        TriMesh(verts=t_vertices, faces=t_faces, material=mat) #, dynamics=False, static=True)

        #for vertex in list(tree.iter_vertices()):
            #Box(pos=vertex, lx=0.05, ly=0.05, lz=0.05, dynamics=False, static=True, material=mat)
        #Sphere()

        # create bbox visualization
        pass
        self._log.info(u"Building kd-tree vizualization done.")

    def _build_tree_visualization(self):
        min_depth   = self._tree_min_depth_var.get()
        max_depth   = self._tree_max_depth_var.get()
        mat         = GLMaterial(
                diffuse       = (0, 1, 0, 0.1),
                blend_factors = (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                )

        if hasattr(self, 'tree'):
            self._log.info(u"Building kd-tree bounding box visualization...")
            stack = [(self.tree.root, 0), ]
            while stack:
                node, level = stack.pop()
                if level >= min_depth and level <= max_depth:
                    bbox = node.get_bbox()
                    bounds = bbox.getBounds()
                    self._tree_boxes.append(Box(pos=bbox.center(), lx=bounds[0][0] - bounds[1][0], ly=bounds[0][1] - bounds[1][1], lz=bounds[0][2] - bounds[1][2], material=mat))
                if level < max_depth:
                    if node.left_child:
                        stack.append((node.left_child, level+1))
                    if node.right_child:
                        stack.append((node.right_child, level+1))
            self._log.info(u"Building kd-tree bounding box visualization done.")
        else:
            self._log.error(u"No kd-tree found. Please build the tree first.")

    def _generate_trimesh_params(self, vertices):
        result_vertices = []
        result_faces = []
        for n, vertex in enumerate(vertices):
            n = n * 4
            result_vertices.append(vertex)
            result_vertices.append(vertex+(0.1, 0  , 0  ))
            result_vertices.append(vertex+(0  , 0.1, 0  ))
            result_vertices.append(vertex+(0  , 0  , 0.1))
            result_faces.append((n  , n+1, n+2))
            result_faces.append((n  , n+1, n+3))
            result_faces.append((n  , n+2, n+3))
            result_faces.append((n+1, n+2, n+3))

        return (result_vertices, result_faces)


option_frames = [KdTreeOptionFrame, ]
