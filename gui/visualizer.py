#!/usr/bin/env python


import wx
import core.ccdl as ccdl
from core.variables import *

class SingleChannelVisualizer( wx.Panel ):
    def __init__(self, parent, sensor_id=0, size=(50, 25)):
        wx.Panel.__init__(self, parent, -1,
                          style=wx.NO_FULL_REPAINT_ON_RESIZE,
                          size=size)

class MultiChannelVisualizer(wx.Panel):
    pass

