#!/usr/bin/python
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is the Python Computer Graphics Kit.
#
# The Initial Developer of the Original Code is Matthias Baas.
# Portions created by the Initial Developer are Copyright (C) 2004
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****
# $Id: viewer.py,v 1.13 2006/03/03 09:13:59 mbaas Exp $

"""Viewer tool.

Global options:

background     Background color (must be anything that can be passed to the
               vec4 constructor).
fullscreen     Boolean indicating if a full screen view should be used
stereo         Stereo setting (None, "vsplit", "glstereo")
eyedistance    Eye distance for stereo display
polygonmode    Drawing mode ("fill", "line", "point")
navigationmode Selects the navigation mode ("maya", "max", "softimage")
resolution     (width, height)  (aspect is ignored)
fps            Framerate
camera         Specify camera to be used
"""

import sys
import os
import os.path
import logging
from optparse import OptionParser
from ConfigParser import SafeConfigParser

#sys.path = [r"D:\tmp\pygame_src\pygame-1.6.2\build\lib.win32-2.3"]+sys.path
import pygame
from pygame.locals import *
from cgkit._OpenGL.GL import *
#from cgkit._OpenGL.GLU import *
import cgkit._Image as Image

from math import *
from cg2kit import *
from cgkit.scene import getScene
import cgkit
from cgkit.cmds import *
from cgkit.tool import Tool
from cgkit.Interfaces import *

import cgkit.wintab
from cgkit.wintab.constants import *
import cgkit.spacedevice

from Tkinter import *
from tk_global_frame import GlobalOptionsFrame


