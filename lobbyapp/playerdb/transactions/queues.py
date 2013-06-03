from lobbyapp.playerdb.transactions.base import PlayerDatabaseTransaction
from lobbyapp.playerdb.root import PS_QUEUE, PS_NOTHING, PS_ALPHA

from lobbyapp.queuemangr.alpha import AlphaMatch

from lobbyapp.eventprocessor.api import MatchFound, MatchDodged

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

        pir.status = PS_NOTHING
        pir.alpha = None
        pir.queue = None

        # remove the match for waiting lists
        self.pdb.alphas.remove(alpha)
        alpha.was_dodged()

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

        # append the alpha to lists
        self.pdb.alphas.append(am)


        return True



class TREnqueue(PlayerDatabaseTransaction):    # ASYNCHRONOUS
    """
    Enqueue a player of fail to do so, because
    he's already in (returning False)

    This is done by run returning self.Result* class
    """

    def __init__(self, pdb, pid, qname):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid
        self.qname = qname

    def run(self):
        print 'TREnqueue(%s, %s)' % (self.pid, self.qname)

        try:
            self.pdb.qmangr.queues[self.qname].enqueue(self.pid)
        except ValueError:
            return False

        pir = self.pdb.ensure(self.pid)

        pir.status = PS_QUEUE
        pir.queue = self.qname


class TRDequeue(PlayerDatabaseTransaction):
    def __init__(self, pdb, pid):
        PlayerDatabaseTransaction.__init__(self, pdb)
        self.pid = pid

    def run(self):
        print 'TRDequeue(%s)' % self.pid
        pir = self.pdb.ensure(self.pid)
        if pir.status != PS_QUEUE:
            return False    # not queued - abort

        try:
            self.pdb.qmangr.queues[pir.queue].dequeue(self.pid)
        except ValueError:
            return False

        pir.status = PS_NOTHING
        pir.queue = None
