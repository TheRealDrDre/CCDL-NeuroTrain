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


__all__ = ["EmotiveManager", "ConnectionError", "LibraryNotFoundError",
           "ManagerWrapper"]

EDK_DLL_PATH = ".\\edk.dll"

CCDL_USER_EVENT = 1001
CCDL_SAMPLING_EVENT = 1002
CCDL_CONNECTION_EVENT = 1003

CCDL_EVENTS = (CCDL_USER_EVENT, CCDL_SAMPLING_EVENT,
               CCDL_CONNECTION_EVENT)

class ConnectionError(Exception):
    """A specific error when the DLL is not found"""
    def __init__(self, path):
        #super(LibraryNotFoundError, self).__init__(self, args=path)
        self.path = path
    
    def __str__(self):
        return "Cannot connect to any EmotiveEngine using %s" % self.path


class LibraryNotFoundError(Exception):
    """A specific error when the DLL is not found"""
    def __init__(self, path):
        #super(LibraryNotFoundError, self).__init__(self, args=path)
        self.path = path
    
    def __str__(self):
        return "Cannot find library at path %s" % self.path


class Sensor(object):
    """An abstraction for a sensor"""
    def __init__(self, name="", id=0, position=(0,0,0),
                 connected=False, included=False):
        self.name = name
        self.id = id
        self.position = position
        self.connected = connected
        self.included = included

class Headset():
    """An abstraction of an headset"""
    def __init__(self):
        pass   # Still unimplemented

class EmotivManager ():
    #code
    def __init__(self ):
        self.edk = None
        self.edk_loaded = False
        self.load_edk()
        self._connected = False # Whether connected or not
        self._has_user = False # Whether there is a user or not
        self._sampling = False  # Whether sampling or not
        self._sampling_interval = 1      # Sampling interval in secs
        self._monitor_interval = 2.0
        self._listeners = zip(CCDL_EVENTS, [[] for i in CCDL_EVENTS])
        
        ## Emotive C structures
        ##
        ## *** NOTE!!! ***
        ## These structures should be re-allocated every single time
        ## a connection is made, RIGHT BEFORE connecting.  They depend
        ## on some parameters (like sampling rate) that should be settable
        ## from the GUI.  To set them properly, one should always disconnect
        ## first and then reconnect with new parameters
        ## The structures should be de-allocated (with self.cleanup()) only
        ## when one is completely done, and no further connection can be
        ## pursued (e.g., when the manager is deleted or the main window
        ## exits)
        
        self.eEvent      = self.edk.EE_EmoEngineEventCreate()
        self.eState      = self.edk.EE_EmoStateCreate()
        self.userID      = c_uint(0)
        self.nSamples   = c_uint(0)
        self.nSam       = c_uint(0)
        self.nSamplesTaken  = pointer(self.nSamples)
        self.da = zeros(128,double)
        self.data     = pointer(c_double(0))
        self.user                    = pointer(self.userID)
        self.composerPort          = c_uint(1726)
        self.secs            = c_float(1)
        self.datarate        = c_uint(0)
        self.option      = c_int(0)
        self.state     = c_int(0)
    
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
        self._connected = val
    
    def Connect(self):
        """Attempts a connection to the headset"""
        if self.connected:
            # If trying to connect while connected, do nothing
            pass            
        else:
            # If trying to connect while disconnected, then
            # attempt to connect to an Emotive engine
            conn = self.edk.EE_EngineConnect("Emotiv Systems-5")
            
            if conn == 0:
                # If the result is 0, the connection was successful.
                self.connected = True
                
            else:
                # If not, we failed, and we need to set connected back
                # to False and raise an Error
                self.connected = False
                raise ConnectionError(EDK_DLL_PATH)


    def Disconnect(self):
        """Disconnects from the EmoEngine"""
        if self.connected:
            conn = self.edk.EE_EngineDisconnect()
            #self.edk.EE_EmoStateFree(self.eState)
            #self.edk.EE_EmoEngineEventFree(self.eEvent)
            if conn == 0:
                self.connected = False
            else:
                raise Exception("Cannot disconnect from EmoEngine")


    @property
    def sampling_interval(self):
        """Returns the sampling interval"""
        return self._sampling_interval
    
    @sampling_interval.setter
    def sampling_interval(self, val):
        """Sets the sampling interval"""
        self._sampling_interval = val

    @property
    def sampling(self):
        """Returns whether the object is currently sampling or not"""
        return self._sampling
    
    @sampling.setter
    def sampling(self, bool):
        """Sets the sampling state"""
        if self.has_user:
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
        """Samples data from the headset every sampling interval"""
        if self.has_user and self.sampling:
            # Acquires data here
            # ...
            # And then notifies some other object (GUI) that
            # will analyze the data properly.
            # ...
            # 
            # And then sleep!
            time.sleep(self.sampling_interval)
            
    
    @property
    def sensor_quality_interval(self):
        return self._monitor_interval
    
    @sensor_quality_interval.setter
    def sensor_quality_interval(self, val):
        self._monitor_interval = val

    
    def Monitor(self):
        if self.connected:
            state = self.edk.EE_EngineGetNextEvent(eEvent)
            if state == 0:
                eventType = self.edk.EE_EmoEngineEventGetType(self.eEvent)
                self.edk.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                if eventType == variables.EE_UserAdded: 
                    print "User added"
                    libEDK.EE_DataAcquisitionEnable(userID,True)
                    self.has_user = False
                    # Here it should check the status of the given electrodes
                    #
                    # And then notify some other object (maybe subclass method?)
                    #
                    # And then sleep
                elif eventType == variables.EE_UserRemoved:
                    self.has_user = False
                    # Disconnect
        time.sleep(self.monitor_interval)

    @property
    def has_user(self):
        return self._has_user
    
    @has_user.setter
    def has_user(self, val):
        """Sets the user (only if the manager is already connected)"""
        if self.connected:
            self._has_user = val
        else:
            # here should raise some exceptions
            pass
    
    ## EVENTS MODEL
    
    def AddListener(id, obj):
        """Adds a listener"""
        if id in CCDL_EVENTS:
            if obj is not None and "refresh" in obj.__dict__:
                if obj not in self._listeners[id]:
                    self._listeners.Add(obj)

    def cleanup(self):
        """Cleanly removes C++ allocated objects"""
        self.edk.EE_EmoStateFree(self.eState)
        self.edk.EE_EmoEngineEventFree(self.eEvent)
        
    def __del__(self):
        """Disconnects before destroying the object"""
        if self.connected:
            conn = self.edk.EE_EngineDisconnect()
            self.cleanup()
            
            
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
