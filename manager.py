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

#print ctypes.util.find_library('edk.dll')  


__all__ = ["EmotiveManager"]

EDK_DLL_PATH = ".\\edk.dll"

class LibraryNotFoundError(Exception):
    """A specific error when the DLL is not found"""
    def __init__(self, path):
        #super(LibraryNotFoundError, self).__init__(self, args=path)
        self.path = path
    
    def __str__(self):
        return "Cannot find library at path %s" % self.path

# Here a thread that collects data

class EmotivManager ():
    #code
    def __init__(self ):
        self.edk = None
        self.edk_loaded = False
        self.load_edk()
        self._connected = False # Whether connected or not
        self._sampling = False  # Whether sampling or not
        self._sampling_interval = 1      # Sampling interval in secs            
        
        ## Emotive C structures
        eEvent      = self.edk.EE_EmoEngineEventCreate()
        eState      = self.edk.EE_EmoStateCreate()
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
    
    def load_edk(self):
        """Loads the EDK.dll library"""
        if os.path.exists( EDK_DLL_PATH ):
            self.edk = cdll.LoadLibrary( EDK_DLL_PATH )
            self.edk_loaded = True
        else:
            raise LibraryNotFoundError(EDK_DLL_PATH)
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, val):
        self._connected = bool
    
    def Connect(self):
        """Attempts a connection to the headset"""
        if self.connected:
            # If trying to connect while connected, do nothing
            pass            
        else:
            # If trying to connect while disconnected, then
            # attempt to connect to an Emotive engine
            conn = self.edk.EE_EngineConnect("Emotiv Systems-5")
            
            # If the result is 0, the connection was successful.
            # If not, we failed, and we need to set connected back
            # to False
            if conn == 0:
                self.connected = True
            else:
                self.connected = False


    def Disconnect(self):
        """Disconnects from the EmoEngine"""
        if self.connected:
            conn = self.edk.EE_EngineDisconnect()
            self.edk.EE_EmoStateFree(self.eState)
            self.edk.EE_EmoEngineEventFree(self.eEvent)
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
        """Disconnects before destroying the object"""
        if self.connected:
            conn = self.edk.EE_EngineDisconnect()
            self.edk.EE_EmoStateFree(self.eState)
            self.edk.EE_EmoEngineEventFree(self.eEvent)