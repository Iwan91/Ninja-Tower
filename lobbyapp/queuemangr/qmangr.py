
from satella.instrumentation import CounterCollection

from lobbyapp.queuemangr.base import Queue 

class QueueManager(object):
    def __init__(self, config, rootcc):
        """
        Initializes queues.

        @param config: a peculiar set of nested dictionaries describing target
            classes. See sample config.json for reference
        @param rootcc: root counter collection
        @param to_eventprocessor: queue linking to EventProcessor
        @type to_eventprocessor: L{Queue.Queue}
        """

        cc = CounterCollection('queues')       

        self.queues = {}    #: dict(queue name => Queue object)
        for qname, qvalue in config.iteritems():
            if 'players_per_match' not in qvalue: raise ValueError, 'config invalid'

            self.queues[qname] = Queue(qname, 
                                       qvalue['players_per_match'],
                                       cc)

        rootcc.add(cc)

    def has_queue(self, qname):
        """Returns whether a queue with given name is available"""
        return qname in self.queues


    def get_queues(self):
        """Returns a sequence of queues"""
        return self.queues.values()