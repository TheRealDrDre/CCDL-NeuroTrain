#!/usr/bin/env python

import wx
import wx.lib.agw.peakmeter as pm
import numpy as np
import scipy as sp
import scipy.signal as sig
import core.ccdl as ccdl
import core.variables 
import gui
import threading
import time

class SingleChannelVisualizer( gui.ManagerPanel ):
    def __init__(self, parent, manager, size=(50, 25)):
        # Parameters for periodogram.
        self.length = 8       # Length of the time series to analyze
        self.window = 1       # Moving window for periodogram
        self.overlap = 0.5    # Overlap between moving windows in periodogram
        self.sampling = 128   # Internal sampling rate (fixed, for now)
        
        self.sensor_data =  np.zeros((0, len(core.variables.CHANNELS)),
                                      order="C", dtype=np.double)
        
        self._visualizing = False    # Whether the peakmeter is being updated
        #self.connected = False      # Whether the headset is connected
        self.update = 0.5           # Interval at which the PeakMeter is updated
        
        gui.ManagerPanel.__init__(self, parent, manager,
                                  manager_state=True,
                                  monitored_events=(ccdl.HEADSET_FOUND_EVENT,))
        self.manager.add_listener(ccdl.SAMPLING_EVENT, self.save_sensor_data)
        
        self.channel = 1  # Starts with first real channel
        
    @property
    def visualizing(self):
        return self._visualizing
    
    @visualizing.setter
    def visualizing(self, value):
        self._visualizing = value
        self.update_interface()
        
        
    def create_objects(self):
        """Creates the GUI objects"""
        meter = pm.PeakMeterCtrl(self, wx.ID_ANY, style=wx.SIMPLE_BORDER,
                                      agwStyle=pm.PM_VERTICAL) #, size=(400, 100))
        meter.SetMeterBands(32, 20)  # Visualize from 1 to 32 Hz
        meter.SetRangeValue(3.0, 6.0, 9.0)
        meter.ShowGrid(True)
        meter.SetBandsColour(wx.Colour(255,0,0), wx.Colour(255, 153, 0), wx.Colour(255,255,0))
        
        meter.SetData([0]*32, offset=0, size=32)
        self.meter = meter
        
        sensors = [core.variables.SENSOR_NAMES[i] for i in core.variables.SENSORS]
        selector = wx.RadioBox(self, wx.ID_ANY, "Select Channel", wx.DefaultPosition,
                               wx.DefaultSize, sensors, 7)
        self.selector = selector
        self.Bind(wx.EVT_RADIOBOX, self.on_select_channel, self.selector)
        
        self.start_btn = wx.Button(self, wx.ID_ANY, "Start", size=(100, 25))
        self.stop_btn = wx.Button(self, wx.ID_ANY, "Stop", size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.on_start, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_btn)
        
        
    def on_start(self, evt):
        """Starts the visualizing thread"""
        self.visualizing = True
        visThread = threading.Thread(group=None, target=self.update_meter)
        visThread.start()
        self.update_interface() 
    
    def on_stop(self, evt):
        """Stops the thread"""
        self.visualizing = False
        
        
    def update_meter(self):
        """Updates the PeakMeter data every UPDATE secs"""
        while self.visualizing:
            self.analyze_data()
            time.sleep(self.update)
    
    def refresh(self, args):
        """Just a shortcut for update_interface"""
        self.update_interface()
    
    def update_interface(self):
        """Updates the interface"""
        if self.manager.has_user :  # 'or True' for testing purposes
            self.selector.Enable()
 
            if self.visualizing:
                self.start_btn.Disable()
                self.stop_btn.Enable()
                self.meter.Enable()
                self.meter.SetBandsColour(wx.Colour(255,0,0),
                                          wx.Colour(255, 153, 0),
                                          wx.Colour(255,255,0))
            else:
                self.meter.SetBandsColour(wx.Colour(100,100,100),
                                          wx.Colour(100,100,100),
                                          wx.Colour(100,100,100))

                self.start_btn.Enable()
                self.stop_btn.Disable()
                self.meter.Disable()
        else:
            self.selector.Disable()
            self.start_btn.Disable()
            self.stop_btn.Disable()
            self.meter.Disable()
            self.meter.SetBandsColour(wx.Colour(100,100,100),
                                      wx.Colour(100,100,100),
                                      wx.Colour(100,100,100))

    
        
    def do_layout(self):
        """Lays out the components"""
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.start_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        box1.Add(self.stop_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add(self.selector, 0, wx.EXPAND | wx.HORIZONTAL)
        box2.Add(box1)
        box2.Add(self.meter, 1, wx.EXPAND | wx.HORIZONTAL)
        self.SetSizerAndFit(box2)
        self.update_interface()


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
                
    
    def on_select_channel(self, evt):
        """Updates the selected channel"""
        box_id = self.selector.GetSelection()
        sensor_id = core.variables.SENSORS[box_id]
        channel_id = core.variables.CHANNELS.index(sensor_id)
        self.channel = channel_id
    
    
    def analyze_data(self):
        """Creates the periodogram of a series"""
        sr = self.sampling
        if self.sensor_data.shape[0] >= sr * self.length:
            nperseg = self.window * sr
            noverlap = int(self.overlap * float(sr))
            freq, density = sig.welch(self.sensor_data[:, self.channel], fs=sr, nperseg = nperseg,
                                      noverlap = noverlap, scaling='density')

            density = sp.log(density)[1:]
            freq = freq[1:]
            self.meter.SetData(density[0:32], offset=0, size=32)
        

