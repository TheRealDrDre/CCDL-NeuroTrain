## ----
## Python GUI for neurofeedback

from threading import Thread
import ctypes
import sys
import os
import ccdl
from ctypes import *
from numpy import *
import variables
import time
import types
from ctypes.util import find_library


__all__ = ["EmotivManager", "ConnectionError", "LibraryNotFoundError",
           "ManagerWrapper"]

EDK_DLL_PATH = ".\\edk.dll"


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

class EmotivManager(object):
    #code
    def __init__(self ):
        self.edk = None
        self.edk_loaded = False
        self.load_edk()
        self._connected = False # Whether connected or not
        self._has_user = False # Whether there is a user or not
        self._sampling = False  # Whether sampling or not
        self._sampling_interval = 1      # Sampling interval in secs
        self._monitoring = False
        self._monitor_interval = 0.5
        self._listeners = dict(zip(ccdl.EVENTS, [[] for i in ccdl.EVENTS]))
        
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
            
            # Sets the correct values for the EDK and EmoState functions
            self.edk.EE_EmoEngineEventCreate.restype = c_void_p

            self.edk.EE_EmoEngineEventGetEmoState.argtypes = [c_void_p,
                                                              c_void_p]
            self.edk.EE_EmoEngineEventGetEmoState.restype = c_int

            self.edk.ES_GetTimeFromStart.argtypes = [c_void_p]
            self.edk.ES_GetTimeFromStart.restype = c_float

            self.edk.EE_EmoStateCreate.restype = c_void_p

            self.edk.ES_GetWirelessSignalStatus.restype = c_int
            self.edk.ES_GetWirelessSignalStatus.argtypes = [c_void_p]

            self.edk.ES_ExpressivIsBlink.restype = c_int
            self.edk.ES_ExpressivIsBlink.argtypes = [c_void_p]

            self.edk.ES_AffectivGetEngagementBoredomScore.restype = c_float
            self.edk.ES_AffectivGetEngagementBoredomScore.argtypes = [c_void_p]
            
            self.edk.ES_GetBatteryChargeLevel.restype = c_void_p
            self.edk.ES_GetBatteryChargeLevel.argtypes = [c_void_p, 
                                                          POINTER(c_int),
                                                          POINTER(c_int)]

            # Finally, flag the library as loaded.
            self.edk_loaded = True
        else:
            raise LibraryNotFoundError(EDK_DLL_PATH)
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, val):
        self._connected = val
    
    def connect(self):
        """Attempts a connection to the headset"""
        if self.connected:
            # If trying to connect while connected, do nothing
            pass            
        else:
            # If trying to connect while disconnected, then
            # attempt to connect to an Emotive engine
            conn = self.edk.EE_EngineConnect("Emotiv Systems-5")
            
            if conn == variables.EDK_OK:
                # If the result is 0, the connection was successful.
                self.connected = True
                
                #eventType = self.edk.EE_EmoEngineEventGetType(self.eEvent)
                #print "State after connect: %d" % eventType
                
            else:
                # If not, we failed, and we need to set connected back
                # to False and raise an Error
                self.connected = False
                raise ConnectionError(EDK_DLL_PATH)


    def disconnect(self):
        """Disconnects from the EmoEngine"""
        if self.connected:
            conn = self.edk.EE_EngineDisconnect()
            
            #self.edk.EE_EmoStateFree(self.eState)
            #self.edk.EE_EmoEngineEventFree(self.eEvent)
            if conn == variables.EDK_OK:
                # If the disconnection was successful
                self.connected = False
            else:
                raise Exception("Cannot disconnect from EmoEngine")
            
            # Either way, we should stop sampling
            self.monitoring = False


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
                    # Prepares the data buffer
                    self.hData = self.edk.EE_DataCreate()
                    self.edk.EE_DataSetBufferSizeInSec(c_float(self.sampling_interval))  # This needs to change to sampling interval
                    
                    # Here we start the thread
                    self._sampler = Thread(self.sample)
                    self._sampler.start()
        
    def sample(self):
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
    def monitor_interval(self):
        """Returns the current monitor interval"""
        return self._monitor_interval
    
    @monitor_interval.setter
    def monitor_interval(self, val):
        """Sets the monitor_interval to val"""
        self._monitor_interval = val

    @property
    def monitoring(self):
        """Returns True if the app is monitoring the headset,
        and False otherwise"""
        return self._monitoring

    @monitoring.setter
    def monitoring(self, bool):
        "Sets the monitoring state"
        #print "Setting the monitoring property: %s" % bool
        if self._monitoring:
            if bool:
                # Should throw exception here---
                # Cannot start a second monitoring thread!
                pass
            else:
                # This means we are stopping monitorng
                self._monitoring = False
        else:
            if bool:
                self._monitoring = True
                self._monitor = Thread(target=self.monitor)
                # Here we start the thread
                self._monitor.start()
    
    
    def monitor(self):
        """The one function that continuously monitors the status of a
        headset (and whether a user is connected or not)"""

        counter = 0
        
        while self.monitoring:
            
            # Retrieves the next event
            state = self.edk.EE_EngineGetNextEvent(self.eEvent)
            print "[%d] Checked state: %s" % (counter, state)

            if state == variables.EDK_OK:
                # If we received an event, it means that we must have an user
                # (unless the event was UserRemoved)
                if not self.has_user:
                    self.has_user = True
                    
                    
                # if the call was successful, then we do have a new
                # event, and we now need to examine its type.
                
                eventType = self.edk.EE_EmoEngineEventGetType(self.eEvent)
                
                if eventType == variables.EE_User_Added:   # Code 16, 0x0010
                    print "[%d] User added" % counter
                    self.edk.EE_EmoEngineEventGetUserId(self.eEvent, self.user)

                    print "\t User: %s" % self.userID
                    
                    # This function is actually for sampling
                    
                    #self.edk.EE_DataAcquisitionEnable(self.userID, True)                    
                    
                    # Here it should check the status of the given electrodes
                    #
                    # And then notify some other object (maybe subclass method?)
                    #
                    # And then sleep
                
                elif eventType == variables.EE_User_Removed:
                    print "[%d] User removed" % counter
                    self.has_user = False
                    
                elif eventType == variables.EE_EmoState_Updated:
                    print "[%d] EmoState updated: (%d)"  % (counter, eventType)
                    
                    self.edk.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                    print "\tFor user: %s" %self.userID
                    code = self.edk.EE_EmoEngineEventGetEmoState(self.eEvent, self.eState)
                    head = self.edk.ES_GetHeadsetOn(self.eState)
                    num = self.edk.ES_GetNumContactQualityChannels(self.eState)
                    t = self.edk.ES_GetTimeFromStart(self.eState)
                    level = c_int(0)
                    max_level = c_int(10)
                    plevel = pointer(level)
                    pmax_level = pointer(max_level)
                    k = self.edk.ES_GetBatteryChargeLevel(self.eState, plevel, pmax_level)
                    sr = c_uint(0)
                        
                    self.edk.EE_DataGetSamplingRate(self.userID, pointer(sr))
                    print("\tSamping rate: %s" % sr)
                    print "\tCode: %d, %s" % (code, code is variables.EDK_OK)
                    print "\tHeadset on: %d" % head
                    print "\tNum of channels: %d" % num
                    print "\tTime from start: %10.3f/%s" % (t, t)
                    print "\tBattery: %s/%s" % (level.value, max_level.value)
                
                else:
                    print "[%d] Unknown event: %d" % (counter, eventType)
            
            elif state == variables.EDK_NO_EVENT:
                # If the state is NO-EVENT, then it likely means that
                # there is no headset connected, and no data can be acquired.
                self.has_user = False
                pass
                #print "[%d] No event" % counter
                
            else:
                # Here should raise an exception (probably).
                print "[%d] Unknown state %d" % (counter, self.state)
                
                
            #print "Sleeping now for %ss" % self.monitor_interval
            time.sleep(self.monitor_interval)
            counter += 1

    @property
    def has_user(self):
        """Whether a user is connected or not"""
        return self._has_user
    
    @has_user.setter
    def has_user(self, val):
        """Sets the user (only if the manager is already connected)"""
        if self.connected:
            # If connected, change the value and notify
            # all the relevant listeners
            self._has_user = val
            self.execute_event_functions(ccdl.USER_EVENT)
            
        else:
            # here should raise some exceptions --- cannot
            # change the user if we are not event connected!
            pass
    
    # ------------------------------------------------------------- #
    # EVENTS MODEL
    # ------------------------------------------------------------- #
    
    def add_listener(self, id, obj):
        """Adds a listener"""
        
        if id in ccdl.EVENTS:
            if type(obj) in (types.FunctionType, types.MethodType):
                if obj not in self._listeners[id]:
                    #print "Adding listener %s" % obj
                    self._listeners[id].append(obj)
            else:
                
                # Maybe throw an exception if it's not a function?
                pass
        else:
            raise ccdl.EventError(event_id)


    def execute_event_functions(self, event_id):
        """Executes all the listener functions associated with a given
        event ID"""
        print self._listeners
        print len(self._listeners[event_id])
        if event_id in ccdl.EVENTS:
            for func in self._listeners[event_id]:
                func()
        else:
            raise ccdl.EventError(event_id)
            

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
    
    def __init__(self, manager=None, monitored_events=()):
        """Sets the manager"""
        self._manager = manager
        self.monitored_events = monitored_events
    
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
        if mngr is not None:
            for i in self.monitored_events:
                mngr.add_listener(self.refresh)
            
        
    @property
    def monitored_events(self):
        return self._monitored_events
    
    @monitored_events.setter
    def monitored_events(self, event_ids):
        print "Setting the monitoring events %s for object %s" % (event_ids, self)
        self._monitored_events = tuple(event_ids)
        if self.manager is not None:
            for i in event_ids:
                self.manager.add_listener(i, self.refresh)
    
    
