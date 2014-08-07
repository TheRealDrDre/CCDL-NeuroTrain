#!/usr/bin/env python

import gui.gui as gui
import wx

if __name__ == '__main__':
    app = wx.App()
    frame = gui.NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
