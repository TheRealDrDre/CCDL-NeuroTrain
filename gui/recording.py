#!/usr/bin/env python

## --------------------------------------------------------------- ##
## RECORDING.py
## --------------------------------------------------------------- ##
## Defines a few widgets that record EEG data during a session.
## --------------------------------------------------------------- ##

from .gui import ManagerPanel
import core.ccdl as ccdl
import core.variables as var
import os
import time
import threading 
import wx
import numpy as np

wildcard = "EEG raw data (*.eeg)|*.eeg|"     \
           "Text File (*.txt)|*.txt|" \
           "All files (*.*)|*.*"

class TimedSessionRecorder(ManagerPanel):
    """A simple object that just records the data"""
    
    SET_FILENAME = 2001      # ID of the Filename button
    START_RECORDING = 2002   # ID of the Recording button
    ABORT_RECORDING = 2003   # ID of the abort recording button
    
    def __init__(self, parent, manager):
        """Inits a new Timed Session Recoding Panel"""
        ManagerPanel.__init__(self, parent, manager,
                              manager_state=True,
                              monitored_events=(ccdl.USER_EVENT,))
        self.manager.add_listener(ccdl.SAMPLING_EVENT, self.save_sensor_data)
        
    def refresh(self, param):
        """Updates the interface when the user is updated"""
        self.update_interface()
    
    
    def create_objects(self):
        """Creates the objects"""
        self.file_open = False
        self._filename = None
        self.file = None
        self.session_duration = 60
        self._time_left = self.session_duration
        self.samples_collected = 0
        self.recording = False

        self._filename_lbl = wx.StaticText(self, wx.ID_ANY, "Data file:")
        
        self._file_lbl = wx.StaticText(self, wx.ID_ANY, "[No file]", size=(100, 25), 
                                           style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_START|wx.BORDER)
        
        self._file_btn = wx.Button(self, TimedSessionRecorder.SET_FILENAME,
                                   "Set File")

        self._timer_lbl = wx.StaticText(self, wx.ID_ANY, "Session Duration (Mins):",
                                        size=(150, 25))
        
        self._timer_spn = wx.SpinCtrl(self, -1, size=(10,25),
                                        style=wx.SP_VERTICAL)
        
        self._start_btn = wx.Button(self, TimedSessionRecorder.START_RECORDING,
                                    "Start")
        
        self._abort_btn = wx.Button(self, TimedSessionRecorder.ABORT_RECORDING,
                                    "Abort")
        
        self._timeleft_lbl = wx.StaticText(self, wx.ID_ANY, "00:00:00",
                                           size=(200, 80), style=wx.ALIGN_CENTER)
        
        self._timeleft_lbl.SetFont( wx.Font(40, family=wx.FONTFAMILY_DEFAULT,
                                            style=wx.FONTSTYLE_NORMAL, weight=wx.BOLD))
        self._timer_spn.SetRange(1, 100)
        self._timer_spn.SetValue(1)
        
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, self._timer_spn)
        self.Bind(wx.EVT_BUTTON, self.on_start_button, self._start_btn)
        self.Bind(wx.EVT_BUTTON, self.on_abort_button, self._abort_btn)
        self.Bind(wx.EVT_BUTTON, self.on_file_button, self._file_btn)
        
        
    def do_layout(self):
        """Lays out the components"""
        param = wx.StaticBox(self, -1, "Session Parameters")
        parambox= wx.StaticBoxSizer(param, wx.VERTICAL)
        row1 = wx.BoxSizer(wx.HORIZONTAL)
        
        row1.Add(self._filename_lbl, 0, wx.ALL|wx.LEFT, 2)
        row1.Add(self._file_lbl, 1, wx.ALL|wx.CENTER, 2)
        row1.Add(self._file_btn, 0, wx.ALL|wx.RIGHT, 2)
        
        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(self._timer_lbl, 0, wx.ALL|wx.LEFT, 2)
        row2.Add(self._timer_spn, 1, wx.ALL|wx.CENTER, 2)
        row2.Add(self._start_btn, 0, wx.ALL|wx.RIGHT, 2)
        
        row3 = wx.BoxSizer(wx.HORIZONTAL)
        row3.Add(self._timeleft_lbl, 1, wx.ALL|wx.EXPAND, 2)
        row3.Add(self._abort_btn, 0, wx.ALL|wx.LEFT, 2)
        
        box1 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(row1, 1, wx.ALL | wx.EXPAND, 10)
        box1.Add(row2, 1, wx.ALL | wx.EXPAND, 10)
  
        parambox.Add(box1, 1, wx.ALL | wx.EXPAND, 2)
        
        box2 = wx.BoxSizer(wx.VERTICAL)
        box2.Add(parambox, 1, wx.ALL | wx.EXPAND, 10)
        box2.Add(row3, 1, wx.ALL|wx.EXPAND, 10)
    
        self.SetSizerAndFit(box2)
        
        self.update_interface()
    
    def on_spin(self, event):
        """
        Updates the session duration after a user event
        originated from the Spin Control
        """
        self.session_duration = self._timer_spn.GetValue() * 60
        self.time_left = self.session_duration
        
        # Updates the label
        self._timeleft_lbl.SetLabel(self.sec2str(self.time_left))
    
    
    def sec2str(self, num):
        """
        Simple function to transform a number of seconds into
        an equivalent string in the format HH:MM:SS
        """
        h = int(num / (60*60))
        m = int(num / 60)
        s = num % 60
        return "%02d:%02d:%02d" % (h, m, s)
        
    
    def update_interface(self):
        """Updates the interface based on the internal model"""
        self.on_spin(None)
        if self.manager.has_user  or True:  # 'or True' for testing purposes
            self._filename_lbl.Enable()
            self._file_lbl.Enable()
            self._timer_lbl.Enable()
            self._timeleft_lbl.Enable()
            self._timeleft_lbl.Disable()
 
            if self.file_open:
                if self.recording:
                    self._file_btn.Disable()
                    self._timer_spn.Disable()
                    self._start_btn.Disable()
                    self._abort_btn.Enable()
                    self._timeleft_lbl.Enable()
                else:
                    self._file_btn.Enable()
                    self._timer_spn.Enable()
                    self._start_btn.Enable()
                    self._abort_btn.Disable()
                    self._timeleft_lbl.Disable()
            else:
                self._file_btn.Enable()
                self._timer_spn.Enable()
                self._start_btn.Disable()
                self._abort_btn.Disable()
                self._timeleft_lbl.Disable()
        else:
            self._filename_lbl.Disable()
            self._file_lbl.Disable()
            self._file_btn.Disable()
            self._timer_lbl.Disable()
            self._timer_spn.Disable()
            self._start_btn.Disable()
            self._timeleft_lbl.Disable()
            self._abort_btn.Disable()
        
        
    def timer(self):
        """Runs a simple timer that collects data for given time"""
        print("Started timer function")
        while self.recording and self.time_left > 0:
            time.sleep(1)   # Sleeps one second
            self.time_left -= 1
        
        # When the loop ends, warn the user
        # that session has terminated
        dlg = wx.MessageDialog(self,
                               """%d Sample were saved on file %s""" % (self.samples_collected, self.filename),
                               "Recording Session Terminated",
                               wx.OK | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        
        # Automatically resets the counter, closes the files,
        # and updates the user interface
        self.time_left = self.session_duration
        self.recording = False
        self.file.close()
        self.file_open = False
        self.filename = None
        self.update_interface()
    
    def on_start_button(self, event):
        """Starts the recording thread"""
        if self.file_open and not self.recording:
            thread = threading.Thread(group=None, target=self.timer)
            self.recording = True
            thread.start()
        
            # Updates the interface to reflect current changes in the model
            self.update_interface()
    
    def on_file_button(self, event):
        """
        Opens up a file saving dialog when the "File" button is pressed.
        """
        dlg = wx.FileDialog(self, message="Save EEG data as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard=wildcard, style=wx.SAVE)

        dlg.SetFilterIndex(1)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()

        dlg.Destroy()
        self.update_interface()
    
    def on_abort_button(self, event):
        """Aborts a recording session by setting the recording flag to false"""
        print("On abort")
        if self.recording:
            self.recording = False
            
    
    @property
    def filename(self):
        """
        Returns the path of the current file (where data is going
        to be saved)
        """
        return self._filename 
        
    @filename.setter
    def filename(self, name):
        if name is not None:
            try:
                self.init_file( name )
                self._filename = name
                self._file_lbl.SetLabel(name)
            except Exception, e:
                # Should show some dialog here
                pass
        else:
            self._filename = None
            self.file_open = False
            self._file_lbl.SetLabel("[No file]")
        
            
    @property
    def time_left(self):
        """Returns the amount of time left in this session"""
        return self._time_left
        
    @time_left.setter
    def time_left(self, val):
        """Sets the amount of time left in the current session"""
        self._time_left = val
        self._timeleft_lbl.SetLabel( self.sec2str(self._time_left) )
        
    def init_file(self, name):
        """Inits the file sink"""
        self.file = file(name, "w")
        self.file_open = True
        for channel in var.CHANNELS[: -1]:
            self.file.write( "%s\t" % var.CHANNEL_NAMES[channel] )
        self.file.write( "%s\n" % var.CHANNEL_NAMES[-1] )
        
    
    def save_sensor_data(self, data):
        """
        Saves sensory data on a file
        @param data A NumPy SxC array of S samples and C channels
        """
        if self.file_open and self.recording:
            n_samples, n_channels = data.shape
            for s in xrange(n_samples):
                for c in xrange(n_channels - 1):
                    self.file.write("%f\t" % data[s, c])
                self.file.write("%f\n" % data[s, n_channels - 1])
            self.samples_collected += n_samples
        