#!/usr/bin/env python

## New Sensor Panel

import wx
import core.ccdl as ccdl
from core.variables import *


class SensorPanel2(wx.Panel):
    """A small widget that displays the state of a sensor"""
    BACKGROUNDS  = {-1: wx.Colour(125, 125, 125),  # grey
                    0 : wx.Colour(0,0,0),       # Black
                    1 : wx.Colour(255,0,0),     # Red
                    2 : wx.Colour(255, 153, 9), # Orange
                    3 : wx.Colour(255, 255, 0), # Yellow
                    4 : wx.Colour(0,255,0)}     # Green
    
    FOREGROUNDS = {-1: wx.Colour(25, 25, 25),   # dark grey
                   0 : wx.Colour(255,255,255),  # White
                   1 : wx.Colour(255,255,255),  # White
                   2 : wx.Colour(0, 0, 0),      # Black 
                   3 : wx.Colour(0, 0, 0),      # Black
                   4 : wx.Colour(255,255,255)} # White
    
    def __init__(self, parent, sensor_id=0, size=(50, 25)):
        wx.Panel.__init__(self, parent, -1,
                          style=wx.NO_FULL_REPAINT_ON_RESIZE,
                          size=size)
        
        self._sensor_id = sensor_id

        if sensor_id in COMPLETE_SENSORS:
            self._sensor_name = SENSOR_NAMES[sensor_id]
        else:
            self._sensor_name = "???"

        self._sensor_enabled = False
        self._quality = -1 ## Recording quality
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetTransparent(True)
        
    @property
    def sensor_id(self):
        return self._sensor_id
    
    @sensor_id.setter
    def sensor_id(self, id):
        self._sensor_id = id
        self._sensor_name = SENSOR_NAMES[id]
    
    @property
    def sensor_name(self):
        """Returns the sensor name"""
        return self._sensor_name
    
    @sensor_name.setter
    def sensor_name(self, name):
        """Sets the sensor name (nothing else)"""
        self._sensor_name = name
        
    @property
    def sensor_enabled(self):
        """Returns whether the sensor is enabled or not"""
        return self._sensor_enabled
    
    @sensor_enabled.setter
    def sensor_enabled(self, bool):
        """Sets the state of the sensor (enabled or not), and changes
        the state of the GUI components accordingly
        """
        if bool:
            self._checkbox.Enable()
        else:
            self._checkbox.Disable()
        self._sensor_enabled = bool     
    
    
    @property
    def quality(self):
        return self._quality
    
    @quality.setter
    def quality(self, val):
        if (self._quality != val):
            self._quality = val
            self.Refresh()
            print "%s, %d" % (self.sensor_name, self.quality)
                
                
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetFont(self.GetFont())
        w, h = self.GetSize()
        radius = min(w, h)/2
        
        if self.Enabled:
            fg = SensorPanel2.FOREGROUNDS[self.quality]
            bg = SensorPanel2.BACKGROUNDS[self.quality]
        else:
            fg = SensorPanel2.FOREGROUNDS[-1]
            bg = SensorPanel2.BACKGROUNDS[-1]
            
        dc.SetPen(wx.Pen(bg)) 
        dc.SetBrush(wx.Brush(bg))
        dc.DrawCircle(w/2, h/2, radius)
        
        textWidth, textHeight = dc.GetTextExtent( self.sensor_name )
        textX = (w - textWidth) / 2
        textY = (h - textHeight) / 2
        #dc.SetPen(wx.Pen(fg))
        #dc.SetBrush(wx.Brush(fg))
        dc.SetTextForeground(fg)
        dc.DrawText(self.sensor_name, textX, textY)
    
    def OnSize(self, event):
        self.Refresh()

