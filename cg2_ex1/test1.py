from Tkinter import *
from cg2kit import *

class TestOptionFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master, 
                borderwidth=1,
                relief=GROOVE)
        self._label = Label(self, text="Test 1")
        self._label.grid(row=0)

option_frames = [TestOptionFrame, ]
Sphere()
