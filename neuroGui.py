#!/usr/bin/env python

# Neurofeedback GUI

import wx
import ccdl
from variables import *
from manager import EmotivManager, ManagerWrapper


SENSORS = (ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, ED_P7, ED_O1, ED_O2,
           ED_P8, ED_T8, ED_FC6, ED_F4, ED_F8, ED_AF4)

SENSOR_NAMES = {ED_AF3 : "AF3", ED_F7 : "F7", ED_F3 : "F3", ED_FC5 : "FC5",
                ED_T7 : "T7", ED_P7 : "P7", ED_O1 : "O1", ED_O2 : "O2",
                ED_P8 : "P8", ED_T8 : "T8", ED_FC6 : "FC6", ED_F4 : "F4",
                ED_F8 : "F8", ED_AF4 : "AF4"}


SENSOR_POSITIONS = {ED_AF3 : (85, 62), ED_F7 : (37, 113), ED_F3 : (118, 109),
                    ED_FC5 : (67, 146), ED_T7 : (19, 190), ED_P7 : (70, 287),
                    ED_O1 : (114, 336), ED_O2 : (196, 336), ED_P8 : (241, 287),
                    ED_T8 : (291, 190), ED_FC6 : (243, 146), ED_F4 : (192, 109),
                    ED_F8 : (274, 113), ED_AF4 : (224, 62)}

