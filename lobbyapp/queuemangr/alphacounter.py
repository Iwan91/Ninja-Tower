from time import sleep

from satella.threads import BaseThread

from satella.instrumentation.exctrack import Trackback

from satella.instrumentation.counters import DeltaCounter, PulseCounter
from satella.instrumentation import CounterCollection


from lobbyapp.eventprocessor.api import MatchOKAndWillStart, MatchFAILED

class AlphaCounter(BaseThread):
    """
    A worker that examines existing alpha matches and makes matches
    if they are OK
    """
    def __init__(self, pdb, rootcc):
        """
        @param pdb: PlayerDatabase
        @param rootcc: Root CounterCollection
        """
        BaseThread.__init__(self)
        self.pdb = pdb

        cc = CounterCollection('alpha_counter', 
                               description=u'Module that creates games from hero picking rooms')
        self.matches_dt = PulseCounter('matches_made', resolution=60, units=u'matches per minute',
                                       description=u'successful allocations')
        self.matches_dt_so = PulseCounter('matches_failed_so', resolution=60, units=u'matches per minute',
                                       description=u'fails to allocate due to shard overload')
        self.matches_dt_fl = PulseCounter('matches_failed_fl', resolution=60, units=u'matches per minute',
                                       description=u'fails to allocate due to other reasons')
        cc.add(self.matches_dt)
        cc.add(self.matches_dt_so)
        cc.add(self.matches_dt_fl)
        rootcc.add(cc)


    def process(self):
        """Attempts to make a match"""
        from lobbyapp.playerdb.transactions.start_match import TRStartMatch

        for alpha in [a for a in self.pdb.alphas if a.should_start_due_to_time() or a.has_everybody_locked_in()]:
            # This access is exempt from atomicity
            from lobbyapp.playerdb.transactions import TRStartMatch
            k = TRStartMatch(self.pdb, alpha).start()
            if isinstance(k, tuple):
                self.matches_dt.update()
                # SUCCESS!!!
                target_ip, target_port_tcp, target_port_udp = k
                for pid in alpha.team1+alpha.team2:
                    mf = MatchOKAndWillStart(pid, target_ip, target_port_tcp, target_port_udp)
                    self.pdb.to_eventprocessor.put(mf)
            elif isinstance(k, str):
                if k == 'shard overload':
                    self.matches_dt_so.update()
                else:
                    self.matches_dt_fl.update()
                # loud failure                    
                for pid in alpha.team1+alpha.team2:
                    mf = MatchFAILED(pid, k)
                    self.pdb.to_eventprocessor.put(mf)
            else:
                pass    # silent failure


    def run(self):
        try:
            while not self._terminating:
                self.process()
                sleep(5)
        except:
            print Trackback().pretty_print()