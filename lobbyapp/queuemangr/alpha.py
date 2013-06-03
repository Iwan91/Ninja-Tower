from time import time

GRACE_PERIOD = 60       # you have a minute to choose characters

class AlphaMatch(object):
    """Object that represents a single alpha match"""
    def __init__(self, qname, team1, team2):
        """
        @param qname: What queue was it organized from?
        @type qname: str
        @param team1: array of team1's PIDs
        @param team2: array of team2's PIDs
        """
        self.started_on = time()

        print 'Match made with %s against %s' % (team1, team2)

        self.team1 = team1      #: list of pids
        self.team2 = team2
        self.qname = qname

        self.picks_team1 = {}   #: pid => hero_name
        self.picks_team2 = {}

        self.lockins_team1 = [] # list of team1 pids that have locked in
        self.lockins_team2 = [] # list of team2 pids that have locked in

        self.invalid = False    # set to True upon a dodge
        # The rationale for invalid is as follows - access to PDB's alpha table
        # is not done in an atomic manner. It may happen that a match that should
        # start is suddenly dodged, but a TRStartMatch has been scheduled to run
        # against it by the thread that is accessing them in an asynchronous manner.
        # Therefore, TRMatchDodge will run first marking it as invalid, and TRStartMatch
        # will later detect it and abort.                                 

    def should_start_due_to_time(self):
        """Returns whether timer has expired and game should forcibly start"""
        return (time() - self.started_on) > GRACE_PERIOD

    def get_those_who_did_not_lock(self):
        """Returns a list of those who haven't locked"""
        a = [x for x in self.team1 if x not in self.lockins_team1]
        b = [x for x in self.team2 if x not in self.lockins_team2]
        return a+b

    def whom_picked_pid(self, pid):
        """Returns name of the character picked by pid. Returns IndexError on invalid"""
        picks = self.picks_team1 if pid in self.team1 else self.picks_team2
        try:
            return picks[pid]
        except KeyError:
            raise IndexError

    def was_dodged(self):
        """Called when this match was dodged and is invalid"""
        self.invalid = True

    def has_everybody_locked_in(self):
        """Has everybody locked in?"""
        return (len(self.lockins_team1) == len(self.team1)) and (len(self.lockins_team2) == len(self.team2))

    def has_picked_hero(self, pid):
        """Returns whether pid has picked a hero"""
        picks = self.picks_team1 if pid in self.team1 else self.picks_team2
        return pid in picks

    def lockin(self, pid):
        """Return True on success, False on fail"""
        lockins = self.lockins_team1 if pid in self.team1 else self.lockins_team2
        if pid in lockins:
            return False

        lockins.append(pid)
        return True

    def get_teammates_for(self, pid):
        """Return list of teammates, including pid
        that are in pid's team"""
        return self.team1 if pid in self.team1 else self.team2

    def can_pick(self, pid, hero):
        """
        Returns whether it is possible for PID for pick
        a hero because he has not been picked yet
        """
        # determine team

        picks = self.picks_team1 if pid in self.team1 else self.picks_team2
        return hero not in picks.values()

    def pick(self, pid, hero):
        """
        Make hero pick a character
        """
        picks = self.picks_team1 if pid in self.team1 else self.picks_team2
        picks[pid] = hero