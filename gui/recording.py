#!/usr/bin/env python

## --------------------------------------------------------------- ##
## RECORDING.py
## --------------------------------------------------------------- ##
## Defines a few widgets that record EEG data during a session.
## --------------------------------------------------------------- ##

from .gui import ManagerPanel
import core.ccdl as ccdl
import wx

class TimedSessionRecorder(ManagerPanel):
    """A simple object that just records the data"""
    
    SET_FILENAME = 2001      # ID of the Filename button
    START_RECORDING = 2002   # ID of the Recording button
    
    def __init__(self, parent, manager):
        """Inits a new Timed Session Recoding Panel"""
        ManagerPanel.__init__(self, parent, manager,
                              manager_state=True,
                              monitored_events=(ccdl.USER_EVENT, ccdl.MONITORING_EVENT))
        self.manager.add_listener(ccdl.SAMPLING_EVENT, self.record_data)
        
    def refresh(self, param):
        pass
    
    def record_data(self, arg):
        """Records data on a file (if the file is set)"""
        if self.file_open:
            pass
    
    def create_objects(self):
        """Creates the objects"""
        self.file_open = False
        self._filename = None
        self.file = None
        self.session_duration = 60
        self.time_left = self.session_duration
        self.samples_collected = 0
        self.recording = False

        self._filename_lbl = wx.StaticText(self, wx.ID_ANY, "---",
                                           size=(100, 25))
        
        self._file_lbl = wx.StaticText(self, wx.ID_ANY, "Anonymous",
                                           size=(100, 25))
        
        self._file_btn = wx.Button(self, TimedSessionRecorder.SET_FILENAME,
                                   "Set File")

        self._timer_lbl = wx.StaticText(self, wx.ID_ANY, "Session Duration (Mins):",
                                        size=(150, 25))
        
        self._timer_spn = wx.SpinCtrl(self, -1, size=(10,25),
                                        style=wx.SP_VERTICAL)
        
        self._start_btn = wx.Button(self, TimedSessionRecorder.START_RECORDING,
                                    "Start")
        
        self._abort_btn = wx.Button(self, TimedSessionRecorder.START_RECORDING,
                                    "Abort")
        
        self._timeleft_lbl = wx.StaticText(self, wx.ID_ANY, "0:00:00",
                                           size=(200, 80))
        
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
        
        box1 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(row1, 1, wx.ALL | wx.EXPAND, 10)
        box1.Add(row2, 1, wx.ALL | wx.EXPAND, 10)
  
        parambox.Add(box1, 1, wx.ALL | wx.EXPAND, 2)
        
        box2 = wx.BoxSizer(wx.VERTICAL)
        box2.Add(parambox, 1, wx.ALL | wx.EXPAND, 10)
        box2.Add(self._timeleft_lbl, 1, wx.ALL|wx.EXPAND, 10)
    
        self.SetSizerAndFit(box2)
        
        self.update_interface()
    
    def on_spin(self, event):
        self.session_duration = self._timer_spn.GetValue() * 60
        self.time_left = self.session_duration
        self._timeleft_lbl.SetLabel(self.sec2str(self.time_left))
    
    def sec2str(self, num):
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
        while recording and self.time_left <= 0:
            time.sleep(1000)   # Sleeps one second
            self.time_left -= 1
        
        # If the loop is interrupted, automatically resets the
        # counter and updates the user interface
        self.time_left = self.session_duration
        self.update_interface()
    
    def on_start_button(self, event):
        """Starts the recording thread"""
        if self.file_open and not self.recording:
            thread = Thread(self.timer)
            self.recording = True
            thread.start()
        
            # Updates the interface to reflect current changes in the model
            update_interface()
    
    def on_abort_button(self, event):
        """Aborts a recording session by setting the recording flag to false"""
        if self.recording:
            self.recording = False
            
    
    @property
    def filename(self):
        return self._filename 
        
    @filename.setter
    def filename(self, name):
        self._filename = name
            
    def init_file(self):
        """Inits the file sink"""
        self.file = File(self.filename, "w")
        self.file_open = True
    
    def save_sensor_data(self, data):
        """Saves sensory data on a file"""
        if self.file_open and recording:
            for i in data[:-1]:
                self.file.write("%03f\t" % i)
            self.file.write("%03f\n" % data[-1])
        