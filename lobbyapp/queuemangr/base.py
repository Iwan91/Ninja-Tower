from satella.instrumentation.counters import CallbackCounter
from satella.instrumentation import CounterCollection

class Queue(object):
    """
    A player queue.
    Not thread safe.
    """
    def __init__(self, qname, ppm, rootcc):
        """
        Constructs the queue

        @param qname: queue name identifier
        @type qname: str

        @param ppm: Players required per match of this type
        @type ppm: int

        @param rootcc: Collection counter for queues
        """
        self.qname = qname  #: name of the queue
        self.players_per_match = ppm

        self.players = []   #: pids of players in queue

        # ---------------- instrumentation section
        cc = CounterCollection(self.qname)
        players_counter = CallbackCounter('players', lambda: len(self.players), 
                                          description=u'players waiting in this queue')
        cc.add(players_counter)
        rootcc.add(cc)

    def can_make_match(self):
        return len(self.players) >= self.players_per_match

    def enqueue(self, pid):
        if pid in self.players:
            raise ValueError, 'player already in the queue'

        self.players.append(pid)

    def dequeue(self, pid):
        if pid not in self.players:
            raise ValueError, 'player not in queue'

        self.players.remove(pid)

    def get_pids(self):
        """Return a sequence of PID's - players to make a match"""
        if not self.can_make_match():
            raise ValueError, 'cannot make a match!'

        pps = self.players[:self.players_per_match]
        del self.players[:self.players_per_match]
        return pps