class ManagerPanel(wx.Panel, ManagerWrapper):
    """A subclass for all panels that wraps around an Emotiv Manager"""
    def __init__(self, parent, manager, monitored_events=()):
        wx.Panel.__init__(self, parent, -1,
                         style=wx.NO_FULL_REPAINT_ON_RESIZE)
        ManagerWrapper.__init__(self, manager, monitored_events=monitored_events)
        self.create_objects()
        self.do_layout()
        self.refresh()    
    
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
        
        spin = wx.SpinCtrl(self, -1, min=1, max=10)

        text = wx.StaticText(self, -1,
                            "Sampling interval (in seconds)",
                            (25, 15))
        self.sampling_interval_spn = spin
        self.sampling_interval_lbl = text
        
        spin = wx.SpinCtrlDouble(self, -1, min=0.1, max=0.5, inc=0.1)
        
        
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
        box1.Add(self.monitor_interval_lbl)
        box1.Add(self.monitor_interval_spn)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.sampling_interval_lbl)
        box2.Add(self.sampling_interval_spn)

        box3 = wx.StaticBox(self, -1, "EDK Connection")
        bsizer3 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        bsizer3.Add(self.connect_btn, 0, wx.TOP|wx.LEFT, 10)
        bsizer3.Add(self.disconnect_btn, 0, wx.TOP|wx.LEFT, 10)
        
        box4 = wx.StaticBox(self, -1, "Connection Parameters")
        bsizer4 = wx.StaticBoxSizer(box4, wx.VERTICAL)
        bsizer4.Add(box1, 0, wx.TOP|wx.LEFT, 10)
        bsizer4.Add(box2, 0, wx.TOP|wx.LEFT, 10)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(bsizer3, 1, wx.EXPAND|wx.ALL, 25)
        box.Add(bsizer4, 1, wx.EXPAND|wx.ALL, 25)        
        
        self.SetSizer(box)

    def refresh(self):
        """Refreshes the buttons based on the state of the connection"""
        if self.manager is None:
            # If no manager is found, then no button should be pressed.
            self.connect_btn.Disable()
            self.disconnect_btn.Disable()
            
            self.monitor_interval_lbl.Disable()
            self.monitor_interval_spn.Disable()
            
            self.sampling_interval_lbl.Disable()
            self.sampling_interval_spn.Disable()
            
        else:
            # If we have a manager, then we can should load the interval
            # parameters first
            
            val = self.manager.monitor_interval
            self.monitor_interval_spn.SetValue(val)
            
            val = self.manager.sampling_interval
            self.sampling_interval_spn.SetValue(val)
            
            # Now we enable/disable buttons based on connection 
            if self.manager.connected:
                # If connected, the only option is Disconnect
                self.connect_btn.Disable()
                self.disconnect_btn.Enable()
                
                # And the parameters cannot be changed
                self.monitor_interval_lbl.Disable()
                self.monitor_interval_spn.Disable()
                
                self.sampling_interval_lbl.Disable()
                self.sampling_interval_spn.Disable()
                
            else:
                # If disconnected, the only option is Connect
                self.connect_btn.Enable()
                self.disconnect_btn.Disable()
                
                # When disconnected, and only when disconnected,
                # the interval parameters can be changed 
                self.monitor_interval_lbl.Enable()
                self.monitor_interval_spn.Enable()
                
                self.sampling_interval_lbl.Enable()
                self.sampling_interval_spn.Enable()

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
                dlg = wx.MessageDialog(self, "%s" % e,
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
                
        self.refresh()
            

class SensorPanel(wx.Panel):
    """A small widget that displays the state of a sensor"""
    def __init__(self, parent, sensor_id=0, size=(50, 25)):
        wx.Panel.__init__(self, parent, -1,
                          style=wx.NO_FULL_REPAINT_ON_RESIZE,
                          size=size)
        
        self._sensor_id = sensor_id
        if sensor_id in SENSORS:
            self._sensor_name = SENSOR_NAMES[sensor_id]
        else:
            self._sensor_name = "???"
        self._checkbox = wx.CheckBox(self, -1, self._sensor_name)
        self._sensor_enabled = False
        self._sensor_recording = False  ## Currently unused
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
    

class UserPanel(ManagerPanel):
    """A Class that visualizes the user and its sensors"""
    
    def __init__(self, parent, manager):
        ManagerPanel.__init__(self, parent, manager,
                              monitored_events=(ccdl.USER_EVENT, ccdl.MONITORING_EVENT))
    def create_objects(self):
        """Creates the objects"""
        self.user_lbl = wx.StaticText(self, -1, "No User Found")
        
        # Creates the sensor panel
        self.sensor_panel = wx.Panel(self)
        self.img = wx.Image("images/channels.gif", type=wx.BITMAP_TYPE_GIF)
        img = wx.Image("images/channels.gif", type=wx.BITMAP_TYPE_GIF)
        img = img.ConvertToBitmap()
        wx.StaticBitmap(self.sensor_panel, -1, img, (0, 0))
        
        # Creates the sensors and adds them to the sensor panel
        sensors = [SensorPanel(self.sensor_panel, x) for x in SENSORS]
        self.sensors = tuple(sensors)
        
        
    def do_layout(self):
        """Lays out the components"""
        box = wx.StaticBox(self, -1, "User")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        bsizer.Add(self.user_lbl)
        
        for i in self.sensors:
            i.SetPosition(SENSOR_POSITIONS[i.sensor_id])
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(bsizer, 0, wx.ALL | wx.EXPAND, 25)
        sizer.Add(self.sensor_panel)
        
        
        self.SetSizer(sizer)
    
    def set_all_enabled(self, bool):
        """Enables or disables all components"""
        if bool:
            self.user_lbl.Enable()
            for i in self.sensors:
                i.Enable()
            
        else:
            self.user_lbl.Disable()
            for i in self.sensors:
                i.Disable()
            
    
    def refresh(self):
        if self.manager.has_user:
            self.user_lbl.SetLabel("Headset Connected")
            self.set_all_enabled(True)
        else:
            self.user_lbl.SetLabel("No Headset Found")
            self.set_all_enabled(False)


class NeuroTrainFrame(wx.Frame):
    """The main frame"""
    
    def __init__(self, parent, title):
        """Inits the frame"""
        wx.Frame.__init__(self, parent, title=title, size=(250, 200))
        #ManagerWrapper.__init__()
        self.create_objects()
        self.do_layout()
        self.Show()

    def create_objects(self):
        """Creates and instantiates all the objects that will be referenced
        multiple times in the GUI
        """
        self.manager = EmotivManager()
        self.connect_panel = ConnectPanel(self, self.manager)
        self.user_panel = UserPanel(self, self.manager)
        
        
    def do_layout(self):
        """Lays out the interface"""
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.connect_panel)
        box.Add(self.user_panel)
        
        metabox = wx.BoxSizer(wx.HORIZONTAL)
        metabox.Add(box, wx.ALIGN_CENTER, 10)
        self.SetSizer(metabox)
        
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        
    def on_quit(self, event):
        self.manager.monitoring = False
        #self.manager.has_user = False
        #self.manager.sampling = False
        #self.Close()
        self.Destroy()
        print "Quitting..."
    


if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
