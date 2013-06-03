from time import sleep

from satella.threads import BaseThread

from satella.instrumentation.counters import DeltaCounter, PulseCounter
from satella.instrumentation import CounterCollection


class OpportunisticMatchMaker(BaseThread):
    """
    A worker that determines whether a match can be organized from a
    queue, and it this happens, launches a transaction
    """
    def __init__(self, pdb, rootcc):
        """
        @param pdb: PlayerDatabase
        @param rootcc: Root CounterCollection
        """
        BaseThread.__init__(self)
        self.pdb = pdb

        cc = CounterCollection('match_maker', 
                               description=u'Module that organizes matches from enqueued players')
        self.total_matches_made = DeltaCounter('matches_made', units=u'matches', description=u'total matches made')
        self.matches_dt = PulseCounter('matches_made_p', resolution=60, units=u'matches per minute',
                                       description=u'organized matches per minute')
        cc.add(self.total_matches_made)
        cc.add(self.matches_dt)
        rootcc.add(cc)


    def process(self):
        """Attempts to make a match"""
        from lobbyapp.playerdb.transactions.queues import TRMatchFound

        for queue in self.pdb.qmangr.get_queues():
            if queue.can_make_match():
                if TRMatchFound(self.pdb, queue.qname).start():
                    self.total_matches_made.update(+1)
                    self.matches_dt.update()

    def run(self):
        while not self._terminating:
            self.process()
            sleep(5)