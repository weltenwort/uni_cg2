from pandac.PandaModules import loadPrcFileData, loadPrcFile
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

import logging
logging.basicConfig(level=logging.DEBUG)
from Tkinter import *
import sys
import math
import direct.directbase.DirectStart
from direct.directtools.DirectGrid import DirectGrid
from direct.tkwidgets.AppShell import AppShell
from pandac.PandaModules import DirectionalLight, Vec4, TransparencyAttrib

from surface import ImplicitSurface
from camera import CameraHandler
from profilehooks import profile
from debughelpers import log_exceptions, dump_args

#try:
#    import psyco
#    psyco.log()
#    psyco.full()
#except ImportError:
#    pass

class BaseApp(AppShell):
    appname = 'CG2'
    usecommandarea = 1
    usestatusarea  = 1
    frameHeight = 600

    def _get_filename(self):
        return self.getVariable('surface', 'filename').get()
    surface_filename = property(_get_filename)

    def _get_invert_normals(self):
        return bool(self.getVariable('surface', 'invert normals').get())
    surface_invert_normals = property(_get_invert_normals)

    def _get_regular_grids(self):
        return [ bool(self.getVariable('surface', 'regular grid %d' % index).get()) for index in range(self._num_surfaces) ]
    surface_regular_grids = property(_get_regular_grids)

    def _get_implicit_surfaces(self):
        return [ bool(self.getVariable('surface', 'implicit surface %d' % index).get()) for index in range(self._num_surfaces) ]
    surface_implicit_surfaces = property(_get_implicit_surfaces)

    def _get_point_cloud(self):
        return bool(self.getVariable('surface', 'point cloud').get())
    surface_point_cloud = property(_get_point_cloud)

    def _get_halfedge_mesh(self):
        return bool(self.getVariable('surface', 'halfedge mesh').get())
    surface_halfedge_mesh = property(_get_halfedge_mesh)

    def _get_subdivisions(self):
        return [int(widget.get()) for widget in self.tk_subdivisions]
    surface_subdivisions = property(_get_subdivisions)

    def _get_degree(self):
        return int(self.tk_degree.get())
    surface_degree = property(_get_degree)

    def _get_radius(self):
        return float(self.tk_radius.get())
    surface_radius = property(_get_radius)

    def _get_light_angle(self):
        return int(self.tk_light_angle.get())
    surface_light_angle = property(_get_light_angle)

    def _get_optimization_choice(self):
        return int(self.var_optimization_choice.get())
    surface_optimization_choice = property(_get_optimization_choice)

    def _get_face_count(self):
        return float(self.tk_face_count.get())
    surface_face_count = property(_get_face_count)

    def _get_improvement_rate(self):
        return float(self.tk_improvement_rate.get())
    surface_improvement_rate = property(_get_improvement_rate)

    def __init__(self):
        self._log = logging.getLogger('BaseApp')
        self._num_surfaces = 1
        AppShell.__init__(self)
        self.initialiseoptions(BaseApp)
        self.createScene()

    def createInterface(self):
        self._log.info(u"Creating interface...")
        self.var_optimization_choice = IntVar()
        self.tk_filename = self.newCreateLabeledEntry(
                parent   = self.interior(),
                category = "surface",
                text     = "filename",
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_invert_normals = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "invert normals",
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_light_angle = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "light angle",
                max      = 360,
                min      = 1,
                resolution = 1,
                command  = self.rotate_light,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_subdivisions = []
        for index in range(self._num_surfaces):
            self.tk_subdivisions.append(self.newCreateEntryScale(
                    parent   = self.interior(),
                    category = "surface",
                    text     = "subdivisions %d" % index,
                    max      = 30,
                    resolution = 1,
                    side     = TOP,
                    fill     = X,
                    expand   = 0))
        self.tk_degree = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "degree",
                max      = 3,
                min      = 1,
                resolution = 1,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_radius = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "radius",
                max      = 0.5,
                min      = 0,
                resolution = 0.01,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_face_count = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "face count",
                max      = 1,
                min      = 0.05,
                resolution = 0.05,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_improvement_rate = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "improvement rate",
                max      = 1,
                min      = 0.05,
                resolution = 0.05,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_optimization_choice_0 = self.newCreateRadiobutton(
                parent   = self.interior(),
                category = "surface",
                text     = "optimize until face count",
                variable = self.var_optimization_choice,
                value    = 0,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_optimization_choice_1 = self.newCreateRadiobutton(
                parent   = self.interior(),
                category = "surface",
                text     = "optimize until improvement rate",
                variable = self.var_optimization_choice,
                value    = 1,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_optimization_choice_2 = self.newCreateRadiobutton(
                parent   = self.interior(),
                category = "surface",
                text     = "don't optimize",
                variable = self.var_optimization_choice,
                value    = 2,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_point_cloud = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "point cloud",
                command  = self._toggle_point_cloud,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_regular_grids = []
        for index in range(self._num_surfaces):
            self.tk_regular_grids.append(self.newCreateCheckbutton(
                    parent   = self.interior(),
                    category = "surface",
                    text     = "regular grid %d" % index,
                    command  = self._toggle_regular_grids,
                    side     = TOP,
                    fill     = X,
                    expand   = 0))
        self.tk_implicit_surfaces = []
        for index in range(self._num_surfaces):
            self.tk_implicit_surfaces.append(self.newCreateCheckbutton(
                    parent   = self.interior(),
                    category = "surface",
                    text     = "implicit surface %d" % index,
                    command  = self._toggle_implicit_surfaces,
                    side     = TOP,
                    fill     = X,
                    expand   = 0))
        self.tk_halfedge_mesh = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "halfedge mesh",
                command  = self._toggle_halfedge_mesh,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_apply = self.buttonAdd(
                buttonName    = 'Apply',
                helpMessage   = 'Apply',
                statusMessage = 'Apply',
                command       = self.apply)
        self.tk_apply_halfedge_mesh = self.buttonAdd(
                buttonName    = 'Apply Halfedge only',
                helpMessage   = 'Apply Halfedge only',
                statusMessage = 'Apply Halfedge only',
                command       = self.apply_halfedge)

        # set default values
        self.getVariable('surface', 'filename').set("pointdata/cat.off")
        self.tk_degree.set(1)
        self.tk_radius.set(0.05)
        self.tk_light_angle.set(1)
        self.getVariable('surface', 'regular grid 0').set(1)
        self.getVariable('surface', 'point cloud').set(1)

    def createScene(self):
        self._log.debug(u"Creating scene...")
        base.setBackgroundColor(0.3, 0.3, 0.3)
        self.gl_dlight = DirectionalLight('dlight')
        self.gl_dlight.setColor(Vec4(1, 1, 1, 1))
        self.np_dlight = render.attachNewNode(self.gl_dlight)
        #self.np_dlight.setHpr(90, 0, 0)
        self.np_dlight.lookAt(1, 1, -10)
        self.l_marker = loader.loadModel("models/misc/Dirlight")
        self.l_marker.reparentTo(self.np_dlight)
        self.l_marker.setScale(0.1, 0.1, 0.1)
        render.setLight(self.np_dlight)
        render.setTransparency(TransparencyAttrib.MAlpha)
        self._camera_control = CameraHandler()
        self.clearScene()
        self.rotate_light(0)

    def clearScene(self):
        if not hasattr(self, 'surfaces'):
            self.surfaces = [None,] * self._num_surfaces
        if not hasattr(self, 'grids'):
            self.grids = [None,] * self._num_surfaces
        if not hasattr(self, 'implicit_surfaces'):
            self.implicit_surfaces = [None,] * self._num_surfaces

        for surface_index in range(self._num_surfaces):
            if self.surfaces[surface_index]:
                self.surfaces[surface_index] = None
                if self.grids[surface_index]:
                    self.grids[surface_index].removeNode()
                self.grids[surface_index] = None
                if self.implicit_surfaces[surface_index]:
                    self.implicit_surfaces[surface_index].removeNode()
                self.implicit_surfaces[surface_index] = None

        if hasattr(self, 'point_cloud') and self.point_cloud:
            self.point_cloud.removeNode()
        self.point_cloud = None

        if hasattr(self, 'halfedge_mesh') and self.halfedge_mesh:
            self.halfedge_mesh.removeNode()
        self.halfedge_mesh = None

    @log_exceptions
    @profile(immediate=True)
    def apply(self):
        self._log.info("Applying values...")
        self.clearScene()
        for index in range(self._num_surfaces):
            self.surfaces[index] = ImplicitSurface.from_file(self.surface_filename, self.surface_invert_normals)
        self._toggle_implicit_surfaces()
        self._toggle_regular_grids()
        self._toggle_point_cloud()
        self._toggle_halfedge_mesh()
        self._camera_control.setTarget(*self.surfaces[0].center[0:3])

    @log_exceptions
    @profile(immediate=True)
    def apply_halfedge(self):
        self._log.info(u"Applying halfedge changes...")
        if hasattr(self, 'halfedge_mesh') and self.halfedge_mesh:
            self.halfedge_mesh.removeNode()
        self.halfedge_mesh = None
        self._toggle_halfedge_mesh()

    @log_exceptions
    def _toggle_regular_grids(self):
        for index in range(self._num_surfaces):
            self._toggle_regular_grid(index)

    def _toggle_regular_grid(self, index):
        if self.surfaces[index]:
            self._log.debug(u"Toggling regular grid %d display..." % index)
            if not self.grids[index]:
                self._log.debug(u"Creating regular grid %d..." % index)
                self.grids[index] = render.attachNewNode(self.surfaces[index].get_parameter_grid(self.surface_subdivisions[index], self.surface_degree, self.surface_radius))
                self.grids[index].setLightOff()
            if self.surface_regular_grids[index]:
                self._log.debug(u"Regular grid %d is now visible." % index)
                self.grids[index].show()
            else:
                self._log.debug(u"Regular grid %d is now hidden." % index)
                self.grids[index].hide()
        else:
            self._log.debug(u"No surface loaded, cannot create regular grid %d..." % index)

    @log_exceptions
    def _toggle_implicit_surfaces(self):
        for index in range(self._num_surfaces):
            self._toggle_implicit_surface(index)

    def _toggle_implicit_surface(self, index):
        if self.surfaces[index] and self.surface_subdivisions[index] > 0:
            self._log.debug(u"Toggling implicit surface %d display..." % index)
            if not self.implicit_surfaces[index]:
                self._log.debug(u"Creating implicit surface %d with %d subdivisions..." % (index, self.surface_subdivisions[index]))
                self.implicit_surfaces[index] = render.attachNewNode(self.surfaces[index].get_implicit_surface(self.surface_subdivisions[index], self.surface_degree, self.surface_radius))
            if self.surface_implicit_surfaces[index]:
                self._log.debug(u"implicit surface %d is now visible." % index)
                self.implicit_surfaces[index].show()
            else:
                self._log.debug(u"implicit surface %d is now hidden." % index)
                self.implicit_surfaces[index].hide()
        else:
            self._log.debug(u"No surface loaded or 0 subdivisions requested, cannot create implicit surface %d..." % index)

    @log_exceptions
    def _toggle_point_cloud(self):
        if self.surfaces[0]:
            self._log.debug(u"Toggling point cloud display...")
            if not self.point_cloud:
                self._log.debug(u"Creating point_cloud...")
                self.point_cloud = render.attachNewNode(self.surfaces[0].get_original_point_cloud())
                self.point_cloud.setLightOff()
            if self.surface_point_cloud:
                self._log.debug(u"point cloud is now visible.")
                self.point_cloud.show()
            else:
                self._log.debug(u"point cloud is now hidden.")
                self.point_cloud.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create point cloud...")

    @log_exceptions
    def _toggle_halfedge_mesh(self):
        if self.surfaces[0]:
            self._log.debug(u"Toggling halfedge mesh display...")
            if not self.halfedge_mesh:
                self._log.debug(u"Creating halfedge mesh...")
                if self.surface_optimization_choice == 0:
                    self.halfedge_mesh = render.attachNewNode(self.surfaces[0].get_halfedge_mesh(self.surface_optimization_choice, self.surface_face_count))
                elif self.surface_optimization_choice == 1:
                    self.halfedge_mesh = render.attachNewNode(self.surfaces[0].get_halfedge_mesh(self.surface_optimization_choice, self.surface_improvement_rate))
                else:
                    self.halfedge_mesh = render.attachNewNode(self.surfaces[0].get_halfedge_mesh(self.surface_optimization_choice, None))
            if self.surface_halfedge_mesh:
                self._log.debug(u"halfedge mesh is now visible.")
                self.halfedge_mesh.show()
            else:
                self._log.debug(u"halfedge mesh is now hidden.")
                self.halfedge_mesh.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create halfedge mesh...")

    @log_exceptions
    def rotate_light(self, val):
        if hasattr(self, 'np_dlight'):
            #self._log.debug(u"Setting light angle %d..." % self.surface_light_angle)
            angle_radians = self.surface_light_angle * (math.pi / 180.0)
            self.np_dlight.setPos(1.0*math.sin(angle_radians), -1.0*math.cos(angle_radians), 1)
            #self._log.debug(u"Light pos: %f, %f, %f" % self.np_dlight.getPos())
            self.np_dlight.lookAt(0, 0, 0)

app = BaseApp()
run()
