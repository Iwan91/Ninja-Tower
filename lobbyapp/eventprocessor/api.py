class ExternalEvent(object):
    """Base class for events coming from another 
    source than SelectLayer to EventProcessor"""
    def __init__(self, pid):
        self.pid = pid

class MatchFound(ExternalEvent):
    def __init__(self, pid, team1, team2, qname, heroes):
        """@param team1: sequence of logins of players that comprise team1
        @param heroes: sequence of available heroes"""
        self.pid = pid
        self.team1 = team1
        self.team2 = team2
        self.qname = qname
        self.heroes = heroes

class MatchDodged(ExternalEvent):
    """sent to victims of a dodge"""
    def __init__(self, pid, queue):
        self.pid = pid
        self.queue = queue

class HeroPicked(ExternalEvent):
    def __init__(self, pid, login, hero):
        self.pid = pid
        self.login = login
        self.hero = hero

class PlayerLockedIn(ExternalEvent):
    def __init__(self, pid, login):
        self.pid = pid
        self.login = login

class MatchOKAndWillStart(ExternalEvent):
    def __init__(self, pid, target_ip, target_port_tcp, target_port_udp):
        self.pid = pid
        self.target_ip = target_ip
        self.target_port_tcp = target_port_tcp
        self.target_port_udp = target_port_udp

class MatchFAILED(ExternalEvent):
    def __init__(self, pid, code):
        self.pid = pid
        self.code = code

class ForceToMatch(ExternalEvent):
    def __init__(self, pid, target_ip, target_port_tcp, target_port_udp):
        """Player has left the launcher whilst a match was in progress"""
        self.pid = pid
        self.target_ip = target_ip
        self.target_port_tcp = target_port_tcp
        self.target_port_udp = target_port_udp

class MatchEnded(ExternalEvent):
    def __init__(self, pid, victor, mof, last_round):
        self.pid = pid
        self.victor = victor
        self.mof =  mof
        self.last_round = last_round