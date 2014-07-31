#!/usr/bin/env python

# Neurofeedback GUI

import wx

# As of now, it does nothing at all

class NeuroTrainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(NeuroTrainFrame, self).__init__(parent, title=title, size=(250, 200))
        self.Show()

if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
