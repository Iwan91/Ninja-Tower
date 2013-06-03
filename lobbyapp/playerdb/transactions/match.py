from lobbyapp.playerdb.transactions.base import PlayerDatabaseTransaction
from lobbyapp.playerdb.root import PS_NOTHING

from lobbyapp.eventprocessor.api import MatchEnded

class TRRoundEnded(PlayerDatabaseTransaction):
    """
    Information that a round has ended was received
    """
    def __init__(self, pdb, gugid, statistics_element):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.gugid = gugid
        self.statistics_element = statistics_element

    def run(self):
        print 'TRRoundEnded(%s, ...)' % self.gugid

        # find the match
        matches = [x for x in self.pdb.betagammas if x.gugid == self.gugid]
        try:
            match, = matches
        except ValueError:
            return False

        # remove it from list
        self.pdb.betagammas.remove(match)

        # sign off it's end
        players = match.team1.keys() + match.team2.keys()

        for pid in players:
            pir = self.pdb.ensure(pid)

            pir.betagamma = None
            pir.conn_triple = None
            pir.status = PS_NOTHING

            mf = MatchEnded(pid, self.statistics_element['winner'],
                                 self.statistics_element['status'],
                                 1)

            self.pdb.to_eventprocessor.put(mf)
