USER_EVENT = 1001
SAMPLING_EVENT = 1002
CONNECTION_EVENT = 1003
MONITORING_EVENT = 1004

EVENTS = (USER_EVENT, SAMPLING_EVENT, CONNECTION_EVENT, MONITORING_EVENT)


class EventError(Exception):
    """A specific error when the DLL is not found"""
    def __init__(self, event_id):
        #super(LibraryNotFoundError, self).__init__(self, args=path)
        self.event_id = event_id
    
    def __str__(self):
        return "Unknown Event ID: %s" % self.event_id
    
    def __repr__(self):
        return self.__str__()