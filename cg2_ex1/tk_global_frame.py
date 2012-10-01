from Tkinter import *

from cg2kit import *

class GlobalOptionsFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master,
                borderwidth=1,
                relief=GROOVE)
        self._tk_title = Label(self, text="Global Options", width=30)
        self._tk_title.grid(row=0, sticky=W)
        self._button_clear = Button(self, text="Clear Scene", command=self._clear_scene)
        self._button_clear.grid(row=1, sticky=E+W)

    def _clear_scene(self):
        getScene().clear()
