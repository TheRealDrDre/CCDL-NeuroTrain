#!/usr/bin/env python

import wx
from core.manager import ManagerWrapper

class Recorder(object, ManagerWrapper):
    def store_sensor_data(self, C=len(variables.CHANNELS)):
        """Collects the new data at every monitor interval"""
        
        # Updates the data array
        self.edk.EE_DataUpdateHandle(0, self.hData)
        self.edk.EE_DataGetNumberOfSample(self.hData, self.nSamplesTaken)
        N = self.nSamplesTaken[0]
        
        if N != 0:   # Only if we have collected > 0 samples
            # Create the C-style array for storing the data
            arr = (ctypes.c_double * N)()
            ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))
            
            # Create a numpy array and copy the C-style array
            # data into it.
            data = np.zeros((N, C))
            for sample in range(N):
                for channel in range(C):
                    self.edk.EE_DataGet(self.hData,
                                        variables.CHANNELS[channel],
                                        byref(arr), N)
                    data[sample, channel] = arr[sample]
            
            # Save data into an internal growing array
            self.data_buffer = np.vstack( (self.data_buffer, data) )


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

