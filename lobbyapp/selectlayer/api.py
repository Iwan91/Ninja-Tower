# Events exported from SelectLayer to EventProcessor
class SelectLayerEvent(object):
    def __init__(self, pid):
        self.pid = pid

class DataArrived(SelectLayerEvent):
    def __init__(self, pid, data):
        SelectLayerEvent.__init__(self, pid)
        self.data = data

class PlayerOnline(SelectLayerEvent):
    pass

class PlayerOffline(SelectLayerEvent):
    pass

# Events exported from EventProcessor to SelectLayer
class EventProcessorEvent(object):
    def __init__(self, pid):
        self.pid = pid

class SendData(EventProcessorEvent):
    def __init__(self, pid, data):
        EventProcessorEvent.__init__(self, pid)
        self.data = data

class PDBHelperInterface(object):
    """PDB helper passed to select layer must implement this
    interface"""

    def authenticate(self, login, password):
        """
        @param login: User login
        @type login: str

        @param password: User password
        @type password: str

        @return: (pid, 0) if credentials are OK
            (-1, None) if credentials are invalid
            (-2, datetime.datetime x) if banned until
        """
        raise NotImplementedError, 'abstract method'

