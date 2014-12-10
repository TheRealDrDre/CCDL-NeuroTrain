#!/usr/bin/env python

import wx
import wx.lib.agw.peakmeter as pm
import numpy as np
import scipy as sp
import scipy.signal as sig
import core.ccdl as ccdl
import core.variables 
import gui

class SingleChannelVisualizer( gui.ManagerPanel ):
    def __init__(self, parent, manager, size=(50, 25)):
        # Parameters for periodogram.
        self.length = 2
        self.window = 1
        self.overlap = 0.5
        self.sampling = 128
        self.sensor_data =  np.zeros((0, len(core.variables.CHANNELS)),
                                      order="C", dtype=np.double)
        self.recording = False
        self.connected = False
        
        # parameters for visualization
        self.update = 1
        gui.ManagerPanel.__init__(self, parent, manager,
                                  manager_state=True,
                                  monitored_events=(ccdl.HEADSET_FOUND_EVENT,))
        self.manager.add_listener(ccdl.SAMPLING_EVENT, self.save_sensor_data)
        
        self.channel = 1  # Starts with first real channel
        
        
    def create_objects(self):
        meter = pm.PeakMeterCtrl(self, wx.ID_ANY, style=wx.SIMPLE_BORDER,
                                      agwStyle=pm.PM_VERTICAL) #, size=(400, 100))
        meter.SetMeterBands(self.sampling / 4, 20)
        meter.SetRangeValue(3.0, 6.0, 9.0)
        meter.ShowGrid(True)
        meter.SetBandsColour(wx.Colour(255,0,0), wx.Colour(255, 153, 0), wx.Colour(255,255,0))
        #data = np.ones((1, 32))
        #data = data/4.0
        
        meter.SetData([0]*32, offset=0, size=32)
        self.meter = meter
        
        sensors = [core.variables.SENSOR_NAMES[i] for i in core.variables.SENSORS]
        selector = wx.RadioBox(self, wx.ID_ANY, "Select Channel", wx.DefaultPosition,
                               wx.DefaultSize, sensors, 7)
        self.selector = selector
        self.Bind(wx.EVT_RADIOBOX, self.on_select_channel, self.selector)
        
        
    def update_interface(self):
        """Updates the interface"""
        pass
    
        
    def do_layout(self):
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add(self.selector, 1, wx.EXPAND | wx.HORIZONTAL)
        box1.Add(self.meter, 1, wx.EXPAND | wx.HORIZONTAL)
        self.SetSizerAndFit(box1)

    def save_sensor_data(self, data):
        """
        Accumulates recorded data into an array. If the array exceeds
        the specified self.length, only the last (length * sampling)
        samples are kept.
        """
        self.sensor_data = np.vstack( (self.sensor_data, data) )
        n_samples, n_channels = self.sensor_data.shape
        max_length = self.length * self.sampling
        
        if n_samples > max_length:
            self.sensor_data = self.sensor_data[n_samples - max_length:,]
            
        if self.sensor_data.shape[0] == max_length:
            self.analyze_data()
    
    def on_select_channel(self, evt):
        """Updates the selected channel"""
        box_id = self.selector.GetSelection()
        sensor_id = core.variables.SENSORS[box_id]
        channel_id = core.variables.CHANNELS.index(sensor_id)
        print channel_id
        self.channel = channel_id
    
    def analyze_data(self):
        """Creates the periodogram of a series"""
        if self.sensor_data.shape[0] >= 256:
            sr = self.sampling
            nperseg = self.window * sr
            noverlap = int(self.overlap * float(sr))
            #print("Rate %s, NPerSeg %s, NOverlap %s, Shape %s" % (sr, nperseg, noverlap, self.sensor_data.shape))
            
            freq, density = sig.welch(self.sensor_data[:, self.channel], fs=sr, nperseg = nperseg,
                                      noverlap = noverlap, scaling='density')

            density = sp.log(density)[1:]
            freq = freq[1:]
            self.meter.SetData(density[0:32], offset=0, size=32)
        

