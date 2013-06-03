from lobbyapp.playerdb.transactions.base import PlayerDatabaseTransaction
from lobbyapp.playerdb.transactions.queues import TRDequeue
from lobbyapp.playerdb.transactions.alpha import TRMatchDodge
from lobbyapp.playerdb.root import PS_QUEUE, PS_NOTHING, PS_ALPHA, PS_GAMMA, PS_BETA
from lobbyapp.eventprocessor.api import ForceToMatch

class TRPlayerOnline(PlayerDatabaseTransaction):    # SYNCHRONOUS
    """
    Process that a player is online, and determine what
    should be done with him.

    This is done by run returning self.Result* class
    """

    def __init__(self, pdb, pid):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid

    def run(self):
        pir = self.pdb.ensure(self.pid)
        if pir.status == PS_GAMMA:
            # player has a game in progress!
            ip, tcp, udp = pir.conn_triple
            mf = ForceToMatch(self.pid, ip, tcp, udp)
            self.pdb.to_eventprocessor.put(mf)

class TRPlayerOffline(PlayerDatabaseTransaction):   # ASYNCHRONOUS
    def __init__(self, pdb, pid):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid

    def run(self):
        print 'TRPlayerOffline(%s)' % self.pid
        pir = self.pdb.ensure(self.pid) # get info about the player

        if pir.status == PS_QUEUE:      # enqueued ....
            # ...dequeue him first
            TRDequeue(self.pdb, self.pid).start(slave=True)
            self.pdb.drop_pid(self.pid)
        elif pir.status == PS_NOTHING:
            self.pdb.drop_pid(self.pid)
        elif pir.status == PS_ALPHA:
            TRMatchDodge(self.pdb, self.pid).start(slave=True)
            self.pdb.drop_pid(self.pid)
        else:
            # he's matching. So far not implemented
            # too bad.
            pass