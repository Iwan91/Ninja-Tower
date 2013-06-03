from random import choice

from satella.channels.sockets import Socket
from satella.channels import FatalException, NonfatalException

from lobbyapp.playerdb.transactions.base import PlayerDatabaseTransaction
from lobbyapp.playerdb.transactions.alpha import TRHeroPick
from lobbyapp.playerdb.root import PS_GAMMA, PS_NOTHING

from socket import SOCK_STREAM, AF_INET, socket, error as SocketError
from lobbyapp.selectlayer.jsonsocket import JSONSocket

from lobbyapp.queuemangr.betagamma import BetaGamma

class TRStartMatch(PlayerDatabaseTransaction):
    """
    Starts a match
    """
    def __init__(self, pdb, startMatch):
        """
        Depends on cshardmgr interfacing, available in PlayerDatabase !

        @param startMatch: AlphaMatch object
        """
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.alpha = startMatch

    def _rollback(self):
        """dequeue all players"""
        # Sign off all players as entering PS_GAMMA
        for pid in self.alpha.team1+self.alpha.team2:
            # sign off players as playing -> GAMMA
            pir = self.pdb.ensure(pid)
            pir.status = PS_NOTHING
            pir.alpha = None
            pir.queue = None        


    def run(self):
        """Returns a tuple (IP, address) on success. Returns a string with
        error code on failure. Returns with False on silent errors"""

        print 'TRStartMatch(%s)' % self.alpha

        if self.alpha.invalid: return False    # cannot make a match - it's been invalidated
        self.pdb.alphas.remove(self.alpha)  # if alpha is valid then it's in the tables

        # Has everybody locked in? If no we need to forcibly lock them in
        if not self.alpha.has_everybody_locked_in():
            for notlocked in self.alpha.get_those_who_did_not_lock():
                # get applicable characters for player
                heroes = self.pdb.pdbhelper.get_available_heroes(notlocked)
                if len(heroes) == 0:    # NO HEROES FOR PLAYER ?!?!?!?!?!?
                    self._rollback()
                    return '%s has no heroes to play with'

                if TRHeroPick(self.pdb, notlocked, choice(heroes)).start(slave=True) != None:
                    self._rollback()
                    return 'picking hero for %s failed'


        # ============= PRECONDITIONS SATISFIED. EVERYBODY ONLINE AND WITH A HERO PICKED

        # Sign off all players as entering PS_GAMMA
        for pid in self.alpha.team1+self.alpha.team2:
            # sign off players as playing -> GAMMA
            pir = self.pdb.ensure(pid)
            pir.status = PS_GAMMA
            pir.alpha = None
            pir.queue = None

        # Ok, so let's examine the match...
            # Here we begin constructing tables
        players = []
        for pid in self.alpha.team1+self.alpha.team2:
            team_no = 0 if pid in self.alpha.team1 else 1
            pd = {
                'login': self.pdb.ensure(pid).login,
                'password': repr(self.pdb.pdbhelper.get_password_for_pid(pid)),
                'character': self.alpha.whom_picked_pid(pid),
                'team': team_no
            }
            players.append(pd)

        bpf = {
            'players': players,
            'map_name': 'Town',
        }


        # Compute the GUGID
        gugid = '.'.join(map(str, self.alpha.team1) + map(str, self.alpha.team2))

        # ALLOCATE THE MATCH!!!
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect(self.pdb.cshardmgr_interface)
        except SocketError:
            self._rollback()
            return 'internal error: no cshard uplink'

        s = JSONSocket(Socket(s))
        s.settimeout(20)

        try:
            s.write({'request': 'allocate-shard',
                     'gugid': gugid,
                     'bpf_chunk': bpf})

            rsp = s.read()
        except (FatalException, NonfatalException):
            self._rollback()
            return 'internal error: cshard replica failure'

        if 'response' not in rsp:
            self._rollback()
            return 'internal error: malformed cshard replica'

        if rsp['response'] == 'recess':
            self._rollback()
            return 'shard overload'


        conntriple = (rsp['tcp-interface'], rsp['tcp-port'], rsp['udp-port'])

        # create BetaGamma object
        team1 = dict([(pid, self.alpha.whom_picked_pid(pid)) for pid in self.alpha.team1])
        team2 = dict([(pid, self.alpha.whom_picked_pid(pid)) for pid in self.alpha.team2])

        bg = BetaGamma(team1, team2, gugid, self.alpha.qname)

        self.pdb.betagammas.append(bg)

        # Set the target server for players
        for pid in self.alpha.team1+self.alpha.team2:
            self.pdb.ensure(pid).conn_triple = conntriple
            self.pdb.ensure(pid).betagamma = bg

        return conntriple