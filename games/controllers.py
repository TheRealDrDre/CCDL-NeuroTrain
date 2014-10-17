#!/usr/bin/env python

ALPHA_BAND = (8, 13)
THETA_BAND = (4, 8)
BETA_BAND = (13, 18)

from core.variables import *
from scipy.signal import welch

class SpectrumAnalyzer(object):
    """A class that analyzes spectral activity in EEG time series"""
    def __init__(self, band=ALPHA_BAND, channels=SENSORS, sampling_frequency=128):
        self.band = ALPHA_BAND
        self.channels = channels
        self.sampling_frequency = sampling_frequency
        
    @property
    def band(self):
        """Returns the frequency band"""
        return self._band
    
    @band.setter
    def band(self, val):
        """Sets the frequency band"""
        if len(val) is 2:
            self.band = tuple(val)
            
        else:
            # Should raise an error here
            pass
        
    @property
    def channels(self):
        return self._channels
    
    @channels.setter
    def channels(self, val):
        """Sets the channels that will be used in this analyzer"""
        if type(val) in [types.TupleType, types.ListType]:
            
            # If we have a real list
            if len([x for x in val if x in SENSORS] = len(val):
                
                #if all the values correspond to possible channels
                self._channels = tuple(val)  # Make sure it's a tuple
            
            else:
                
                # Should raise a "Unknown Channel" error or sorts
                pass
        else:
            # Should raise an exception
    
    
    def analyze(data):
        """Returns the frequency for the given channels"""
        ## Do welch periodogram here
        pass
            

class GameController(object):
    """A class that controls an internal world model based on EEG data"""
    def __init__(self):
        self._analyzers = []
        self._world = {}
        self._listeners = []

    def set_world_property(self, property, value):
        pass
    
    def get_world_property(self, property):
        pass

def class AlphaTheta(object):
    """A Simple Alpha Theta Controller"""
    pass