# Viewer
class Viewer(object):
    """Viewer tool."""
    
    def __init__(self):
        self._init_log()
        self._init_config(['cg2_defaults.conf'])
        self._init_modules()
        self._init_input()
        self._init_tk()
        self._init_gl()
        #self._init_camera()

    def _init_log(self):
        logging.basicConfig(level=logging.DEBUG)
        self._log = logging.getLogger("Application")
        self._log.info(u"Starting up...")
    
    def _init_config(self, default_config_files):
        self._log.info(u"Initializing configuration...")
        config_files = list(default_config_files)
        
        parser = OptionParser()
        parser.add_option('-c', '--conf', dest='config_file', default=None, help=u"config file to use (besides cg1_defaults.conf)")
        (options, args) = parser.parse_args()
        
        if options.config_file:
            config_files.append(options.config_file)
        
        self._log.info(u"Reading config files %s...", config_files)
        self._config = SafeConfigParser()
        self._config.read(config_files)

        #scene = getScene()
        #scene.setGlobal("stereo", self.options.stereo)
        #scene.setGlobal("polygonmode", self.options.polygon_mode)
        #scene.setGlobal("navigationmode", self.options.navigation_mode)
        #self.separate_specular_color = False
        #self.draw_orientation = True

        self._modules = args
        
        sys.setrecursionlimit(4000)
        self._log.info(u"Recursion limit is now %d." % sys.getrecursionlimit())

    def _init_modules(self):
        self._log.info(u"Initializing modules...")
        self._scene_globals = {'scene' : cgkit.scene.getScene()}
        for filename in self._modules:
            execfile(filename, self._scene_globals)
        self.tk_option_frame_classes = list(self._scene_globals['option_frames'])

    def _init_input(self):
        self._log.info(u"Initializing input...")
        self.keydict = {
              8  : KEY_BACK,
              9  : KEY_TAB,
             13 : KEY_RETURN,
             27 : KEY_ESCAPE,
             32 : KEY_SPACE,
            276 : KEY_LEFT,
            273 : KEY_UP,
            275 : KEY_RIGHT,
            274 : KEY_DOWN,
            301 : KEY_CAPSLOCK,
            304 : KEY_SHIFT_LEFT,
            303 : KEY_SHIFT_RIGHT,
            306 : KEY_CONTROL_LEFT,
            305 : KEY_CONTROL_RIGHT,
            308 : KEY_ALT_LEFT,
            307 : KEY_ALT_RIGHT,
            310 : KEY_WINDOWS_LEFT,
            309 : KEY_WINDOWS_RIGHT,
            319 : KEY_WINDOWS_MENU,
            317 : KEY_PRINT,
            302 : KEY_SCROLL,
             19 : KEY_PAUSE,
            277 : KEY_INSERT,
            127 : KEY_DELETE,
            278 : KEY_HOME,
            279 : KEY_END,
            280 : KEY_PRIOR,
            281 : KEY_NEXT,
            282 : KEY_F1,
            283 : KEY_F2,
            284 : KEY_F3,
            285 : KEY_F4,
            286 : KEY_F5,
            287 : KEY_F6,
            288 : KEY_F7,
            289 : KEY_F8,
            290 : KEY_F9,
            291 : KEY_F10,
            292 : KEY_F11,
            293 : KEY_F12,
            300 : KEY_NUMLOCK,
            256 : KEY_NUMPAD0,
            257 : KEY_NUMPAD1,
            258 : KEY_NUMPAD2,
            259 : KEY_NUMPAD3,
            260 : KEY_NUMPAD4,
            261 : KEY_NUMPAD5,
            262 : KEY_NUMPAD6,
            263 : KEY_NUMPAD7,
            264 : KEY_NUMPAD8,
            265 : KEY_NUMPAD9,
            266 : KEY_NUMPAD_DECIMAL,
            267 : KEY_NUMPAD_DIVIDE,
            268 : KEY_NUMPAD_MULTIPLY,
            269 : KEY_NUMPAD_SUBTRACT,
            270 : KEY_NUMPAD_ADD,
            271 : KEY_NUMPAD_ENTER
            }

    def _init_tk(self):
        self._log.info(u"Initializing tk widgets...")
        self.tk_root = Tk()
        self.tk_option_frames = []
        self.tk_run_button = Button(self.tk_root, text="Run", command=self.run_gl)
        self.tk_run_button.grid(row=0, column=0, sticky=W+E)
        self.tk_option_frame_classes = [GlobalOptionsFrame, ] + getattr(self, 'tk_option_frame_classes', [])
        for index, option_frame_class in enumerate(self.tk_option_frame_classes):
            option_frame = option_frame_class(self.tk_root)
            option_frame.grid(row=index+1, column=0, sticky=W+E)
            self.tk_option_frames.append(option_frame)

    def _init_gl(self):
        self._log.info(u"Initializing opengl renderer...")
        passed, failed = pygame.init()
        if failed>0:
            self._log.error(u"Warning: %d pygame modules couldn't be initialized" % failed)
        self.gl_renderer = GLRenderInstance()

    def _init_camera(self):
        scene = getScene()

        if self._config.has_option('scene', 'camera'):
            cname = self._config.get('scene', 'camera')
        else:
            cname = None
        
        # Search for a camera...
        cam = None
        for obj in scene.walkWorld():
            prots = obj.protocols()
            if ICamera in prots:
                if obj.name==cname or cname==None :
                    cam = obj
                    break

        if cname!=None and cam==None:
            raise ValueError, 'Camera "%s" not found.' % cname

        # No camera? Then create a default camera...
        if cam==None:
            self._log.info(u"No camera set, using a default camera.")
            bbmin, bbmax = scene.boundingBox().getBounds()
            dif = bbmax-bbmin
            b1 = scene.up.ortho()
            b2 = scene.up.cross(b1)
            pos = dif.length()*(0.5*b1+b2) + (bbmax.z+0.5*dif.z)*scene.up
            if abs(dif.z)<0.0001:
                pos += 0.8*dif.length()*scene.up
            cam = TargetCamera(pos = pos,
                               target = 0.5*(bbmin+bbmax)-0.2*(dif.z*scene.up),
                               fov = 50)
        else:
            self._log.info(u"Camera: %s" % cam.name)

        self._camera = cam

    def run(self):
        self.tk_root.mainloop()

    def run_gl(self):
        # Create a camera control component
        self._init_camera()
        CameraControl(cam=self._camera, mode=1)

        # Get options...
        width = self._config.getint('window', 'width')
        height = self._config.getint('window', 'height')

        # Open a window...
        pygame.display.set_caption("OpenGL viewer")
        flags = OPENGL | DOUBLEBUF
        self.gl_surface = pygame.display.set_mode((width,height), flags)

        # Try to get the native window handle
        # (this only works with pygame 1.6.2 and later)
        try:
            info = pygame.display.get_wm_info()
            hwnd = info["window"]
        except:
            hwnd = None

        # Event loop...
        self._running = True
        self._timer = getScene().timer()
        self._clock = pygame.time.Clock()
        self._cnt = 0
        self._timer.startClock()
        self._fps = self._config.getint('general', 'framerate')

        self.tk_root.after(50, self._loop_once, width, height)
        self._log.info(u"3d visualization running...")
    
    def stop_gl(self):
        self._running = False

    def _loop_once(self, width, height):
        if self._running:
            self.tk_root.after(1000/self._fps, self._loop_once, width, height)

            # Display the scene
            self.draw(self._camera, width, height)
            pygame.display.flip()

            # Handle events
            events = pygame.event.get()
            self.handleEvents(events)

            self._timer.step()

            # Sync
            self._clock.tick(1000/self._fps)

    # handleEvents
    def handleEvents(self, events):
        eventmanager = eventManager()
        width = self._config.getint('window', 'width')
        height = self._config.getint('window', 'height')
        for e in events:
            if e.type==QUIT:
                self._running=False
            # KEYDOWN?
            elif e.type==KEYDOWN:
                if e.key==27:
                    self._running=False
                key = e.unicode
                code = self.keydict.get(e.key, e.key)
                mods = self.convertMods(e.mod)
                eventmanager.event(KEY_PRESS, KeyEvent(key, code, mods))
