#!/usr/bin/env python

import wx
from core.manager import ManagerWrapper

class Recorder(object, ManagerWrapper):
    """A simple object that just records the data"""
    def __init__(self, filename):
        self._filename = filename
        self._file_opened = False
    
    @property
    def filename(self):
        return self._filename 
        
    @filename.setter
    def filename(self, name)
        self._filename = name
    
    def init_file(self):
        """Inits the file sink"""
        self._file = File(self.filename, "w")
        self._file_opened = True
    
    def receive_sensor_data(self, data):
        """Saves sensory data on a file"""
        for i in data:
            self.file.write("%03f" % i)
        

class Game(object, ManagerWrapper):
    """A Game is an object that contains and uses analyzers to
    update a simulated world that is visualized on a panel
    """
    def __init__(self, manager=manager, analyzers=[]):
        """Initializes a game"""
        ManagerWrapper.__init__(self, manager)
        self._analyzers = analyzers


class ThetaAlphaVisualizer(wx.Panel):
    pass

