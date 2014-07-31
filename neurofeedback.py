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

class Emotiv ():
    #code
    def __init__(self ):
        self._connected = False
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, bool):
        if self.connected() == bool
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
                    self._connected = True
                else:
                    self._connected = False
            else:
    
    if libEDK.EE_EngineConnect("Emotiv Systems-5") != 0:
        print "Emotiv Engine start up failed."
    


class EEG_Sampler( Thread ):
    """A class that samples EEG data from the Emotive set at a given precision"""
    def __init__(self, rate = 1000):
        self.rate = rate
    
