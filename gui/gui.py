#!/usr/bin/env python

# Neurofeedback GUI

import wx
import core.ccdl as ccdl
import copy
import traceback
import core.variables as variables
from ctypes import *
from core.variables import *
from core.manager import EmotivManager, ManagerWrapper

__all__ = ["ManagerPanel", "ConnectPanel", "UserPanel"]

SENSOR_POSITIONS = {ED_CMS : (37, 233), ED_DRL : (274, 233),
                    ED_AF3 : (85, 62), ED_F7 : (37, 113), ED_F3 : (118, 109),
                    ED_FC5 : (67, 146), ED_T7 : (19, 190), ED_P7 : (70, 287),
                    ED_O1 : (114, 336), ED_O2 : (196, 336), ED_P8 : (241, 287),
                    ED_T8 : (291, 190), ED_FC6 : (243, 146), ED_F4 : (192, 109),
                    ED_F8 : (274, 113), ED_AF4 : (224, 62)}

class ManagerPanel(wx.Panel, ManagerWrapper):
    """A subclass for all panels that wraps around an Emotiv Manager"""
    def __init__(self, parent, manager, monitored_events=(),
                 manager_state=None):
        wx.Panel.__init__(self, parent, -1,
                         style=wx.NO_FULL_REPAINT_ON_RESIZE)
        ManagerWrapper.__init__(self, manager,
                                monitored_events=monitored_events)
        self._manager_state = manager_state # A variable to store the previous state
        self.create_objects()
        self.do_layout()
        self.refresh(None)    
    
    @property
    def manager_state(self):
        return self._manager_state
    
    @manager_state.setter
    def manager_state(self, val):
        self._manager_state = val
    
    def create_objects(self):
        """Creates the objects that will be accessed later"""
        pass
    
    def do_layout(self):
        """Lays out the objets into an interface"""
        pass

