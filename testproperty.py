#!/usr/bin/env python

class pikaloo(object):
    def __init__(self, z=0):
        self._zoom = 0
        
    @property
    def zoom(self):
        print "Getting zoom"
        return self._zoom
    
    @zoom.setter
    def zoom(self, val):
        print "Setting zoom"
        self._zoom = val