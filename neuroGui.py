#!/usr/bin/env python

# Neurofeedback GUI

import wx
import manager

# As of now, it does nothing at all

class NeuroTrainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(NeuroTrainFrame, self).__init__(parent, title=title, size=(250, 200))
        self.create_objects()
        self.do_layout()
        self.Show()

    def create_objects(self):
        """Creates and instantiates all the objects that will be referenced
        multiple times in the GUI
        """
        self._manager = 
    

if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
