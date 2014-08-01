#!/usr/bin/env python

# Neurofeedback GUI

import wx
from manager import EmotivManager

# As of now, it does nothing at all

class ManagerWrapper(object):
    """An object that contains an EmotivManager"""
    
    def __init__(self, manager=None):
        """Sets the manager"""
        self._manager = manager
    
    def refresh(self):
        """A method that should be called by the manager whenever
        some of its properties change """
        pass
    
    @property
    def manager(self):
        return self._manager
    
    @manager.setter
    def manager(self, mngr):
        self._manager = mngr
    

# CONNECT PANEL
#
# A connect panel manages the connection to EDK through the internal manager.
#
class ConnectPanel(wx.Panel, ManagerWrapper):
    """A Simple Panel that Connects or Disconnects to an Emotiv System"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1,
                         style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.create_objects()
        self.do_layout()
    
    def create_objects(self):
        """Creates the internal objects"""
        self.edk_connect_btn = wx.Button(self, 12, "Connect to the Headset", (20, 20))
        self.edk_disconnect_btn = wx.Button(self, 11, "Disconnect from Headset", (20, 20))
    
    def do_layout(self):
        """Lays out the components"""
                 
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.edk_connect_btn)
        self.edk_connect_btn.SetDefault()
        self.edk_connect_btn.SetSize(self.edk_connect_btn.GetBestSize())
        
        self.Bind(wx.EVT_BUTTON, self.on_connect, self.edk_disconnect_btn)
        self.edk_disconnect_btn.SetSize(self.edk_connect_btn.GetBestSize())
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.edk_connect_btn)
        box.Add(self.edk_disconnect_btn)
        self.SetSizer(box)

    def refresh(self):
        """Refreshes the buttons based on the state of the connection"""
        if self.manager is None:
            # If no manager is found, then no button should be pressed.
            self.edk_connect_btn.Disable()
            self.edk_disconnect_btn.Disable()
            
        else:
            if self.manager.connected:
                # If connected, the only option is Disconnect
                self.edk_connect_btn.Disable()
                self.edk_disconnect_btn.Enable()
            else:
                # If disconnected, the only option is Connect
                self.edk_connect_btn.Enable()
                self.edk_disconnect_btn.Disable()

    def on_connect(self, event):
        """Handles the connection events"""
        print "on_connect %s" % event.GetId()
        if (event.GetId() == 12):
            try:
                self.manager.Connect()
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
                self.manager.Disconnect()
            except Exception as e:
                dlg = wx.MessageDialog(self, "%s" % e,
                                       'Error While Disconnecting',
                                        wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                        )
                dlg.ShowModal()
                dlg.Destroy()
                
        self.refresh()
            

class NeuroTrainFrame(wx.Frame, ManagerWrapper):
    def __init__(self, parent, title):
        super(NeuroTrainFrame, self).__init__(parent, title=title, size=(250, 200))
        self.create_objects()
        self.do_layout()
        self.Show()

    def create_objects(self):
        """Creates and instantiates all the objects that will be referenced
        multiple times in the GUI
        """
        self.manager = EmotivManager()
        connect_panel = ConnectPanel(self)
        ConnectPanel.manager = self.manager
    
    def do_layout(self):
        pass

    def on_connect(self, event):
        """Handles the connection events"""
        pass

if __name__ == '__main__':
    app = wx.App()
    frame = NeuroTrainFrame(None, title="NeuroTrain")
    app.MainLoop()
