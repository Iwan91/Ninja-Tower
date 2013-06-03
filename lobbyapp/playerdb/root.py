from satella.threads import Monitor
from satella.instrumentation.counters import PulseCounter, DeltaCounter, CallbackCounter
from satella.instrumentation import CounterCollection

PS_NOTHING = 0  #: offline or not in game or queue or setup
PS_QUEUE = 1    #: player in queue
# alpha -> beta -> gamma -> beta -> gamma -> ... 
PS_ALPHA = 2  #: player arranging a match     " phase alpha "
PS_GAMMA = 3    #: player actively playing    " phase gamma "
PS_BETA = 4    #: break between rounds       " phase beta "

class PlayerDatabase(Monitor):
    """
    Class that monitors what given players are doing,
    without caring about whether they are logged in 
    or not.

    The class must answer following questions:

        - What is given player doing?
            * If he's in a queue, for what kind of match?
            * If he's alpha-ing, from what queue?
    """

    class PlayerInformationRecord(object):
        def __init__(self, pid, login, *args):
            self.pid = pid
            self.login = login
            if len(args) == 0: # Player not queued or matching
                self.status = PS_NOTHING
                self.queue = None       #: present on QUEUE and ALPHA
                self.alpha = None       #: present on ALPHA
                self.match = None
                self.betagamma = None   #: present on GAMMA and BETA

                self.conn_triple = None   #: present on GAMMA - (ip, tcp_port, udp_port) of target server

    def __init__(self, pdbhelper, rootcc, qmangr, to_eventprocessor, cshardmgr_interface):
        """@type pdbhelper: L{lobbyapp.playerdb.api.PDBHelperInterface} implementation.
        @type qmangr: L{lobbyapp.queuemangr.QueueManager}
        @param to_eventprocessor: Queue that can be used to send orders to EventProcessor
        @type to_eventprocessor: L{Queue.Queue}
        @param cshardmgr_interface: interface to CShardMgr
        @type cshardmgr_interface: tuple(str, int)"""
        Monitor.__init__(self)

        self.pirs = {}  #: pid => PlayerInformationRecord

        self.cshardmgr_interface = cshardmgr_interface

        self.pdbhelper = pdbhelper
        self.qmangr = qmangr
        self.alphas = []        # all existing AlphaMatches
        self.betagammas = []    # all existing BetaGammas

        self.to_eventprocessor = to_eventprocessor

        cc = CounterCollection('player_database')
        self.transactions_counter = PulseCounter('transactions', resolution=60,
                                                 units=u'transactions per minute',
                                                 description=u'player database transactions performed')
        alphas_waiting = CallbackCounter('alphas_waiting', self.alphas.__len__,
                                         description=u'matches being prepared')
        betagammas = CallbackCounter('betagammas', self.betagammas.__len__,
                                         description=u'matches being played')
        cc.add(self.transactions_counter)
        cc.add(alphas_waiting)
        cc.add(betagammas)
        rootcc.add(cc)        

    def drop_pid(self, pid):
        """Player with given pid has disconnected and there is no data that
        we need to keep alongside."""
        del self.pirs[pid]

    def applies_for_queue(self, pid):
        """Returns whether pid can be queued"""
        return self.ensure(pid).status == PS_NOTHING


    def ensure(self, pid):
        """Ensures that a PlayerInformationRecord exists for given
        player and returns it."""
        if pid not in self.pirs:
            # get the player's login
            login = self.pdbhelper.get_login_for_pid(pid)
            self.pirs[pid] = self.PlayerInformationRecord(pid, login)

        return self.pirs[pid]