# CONNECT PANEL
#
# A connect panel manages the connection to EDK through the internal manager.
#
class ConnectPanel(ManagerPanel):
    """A Simple Panel that Connects or Disconnects to an Emotiv System"""
    
    def __init__(self, parent, manager):
        """A ManagerPanel that monitors connection events"""
        ManagerPanel.__init__(self, parent, manager,
                              monitored_events=(ccdl.CONNECTION_EVENT,))
    
    def create_objects(self):
        """Creates the internal objects"""
        self.connect_btn = wx.Button(self, 12, "Connect to the Headset", (20, 20))
        self.disconnect_btn = wx.Button(self, 11, "Disconnect from Headset", (20, 20))
                
        spin = wx.SpinCtrlDouble(self, -1, min=0.05, max=0.5, inc=0.025,
                                 size=(75, 25))
        
        
        text = wx.StaticText(self, -1,
                            "Monitoring Interval (in seconds)",
                            (25, 15))
        
        self.monitor_interval_spn = spin
        self.monitor_interval_lbl = text
        
        self.Bind(wx.EVT_SPINCTRL, self.on_monitor_interval_change,
                  self.monitor_interval_spn)
        self.Bind(wx.EVT_TEXT, self.on_monitor_interval_change,
                  self.monitor_interval_spn)
        

    def on_monitor_interval_change(self, evt):
        """Whenever the monitor's spin control changes,
        Sets a new interval value in the manager"""
        val = float(self.monitor_interval_spn.GetValue())
        self.manager.monitor_interval = val

    
    def do_layout(self):
        """Lays out the components"""
                 
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.connect_btn)
        self.connect_btn.SetDefault()
        self.connect_btn.SetSize(self.connect_btn.GetBestSize())
        
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.disconnect_btn)
        self.disconnect_btn.SetSize(self.connect_btn.GetBestSize())
        
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.monitor_interval_lbl, 0, wx.ALL|wx.LEFT, 5)
        box1.Add(self.monitor_interval_spn, 0, wx.ALL|wx.CENTER, 5)

        box3 = wx.StaticBox(self, -1, "EDK Connection")
        bsizer3 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        bsizer3.Add(self.connect_btn, 0, wx.TOP|wx.LEFT, 5)
        bsizer3.Add(self.disconnect_btn, 0, wx.TOP|wx.LEFT, 5)
        bsizer3.Add(box1, 0, wx.ALL|wx.LEFT, 5)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(bsizer3, 1, wx.EXPAND|wx.ALL, 10)
        
        self.SetSizer(box)

    def refresh(self, arg=None):   # ARG is unused
        """Refreshes the buttons based on the state of the connection"""
        if self.manager is None:
            # If no manager is found, then no button should be pressed.
            self.connect_btn.Disable()
            self.disconnect_btn.Disable()
            
            self.monitor_interval_lbl.Disable()
            self.monitor_interval_spn.Disable()
                        
        else:
            # If we have a manager, then we can should load the interval
            # parameters first
            
            val = self.manager.monitor_interval
            self.monitor_interval_spn.SetValue(val)
            
            # Now we enable/disable buttons based on connection 
            if self.manager.connected:
                # If connected, the only option is Disconnect
                self.connect_btn.Disable()
                self.disconnect_btn.Enable()
                
                # And the parameters cannot be changed
                self.monitor_interval_lbl.Disable()
                self.monitor_interval_spn.Disable()
                    
            else:
                # If disconnected, the only option is Connect
                self.connect_btn.Enable()
                self.disconnect_btn.Disable()
                
                # When disconnected, and only when disconnected,
                # the interval parameters can be changed 
                self.monitor_interval_lbl.Enable()
                self.monitor_interval_spn.Enable()
                

    def on_connect(self, event):
        """Handles the connection events"""
        print "on_connect %s" % event.GetId()
        if (event.GetId() == 12):
            try:
                mngr = self.manager
                mngr.connect()
                
                print mngr.monitoring
                mngr.monitoring = True
                print "...Set"
                print mngr.monitoring
            except Exception as e:
                dlg = wx.MessageDialog(self, "%s" % traceback.format_exc(),
                               'Error While Connecting',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
                dlg.ShowModal()
                dlg.Destroy()
                
        else:
            try:
                self.manager.disconnect()
            except Exception as e:
                dlg = wx.MessageDialog(self, "%s" % e,
                                       'Error While Disconnecting',
                                        wx.OK | wx.ICON_INFORMATION
                                        )
                dlg.ShowModal()
                dlg.Destroy()
                
        self.refresh(None)
            

class SensorPanel(wx.Panel):
    """A small widget that displays the state of a sensor"""
    COLOR_MAP = {0 : wx.Colour(0,0,0),       # Black
                 1 : wx.Colour(255,0,0),     # Red
                 2 : wx.Colour(255, 153, 9), # Orange
                 3 : wx.Colour(255, 255, 0), # Yellow
                 4 : wx.Colour(0,255,0)}     # Green
    
    def __init__(self, parent, sensor_id=0, size=(50, 25)):
        wx.Panel.__init__(self, parent, -1,
                          style=wx.NO_FULL_REPAINT_ON_RESIZE,
                          size=size)
        
        self._sensor_id = sensor_id
        #self.SetAlignment(wx.ALIGN_LEFT)
        if sensor_id in COMPLETE_SENSORS:
            self._sensor_name = SENSOR_NAMES[sensor_id]
        else:
            self._sensor_name = "???"
        self._checkbox = wx.CheckBox(self, -1, self._sensor_name, size=(45,20))
        self._sensor_enabled = False
        self._sensor_recording = False  ## Currently unused
        self._quality = -1 ## Recordin quality
        #self.do_layout()
        
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
        return self_quality
    
    @quality.setter
    def quality(self, val):
        print " **** QUALITY ****"
        if (self._quality != val):
            self._quality = val
            self._checkbox.SetLabel("%s:%d" % (variables.SENSOR_NAMES[self.sensor_id], val))
            self._checkbox.Refresh()
            if val in SensorPanel.COLOR_MAP.keys():
                col = SensorPanel.COLOR_MAP[val]
                self._checkbox.SetForegroundColour(col)
            else:
                self._checkbox.SetForegroundColour(wx.Colour(0,0,255))

class UserPanel(ManagerPanel):
    """A Class that visualizes the user and its sensors"""
    
    def __init__(self, parent, manager):
        ManagerPanel.__init__(self, parent, manager,
                              manager_state=True,
                              monitored_events=(ccdl.USER_EVENT, ccdl.MONITORING_EVENT))
        self.manager.add_listener(ccdl.SENSOR_QUALITY_EVENT, self.update_quality)
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self._sensor_quality = dict(zip(variables.COMPLETE_SENSORS,
                                    [0] * len(variables.COMPLETE_SENSORS)))

        
    def create_objects(self):
        """Creates the objects"""
        ## NEW CODE FROM HEADSET PANEL:
        self._battery_lbl = wx.StaticText(self, -1, "Battery Level:", size=(150, 20))
        self._wireless_lbl = wx.StaticText(self, -1, "Wireless Signal Strength:", size=(150, 20))
        self._sampling_rate_lbl = wx.StaticText(self, -1, "Sampling Rate:", size=(150, 20))
        self._num_channels_lbl = wx.StaticText(self, -1, "Num of Available Channels:", size=(150, 20))
        self._time_lbl = wx.StaticText(self, -1, "Time from start:", size=(150, 20))
        
        # Gauges
        self._battery_gge = wx.Gauge(self, -1, 5, size=(100, 20))
        self._wireless_gge= wx.Gauge(self, -1, 2, size=(100, 20))
        
        # Text info:
        self._sampling_rate_txt = wx.StaticText(self, -1, "128", size=(100, 20))
        self._num_channels_txt = wx.StaticText(self, -1, "18", size=(100, 20))
        self._time_txt = wx.StaticText(self, -1, "0:00", size=(100, 20))
        
        self.all_components = (self._battery_lbl, self._wireless_lbl,
                               self._sampling_rate_lbl, self._time_lbl,
                               self._num_channels_lbl,
                               
                               # Gauges
                               self._battery_gge, self._wireless_gge,
                               
                               # Infotexts
                               self._sampling_rate_txt, self._num_channels_txt,
                               self._time_txt)
        # OLD CODE
        
        img = wx.Image("images/channels.gif", type=wx.BITMAP_TYPE_GIF)
        img = img.ConvertToBitmap()
        self.enabled_img = img
        self.disabled_img = self.enabled_img.ConvertToDisabled(255)
        self._background_bitmap = self.enabled_img

        # Creates the sensor panel
        self.sensor_panel = wx.Panel(self)
        self.sensor_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        
        # Creates the sensors and adds them to the sensor panel
        sensors = [SensorPanel(self.sensor_panel, x) for x in COMPLETE_SENSORS]
        self.sensors = tuple(sensors)
        self.SetSize(img.GetSize())
    
    @property    
    def background_bitmap(self):
        """Returns the background image"""
        return self._background_bitmap
    
    @background_bitmap.setter
    def background_bitmap(self, bmp):
        """Sets a new background images and forces a redraw
        of the sensor sub-panel"""
        if self._background_bitmap is not bmp:
            self._background_bitmap = bmp
            self.sensor_panel.Refresh()
        
    @property
    def sensor_quality(self):
        """An array containing the recording quality of each sensor"""
        return self._sensor_quality
    
    @sensor_quality.setter
    def sensor_quality(self, data):
        """Changes the sensor quality array values"""
        print "Sensory quality setter: %s" % data
        if data != self._sensor_quality:
            self._sensor_quality = data
            
            for sensor in self.sensors:
                sensor.quality = data[sensor[sensor.sensor_id]]
            
            #for sensor in variables.COMPLETE_SENSORS:
            #    name = variables.SENSOR_NAMES[sensor]
            #   print "   %s : %d" % (name, data[sensor])
              
    def update_quality(self, data):
        #print ".... SENSOR QUALITY RECEIVED: %s" % data
        if data != self._sensor_quality:
            self._sensor_quality = data
            
            for sensor in self.sensors:
                sensor.quality = data[sensor.sensor_id]
            
            for sensor in variables.COMPLETE_SENSORS:
                name = variables.SENSOR_NAMES[sensor]
                print "   %s : %d" % (name, data[sensor])
        self.sensory_quality = data

    
    def do_layout(self):
        """Lays out the components"""
        box = wx.StaticBox(self, -1, "Headset")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        #bsizer.Add(self.user_lbl)
        
        for i in self.sensors:
            i.SetPosition(SENSOR_POSITIONS[i.sensor_id])
        
        sizer = wx.BoxSizer(wx.VERTICAL)        
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        
        for label in [self._battery_lbl, self._wireless_lbl,
                      self._sampling_rate_lbl, self._time_lbl,
                      self._num_channels_lbl]:
            sizer1.Add(label, 1, wx.ALL| wx.EXPAND, 1)
            
        for cntrl in [self._battery_gge, self._wireless_gge,
                      self._sampling_rate_txt, self._time_txt,
                      self._num_channels_txt]:
            sizer2.Add(cntrl, 1, wx.ALL| wx.EXPAND, 1)
            
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(sizer1)
        sizer3.Add(sizer2)
        sizer.Add(sizer3)
        sizer.Add(self.sensor_panel)
        bsizer.Add(sizer)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(bsizer, 1, wx.EXPAND|wx.ALL, 10)
        
        self.SetSizerAndFit(box)
        self.refresh(None)
    
    
    def on_erase_background(self, evt):
        """Redraws the background image"""
        dc = evt.GetDC()
 
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.background_bitmap, 0, 0)
    
    def set_all_enabled(self, bool):
        """Enables or disables all components"""
        if bool:
            self.user_lbl.Enable()
            for i in self.sensors:
                i.Enable()
            for c in self.all_components:
                c.Enable()
            
        else:
            for i in self.sensors:
                i.Disable()
            for c in self.all_components:
                c.Disable()
    
    def update_gauges(self):
        """Updates the values of gauges and labels"""
        mgr = self.manager
        self._battery_gge.SetValue(mgr.battery_level)
        self._wireless_gge.SetValue(mgr.wireless_signal)
        self._sampling_rate_txt.SetLabel("128")
        self._num_channels_txt.SetLabel("18")   
                    
    
    def refresh(self, arg=None):  # ARG argument is unused
        """Updates the components based on the manager's state"""
        has_user = self.manager.has_user
        if has_user is not self.manager_state:
            self.manager_state = has_user
            if self.manager.has_user:
                self.update_gauges()
                for c in self.all_components:
                    c.Enable()
                
                #self.user_lbl.SetLabel("Headset Connected")
                self.set_all_enabled(True)
                self.background_bitmap = self.enabled_img

            else:
                self.set_all_enabled(False)
                self.background_bitmap = self.disabled_img
                # A few fix-ups:
                self._sampling_rate_txt.SetLabel("--")
                self._num_channels_txt.SetLabel("--")
                self._battery_gge.SetValue(0)
                self._wireless_gge.SetValue(0)
            self.Update()




