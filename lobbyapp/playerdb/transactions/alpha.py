from lobbyapp.playerdb.transactions.base import PlayerDatabaseTransaction
from lobbyapp.playerdb.root import PS_QUEUE, PS_NOTHING, PS_ALPHA

from lobbyapp.queuemangr.alpha import AlphaMatch
from lobbyapp.playerdb.transactions.queues import TREnqueue

from lobbyapp.eventprocessor.api import MatchFound, MatchDodged, HeroPicked, PlayerLockedIn


class TRLockIn(PlayerDatabaseTransaction):
    """
    Player has locked in
    """
    def __init__(self, pdb, pid):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid

    def run(self):
        """
        Returns:
            False on transaction failure
            None on success
            2 on hero not picked
        """
        print 'TRLockIn(%s)' % self.pid

        pir = self.pdb.ensure(self.pid)

        if pir.status != PS_ALPHA:
            return False    # not alphaing

        if not pir.alpha.has_picked_hero(self.pid):
            return 2    # hero not picked

        if not pir.alpha.lockin(self.pid):
            return False    # already locked in?

        # inform EVERYBODY
        for teammate in pir.alpha.team1+pir.alpha.team2:
            mf = PlayerLockedIn(teammate,
                                pir.login)
            self.pdb.to_eventprocessor.put(mf)


class TRHeroPick(PlayerDatabaseTransaction):
    """
    Player has picked a hero.
    """
    def __init__(self, pdb, pid, hero):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid
        self.hero = hero

    def run(self):
        """
        Returns:
            False on TransactionError
            None on Success
            2 on Cannot pick - already picked
        """
        print 'TRHeroPick(%s, %s)' % (self.pid, self.hero)

        pir = self.pdb.ensure(self.pid)
        if pir.status != PS_ALPHA:
            return False # not alpha, can't pick

        #if not pir.alpha.can_pick(self.pid, self.hero):
        #    return 2    # cannot pick, already picked

        if self.hero not in self.pdb.pdbhelper.get_available_heroes(self.pid):
            return False    # cannot pick, not available for you

        # Can pick, pick the character
        pir.alpha.pick(self.pid, self.hero)

        # relay to EVERYBODY
        for teammate in pir.alpha.team1+pir.alpha.team2:
            mf = HeroPicked(teammate, pir.login, self.hero)
            self.pdb.to_eventprocessor.put(mf)



class TRMatchDodge(PlayerDatabaseTransaction):
    """
    Player has dodged an alpha.

    The dodger will be removed from the queue, and
    victim players will be put back into their queue
    """
    def __init__(self, pdb, pid):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid

    def run(self):
        print 'TRMatchDodge(%s)' % self.pid

        pir = self.pdb.ensure(self.pid)

        if pir.status != PS_ALPHA:
            return False # not alpha, can't dodge

        # get all match participants
        alpha = pir.alpha
        participants = alpha.team1 + alpha.team2

        # remove the offender and PS_NOTHING him
        participants.remove(self.pid)

        # remove and invalidate the match
        pir.alpha.was_dodged()
        self.pdb.alphas.remove(pir.alpha)

        # null offender's PIR
        pir.status = PS_NOTHING
        pir.alpha = None
        pir.queue = None

        # requeue the victims, inform them that match has been dodged
        for victim in participants:
            vpir = self.pdb.ensure(victim)
            vpir.status = PS_NOTHING
            vpir.alpha = None
            vpir.queue = None
            TREnqueue(self.pdb, victim, alpha.qname).start(slave=True)

            md = MatchDodged(victim, alpha.qname)
            self.pdb.to_eventprocessor.put(md)


class TRMatchFound(PlayerDatabaseTransaction):
    """
    Match was found for a given queue
    """
    def __init__(self, pdb, qname):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.qname = qname

    def run(self):
        print 'TRMatchFound(%s)' % self.qname

        # can the queue make an alpha?
        if not self.pdb.qmangr.queues[self.qname].can_make_match():
            return False

        # get participants, split them in half
        pids = self.pdb.qmangr.queues[self.qname].get_pids()
        if len(pids) % 2 == 0:   # splittable in half exactly
            team1, team2 = pids[:len(pids)/2], pids[len(pids)/2:]
        else:   # must be sandbox
            team1 = pids
            team2 = []

        # Get a brand new 'alpha match' object
        am = AlphaMatch(self.qname, team1, team2)

        for pid in pids:
            # mark folks off
            pir = self.pdb.ensure(pid)
            pir.status = PS_ALPHA
            pir.alpha = am

            # inform them
            mf = MatchFound(pid, 
                           [self.pdb.ensure(pid).login for pid in team1],
                           [self.pdb.ensure(pid).login for pid in team2],
                           self.qname,
                           self.pdb.pdbhelper.get_available_heroes(pid))

            self.pdb.to_eventprocessor.put(mf)

        self.pdb.alphas.append(am)

        return True

