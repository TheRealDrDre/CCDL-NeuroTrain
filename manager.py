## ----
## Python GUI for neurofeedback

from threading import Thread
import ctypes
import sys
import os
from ctypes import *
from numpy import *
from variables import *
import time
from ctypes.util import find_library

print ctypes.util.find_library('edk.dll')  
print os.path.exists('.\\edk.dll')
libEDK = cdll.LoadLibrary(".\\edk.dll")

# Here a thread that collects data

class EmotivManager ():
    #code
    def __init__(self ):
        self._connected = False # Whether connected or not
        self._sampling = False  # Whether sampling or not
        self._sampling_interval = 1      # Sampling interval in secs
        
        ## Emotive C structures
        eEvent      = libEDK.EE_EmoEngineEventCreate()
        eState      = libEDK.EE_EmoStateCreate()
        userID      = c_uint(0)
        nSamples   = c_uint(0)
        nSam       = c_uint(0)
        nSamplesTaken  = pointer(nSamples)
        da = zeros(128,double)
        data     = pointer(c_double(0))
        user                    = pointer(userID)
        composerPort          = c_uint(1726)
        secs            = c_float(1)
        datarate        = c_uint(0)
        readytocollect  = False
        option      = c_int(0)
        state     = c_int(0)
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, bool):
        self._connected = bool
    
    def Connect(self):
        """Attempts a connection to the headset"""
        if self.connected == bool
            # If trying to connect while connected, or trying
            # to disconnect while disconnected, do nothing
            pass            
        else:
            if bool:
                # If trying to connect while disconnected, then
                # attempt to connect to an Emotive engine
                conn = libEDK.EE_EngineConnect("Emotiv Systems-5")
                
                # If the result is 0, the connection was successful.
                # If not, we failed, and we need to set connected back
                # to False
                if conn == 0:
                    self.connected = True
                else:
                    self.connected = False
            else:
    
    def Disconnect(self,):
        """Disconnects from the EmoEngine"""
        if self.connected:
            conn = libEDK.EE_EngineDisconnect()
            if conn == 0:
                self.connected = False
            else:
                raise Exception("Cannot disconnect from EmoEngine")


    @property
    def sampling(self):
        """Returns whether the object is currently sampling or not"""
        return self._sampling
    
    @sampling.setter
    def sampling(self, bool):
        """Sets the sampling state"""
        if self.sampling:
            if bool:
                # Should throw exception here---
                # Cannot start a second sampling thread!
                pass   
            else:
                # This means we are stoppin data sampling
                self._sampling = bool
        else:
            if bool:
                self._sampler = Thread(self.Sample)
                # Here we start the thread
                self._sampler.start()
        
    def Sample(self):
        if self.sampling:
            # Acquires data here
            # ...
            # And then notifies some other object (GUI) that
            # will analyze the data properly.
            # ...
            # And then sleep!
            time.sleep(self.interval)
    
        
    def __del__(self):
        """Frees memory when destroying the object"""
        libEDK.EE_EmoStateFree(self.eState)
        libEDK.EE_EmoEngineEventFree(self.eEvent)

