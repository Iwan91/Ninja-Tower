from struct import pack

class ReportPlayerDied(object):
    def __init__(self, pid):
        self.pid = pid

    def ton(self):
        return pack('<BH', 0, self.pid)

class ReportSkillDeployed(object):
    def __init__(self, pid, skid):
        self.pid = pid
        self.skid = skid

    def ton(self):
        return pack('<BHH', 6, self.pid, self.skid)

class ReportPlayerRevived(object):
    def __init__(self, pid):
        self.pid = pid

    def ton(self):
        return pack('<BH', 1, self.pid)

class ReportPlayerHPChanged(object):
    def __init__(self, pid, hp):
        self.pid = pid
        self.hp = hp

    def ton(self):
        return pack('<BHH', 5, self.pid, self.hp)

class ReportTrackedShotCreated(object):
    def __init__(self, sid, stype, x, y, dx, dy, anim):
        self.sid = sid
        self.stype = stype
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.anim = anim
    def ton(self):
        return pack('<BHHHHffB', 2, self.sid, self.stype, self.x, self.y, self.dx, self.dy, self.anim)

class ReportBuffStatus(object):
    def __init__(self, pid, bid, stacks, expires_in):
        """@param expires_in: deciseconds"""
        self.pid = pid
        self.bid = bid
        self.stacks = stacks
        self.expires_in = expires_in

    def ton(self):
        return pack('<BHHBH', 7, self.pid, self.bid, self.stacks, self.expires_in)

class ReportUntrackedShotCreated(object):
    def __init__(self, sid, stype, x, y, dx, dy, anim):
        self.sid = sid
        self.stype = style
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.anim = anim
    def ton(self):
        return pack('<BHHHHffB', 4, self.sid, self.stype, self.x, self.y, self.dx, self.dy, self.anim)

class ReportShotDestroyed(object):
    def __init__(self, sid):
        self.sid = sid

    def ton(self):
        return pack('<BH', 3, self.sid)
