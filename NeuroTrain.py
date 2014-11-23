#!/usr/bin/env python

import gui.main as m
import wx


# Just loads the libraries and starts the Windowing App
if __name__ == '__main__':
    app = wx.App()
    frame = m.NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
