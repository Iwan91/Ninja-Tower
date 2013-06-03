class BetaGamma(object):
    """
    A concrete, solidified match
    """

    def __init__(self, team1, team2, gugid, qname):
        """
        @param team1: dict (pid => character name)
        """
        self.team1 = team1
        self.team2 = team2
        self.gugid = gugid
        self.qname = qname