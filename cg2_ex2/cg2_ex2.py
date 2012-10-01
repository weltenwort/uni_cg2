from pandac.PandaModules import loadPrcFileData, loadPrcFile
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

import logging
logging.basicConfig(level=logging.DEBUG)
from Tkinter import *
import sys
import direct.directbase.DirectStart
from direct.directtools.DirectGrid import DirectGrid
from direct.tkwidgets.AppShell import AppShell
from pandac.PandaModules import DirectionalLight, Vec4, TransparencyAttrib

from surface import Surface
from camera import CameraHandler

class BaseApp(AppShell):
    appname = 'CG2'
    usecommandarea = 1
    usestatusarea  = 1

    def _get_filename(self):
        return self.getVariable('surface', 'filename').get()
    surface_filename = property(_get_filename)

    def _get_plane(self):
        return bool(self.getVariable('surface', 'display plane').get())
    surface_plane = property(_get_plane)

    def _get_mls_surface(self):
        return bool(self.getVariable('surface', 'mls surface').get())
    surface_mls_surface = property(_get_mls_surface)

    def _get_bezier_surface(self):
        return bool(self.getVariable('surface', 'bezier surface').get())
    surface_bezier_surface = property(_get_bezier_surface)

    def _get_point_cloud(self):
        return bool(self.getVariable('surface', 'point cloud').get())
    surface_point_cloud = property(_get_point_cloud)

    def _get_subdivisions(self):
        return int(self.tk_subdivisions.get())
    surface_subdivisions = property(_get_subdivisions)

    def _get_bezier_factor(self):
        return int(self.tk_bezier_factor.get())
    bezier_factor = property(_get_bezier_factor)

    def __init__(self):
        self._log = logging.getLogger('BaseApp')
        AppShell.__init__(self)
        self.initialiseoptions(BaseApp)
        self.createScene()

    def createInterface(self):
        self._log.info(u"Creating interface...")
        self.tk_filename = self.newCreateLabeledEntry(
                parent   = self.interior(),
                category = "surface",
                text     = "filename",
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_subdivisions = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "subdivisions",
                max      = 20,
                resolution = 1,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_bezier_factor = self.newCreateEntryScale(
                parent   = self.interior(),
                category = "surface",
                text     = "bezier factor",
                min      = 1,
                max      = 20,
                resolution = 1,
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
        self.tk_plane = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "display plane",
                command  = self._toggle_plane,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_mls_surface = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "mls surface",
                command  = self._toggle_mls_surface,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_bezier_surface = self.newCreateCheckbutton(
                parent   = self.interior(),
                category = "surface",
                text     = "bezier surface",
                command  = self._toggle_bezier_surface,
                side     = TOP,
                fill     = X,
                expand   = 0)
        self.tk_apply = self.buttonAdd(
                buttonName    = 'Apply',
                helpMessage   = 'Apply',
                statusMessage = 'Apply',
                command       = self.apply)

        # set default values
        self.getVariable('surface', 'filename').set("pointdata/franke4.off")
        self.getVariable('surface', 'mls surface').set(1)
        self.getVariable('surface', 'point cloud').set(1)
        self.tk_bezier_factor.set(1)

    def createScene(self):
        self._log.debug(u"Creating scene...")
        base.setBackgroundColor(0, 0, 0)
        self.gl_dlight = DirectionalLight('dlight')
        self.gl_dlight.setColor(Vec4(1, 1, 1, 1))
        self.np_dlight = render.attachNewNode(self.gl_dlight)
        #self.np_dlight.setHpr(90, 0, 0)
        self.np_dlight.lookAt(1, 1, -10)
        render.setLight(self.np_dlight)
        render.setTransparency(TransparencyAttrib.MAlpha)
        CameraHandler()
        self.surface = None
        self.plane = None
        self.mls_surface = None
        self.bezier_surface = None
        self.point_cloud = None

    def apply(self):
        self._log.debug(u"""Applying values
        filename: '%s',
        subdivisions: '%f',
        bezier factor: '%f'""" % (
            self.surface_filename,
            self.surface_subdivisions,
            self.bezier_factor))
        if self.surface:
            del self.surface
            if self.plane:
                self.plane.removeNode()
                self.plane = None
            if self.mls_surface:
                self.mls_surface.removeNode()
                self.mls_surface = None
            if self.bezier_surface:
                self.bezier_surface.removeNode()
                self.bezier_surface = None
            if self.point_cloud:
                self.point_cloud.removeNode()
                self.point_cloud = None
        self.surface = Surface.from_file(self.surface_filename)
        self._toggle_plane()
        self._toggle_mls_surface()
        self._toggle_bezier_surface()
        self._toggle_point_cloud()

    def _toggle_plane(self):
        if self.surface:
            self._log.debug(u"Toggling parameter plane display...")
            if not self.plane:
                self._log.debug(u"Creating parameter plane...")
                self.plane = render.attachNewNode(self.surface.get_parameter_plane(self.surface_subdivisions))
            if self.surface_plane:
                self._log.debug(u"Parameter plane is now visible.")
                self.plane.show()
            else:
                self._log.debug(u"Parameter plane is now hidden.")
                self.plane.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create parameter plane...")

    def _toggle_mls_surface(self):
        if self.surface:
            self._log.debug(u"Toggling mls surface display...")
            if not self.mls_surface:
                self._log.debug(u"Creating mls surface...")
                self.mls_surface = render.attachNewNode(self.surface.get_mls_interpolated_surface(self.surface_subdivisions))
            if self.surface_mls_surface:
                self._log.debug(u"mls surface is now visible.")
                self.mls_surface.show()
            else:
                self._log.debug(u"mls surface is now hidden.")
                self.mls_surface.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create mls surface...")

    def _toggle_bezier_surface(self):
        if self.surface:
            self._log.debug(u"Toggling bezier surface display...")
            if not self.bezier_surface:
                self._log.debug(u"Creating bezier surface...")
                self.bezier_surface = render.attachNewNode(self.surface.get_bezier_interpolated_surface(self.surface_subdivisions, self.bezier_factor))
            if self.surface_bezier_surface:
                self._log.debug(u"bezier surface is now visible.")
                self.bezier_surface.show()
            else:
                self._log.debug(u"bezier surface is now hidden.")
                self.bezier_surface.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create bezier surface...")

    def _toggle_point_cloud(self):
        if self.surface:
            self._log.debug(u"Toggling point cloud display...")
            if not self.point_cloud:
                self._log.debug(u"Creating point_cloud...")
                self.point_cloud = render.attachNewNode(self.surface.get_original_point_cloud())
            if self.surface_point_cloud:
                self._log.debug(u"point cloud is now visible.")
                self.point_cloud.show()
            else:
                self._log.debug(u"point cloud is now hidden.")
                self.point_cloud.hide()
        else:
            self._log.debug(u"No surface loaded, cannot create point cloud...")

app = BaseApp()
run()
