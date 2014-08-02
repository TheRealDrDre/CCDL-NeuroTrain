#!/usr/bin/env python

# Neurofeedback GUI

import wx
import ccdl
from manager import EmotivManager, ManagerWrapper


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
                              monitored_events=(ccdl.CONNECTION_EVENT))
    
    def create_objects(self):
        """Creates the internal objects"""
        self.connect_btn = wx.Button(self, 12, "Connect to the Headset", (20, 20))
        self.disconnect_btn = wx.Button(self, 11, "Disconnect from Headset", (20, 20))
        
        spin = wx.SpinCtrlDouble(self, -1, min=1.0, max=100.0, inc=0.1)
        spin.SetValue(1.0)
        
        text = wx.StaticText(self, -1,
                            "Sampling interval (in seconds)",
                            (25, 15))
        self.sampling_interval_spn = spin
        self.sampling_interval_lbl = text
        
        spin = wx.SpinCtrl(self, -1)
        spin.SetRange(1, 100)
        spin.SetValue(1)
        
        text = wx.StaticText(self, -1,
                            "Monitoring Interval (in seconds)",
                            (25, 15))
        
        self.quality_check_interval_spn = spin
        self.quality_check_interval_lbl = text
        
    
    def do_layout(self):
        """Lays out the components"""
                 
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.connect_btn)
        self.connect_btn.SetDefault()
        self.connect_btn.SetSize(self.connect_btn.GetBestSize())
        
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.disconnect_btn)
        self.disconnect_btn.SetSize(self.connect_btn.GetBestSize())
        
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.quality_check_interval_lbl)
        box1.Add(self.quality_check_interval_spn)

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
            
            self.quality_check_interval_lbl.Disable()
            self.quality_check_interval_spn.Disable()
            
            self.sampling_interval_lbl.Disable()
            self.sampling_interval_spn.Disable()
            
        else:
            # If we have a manager, then we can should load the interval
            # parameters first
            
            val = self.manager.monitor_interval
            self.quality_check_interval_spn.SetValue(val)
            
            val = self.manager.sampling_interval
            self.sampling_interval_spn.SetValue(val)
            
            # Now we enable/disable buttons based on connection 
            if self.manager.connected:
                # If connected, the only option is Disconnect
                self.connect_btn.Disable()
                self.disconnect_btn.Enable()
                
                # And the parameters cannot be changed
                self.quality_check_interval_lbl.Disable()
                self.quality_check_interval_spn.Disable()
                
                self.sampling_interval_lbl.Disable()
                self.sampling_interval_spn.Disable()
                
            else:
                # If disconnected, the only option is Connect
                self.connect_btn.Enable()
                self.disconnect_btn.Disable()
                
                # When disconnected, parameters can be changed 
                self.quality_check_interval_lbl.Enable()
                self.quality_check_interval_spn.Enable()
                
                self.sampling_interval_lbl.Enable()
                self.sampling_interval_spn.Enable()

    def on_connect(self, event):
        """Handles the connection events"""
        print "on_connect %s" % event.GetId()
        if (event.GetId() == 12):
            try:
                self.manager.connect()
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
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                        )
                dlg.ShowModal()
                dlg.Destroy()
                
        self.refresh()
            

class UserPanel(ManagerPanel):
    """A Class that visualizes the user and its sensors"""
    
    def create_objects(self):
        """Creates the objects"""
        self.user_lbl = wx.StaticText(self, -1, "No User Found")
        self.sensors = {}
        
    def do_layout(self):
        """Lays out the components"""
        box = wx.StaticBox(self, -1, "User")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        bsizer.Add(self.user_lbl)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(bsizer, 0, wx.ALL | wx.EXPAND, 25)
        
        self.SetSizer(sizer)
        
        
        
    
class NeuroTrainFrame(wx.Frame, ManagerWrapper):
    """The main frame"""
    
    def __init__(self, parent, title):
        """Inits the frame"""
        super(NeuroTrainFrame, self).__init__(parent, title=title, size=(250, 200))
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
        """Really, does nothing here"""
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.connect_panel)
        box.Add(self.user_panel)
        
        metabox = wx.BoxSizer(wx.HORIZONTAL)
        metabox.Add(box, wx.ALIGN_CENTER, 10)
        self.SetSizer(metabox)


if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
