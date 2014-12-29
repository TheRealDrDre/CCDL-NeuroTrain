## ---------------------------------------------------------------- ##
## A generic manager for an Emotive 14-channel wireless EEG
## headset. The manager contains methods for polling and reading
## data in real time
## ---------------------------------------------------------------- ##

from threading import Thread
import ctypes
import sys
import os
import ccdl
from ctypes import *
import numpy as np
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
        self.id = id                 # Numerical ID (see variables.py)
        self.position = position     # 2D Position
        self.connected = connected   # Whether the sensor is connected
        self.included = included     # Whether the sensor is included among the monitored ones.
        self.quality = 0             # Signal (impedence?) quality


class EmotivManager(object):
    """A generic manager for an Emotiv 14-ch headset"""
    def __init__(self ):
        self.edk = None
        self.edk_loaded = False
        self.load_edk()
        self._connected = False # Whether connected or not
        self._has_user = False  # Whether there is a user or not
        self._monitoring = False
        self._monitor_interval = 0.065
        self._headset_connected = False
        
        self._listeners = dict(zip(ccdl.EVENTS, [[] for i in ccdl.EVENTS]))
        
        self._sensor_quality = dict(zip(variables.COMPLETE_SENSORS,
                                    [0] * len(variables.COMPLETE_SENSORS)))
        
        self._battery_level = 0
        self._wireless_signal = variables.EDK_NO_SIGNAL
        
        self._sensor_data = np.zeros((0, len(variables.CHANNELS)),
                                      order="C", dtype=np.double)
        #self._sensor_quality_data = np.zeros((0, len(variables.CHANNELS)),
        #                                      order="C", dtype=np.int)
        
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
        self.da = np.zeros(128,np.double)
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
                self.headset_connected = False
        else:
            if bool:
                self._monitoring = True
                
                # Sets the buffer to collect data
                self.hData = self.edk.EE_DataCreate()
                self.edk.EE_DataSetBufferSizeInSec( c_float(1) ) # self.monitor_interval
                
                # Creates and starts the monitor
                self._monitor = Thread(target=self.monitor)
                self._monitor.start()
    
    
    def monitor(self):
        """The one function that continuously monitors the status of a
        headset (and whether a user is connected or not).
        If sampling is enabled, data will be connected."""

        counter = 0
        
        while self.monitoring:
            
            # Retrieves the next event
            state = self.edk.EE_EngineGetNextEvent(self.eEvent)
            #print "[%d] Checked state: %s %s" % (counter, self.has_user, state)

            if state == variables.EDK_OK:
                # If we received an event, it means that we must have an user
                # (unless the event was UserRemoved)
                
                if not self.has_user:
                    self.has_user = True
                    
                # if the call was successful, then we do have a new
                # event, and we now need to examine its type.
                
                eventType = self.edk.EE_EmoEngineEventGetType(self.eEvent)
                
                if eventType == variables.EE_User_Added:   # Code 16, 0x0010
                    #print "[%d] User added" % counter
                    #if not self.has_user:
                    #    self.has_user = True
                    
                    # Sets the user ID
                    self.edk.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                    self.edk.EE_DataAcquisitionEnable(self.userID,True)
                    
                elif eventType == variables.EE_User_Removed:
                    #print "[%d] User removed" % counter
                    # This never happens...
                    self.has_user = False
                    
                elif eventType == variables.EE_EmoState_Updated:
                    #print "[%d] EmoState updated: (%d)"  % (counter, eventType)
                    
                    self.execute_event_functions(ccdl.MONITORING_EVENT, None)
                    
                    # This is a bunch of quick debug code.
                    self.edk.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                    code = self.edk.EE_EmoEngineEventGetEmoState(self.eEvent, self.eState)
                    #head = self.edk.ES_GetHeadsetOn(self.eState)
                    num = self.edk.ES_GetNumContactQualityChannels(self.eState)
                    t = self.edk.ES_GetTimeFromStart(self.eState)
                    
                    # Monitor Battery Level
                    level = c_int(0)
                    max_level = c_int(10)
                    self.edk.ES_GetBatteryChargeLevel(self.eState, pointer(level), pointer(max_level))
                    self.battery_level = level.value
                    
                    # Monitor Wireless Signal
                    # This is the key marker for connection ---
                    # when the signal is zero, we lost connection
                    self.wireless_signal = self.edk.ES_GetWirelessSignalStatus(self.eState)
                    
                    # Monitor Sampling Rate
                    sr = c_uint(0)
                    self.edk.EE_DataGetSamplingRate(self.userID, pointer(sr))
                    
                    # A simple print report for debug
                    #print("\tSamping rate: %s" % sr)
                    #print "\tCode: %d, %s" % (code, code is variables.EDK_OK)
                    #print "\tHeadset on: %d" % head
                    #print "\tNum of channels: %d" % num
                    #print "\tTime from start: %10.3f" % (t)
                    #print "\tBattery: %s/%s" % (level.value, max_level.value)
                    #print "\tSignal: %s" % (self.wireless_signal)
                
                    # Calls all the functions responsible for collecting data.
                    self.store_sensor_data()     # Sensor data
                    self.store_sensor_quality()  # Contact quality
                    self.store_state_data()      # States (blinks, winks, etc.)
                                    
                else:
                    print "[%d] Other event: %d" % (counter, eventType)
            
            elif state == variables.EDK_NO_EVENT:
                # If the state is NO-EVENT, then it likely means that
                # there is no headset connected, and no data can be acquired.
                
                # *** THAT IS ACTUALLY NOT TRUE!! ***
                #self.has_user = False
                #print "No event"
                pass

            else:
                # Here should raise an exception (probably).
                print "[%d] Unknown state %d" % (counter, self.state)
                
            # After all of this, just sleeps for the amount necessary
            time.sleep(self.monitor_interval)
            counter += 1

    @property
    def headset_connected( self ):
        return self._headset_connected
    
    @headset_connected.setter
    def headset_connected( self, boolean ):
        if boolean != self._headset_connected:
            self._headset_connected = boolean
            self.execute_event_functions( ccdl.HEADSET_FOUND_EVENT, boolean )
    

    ## In the newest model, the monitor contiuously acquires data
    ## and stores it in an internal table, which is dispatched to
    ## the SENSOR_DATA event listeners.
    ##
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
            
            # Save data into an internal array
            self.sensor_data = data
        
    def store_sensor_quality(self):
        """Reads the sensor quality"""
        Q = {}
        for sensor in variables.COMPLETE_SENSORS:
            Q[sensor] = self.edk.ES_GetContactQuality(self.eState, sensor);
            
        self.sensor_quality = Q


    def store_state_data(self):
        """Reads the EmoState data (blinks, winks, etc.)"""
        blink = self.edk.ES_ExpressivIsBlink(self.eState)
        lwink = self.edk.ES_ExpressivIsLeftWink(self.eState)
        rwink = self.edk.ES_ExpressivIsRightWink(self.eState)


    @property
    def has_user(self):
        """Whether a user (a headset) is connected or not"""
        return self._has_user
    
    
    @has_user.setter
    def has_user(self, val):
        """Sets the user (only if the manager is already connected)"""
        if self.connected:
            # If connected, change the value and notify
            # all the relevant listeners
            self._has_user = val
            self.execute_event_functions(ccdl.USER_EVENT, None)
            
        else:
            # here should raise some exceptions --- cannot
            # change the user if we are not event connected!
            pass
    
    
    @property    
    def battery_level(self):
        """The current battery level of a headset"""
        return self._battery_level
    
    @battery_level.setter
    def battery_level(self, val):
        if val != self.battery_level:
            self._battery_level = val
            self.execute_event_functions(ccdl.CONNECTION_EVENT, None)
    
    @property
    def wireless_signal(self):
        """The current strength of the wireless signal"""
        return self._wireless_signal
    
    @wireless_signal.setter
    def wireless_signal(self, val):
        """Sets the current strength of the wireless signal to VAL"""
        if val != self._wireless_signal:
            if self._wireless_signal == variables.EDK_NO_SIGNAL:
                self._wireless_signal = val
                self.has_user = True
                self.headset_connected = True
            
            if val == variables.EDK_NO_SIGNAL:
                self._wireless_signal = val
                self.has_user = False
                self.headset_connected = False
            
            # No need to call this... Headset events and User events wil
            # be called when the has_user and headset_found variables are set
            #self.execute_event_functions(ccdl.CONNECTION_EVENT, None)
    
    @property
    def sensor_quality(self):
        """An array containing the recording quality of each sensor"""
        return self._sensor_quality
    
    @sensor_quality.setter
    def sensor_quality(self, data):
        """Changes the sensor quality values"""
        self._sensor_quality = data
        self.execute_event_functions( ccdl.SENSOR_QUALITY_EVENT, data )
    
    @property
    def sensor_data(self):
        return self._sensor_data
    
    @sensor_data.setter
    def sensor_data(self, data):
        """Updates the sensor data"""
        self._sensor_data = data
        self.execute_event_functions( ccdl.SAMPLING_EVENT, data)
    
    # ------------------------------------------------------------- #
    # EVENTS MODEL
    # ------------------------------------------------------------- #
    
    def add_listener(self, id, obj):
        """Adds a listener"""
        
        if id in ccdl.EVENTS:
            if type(obj) in (types.FunctionType, types.MethodType):
                if obj not in self._listeners[id]:
                    self._listeners[id].append(obj)
            else:
                
                # Maybe throw an exception if it's not a function?
                pass
        else:
            raise ccdl.EventError(id)


    def execute_event_functions(self, event_id, arg):
        """Executes all the listener functions associated with a given
        event ID"""
        if event_id in ccdl.EVENTS:
            for func in self._listeners[event_id]:
                func(arg)
        else:
            raise ccdl.EventError(event_id)
            

    # ------------------------------------------------------------- #
    # CLEAN OBJECT DESTRUCTION
    # ------------------------------------------------------------- #

    def cleanup(self):
        """Cleanly removes C++ allocated objects"""
        self.edk.EE_EmoStateFree(self.eState)
        self.edk.EE_EmoEngineEventFree(self.eEvent)
        self.edk.EE_DataFree(self.hData)
        
    def __del__(self):
        """Disconnects and frees memory before destroying the object"""
        if self.connected:
            self.edk.EE_EngineDisconnect()
            self.cleanup()
            
            
class ManagerWrapper(object):
    """An object that contains an EmotivManager"""
    
    def __init__(self, manager=None, monitored_events=()):
        """Sets the manager"""
        self._manager = manager
        self.monitored_events = monitored_events
    
    def refresh(self, arg):
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
                mngr.add_listener(i, self.refresh)
            
        
    @property
    def monitored_events(self):
        return self._monitored_events
    
    @monitored_events.setter
    def monitored_events(self, event_ids):
        self._monitored_events = tuple(event_ids)
        if self.manager is not None:
            for i in event_ids:
                self.manager.add_listener(i, self.refresh)
    
    
