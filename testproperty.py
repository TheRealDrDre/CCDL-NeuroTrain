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
        
class zumba(pikaloo):
    def __init__(self):
        pikaloo.__init__(self)
        self._monitoring =True
        
    @property
    def monitoring(self):
        print "Getting monitoring..."
        return self._monitoring
    
    @monitoring.setter
    def monitoring(self, val):
        print "Setting monitoring to %s" % val
        self._monitoring = val
        

def same_test():
    mngr = zumba()
    print mngr.monitoring
    print mngr.monitoring
    mngr.monitoring= True
    print "...Set"
    print mngr.monitoring