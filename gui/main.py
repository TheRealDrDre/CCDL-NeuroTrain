#!/usr/bin/env python

## --------------------------------------------------------------- ##
## MAIN.py 
## --------------------------------------------------------------- ##
## Defines the main window of the application.
## --------------------------------------------------------------- ##

import wx
import core.ccdl as ccdl
import core.variables as variables
from ctypes import *
from .gui import *
from .recording import TimedSessionRecorder
from core.manager import EmotivManager, ManagerWrapper

class NeuroTrainFrame(wx.Frame):
    """The main frame"""
    
    def __init__(self, parent, title):
        """Inits the frame"""
        wx.Frame.__init__(self, parent, title=title, size=(250, 200))
        self.create_objects()
        self.do_layout()
        self.Fit()
        self.Show()

    def create_objects(self):
        """Creates and instantiates all the objects that will be referenced
        multiple times in the GUI
        """
        self.manager = EmotivManager()
        self.connect_panel = ConnectPanel(self, self.manager)
        self.user_panel = UserPanel(self, self.manager)
        self.rec_panel = TimedSessionRecorder(self, self.manager)
        
        
    def do_layout(self):
        """Lays out the interface"""
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.user_panel)
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.connect_panel, 1, wx.HORIZONTAL|wx.EXPAND, 0)
        box.Add(hbox, 1, wx.ALL | wx.EXPAND, 0)
        
        metabox = wx.BoxSizer(wx.HORIZONTAL)
        metabox.Add(box, wx.ALIGN_CENTER, 10)
        
        metabox.Add(self.rec_panel, wx.ALIGN_CENTER, 10)
        
        self.SetSizer(metabox)
        
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        
    def on_quit(self, event):
        """Sets all the variables that control the threads to false
        before quitting"""
        self.manager.monitoring = False
        self.manager.has_user = False
        self.manager.sampling = False
        self.Destroy()