#                keyboard.setKeyValue(e.key, True)
            # KEYUP
            elif e.type==KEYUP:
                code = self.keydict.get(e.key, e.key)
                try:
                    key = unicode(chr(e.key))
                except:
                    key = u""
                mods = self.convertMods(e.mod)
                eventmanager.event(KEY_RELEASE, KeyEvent(key, code, mods))
#                keyboard.setKeyValue(e.key, False)
            # MOUSEBUTTONDOWN
            elif e.type==MOUSEBUTTONDOWN:
                x,y = e.pos
                x0 = float(x)/width
                y0 = float(y)/height
                if e.button==1:
                    eventname = LEFT_DOWN
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==2:
                    eventname = MIDDLE_DOWN
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==3:
                    eventname = RIGHT_DOWN
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==4:
                    eventname = MOUSE_WHEEL
                    evt = MouseWheelEvent(120, x, y, x0, y0)
                elif e.button==5:
                    eventname = MOUSE_WHEEL
                    evt = MouseWheelEvent(-120, x, y, x0, y0)
                else:
                    eventname = MOUSE_BUTTON_DOWN
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                eventmanager.event(eventname, evt)
            # MOUSEBUTTONUP
            elif e.type==MOUSEBUTTONUP:
                x,y = e.pos
                x0 = float(x)/width
                y0 = float(y)/height
                if e.button==1:
                    eventname = LEFT_UP
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==2:
                    eventname = MIDDLE_UP
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==3:
                    eventname = RIGHT_UP
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                elif e.button==4:
                    eventname = MOUSE_WHEEL
                    evt = MouseWheelEvent(120, x, y, x0, y0)
                elif e.button==5:
                    eventname = MOUSE_WHEEL
                    evt = MouseWheelEvent(-120, x, y, x0, y0)
                else:
                    eventname = MOUSE_BUTTON_UP
                    evt = MouseButtonEvent(e.button, x, y, x0, y0)
                eventmanager.event(eventname, evt)
            # MOUSEMOTION
            elif e.type==MOUSEMOTION:
                btns = 0
                b1,b2,b3 = e.buttons
                if b1:
                    btns |= 0x1
                if b2:
                    btns |= 0x2
                if b3:
                    btns |= 0x4                
                x,y = e.pos
                dx, dy = e.rel
                x0 = float(x)/width
                y0 = float(y)/height
                dx0 = float(dx)/width
                dy0 = float(dy)/height
                evt = MouseMoveEvent(x, y, dx, dy, x0, y0, dx0, dy0, btns)
                eventmanager.event(MOUSE_MOVE, evt)
            # SYSWMEVENT
            elif e.type==SYSWMEVENT:
                if sys.platform=="win32" and not hasattr(e, "msg") and not pygame.event.get_blocked(SYSWMEVENT):
                    pygame.event.set_blocked(SYSWMEVENT)
                    print "Warning: This version of pygame does not allow processing system events."
                
    def setOptions(self, optparser):
        """Add options specific to this tool."""
        
        Tool.setOptions(self, optparser)
        optparser.add_option("-F", "--full-screen", action="store_true", default=False,
                             help="Full screen display")
        optparser.add_option("-S", "--stereo", metavar="MODE",
                             help="Activate stereo display (vsplit, glstereo)")
        optparser.add_option("-D", "--eye-distance", type="float", default=0.07,
                             help="Default eye distance for stereo display. Default: 0.07")
        optparser.add_option("-B", "--bounding-box", action="store_true", default=False,
                             help="Show bounding boxes")
        optparser.add_option("-P", "--polygon-mode", metavar="MODE",
                             help="Polygon mode (fill, line, point). Default: fill")
        optparser.add_option("-s", "--save", metavar="NAME",
                             help="Save screenshots as images.")
        optparser.add_option("-N", "--navigation-mode", metavar="MODE",
                             help="Navigation mode (MAX, Maya, Softimage). Default: Maya")
        optparser.add_option("-X", "--disable-spacedevice", action="store_true", default=False,
                             help="Disable SpaceMouse/SpaceBall.")
        optparser.add_option("-T", "--disable-wintab", action="store_true", default=False,
                             help="Disable tablet support.")
        
    def convertMods(self, mods):
        """Convert pygame key modifier flags to cgkit modifier flags.
        """
        res = 0
        if mods & 0x0001 or mods & 0x0002:
            res |= KEYMOD_SHIFT
        if mods & 0x0040 or mods & 0x0080:
            res |= KEYMOD_CONTROL
        if mods & 0x0100 or mods & 0x0200:
            res |= KEYMOD_ALT
        return res

    def draw(self, cam, width, height):
        scene = getScene()
        renderer = self.gl_renderer

        # Set handedness
        renderer.left_handed = scene.handedness=="l"
        renderer.setViewport(0,0,width,height)

        renderer.draw_solid = True
        #renderer.draw_bboxes = self.options.bounding_box
        renderer.draw_coordsys = False
        #renderer.draw_orientation = self.draw_orientation
        renderer.smooth_model = True
        renderer.backface_culling = False
        #renderer.separate_specular_color = self.separate_specular_color
        #renderer.polygon_mode = self.polygon_mode  # 0=Point 1=Line 2=Fill
        #renderer.stereo_mode = self.stereo_mode
        renderer.clearcol = vec4(scene.getGlobal("background", vec4(0.5,0.5,0.6,0)))

        # Set projection matrix
        near, far = cam.getNearFar()
        P = cam.projection(width,height,near,far)
        renderer.setProjection(P)

        # Set view matrix
        renderer.setViewTransformation(cam.viewTransformation(), 0)

        # Draw scene
        root = scene.worldRoot()
        renderer.paint(root)

    # saveScreenshot
    def saveScreenshot(self, srf):
        """Save the current window content.

        srf is the pygame Surface object.
        """
        name,ext = os.path.splitext(self.options.save)
        f = int(round(getScene().timer().frame))
        fname = "%s%04d%s"%(name, f, ext)
        print 'Saving "%s"...'%fname
        data = pygame.image.tostring(srf, "RGB")
        img = Image.fromstring("RGB", (srf.get_width(), srf.get_height()), data)
        img.save(fname)

    # setOptionsFromGlobals
    def setOptionsFromGlobals(self):
        Tool.setOptionsFromGlobals(self)

        scene = getScene()
        self.options.full_screen = scene.getGlobal("fullscreen", self.options.full_screen)

        self.options.eye_distance = float(scene.getGlobal("eyedistance", self.options.eye_distance))

        # Check the stereo option and initialize the variable "stereo_mode"
        Sopt = scene.getGlobal("stereo", None)
        self.stereo_mode = self.translateKeyWordOpt(Sopt,
                                { None:0, "vsplit":1, "glstereo":2 },
                                "Unknown stereo mode: '%s'")

        # Check the polygon mode option
        Popt = scene.getGlobal("polygonmode", "fill")
        self.polygon_mode = self.translateKeyWordOpt(Popt,
                                { None:2, "point":0, "line":1, "fill":2 },
                                "Unknown polygon mode: '%s'")

        # Check the navigationmode option
        Nopt = scene.getGlobal("navigationmode", "maya")
        self.navigation_mode = self.translateKeyWordOpt(Nopt,
                            { None:1, "max":0, "maya":1, "softimage":2 },
                            "Unknown navigation mode: '%s'")

        
        
        

######################################################################

if __name__=="__main__":
    viewer = Viewer()
    viewer.run()


