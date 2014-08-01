#!/usr/bin/env python

# Neurofeedback GUI

import wx
from manager import EmotivManager

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
        self._manager = EmotivManager()
    
    def do_layout(self):
        """Lays out the components"""
        edk_connect_btn = wx.Button(self, 10, "Connect to the Headset", (20, 20))
        self.Bind(wx.EVT_BUTTON, self.on_connect, edk_connect_btn)
        edk_connect_btn.SetDefault()
        edk_connect_btn.SetSize(edk_connect_btn.GetBestSize())
        
        edk_disconnect_btn = wx.Button(self, 10, "Disconnect from Headset", (20, 20))
        self.Bind(wx.EVT_BUTTON, self.on_connect, edk_disconnect_btn)
        edk_disconnect_btn.SetSize(edk_connect_btn.GetBestSize())

    def on_connect(self, event):
        """Handles the connection events"""
        pass

if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
